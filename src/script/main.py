import sys
import os
import logging
import socket
from datetime import datetime
# Adiciona o caminho da pasta 'src' ao sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)
# Imports do projeto
from data.conexaoSenior import conexaoSenior
from gerenciadores.gerenciarColaboradores import classificar_usuarios
from gerenciadores.gerenciarAniversariantes import gerenciadorAniversariantes
from email_utils.aniversarioEmpresa import aniversarioEmpresa
from email_utils.aniversarioNascimento import aniversarioNascimento
from utils.config import dict_extract
from dotenv import load_dotenv, find_dotenv

# Use a data atual para execução normal ou defina uma data para simulação
# data_simulada = datetime.strptime("01/06/2025", "%d/%m/%Y")
data_simulada = None # Descomente a linha acima e comente esta para simular

def configurar_logs():
    log_directory = os.path.join(os.getcwd(), "Logs")
    os.makedirs(log_directory, exist_ok=True)
    log_filename = os.path.join(log_directory, datetime.now().strftime("%Y-%m-%d") + "_log_.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding='utf-8',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    nome_host = socket.gethostname()
    ip_local = socket.gethostbyname(nome_host)
    logging.info("--------------===>>>Informacoes do executor<<<===--------------")
    logging.info(f"IPV4: {ip_local}")
    logging.info(f"HOST: {nome_host}")

class Main:
    def __init__(self):
        """Inicializa as classes necessárias para a execução."""
        load_dotenv(find_dotenv())
        self.conexao_senior = conexaoSenior(**dict_extract["Senior"])
        self.gerenciador_aniversariantes = gerenciadorAniversariantes()
        self.email_empresa = aniversarioEmpresa()
        self.email_nascimento = aniversarioNascimento()
        self.data_referencia = data_simulada or datetime.now()
        
    def executar(self):
        """Orquestra a execução de todo o processo."""
        logging.info(">>> Iniciando processo de envio de e-mails.")
        
        if not self.conexao_senior.conexaoBancoSenior():
            logging.error("Falha ao conectar no banco de dados. Encerrando execução.")
            return

        try:
            colaboradores_df = self.conexao_senior.consultaDadosSenior()

            if colaboradores_df.empty:
                logging.warning("Nenhum colaborador encontrado na consulta. Encerrando execucao.")
                return

            resultados_classificacao = classificar_usuarios(colaboradores_df)
            df_validos = resultados_classificacao['validos']
            logging.info(f"Total de registros validos para processamento: {len(df_validos)}")
        
            # --- Lógica de Aniversário de Empresa ---
            logging.info(">>> Processando aniversariantes de tempo de empresa...")
            aniversariantes_mes_seguinte_df = self.gerenciador_aniversariantes.identificar_aniversariantes_mes_seguinte(df_validos, self.data_referencia)
            self.email_empresa.enviar_email_rh_aniversariante_empresa(aniversariantes_mes_seguinte_df, self.data_referencia)
            # self.email_empresa.enviar_emails_gestores_aniversariante_empresa(aniversariantes_mes_seguinte_df, self.data_referencia)

            aniversariantes_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_do_dia(df_validos, self.data_referencia)
            # Lista de anos que recebem o e-mail especial (Star)
            anos_star = [5, 10, 15, 20, 25, 30]
            # Separar aniversariantes Star
            # aniversariantes_star_df = aniversariantes_do_dia_df[aniversariantes_do_dia_df['Anos_de_casa'].isin(anos_star)]
            # Separar aniversariantes normais
            # aniversariantes_normais_df = aniversariantes_do_dia_df[~aniversariantes_do_dia_df['Anos_de_casa'].isin(anos_star)]
            # self.email_empresa.enviar_email_individual_aniversariante_empresa_star(aniversariantes_star_df, self.data_referencia)
            # self.email_empresa.enviar_email_individual_aniversariante_empresa(aniversariantes_normais_df, self.data_referencia)
            # self.email_empresa.enviar_email_diario_gestor_aniversariante_empresa(aniversariantes_do_dia_df, self.data_referencia)
            
            # --- Lógica de Aniversário de Nascimento ---
            logging.info(">>> Processando aniversariantes de nascimento...")
            aniversariantes_nasc_mes_seguinte_df = self.gerenciador_aniversariantes.identificar_aniversariantes_de_nascimento_mes_seguinte(df_validos, self.data_referencia)
            self.email_nascimento.enviar_email_rh_aniversariantes_nascimento(aniversariantes_nasc_mes_seguinte_df, self.data_referencia)
            # self.email_nascimento.enviar_emails_gestores_aniversariantes_nascimento(aniversariantes_nasc_mes_seguinte_df)

            aniversariantes_nasc_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_de_nascimento_do_dia(df_validos, self.data_referencia)
            # self.email_nascimento.enviar_email_individual_aniversariante_nascimento(aniversariantes_nasc_do_dia_df, self.data_referencia)
            # self.email_nascimento.enviar_email_diario_gestor_aniversariante_nascimento(aniversariantes_nasc_do_dia_df, self.data_referencia)

        finally:
            self.conexao_senior.desconectar()
            logging.info(">>> Processo finalizado.")

if __name__ == "__main__":
    configurar_logs()
    main_app = Main()
    main_app.executar()