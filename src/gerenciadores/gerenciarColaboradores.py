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

def _preparar_dataframe(usuarios):
    """Prepara o DataFrame para a classificação."""
    usuarios['Cpf'] = usuarios['Cpf'].astype(str).str.strip().str.zfill(11)
    usuarios['Situacao'] = usuarios['Situacao'].astype(int)
    usuarios['Situacao_superior'] = usuarios['Situacao_superior'].fillna(0).astype(int)
    usuarios['Data_admissao'] = pd.to_datetime(usuarios['Data_admissao'])
    usuarios['Data_demissao'] = pd.to_datetime(usuarios['Data_demissao'])
    return usuarios

def _identificar_duplicados(grupo):
    """Identifica e processa colaboradores com múltiplos registros."""
    grupo_ativos = grupo[grupo['Situacao'] != 7]
    if len(grupo) > 1 and not grupo_ativos.empty and any(grupo['Situacao'] == 7):
        demissao_anterior = grupo.loc[len(grupo) - 2, 'Data_demissao']
        admissao_recente = grupo.loc[len(grupo) - 1, 'Data_admissao']
        intervalo = (admissao_recente - demissao_anterior).days
        grupo['Retorno_em_menos_de_6_meses'] = intervalo < 180
        return grupo
    return None

def classificar_usuarios(usuarios):
    logging.info("Classificando usuários...")
    usuarios = _preparar_dataframe(usuarios)

    validos = []
    invalidos_demitidos = []
    invalidos_sem_email = []
    invalidos_sem_superior = []
    cadastros_duplicados = []

    for _, grupo in usuarios.groupby('Cpf'):
        if grupo['Nome'].str.contains("Mittelstadt", case=False).any() or \
           grupo['Superior'].str.contains("Bianca De Oliveira Luiz Mittelstadt", case=False, na=False).any():
            continue

        grupo = grupo.sort_values('Data_admissao').reset_index(drop=True)
        grupo_ativos = grupo[grupo['Situacao'] != 7]
        
        # --- LÓGICA DE CORREÇÃO ---
        # Primeiro, verificar se é um caso de readmissão.
        # Se for, ele vai para a lista de duplicados e não deve entrar na outra classificação.
        if len(grupo) > 1 and not grupo_ativos.empty and any(grupo['Situacao'] == 7):
            demissao_anterior = grupo.loc[len(grupo) - 2, 'Data_demissao']
            admissao_recente = grupo.loc[len(grupo) - 1, 'Data_admissao']
            intervalo = (admissao_recente - demissao_anterior).days
            grupo['Retorno_em_menos_de_6_meses'] = intervalo < 180
            cadastros_duplicados.append(grupo)
        
        # Se não for um caso de readmissão, então ele entra na classificação normal.
        elif grupo['Situacao'].eq(7).all():
            invalidos_demitidos.append(grupo)
        elif not grupo_ativos['Email_pessoal'].notnull().any():
            invalidos_sem_email.append(grupo_ativos)
        elif not (grupo_ativos['Superior'].notnull() & (grupo_ativos['Situacao_superior'] != 7)).any():
            invalidos_sem_superior.append(grupo_ativos)
        else:
            # Garante que apenas o registro mais recente e ativo seja considerado válido
            registro_valido = grupo_ativos.sort_values('Data_admissao', ascending=False).iloc[[0]]
            validos.append(registro_valido)

    return {
        'validos': pd.concat(validos, ignore_index=True) if validos else pd.DataFrame(),
        'invalidos_demitidos': pd.concat(invalidos_demitidos, ignore_index=True) if invalidos_demitidos else pd.DataFrame(),
        'invalidos_sem_email': pd.concat(invalidos_sem_email, ignore_index=True) if invalidos_sem_email else pd.DataFrame(),
        'invalidos_sem_superior': pd.concat(invalidos_sem_superior, ignore_index=True) if invalidos_sem_superior else pd.DataFrame(),
        'cadastros_duplicados': pd.concat(cadastros_duplicados, ignore_index=True) if cadastros_duplicados else pd.DataFrame()
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
