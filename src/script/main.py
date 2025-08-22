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
from email_utils.emailEmpresa import emailEmpresa
from utils.config import dict_extract
from dotenv import load_dotenv, find_dotenv

from datetime import datetime
data_simulada = datetime.strptime("01/09/2025", "%d/%m/%Y")


# Configuração de logs
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
            logging.StreamHandler(sys.stdout) # Mostra logs no console também
        ],
        force=True
    )
    nome_host = socket.gethostname()
    ip_local = socket.gethostbyname(nome_host)
    logging.info("--------------===>>>Informacoes do executor<<<===--------------")
    logging.info(f"IPV4: {ip_local}")
    logging.info(f"HOST: {nome_host}")

# Classe principal
class Main:
    def __init__(self):
        """Inicializa as classes necessárias para a execução."""
        load_dotenv(find_dotenv())
        self.conexao_senior = conexaoSenior(**dict_extract["Senior"])
        self.gerenciador_aniversariantes = gerenciadorAniversariantes()
        self.email_empresa = emailEmpresa()

    def executar(self):
        """Orquestra a execução de todo o processo."""
        logging.info(">>> Iniciando processo de envio de e-mails.")
        
        # 1. Conectar e buscar dados
        self.conexao_senior.conexaoBancoSenior()
        colaboradores_df = self.conexao_senior.consultaDadosSenior()

        if colaboradores_df.empty:
            logging.warning("Nenhum colaborador encontrado na consulta. Encerrando execucao.")
            return

        # 2. Classificar colaboradores (válidos e inválidos)
        resultados_classificacao = classificar_usuarios(colaboradores_df)
        df_validos = resultados_classificacao['validos']
        
        logging.info(f"Total de registros validos para processamento: {len(df_validos)}")
        
        # 3. Identificar aniversariantes do próximo mês
        aniversariantes_mes_seguinte_df = self.gerenciador_aniversariantes.identificar_aniversariantes_mes_seguinte(df_validos)

        # 4. Enviar e-mails de tempo de empresa (mês seguinte)
        if not aniversariantes_mes_seguinte_df.empty:
            # Enviar e-mail único para o RH
            self.email_empresa.enviar_email_rh(aniversariantes_mes_seguinte_df)
            
            # Enviar e-mails para cada gestor
            self.email_empresa.enviar_emails_gestores(aniversariantes_mes_seguinte_df)
        else:
            logging.info("Nenhum aniversariante de tempo de empresa encontrado para o proximo mes.")
            
        # 5. Enviar e-mails no dia do aniversário de tempo de empresa
        aniversariantes_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_do_dia(df_validos, data_simulada)
        self.email_empresa.enviar_email_individual_aniversariante(aniversariantes_do_dia_df, data_simulada)
        self.email_empresa.enviar_email_diario_gestor_aniversariante(aniversariantes_do_dia_df, data_simulada)

        # 6. Enviar e-mails de aniversário de nascimento
        aniversariantes_nascimento_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_de_nascimento_do_dia(df_validos, data_simulada)
        self.email_empresa.enviar_email_aniversariante_nascimento(aniversariantes_nascimento_do_dia_df, data_simulada)

        logging.info(">>> Processo finalizado com sucesso.")

if __name__ == "__main__":
    configurar_logs()
    main_app = Main()
    main_app.executar()