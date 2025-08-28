import logging
from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta

class gerenciadorAniversariantes:
    def __init__(self):
        self.mes_seguinte = (datetime.now() + relativedelta(months=1)).strftime("%m")

    # ... (funções existentes não foram alteradas) ...
    def calcular_tempo_de_empresa(self, admissoes):
        """Calcula o tempo total de empresa, considerando recontratações."""
        admissoes.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"))

        if len(admissoes) > 1:
            data_demissao_anterior = datetime.strptime(admissoes[-2][1], "%d/%m/%Y")
            data_admissao_recente = datetime.strptime(admissoes[-1][0], "%d/%m/%Y")
            intervalo = data_admissao_recente - data_demissao_anterior

            if intervalo < timedelta(days=180):
                data_admissao_antiga = datetime.strptime(admissoes[0][0], "%d/%m/%Y")
                return max(datetime.now() - data_admissao_antiga, timedelta(0))
        
        data_admissao_recente = datetime.strptime(admissoes[-1][0], "%d/%m/%Y")
        return max(datetime.now() - data_admissao_recente, timedelta(0))


    def identificar_aniversariantes_mes_seguinte_duplicados(df_validos, data_simulada=None):
        data_referencia = data_simulada or datetime.now()
        mes_seguinte = (data_referencia + relativedelta(months=1)).month
        aniversariantes = []

        for cpf, grupo in df_validos.groupby('Cpf'):
            grupo = grupo.sort_values('Data_admissao').reset_index(drop=True)
            nome = grupo.iloc[-1]['Nome']
            email = grupo.iloc[-1]['Email_pessoal']
            primeira_admissao = grupo.iloc[0]['Data_admissao']

            tempo_total_anos = round(grupo['Tempo_FGM'].sum())

            if primeira_admissao.month == mes_seguinte and tempo_total_anos >= 1:
                aniversariantes.append({
                    'Cpf': cpf,
                    'Nome': nome,
                    'Email': email,
                    'Data_primeira_admissao': primeira_admissao,
                    'Tempo_total_anos': tempo_total_anos
                })

        aniversariantes_df = pd.DataFrame(aniversariantes)
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de tempo de empresa com mais de uma admissao para o próximo mês.")
        return aniversariantes_df

    def identificar_aniversariantes_mes_seguinte(self, df_validos, data_simulada=None):
        """Filtra o DataFrame para encontrar aniversariantes de tempo de casa no próximo mês."""
        data_referencia = data_simulada or datetime.now()
        mes_seguinte = (data_referencia + relativedelta(months=1)).month

        aniversariantes_df = df_validos[
            pd.to_datetime(df_validos['Data_admissao']).dt.month == mes_seguinte
        ].copy()

        aniversariantes_df['Anos_de_casa'] = aniversariantes_df.apply(
            lambda row: self.calcular_tempo_de_empresa([(row['Data_admissao'].strftime("%d/%m/%Y"), "")]).days // 365,
            axis=1
        )

        aniversariantes_df = aniversariantes_df[aniversariantes_df['Anos_de_casa'] >= 1]

        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de tempo de empresa para o próximo mês.")
        return aniversariantes_df

    def identificar_aniversariantes_do_dia(self, df_validos, data_simulada=None):
        """Filtra o DataFrame para encontrar aniversariantes de tempo de casa no dia atual."""
        logging.info("Identificando aniversariantes de tempo de empresa do dia.")

        hoje = pd.to_datetime(data_simulada) if data_simulada else pd.to_datetime(datetime.now())
        dia = hoje.day
        mes = hoje.month

        # Garantir que a coluna está em datetime
        df_validos['Data_admissao'] = pd.to_datetime(df_validos['Data_admissao'], errors='coerce')

        aniversariantes_df = df_validos[
            (df_validos['Data_admissao'].dt.day == dia) &
            (df_validos['Data_admissao'].dt.month == mes)
        ].copy()

        # Calcular anos de casa com segurança
        aniversariantes_df['Anos_de_casa'] = aniversariantes_df['Data_admissao'].apply(
            lambda data: (hoje - data).days // 365 if pd.notnull(data) else 0
        ).astype(int)

        aniversariantes_df = aniversariantes_df[aniversariantes_df['Anos_de_casa'] >= 1]

        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de tempo de empresa para o dia {hoje.strftime('%d/%m')}.")
        return aniversariantes_df



    def identificar_aniversariantes_de_nascimento_do_dia(self, df_validos, data_simulada=None):
        """Filtra o DataFrame para encontrar aniversariantes de nascimento no dia atual."""
        logging.info("Identificando aniversariantes de nascimento do dia.")

        hoje = data_simulada if data_simulada else datetime.now()
        dia = hoje.day
        mes = hoje.month

        aniversariantes_df = df_validos[
            (pd.to_datetime(df_validos['Data_nascimento']).dt.day == dia) &
            (pd.to_datetime(df_validos['Data_nascimento']).dt.month == mes)
        ].copy()

        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de nascimento para o dia {hoje.strftime('%d/%m')}.")
        return aniversariantes_df

    # --- NOVA FUNÇÃO ADICIONADA ---
    def identificar_aniversariantes_de_nascimento_mes_seguinte(self, df_validos, data_simulada=None):
        """Filtra o DataFrame para encontrar aniversariantes de nascimento no próximo mês."""
        data_referencia = data_simulada or datetime.now()
        logging.info("Identificando aniversariantes de nascimento do próximo mês.")
        
        mes_seguinte = (data_referencia + relativedelta(months=1)).month

        aniversariantes_df = df_validos[
            pd.to_datetime(df_validos['Data_nascimento']).dt.month == mes_seguinte
        ].copy()
        
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes de nascimento para o próximo mês.")
        return aniversariantes_df