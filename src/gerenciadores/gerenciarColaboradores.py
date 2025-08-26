# Cria listas com colaboradores que: Não tem email pessoal acadastrado, nao tem email corporativo cadastrado, válidos, inválidos
""" 
Usuários válidos tem que ter:
- pelo menos uma matricula com situação diferente de 7
- pelo menos o email pessoal cadastrado
- superior cadastrado.
Caso contrario desses requisitos se torna um usuário inválido, que sera separado por listas de:
- Colaborador totalmente demitido (todas situalções das matriculas do cpf sao 7)
- Colaborador sem email pessoal
- Colaborador sem superior
"""
import logging
import pandas as pd
from datetime import datetime

def classificar_usuarios(usuarios):
    logging.info("Classificando usuarios")
    usuarios['Cpf'] = usuarios['Cpf'].astype(str).str.strip().str.zfill(11)
    usuarios['Situacao'] = usuarios['Situacao'].astype(int)
    usuarios['Situacao_superior'] = usuarios['Situacao_superior'].fillna(0).astype(int)
    usuarios['Data_admissao'] = pd.to_datetime(usuarios['Data_admissao'])
    usuarios['Data_demissao'] = pd.to_datetime(usuarios['Data_demissao'])

    validos = []
    invalidos_demitidos = []
    invalidos_sem_email = []
    invalidos_sem_superior = []
    lista_para_vanessa = []

    cpfs_vanessa = set()

    for cpf, grupo in usuarios.groupby('Cpf'):
        if grupo['Nome'].str.contains("Mittelstadt", case=False).any():
            continue
        if grupo['Superior'].str.contains("Bianca De Oliveira Luiz Mittelstadt", case=False, na=False).any():
            continue

        grupo_ativos = grupo[grupo['Situacao'] != 7]
        todas_demitidas = grupo['Situacao'].eq(7).all()
        tem_email_pessoal = grupo_ativos['Email_pessoal'].notnull().any()
        grupo_ativos_com_superior = grupo_ativos[
            grupo_ativos['Superior'].notnull() & (grupo_ativos['Situacao_superior'] != 7)
        ]
        tem_superior_valido = not grupo_ativos_com_superior.empty

        # Verifica múltiplas admissões
        if len(grupo) > 1:
            grupo_ordenado = grupo.sort_values('Data_admissao')
            admissoes = grupo_ordenado['Data_admissao'].tolist()
            demissoes = grupo_ordenado['Data_demissao'].tolist()
            situacoes = grupo_ordenado['Situacao'].tolist()

            for i in range(len(admissoes) - 1):
                if demissoes[i] != pd.Timestamp('1900-12-31'):
                    intervalo = (admissoes[i+1] - demissoes[i]).days
                    if intervalo < 183 and tem_email_pessoal and tem_superior_valido:
                        tempo1 = (demissoes[i] - admissoes[i]).days
                        tempo2 = (datetime.today() - admissoes[i+1]).days if situacoes[i+1] != 7 else (demissoes[i+1] - admissoes[i+1]).days
                        tempo_total = tempo1 + tempo2
                        grupo_ordenado.loc[:, 'Tempo_empresa_dias'] = tempo_total
                        lista_para_vanessa.append(grupo_ordenado)
                        cpfs_vanessa.add(cpf)
                        break

        grupo['Tempo_empresa_dias'] = (grupo['Data_demissao'] - grupo['Data_admissao']).dt.days
        if todas_demitidas:
            invalidos_demitidos.append(grupo)
        elif not tem_email_pessoal:
            invalidos_sem_email.append(grupo_ativos)
        elif not tem_superior_valido:
            todos_superiores_demitidos = grupo_ativos['Situacao_superior'].eq(7).all()
            if todos_superiores_demitidos:
                grupo_corrigido = grupo_ativos.copy()
                grupo_corrigido = grupo_corrigido.groupby('Cpf', as_index=False).first()
                grupo_corrigido['Superior'] = "Posto de trabalho de superior não ocupado"
                if cpf not in cpfs_vanessa:
                    validos.append(grupo_corrigido)
            else:
                invalidos_sem_superior.append(grupo_ativos)
        else:
            if cpf not in cpfs_vanessa:
                validos.append(grupo_ativos_com_superior)

    colunas = usuarios.columns.tolist() + ['Tempo_empresa_dias']
    return {
        'validos': pd.concat(validos, ignore_index=True) if validos else pd.DataFrame(columns=colunas),
        'invalidos_demitidos': pd.concat(invalidos_demitidos, ignore_index=True) if invalidos_demitidos else pd.DataFrame(columns=colunas),
        'invalidos_sem_email': pd.concat(invalidos_sem_email, ignore_index=True) if invalidos_sem_email else pd.DataFrame(columns=colunas),
        'invalidos_sem_superior': pd.concat(invalidos_sem_superior, ignore_index=True) if invalidos_sem_superior else pd.DataFrame(columns=colunas),
        'lista_para_vanessa': pd.concat(lista_para_vanessa, ignore_index=True) if lista_para_vanessa else pd.DataFrame(columns=colunas)
    }

def verificar_cpfs_repetidos(df):
    cpfs = df['Cpf'].astype(str).str.strip().str.zfill(11)
    cpfs_repetidos = cpfs[cpfs.duplicated()].unique().tolist()
    print(f"> Total de CPFs repetidos encontrados: {len(cpfs_repetidos)}")
    return cpfs_repetidos

def agrupar_por_cpf_df(df_validos):
    df_validos['Cpf'] = df_validos['Cpf'].astype(str).str.strip().str.zfill(11)
    verificar_cpfs_repetidos(df_validos)
    return {cpf: grupo for cpf, grupo in df_validos.groupby('Cpf')}

def processar_cpf_df(cpf, registros_df):
    registros_df['Situacao'] = registros_df['Situacao'].astype(int)
    todas_demitidas = (registros_df['Situacao'] == 7).all()
    registros_ativos = registros_df[registros_df['Situacao'] != 7]

    if len(registros_ativos) > 1:
        logging.warning(f"Inconsistencia: CPF {cpf} com multiplos registros ativos")
        print(f"> CPF {cpf} com {len(registros_ativos)} registros ativos")
        for _, row in registros_ativos.iterrows():
            print(f">  Matrícula - {row['Matricula']} | Situação: {row['Situacao']} | Nome: {row['Nome']} | Email: {row['Email']}")

    return {
        'cpf': cpf,
        'todas_demitidas': todas_demitidas,
        'quantidade_matriculas': len(registros_df),
        'tem_email_pessoal': registros_df['Email_pessoal'].notnull().any(),
        'registros_ativos': len(registros_ativos)
    }
