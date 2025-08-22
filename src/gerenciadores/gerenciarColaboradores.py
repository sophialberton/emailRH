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
import re
import pandas as pd

def classificar_usuarios(usuarios):
    logging.info("> Classificando usuarios")
    usuarios['Cpf'] = usuarios['Cpf'].astype(str).str.strip().str.zfill(11)
    usuarios['Situacao'] = usuarios['Situacao'].astype(int)
    usuarios['Situacao_superior'] = usuarios['Situacao_superior'].fillna(0).astype(int)

    validos = []
    invalidos_demitidos = []
    invalidos_sem_email = []
    invalidos_sem_superior = []

    for cpf, grupo in usuarios.groupby('Cpf'):
        logging.debug(f"Processando CPF: {cpf} com {len(grupo)} registros")

        # Ignora qualquer colaborador com "Mittelstadt" no nome
        if grupo['Nome'].str.contains("Mittelstadt", case=False).any():
            logging.debug(f"Ignorando CPF {cpf} por conter 'Mittelstadt' no nome")
            continue

        # Ignora se o superior for "Bianca De Oliveira Luiz Mittelstadt"
        if grupo['Superior'].str.contains("Bianca De Oliveira Luiz Mittelstadt", case=False, na=False).any():
            logging.debug(f"Ignorando CPF {cpf} por ter como superior 'Bianca De Oliveira Luiz Mittelstadt'")
            continue

        grupo_ativos = grupo[grupo['Situacao'] != 7]
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
            invalidos_sem_superior.append(grupo_ativos)
        else:
            validos.append(grupo_ativos_com_superior)

    colunas = usuarios.columns
    return {
        'validos': pd.concat(validos, ignore_index=True) if validos else pd.DataFrame(columns=colunas),
        'invalidos_demitidos': pd.concat(invalidos_demitidos, ignore_index=True) if invalidos_demitidos else pd.DataFrame(columns=colunas),
        'invalidos_sem_email': pd.concat(invalidos_sem_email, ignore_index=True) if invalidos_sem_email else pd.DataFrame(columns=colunas),
        'invalidos_sem_superior': pd.concat(invalidos_sem_superior, ignore_index=True) if invalidos_sem_superior else pd.DataFrame(columns=colunas)
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
