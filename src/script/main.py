# src/script/main.py
import sys
import os
import logging
import socket
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# Adiciona o caminho da pasta 'src' ao sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from data.conexaoSenior import conexaoSenior
from gerenciadores.gerenciarColaboradores import classificar_usuarios
from gerenciadores.gerenciarAniversariantes import gerenciadorAniversariantes
from email_utils.aniversarioEmpresa import aniversarioEmpresa
from email_utils.aniversarioNascimento import aniversarioNascimento
from utils.config import dict_extract

# Defina a data para simulação ou use a data atual
# data_simulada = datetime.strptime("01/04/2025", "%d/%m/%Y")
data_simulada = None

def configurar_logs():
    log_directory = os.path.join(os.getcwd(), "Logs")
    os.makedirs(log_directory, exist_ok=True)
    log_filename = os.path.join(log_directory, datetime.now().strftime("%Y-%m-%d") + "_log.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding='utf-8',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_filename), logging.StreamHandler(sys.stdout)],
        force=True
    )
    logging.info(f"Executando em: HOST={socket.gethostname()}, IP={socket.gethostbyname(socket.gethostname())}")

class Main:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.conexao_senior = conexaoSenior(**dict_extract["Senior"])
        self.gerenciador_aniversariantes = gerenciadorAniversariantes()
        self.email_empresa = aniversarioEmpresa()
        self.email_nascimento = aniversarioNascimento()
        self.data_referencia = data_simulada or datetime.now()

    def _processar_aniversariantes_empresa(self, df_validos, df_duplicados):
        """Processa e envia todos os e-mails de aniversário de tempo de empresa."""
        logging.info(">>> Processando aniversariantes de tempo de empresa...")
        
        if not df_duplicados.empty:
            aniversariantes_duplicados_df = self.gerenciador_aniversariantes.identificar_aniversariantes_mes_seguinte_duplicados(df_duplicados, self.data_referencia)
            mais_6_meses_df = aniversariantes_duplicados_df[~aniversariantes_duplicados_df['Retorno_em_menos_de_6_meses']]
            menos_6_meses_df = aniversariantes_duplicados_df[aniversariantes_duplicados_df['Retorno_em_menos_de_6_meses']]
            self.email_empresa.enviar_email_rh_aniversariante_empresa_duplicados(mais_6_meses_df, menos_6_meses_df, self.data_referencia)

        aniversariantes_mes_seguinte_df = self.gerenciador_aniversariantes.identificar_aniversariantes_mes_seguinte(df_validos, self.data_referencia)
        self.email_empresa.enviar_email_rh_aniversariante_empresa(aniversariantes_mes_seguinte_df, self.data_referencia)
        self.email_empresa.enviar_emails_gestores_aniversariante_empresa(aniversariantes_mes_seguinte_df, self.data_referencia)
        
        aniversariantes_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_do_dia(df_validos, self.data_referencia)
        anos_star = [5, 10, 15, 20, 25, 30]
        aniversariantes_star_df = aniversariantes_do_dia_df[aniversariantes_do_dia_df['Anos_de_casa'].isin(anos_star)]
        aniversariantes_normais_df = aniversariantes_do_dia_df[~aniversariantes_do_dia_df['Anos_de_casa'].isin(anos_star)]

        self.email_empresa.enviar_email_individual_aniversariante_empresa_star(aniversariantes_star_df, self.data_referencia)
        self.email_empresa.enviar_email_individual_aniversariante_empresa(aniversariantes_normais_df, self.data_referencia)
        self.email_empresa.enviar_email_diario_gestor_aniversariante_empresa(aniversariantes_do_dia_df, self.data_referencia)

    def _processar_aniversariantes_nascimento(self, df_validos):
        """Processa e envia todos os e-mails de aniversário de nascimento."""
        logging.info(">>> Processando aniversariantes de nascimento...")
        aniversariantes_nasc_mes_seguinte_df = self.gerenciador_aniversariantes.identificar_aniversariantes_de_nascimento_mes_seguinte(df_validos, self.data_referencia)
        self.email_nascimento.enviar_email_rh_aniversariantes_nascimento(aniversariantes_nasc_mes_seguinte_df, self.data_referencia)
        self.email_nascimento.enviar_emails_gestores_aniversariantes_nascimento(aniversariantes_nasc_mes_seguinte_df)

        aniversariantes_nasc_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_de_nascimento_do_dia(df_validos, self.data_referencia)
        self.email_nascimento.enviar_email_individual_aniversariante_nascimento(aniversariantes_nasc_do_dia_df, self.data_referencia)
        self.email_nascimento.enviar_email_diario_gestor_aniversariante_nascimento(aniversariantes_nasc_do_dia_df, self.data_referencia)

    def executar(self):
        logging.info(">>> Iniciando processo de envio de e-mails.")
        if not self.conexao_senior.conexaoBancoSenior():
            logging.error("Falha ao conectar no banco de dados. Encerrando execução.")
            return

        try:
            colaboradores_df = self.conexao_senior.consultaDadosSenior()
            if colaboradores_df.empty:
                logging.warning("Nenhum colaborador encontrado. Encerrando execução.")
                return

            resultados = classificar_usuarios(colaboradores_df)
            df_validos = resultados['validos']
            df_duplicados = resultados['cadastros_duplicados']

            self._processar_aniversariantes_empresa(df_validos, df_duplicados)
            self._processar_aniversariantes_nascimento(df_validos)

        finally:
            self.conexao_senior.desconectar()
            logging.info(">>> Processo finalizado.")

if __name__ == "__main__":
    configurar_logs()
    main_app = Main()
    main_app.executar()