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
            grupo = grupo.dropna(subset=['Data_admissao']).drop_duplicates(subset=['Data_admissao', 'Data_demissao'])
            if grupo.empty:
                continue

            # --- PONTO 1: A DATA DE ANIVERSÁRIO É SEMPRE A PRIMEIRA ADMISSÃO ---
            # Independentemente de quantas vezes o colaborador saiu e voltou,
            # a data comemorativa será sempre baseada na sua entrada original na empresa.
            primeira_admissao = grupo['Data_admissao'].min()

            if primeira_admissao.month == mes_seguinte:
                # --- PONTO 2: CÁLCULO PRECISO DO TEMPO TOTAL TRABALHADO ---
                # Pega todos os períodos trabalhados (admissão -> demissão/data_atual)
                periodos = sorted([
                    (row['Data_admissao'], row['Data_demissao'] if pd.notnull(row['Data_demissao']) else data_referencia)
                    for _, row in grupo.iterrows()
                ])

                if not periodos:
                    continue

                # --- LÓGICA DE MESCLAGEM DE PERÍODOS ---
                # O objetivo é consolidar períodos que se sobrepõem ou se tocam
                # (ex: demissão em 01/10 e readmissão em 01/10), para que os dias
                # não sejam contados em duplicidade.
                periodos_mesclados = [periodos[0]]
                for i in range(1, len(periodos)):
                    inicio_atual, fim_atual = periodos[i]
                    inicio_ultimo, fim_ultimo = periodos_mesclados[-1]

                    # Se o período atual começar antes ou no mesmo dia em que o último terminou,
                    # eles são considerados contínuos ou sobrepostos.
                    if inicio_atual <= fim_ultimo:
                        # A mesclagem acontece aqui: o início do período consolidado é mantido
                        # e o fim é estendido para a data de término mais recente.
                        periodos_mesclados[-1] = (inicio_ultimo, max(fim_ultimo, fim_atual))
                    else:
                        # Se não há sobreposição, o período atual é adicionado como um novo item.
                        periodos_mesclados.append((inicio_atual, fim_atual))
                
                # Após a mesclagem, a soma dos dias de cada período consolidado resulta no tempo total correto.
                total_dias_trabalhados = sum(
                    (fim - inicio).days for inicio, fim in periodos_mesclados
                )
                
                anos_de_casa = total_dias_trabalhados // 365
                if anos_de_casa >= 1:
                    ultimo_registro = grupo.sort_values('Data_admissao').iloc[-1]
                    aniversariantes.append({
                        'Nome': ultimo_registro['Nome'],
                        'Data_primeira_admissao': primeira_admissao,
                        'Tempo_total_anos': anos_de_casa,
                        'Retorno_em_menos_de_6_meses': grupo['Retorno_em_menos_de_6_meses'].iloc[0]
                    })
        
        aniversariantes_df = pd.DataFrame(aniversariantes)
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes (múltiplas admissões) para o próximo mês.")
        return aniversariantes_df

    def identificar_aniversariantes_mes_seguinte(self, df_validos, data_simulada=None):
        """
        [LÓGICA PADRÃO] Filtra o DataFrame de 'válidos' para encontrar aniversariantes
        de tempo de casa no próximo mês. O cálculo aqui é simples (data_atual - admissão).
        """
        data_referencia = data_simulada or datetime.now()
        mes_seguinte = (data_referencia + relativedelta(months=1)).month

        aniversariantes_df = df_validos[
            pd.to_datetime(df_validos['Data_admissao']).dt.month == mes_seguinte
        ].copy()

        aniversariantes_df['Anos_de_casa'] = aniversariantes_df.apply(
            lambda row: (data_referencia - row['Data_admissao']).days // 365,
            axis=1
        )
        aniversariantes_df = aniversariantes_df[aniversariantes_df['Anos_de_casa'] >= 1]
        logging.info(f"Encontrados {len(aniversariantes_df)} aniversariantes (admissão única) para o próximo mês.")
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