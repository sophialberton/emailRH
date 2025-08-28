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
from datetime import timedelta

def classificar_usuarios(usuarios, data_simulada=None):
    # Preparação dos dados
    usuarios['Cpf'] = usuarios['Cpf'].astype(str).str.strip().str.zfill(11)
    usuarios['Situacao'] = usuarios['Situacao'].astype(int)
    usuarios['Situacao_superior'] = usuarios['Situacao_superior'].fillna(0).astype(int)
    usuarios['Data_admissao'] = pd.to_datetime(usuarios['Data_admissao'])
    usuarios['Data_demissao'] = pd.to_datetime(usuarios['Data_demissao'])

    # Corrigir demissões inválidas diretamente na coluna original
    usuarios.loc[usuarios['Data_demissao'] < usuarios['Data_admissao'], 'Data_demissao'] = data_simulada

    # Arredondar Tempo_FGM para anos inteiros
    usuarios['Tempo_FGM_anos'] = pd.to_numeric(usuarios['Tempo_FGM'], errors='coerce').round()


    # Listas de classificação
    validos = []
    invalidos_demitidos = []
    invalidos_sem_email = []
    invalidos_sem_superior = []
    invalidos_tempo_fgm_duplicado = []
    lista_para_vanessa = []
    desligado_e_voltou = []
    voltaram_menos_6_meses = []
    voltaram_mais_6_meses = []
    cadastros_menos_6_meses = []
    cadastros_mais_6_meses = []

    for cpf, grupo in usuarios.groupby('Cpf'):
        grupo = grupo.sort_values('Data_admissao')
        grupo_ativos = grupo[grupo['Situacao'] != 7]
        grupo_demitidos = grupo[grupo['Situacao'] == 7]
        tem_multiplas_admissoes = len(grupo) > 1
        tem_registro_ativo = not grupo_ativos.empty

        # Nova lógica de duplicados com base em Tempo_FGM
        grupo_ativos = grupo[grupo['Situacao'] != 7]
        if not grupo_ativos.empty:
            data_admissao_ativa = grupo_ativos.iloc[0]['Data_admissao']
            grupo_duplicado = grupo[(grupo['Data_admissao'] == data_admissao_ativa) & (grupo['Situacao'] == 7)]
            grupo_sem_duplicados = grupo.drop(grupo_duplicado.index)

            if not grupo_duplicado.empty:
                invalidos_tempo_fgm_duplicado.append(grupo_duplicado)

            # Continue o processamento com grupo_sem_duplicados
            grupo = grupo_sem_duplicados


        if tem_multiplas_admissoes and tem_registro_ativo and not grupo_demitidos.empty:
            lista_para_vanessa.append(grupo)
            ultimo_cadastro = grupo.iloc[-1]
            desligado_e_voltou.append(ultimo_cadastro)

            grupo_ordenado = grupo.reset_index(drop=True)
            for i in range(1, len(grupo_ordenado)):
                admissao_atual = grupo_ordenado.loc[i, 'Data_admissao']
                demissao_anterior = grupo_ordenado.loc[i - 1, 'Data_demissao']
                if pd.notnull(demissao_anterior) and pd.notnull(admissao_atual):
                    intervalo = admissao_atual - demissao_anterior
                    destino_lista = (
                        (voltaram_menos_6_meses, cadastros_menos_6_meses)
                        if intervalo < timedelta(days=180)
                        else (voltaram_mais_6_meses, cadastros_mais_6_meses)
                    )
                    destino_lista[0].append(grupo_ordenado.iloc[-1])
                    for _, row in grupo_ordenado.iterrows():
                        if row['Data_admissao'] != row['Data_demissao']:
                            destino_lista[1].append(row)
                    break

        todas_demitidas = grupo['Situacao'].eq(7).all()
        tem_email_pessoal = grupo_ativos['Email_pessoal'].notnull().any()
        grupo_ativos_com_superior = grupo_ativos[
            grupo_ativos['Superior'].notnull() & (grupo_ativos['Situacao_superior'] != 7)
        ]
        tem_superior_valido = not grupo_ativos_com_superior.empty

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
                validos.append(grupo_corrigido)
            else:
                invalidos_sem_superior.append(grupo_ativos)
        else:
            validos.append(grupo_ativos_com_superior)

    colunas = usuarios.columns.tolist()
    return {
        'validos': pd.concat(validos, ignore_index=True) if validos else pd.DataFrame(columns=colunas),
        'invalidos_demitidos': pd.concat(invalidos_demitidos, ignore_index=True) if invalidos_demitidos else pd.DataFrame(columns=colunas),
        'invalidos_sem_email': pd.concat(invalidos_sem_email, ignore_index=True) if invalidos_sem_email else pd.DataFrame(columns=colunas),
        'invalidos_sem_superior': pd.concat(invalidos_sem_superior, ignore_index=True) if invalidos_sem_superior else pd.DataFrame(columns=colunas),
        'lista_para_vanessa': pd.concat(lista_para_vanessa, ignore_index=True) if lista_para_vanessa else pd.DataFrame(columns=colunas),
        'desligado_e_voltou': pd.DataFrame(desligado_e_voltou) if desligado_e_voltou else pd.DataFrame(columns=colunas),
        'voltaram_menos_6_meses': pd.DataFrame(voltaram_menos_6_meses) if voltaram_menos_6_meses else pd.DataFrame(columns=colunas),
        'voltaram_mais_6_meses': pd.DataFrame(voltaram_mais_6_meses) if voltaram_mais_6_meses else pd.DataFrame(columns=colunas),
        'cadastros_menos_6_meses': pd.DataFrame(cadastros_menos_6_meses) if cadastros_menos_6_meses else pd.DataFrame(columns=colunas),
        'cadastros_mais_6_meses': pd.DataFrame(cadastros_mais_6_meses) if cadastros_mais_6_meses else pd.DataFrame(columns=colunas),
        'invalidos_tempo_fgm_duplicado': pd.concat(invalidos_tempo_fgm_duplicado, ignore_index=True) if invalidos_tempo_fgm_duplicado else pd.DataFrame(columns=colunas)
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
