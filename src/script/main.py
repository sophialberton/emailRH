# src/script/main.py
import sys
import os
import logging
import socket
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

# --- INICIALIZAÇÃO E CONFIGURAÇÃO DE AMBIENTE ---
# Adiciona o caminho da pasta 'src' ao sys.path para permitir importações diretas
# de outros módulos do projeto (como 'data', 'gerenciadores', etc.).
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.append(src_path)

from data.conexaoSenior import conexaoSenior
from gerenciadores.gerenciarColaboradores import classificar_usuarios
from gerenciadores.gerenciarAniversariantes import gerenciadorAniversariantes
from email_utils.aniversarioEmpresa import aniversarioEmpresa
from email_utils.aniversarioNascimento import aniversarioNascimento
from utils.config import dict_extract

# --- PONTO DE CONFIGURAÇÃO PARA SIMULAÇÃO ---
# Para testar o comportamento do script em uma data específica,
# descomente a linha abaixo e defina a data desejada.
# Se 'data_simulada' for None, o script usará a data atual.
# data_simulada = datetime.strptime("01/06/2025", "%d/%m/%Y")
data_simulada = None

def configurar_logs():
    """Configura o sistema de logging para registrar as operações em um arquivo e no console."""
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

# --- CLASSE PRINCIPAL QUE ORQUESTRA A EXECUÇÃO ---
class Main:
    def __init__(self):
        """Inicializa a aplicação, carregando configurações e instanciando as classes necessárias."""
        load_dotenv(find_dotenv()) # Carrega as variáveis de ambiente do arquivo .env
        self.conexao_senior = conexaoSenior(**dict_extract["Senior"])
        self.gerenciador_aniversariantes = gerenciadorAniversariantes()
        self.email_empresa = aniversarioEmpresa()
        self.email_nascimento = aniversarioNascimento()
        self.data_referencia = data_simulada or datetime.now()

    def processar_aniversariantes_empresa(self, df_validos, df_duplicados, cadastros_menos_6_meses, cadastros_mais_6_meses):
        """Método focado em todo o fluxo de aniversários de tempo de empresa."""
        logging.info(">>> Processando aniversariantes de tempo de empresa...")
        
        # --- LÓGICA PARA COLABORADORES READMITIDOS (CASOS ESPECIAIS) ---
        if not df_duplicados.empty:
            aniversariantes_duplicados_df = self.gerenciador_aniversariantes.identificar_aniversariantes_mes_seguinte_duplicados(df_duplicados, self.data_referencia)
            # Separa as duas listas para o e-mail da Vanessa
            menos_6_meses_df = aniversariantes_duplicados_df[
                aniversariantes_duplicados_df['Nome'].isin(cadastros_menos_6_meses['Nome'])
            ]
            mais_6_meses_df = aniversariantes_duplicados_df[
                aniversariantes_duplicados_df['Nome'].isin(cadastros_mais_6_meses['Nome'])
            ]
            # mais_6_meses_df = aniversariantes_duplicados_df[~aniversariantes_duplicados_df['Retorno_em_menos_de_6_meses']]
            # menos_6_meses_df = aniversariantes_duplicados_df[aniversariantes_duplicados_df['Retorno_em_menos_de_6_meses']]
            self.email_empresa.enviar_email_rh_aniversariante_empresa_duplicados(mais_6_meses_df, menos_6_meses_df, self.data_referencia)

        # --- LÓGICA MENSAL PARA COLABORADORES COM CADASTRO ÚNICO ---
        aniversariantes_mes_seguinte_df = self.gerenciador_aniversariantes.identificar_aniversariantes_mes_seguinte(df_validos, self.data_referencia)
        self.email_empresa.enviar_email_rh_aniversariante_empresa(aniversariantes_mes_seguinte_df, self.data_referencia) # E-mail para o RH
        # self.email_empresa.enviar_emails_gestores_aniversariante_empresa(aniversariantes_mes_seguinte_df, self.data_referencia) # E-mails para Gestores
        
        # --- LÓGICA DIÁRIA (E-MAILS DE PARABÉNS) ---
        aniversariantes_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_do_dia(df_validos, self.data_referencia)
        
        # Separa aniversariantes "Estrela" (5, 10, 15... anos) dos demais
        anos_star = [5, 10, 15, 20, 25, 30]
        aniversariantes_star_df = aniversariantes_do_dia_df[aniversariantes_do_dia_df['Anos_de_casa'].isin(anos_star)]
        aniversariantes_normais_df = aniversariantes_do_dia_df[~aniversariantes_do_dia_df['Anos_de_casa'].isin(anos_star)]

        # Envia os e-mails individuais e a notificação diária para os gestores
        # self.email_empresa.enviar_email_individual_aniversariante_empresa_star(aniversariantes_star_df, self.data_referencia)
        # self.email_empresa.enviar_email_individual_aniversariante_empresa(aniversariantes_normais_df, self.data_referencia)
        # self.email_empresa.enviar_email_diario_gestor_aniversariante_empresa(aniversariantes_do_dia_df, self.data_referencia)

    def processar_aniversariantes_nascimento(self, df_validos):
        """Método focado em todo o fluxo de aniversários de nascimento."""
        logging.info(">>> Processando aniversariantes de nascimento...")
        # --- LÓGICA MENSAL ---
        aniversariantes_nasc_mes_seguinte_df = self.gerenciador_aniversariantes.identificar_aniversariantes_de_nascimento_mes_seguinte(df_validos, self.data_referencia)
        self.email_nascimento.enviar_email_rh_aniversariantes_nascimento(aniversariantes_nasc_mes_seguinte_df, self.data_referencia)
        self.email_nascimento.enviar_emails_gestores_aniversariantes_nascimento(aniversariantes_nasc_mes_seguinte_df)

        # --- LÓGICA DIÁRIA ---
        aniversariantes_nasc_do_dia_df = self.gerenciador_aniversariantes.identificar_aniversariantes_de_nascimento_do_dia(df_validos, self.data_referencia)
        self.email_nascimento.enviar_email_individual_aniversariante_nascimento(aniversariantes_nasc_do_dia_df, self.data_referencia)
        self.email_nascimento.enviar_email_diario_gestor_aniversariante_nascimento(aniversariantes_nasc_do_dia_df, self.data_referencia)

    def executar(self):
        """Ponto de entrada principal que executa todo o processo."""
        logging.info(">>> Iniciando processo de envio de e-mails.")
        # Garante a conexão com o banco de dados antes de prosseguir
        if not self.conexao_senior.conexaoBancoSenior():
            logging.error("Falha ao conectar no banco de dados. Encerrando execução.")
            return

        try:
            # 1. Busca os dados brutos dos colaboradores
            colaboradores_df = self.conexao_senior.consultaDadosSenior()
            if colaboradores_df.empty:
                logging.warning("Nenhum colaborador encontrado. Encerrando execução.")
                return

            # 2. Classifica os colaboradores, separando-os em grupos
            # Este é um passo CRUCIAL. Ele separa os casos simples ('validos') dos complexos ('duplicados')
            resultados = classificar_usuarios(colaboradores_df)
            df_validos = resultados['validos']
            df_duplicados = resultados['cadastros_duplicados']
            cadastros_menos_6_meses = resultados['cadastros_menos_6_meses']
            cadastros_mais_6_meses = resultados['cadastros_mais_6_meses']

            # 3. Executa os fluxos de processamento para cada tipo de aniversário
            self.processar_aniversariantes_empresa(df_validos, df_duplicados, cadastros_menos_6_meses, cadastros_mais_6_meses)
            # self.processar_aniversariantes_nascimento(df_validos)

        finally:
            # Garante que a conexão com o banco de dados seja sempre fechada
            self.conexao_senior.desconectar()
            logging.info(">>> Processo finalizado.")

# --- PONTO DE EXECUÇÃO DO SCRIPT ---
# Garante que o código dentro deste bloco só será executado quando o arquivo for chamado diretamente
if __name__ == "__main__":
    configurar_logs()
    main_app = Main()
    main_app.executar()