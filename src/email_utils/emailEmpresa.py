import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.utilitariosComuns import utilitariosComuns
from data.conexaoGraph import conexaoGraph
from utils.email_config import EMAIL_TEMPLATES
from utils.config import pictureBirth, linkRedirect
import pandas as pd
import locale
import os

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
EMAIL_RH = os.getenv("EMAIL_RH", "comunicacaointerna@fgmdentalgroup.com")
EMAIL_TESTE = os.getenv("EMAIL_TESTE", "sophia.alberton@fgmdentalgroup.com")
AMBIENTE = os.getenv("AMBIENTE", "QAS")

class emailEmpresa:
    def __init__(self):
        self.utilitariosComuns = utilitariosComuns()
        self.conexaoGraph = conexaoGraph()

    def _enviar_email_formatado(self, destinatarios, assunto, body):
        """Função auxiliar para enviar e-mails, tratando ambiente de QAS/PRD."""
        if not destinatarios:
            logging.warning("Nenhum destinatário para o e-mail.")
            return

        email_para_envio = [EMAIL_TESTE] if AMBIENTE == "QAS" else destinatarios
        self.conexaoGraph.enviar_email(email_para_envio, assunto, body)

    def enviar_email_rh(self, aniversariantes_df):
        """Envia o e-mail consolidado para o RH."""
        if AMBIENTE == "PRD" and datetime.now().day != 27:
            logging.info("Hoje nao e dia 27. E-mail para RH nao sera enviado.")
            return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa para o proximo mes. E-mail para o RH nao enviado.")
            return

        template = EMAIL_TEMPLATES["RH_ANIVERSARIANTES_EMPRESA"]
        mes_seguinte = (datetime.now() + relativedelta(months=1)).strftime("%B").title()
        assunto = template["assunto"].format(mes_seguinte=mes_seguinte)
        
        aniversariantes_df['DiaMes'] = aniversariantes_df['Data_admissao'].dt.strftime('%m-%d')
        aniversariantes_df = aniversariantes_df.sort_values(by='DiaMes')

        dados_tabela = [
            [
                row['Nome'],
                row['Data_admissao'].strftime('%d/%m/%Y'),
                row['Anos_de_casa'],
                row.get('Local', 'N/A'),
                row.get('Superior', 'N/A')
            ] for _, row in aniversariantes_df.iterrows()
        ]
            
        body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(
            template["saudacao"],
            template["mensagem"].format(mes_seguinte=mes_seguinte),
            template["colunas"],
            dados_tabela
        )

        logging.info(f"Enviando e-mail para o RH com {len(dados_tabela)} aniversariantes.")
        self._enviar_email_formatado([EMAIL_RH], assunto, body)

    def enviar_emails_gestores(self, aniversariantes_df):
        """Envia e-mails individuais para cada gestor com seus liderados."""
        if AMBIENTE == "PRD" and datetime.now().day != 27:
            logging.info("Hoje nao e dia 27. E-mails para gestores nao serao enviados.")
            return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante para notificar os gestores.")
            return

        template = EMAIL_TEMPLATES["GESTOR_ANIVERSARIANTES_EMPRESA"]
        mes_seguinte = (datetime.now() + relativedelta(months=1)).strftime("%B").title()
        
        for gestor, grupo in aniversariantes_df.groupby('Superior'):
            email_gestor = grupo['Email_superior'].iloc[0]
            if not email_gestor or pd.isna(email_gestor):
                logging.warning(f"Gestor {gestor} nao possui e-mail cadastrado. Pulando notificacao.")
                continue
            
            nome_gestor_formatado = self.utilitariosComuns.formatar_nome(gestor)
            assunto = template["assunto"].format(mes_seguinte=mes_seguinte)
            
            grupo['DiaMes'] = grupo['Data_admissao'].dt.strftime('%m-%d')
            grupo = grupo.sort_values(by='DiaMes')
            dados_tabela = [
                [row['Nome'], row['Data_admissao'].strftime('%d/%m/%Y'), row['Anos_de_casa']]
                for _, row in grupo.iterrows()
            ]

            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(
                template["saudacao"].format(nome_gestor=nome_gestor_formatado),
                template["mensagem"].format(mes_seguinte=mes_seguinte),
                template["colunas"],
                dados_tabela
            )

            logging.info(f"Enviando e-mail para o gestor {gestor} ({email_gestor}) com {len(dados_tabela)} aniversariantes.")
            self._enviar_email_formatado([email_gestor], assunto, body)

    def enviar_email_individual_aniversariante(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails individuais para cada colaborador aniversariante de tempo de empresa no dia."""
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa hoje.")
            return

        template = EMAIL_TEMPLATES["INDIVIDUAL_ANIVERSARIANTE_EMPRESA"]
        hoje = data_simulada if data_simulada else datetime.now()
        hoje_str = hoje.strftime('%d/%m/%Y')

        for _, row in aniversariantes_df.iterrows():
            nome = self.utilitariosComuns.formatar_nome(row['Nome'])
            destinatarios = [email for email in [row.get('Email_corporativo'), row.get('Email_pessoal')] if email and not pd.isna(email)]

            if not destinatarios:
                logging.warning(f"{nome} não possui e-mail válido cadastrado. Pulando envio.")
                continue

            assunto = template["assunto"]
            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(
                template["saudacao"].format(nome=nome),
                template["mensagem"].format(
                    hoje_str=hoje_str,
                    anos_de_casa=row['Anos_de_casa'],
                    data_admissao=row['Data_admissao'].strftime('%d/%m/%Y')
                ),
                [], []
            )

            logging.info(f"Enviando e-mail de parabéns (tempo de empresa) para {nome} ({', '.join(destinatarios)}).")
            self._enviar_email_formatado(destinatarios, assunto, body)

    def enviar_email_diario_gestor_aniversariante(self, aniversariantes_df, data_simulada=None):
        """Envia e-mail diário para o gestor com os aniversariantes de tempo de empresa do dia."""
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa hoje para notificar gestores.")
            return

        template = EMAIL_TEMPLATES["GESTOR_DIARIO_ANIVERSARIANTE_EMPRESA"]
        hoje = data_simulada if data_simulada else datetime.now()
        hoje_str = hoje.strftime('%d/%m/%Y')

        for gestor, grupo in aniversariantes_df.groupby('Superior'):
            email_gestor = grupo['Email_superior'].iloc[0]
            if not email_gestor or pd.isna(email_gestor):
                logging.warning(f"Gestor {gestor} não possui e-mail cadastrado. Pulando envio.")
                continue

            nome_gestor_formatado = self.utilitariosComuns.formatar_nome(gestor)
            assunto = template["assunto"].format(hoje_str=hoje_str)

            dados_tabela = [
                [row['Nome'], row['Data_admissao'].strftime('%d/%m/%Y'), row['Anos_de_casa']]
                for _, row in grupo.iterrows()
            ]

            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(
                template["saudacao"].format(nome_gestor=nome_gestor_formatado),
                template["mensagem"].format(hoje_str=hoje_str),
                template["colunas"],
                dados_tabela
            )

            logging.info(f"Enviando e-mail diário (tempo de empresa) para o gestor {gestor} ({email_gestor}) com {len(dados_tabela)} aniversariantes.")
            self._enviar_email_formatado([email_gestor], assunto, body)

    def enviar_email_aniversariante_nascimento(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails individuais para cada colaborador aniversariante de nascimento no dia."""
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de nascimento hoje.")
            return

        template = EMAIL_TEMPLATES["INDIVIDUAL_ANIVERSARIANTE_NASCIMENTO"]

        for _, row in aniversariantes_df.iterrows():
            nome = self.utilitariosComuns.formatar_nome(row['Nome'])
            destinatarios = [email for email in [row.get('Email_corporativo'), row.get('Email_pessoal')] if email and not pd.isna(email)]

            if not destinatarios:
                logging.warning(f"{nome} não possui e-mail válido cadastrado. Pulando envio.")
                continue

            assunto = template["assunto"].format(nome=nome)
            body = self.utilitariosComuns.gerar_email_com_imagem(
                imagem_src=pictureBirth,
                texto_alt=template["texto_alt_imagem"],
                link=linkRedirect
            )

            logging.info(f"Enviando e-mail de feliz aniversário para {nome} ({', '.join(destinatarios)}).")
            self._enviar_email_formatado(destinatarios, assunto, body)