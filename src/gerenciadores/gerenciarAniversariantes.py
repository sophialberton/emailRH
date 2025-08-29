# src/gerenciadores/gerenciarAniversariantes.py
import logging
from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

class gerenciadorAniversariantes:
    def __init__(self):
        pass

    def identificar_aniversariantes_mes_seguinte_duplicados(self, df_duplicados, data_simulada=None):
        """
        [LÓGICA CRUCIAL] Identifica aniversariantes (casos de readmissão) do próximo mês.
        Esta função é o coração da correção para os "B.O.s" de cadastros duplicados.
        """
        data_referencia = data_simulada or datetime.now()
        mes_seguinte = (data_referencia + relativedelta(months=1)).month
        aniversariantes = []

        for cpf, grupo in df_duplicados.groupby('Cpf'):
            if grupo.empty:
                continue
            
            grupo = grupo.sort_values('Data_admissao').reset_index(drop=True)
            nome = grupo.iloc[-1]['Nome']
            email = grupo.iloc[-1]['Email_pessoal']
            primeira_admissao = grupo.iloc[0]['Data_admissao']

            # ✅ Conversão segura para número
            grupo['Tempo_FGM'] = pd.to_numeric(grupo['Tempo_FGM'], errors='coerce')
            tempo_total_anos = round(grupo['Tempo_FGM'].sum())


            # --- PONTO 1: A DATA DE ANIVERSÁRIO É SEMPRE A PRIMEIRA ADMISSÃO ---
            # Independentemente de quantas vezes o colaborador saiu e voltou,
            # a data comemorativa será sempre baseada na sua entrada original na empresa.
            # primeira_admissao = grupo['Data_admissao'].min()

            if primeira_admissao.month == mes_seguinte and tempo_total_anos >= 1:
                aniversariantes.append({
                        'Cpf': cpf,
                        'Nome': nome,
                        'Email': email,
                        'Data_primeira_admissao': primeira_admissao,
                        'Tempo_total_anos': tempo_total_anos
                    })
        
        aniversariantes_df = pd.DataFrame(aniversariantes)
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes (múltiplas admissões) para o próximo mês.")
        return aniversariantes_df

    def identificar_aniversariantes_mes_seguinte(self, df_validos, data_simulada=None):
        """
        [LÓGICA ATUALIZADA] Filtra o DataFrame de 'válidos' para encontrar aniversariantes
        de tempo de casa no próximo mês, considerando apenas a data de admissão mais antiga por CPF.
        """
        data_referencia = data_simulada or datetime.now()
        mes_seguinte = (data_referencia + relativedelta(months=1)).month

        # Agrupa por CPF e pega a admissão mais antiga
        df_validos['Data_admissao'] = pd.to_datetime(df_validos['Data_admissao'])
        df_agrupado = df_validos.sort_values('Data_admissao').groupby('Cpf').first().reset_index()

        # Filtra aniversariantes do mês seguinte
        aniversariantes_df = df_agrupado[df_agrupado['Data_admissao'].dt.month == mes_seguinte].copy()

        # Calcula anos de casa
        aniversariantes_df['Anos_de_casa'] = aniversariantes_df.apply(
            lambda row: (data_referencia - row['Data_admissao']).days // 365,
            axis=1
        )

        # Filtra quem tem pelo menos 1 ano de casa
        aniversariantes_df = aniversariantes_df[aniversariantes_df['Anos_de_casa'] >= 1]

        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes (admissão mais antiga) para o próximo mês.")
        return aniversariantes_df

    # ... (demais funções de identificação, que são mais diretas) ...
    def identificar_aniversariantes_do_dia(self, df_validos, data_simulada=None):
        """Filtra o DataFrame para encontrar aniversariantes de tempo de casa no dia atual."""
        hoje = data_simulada or datetime.now()
        aniversariantes_df = df_validos[
            (df_validos['Data_admissao'].dt.day == hoje.day) &
            (df_validos['Data_admissao'].dt.month == hoje.month)
        ].copy()
        aniversariantes_df['Anos_de_casa'] = (hoje - aniversariantes_df['Data_admissao']).dt.days // 365
        aniversariantes_df = aniversariantes_df[aniversariantes_df['Anos_de_casa'] >= 1]
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de tempo de empresa para o dia {hoje.strftime('%d/%m')}.")
        return aniversariantes_df

    def identificar_aniversariantes_de_nascimento_do_dia(self, df_validos, data_simulada=None):
        """Filtra o DataFrame para encontrar aniversariantes de nascimento no dia atual."""
        hoje = data_simulada or datetime.now()
        aniversariantes_df = df_validos[
            (df_validos['Data_nascimento'].dt.day == hoje.day) &
            (df_validos['Data_nascimento'].dt.month == hoje.month)
        ].copy()
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de nascimento para o dia {hoje.strftime('%d/%m')}.")
        return aniversariantes_df

    def identificar_aniversariantes_de_nascimento_mes_seguinte(self, df_validos, data_simulada=None):
        """Filtra o DataFrame para encontrar aniversariantes de nascimento no próximo mês."""
        data_referencia = data_simulada or datetime.now()
        mes_seguinte = (data_referencia + relativedelta(months=1)).month
        aniversariantes_df = df_validos[
            pd.to_datetime(df_validos['Data_nascimento']).dt.month == mes_seguinte
        ].copy()
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de nascimento para o próximo mês.")
        return aniversariantes_df