import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.utilitariosComuns import utilitariosComuns
from data.conexaoGraph import conexaoGraph
from email_utils.email_config import EMAIL_TEMPLATES
from utils.config import pictureBirth, linkRedirect
import pandas as pd
import locale
import os

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
# ["gestaodepessoas@fgmdentalgroup.com", "grupo.coordenadores@fgmdentalgroup.com", "grupo.supervisores@fgmdentalgroup.com", "grupo.gerentes@fgmdentalgroup.com"]
EMAIL_RH = os.getenv("EMAIL_RH", "comunicacaointerna@fgmdentalgroup.com")
EMAIL_TESTE = os.getenv("EMAIL_TESTE", "sophia.alberton@fgmdentalgroup.com")
AMBIENTE = os.getenv("AMBIENTE", "QAS")

class aniversarioNascimento:
    def __init__(self):
        self.utilitariosComuns = utilitariosComuns()
        self.conexaoGraph = conexaoGraph()
    
    def enviar_email_rh_aniversariantes_nascimento(self, aniversariantes_df, data_simulada=None):
        """Envia o e-mail consolidado de aniversariantes de nascimento para o RH."""
        data_referencia = data_simulada or datetime.now()
        if AMBIENTE == "PRD" and data_referencia.day != 27:
            logging.info("Hoje não é dia 27. E-mail de aniversariantes de nascimento para RH não será enviado.")
            return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de nascimento no próximo mês. E-mail para o RH não enviado.")
            return
        template = EMAIL_TEMPLATES["RH_ANIVERSARIANTES_NASCIMENTO"]
        mes_seguinte = (data_referencia + relativedelta(months=1)).strftime("%B").title()
        assunto = template["assunto"].format(mes_seguinte=mes_seguinte)
        
        aniversariantes_df['DiaMes'] = aniversariantes_df['Data_nascimento'].dt.strftime('%m-%d')
        aniversariantes_df = aniversariantes_df.sort_values(by='DiaMes')

        dados_tabela = [
            [
                row['Nome'],
                row['Data_nascimento'].strftime('%d/%m'),
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

        logging.info(f"Enviando e-mail para o RH com {len(dados_tabela)} aniversariantes de nascimento.")
        self.utilitariosComuns.enviar_email_formatado([EMAIL_RH], assunto, body)
    # Mensal Gestores
    def enviar_emails_gestores_aniversariantes_nascimento(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails mensais para cada gestor com seus liderados aniversariantes de nascimento."""
        data_referencia = data_simulada or datetime.now()
        if AMBIENTE == "PRD" and data_referencia.day != 27:
            logging.info("Hoje não é dia 27. E-mails de aniversariantes de nascimento para gestores não serão enviados.")
            return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de nascimento para notificar os gestores no próximo mês.")
            return

        template = EMAIL_TEMPLATES["GESTOR_ANIVERSARIANTES_NASCIMENTO"]
        mes_seguinte = (data_referencia + relativedelta(months=1)).strftime("%B").title()
        
        for gestor, grupo in aniversariantes_df.groupby('Superior'):
            email_gestor = grupo['Email_superior'].iloc[0]
            if not email_gestor or pd.isna(email_gestor):
                logging.warning(f"Gestor {gestor} não possui e-mail cadastrado. Pulando notificação de aniversário de nascimento.")
                continue
            
            nome_gestor_formatado = self.utilitariosComuns.formatar_nome(gestor)
            assunto = template["assunto"].format(mes_seguinte=mes_seguinte)
            
            grupo['DiaMes'] = grupo['Data_nascimento'].dt.strftime('%m-%d')
            grupo = grupo.sort_values(by='DiaMes')
            dados_tabela = [
                [row['Nome'], row['Data_nascimento'].strftime('%d/%m')]
                for _, row in grupo.iterrows()
            ]

            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(
                template["saudacao"].format(nome_gestor=nome_gestor_formatado),
                template["mensagem"].format(mes_seguinte=mes_seguinte),
                template["colunas"],
                dados_tabela
            )

            logging.info(f"Enviando e-mail para o gestor {gestor} ({email_gestor}) com {len(dados_tabela)} aniversariantes de nascimento.")
            self.utilitariosComuns.enviar_email_formatado([email_gestor], assunto, body)
    # Dia do aniversário aniversariante
    def enviar_email_individual_aniversariante_nascimento(self, aniversariantes_df, data_simulada=None):
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
            self.utilitariosComuns.enviar_email_formatado(destinatarios, assunto, body)
    # Dia do aniversário gestores de aniversariantes
    def enviar_email_diario_gestor_aniversariante_nascimento(self, aniversariantes_df, data_simulada=None):
        """Envia e-mail diário para o gestor com os aniversariantes de nascimento do dia."""
        data_referencia = data_simulada or datetime.now()
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de nascimento hoje para notificar gestores.")
            return

        template = EMAIL_TEMPLATES["GESTOR_DIARIO_ANIVERSARIANTE_NASCIMENTO"]
        hoje = data_simulada if data_simulada else data_referencia
        hoje_str = hoje.strftime('%d/%m')

        for gestor, grupo in aniversariantes_df.groupby('Superior'):
            email_gestor = grupo['Email_superior'].iloc[0]
            if not email_gestor or pd.isna(email_gestor):
                logging.warning(f"Gestor {gestor} não possui e-mail cadastrado. Pulando notificação diária de aniversário de nascimento.")
                continue

            nome_gestor_formatado = self.utilitariosComuns.formatar_nome(gestor)
            assunto = template["assunto"]
            
            dados_tabela = [
                [row['Nome'], row['Data_nascimento'].strftime('%d/%m')]
                for _, row in grupo.iterrows()
            ]

            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(
                template["saudacao"].format(nome_gestor=nome_gestor_formatado),
                template["mensagem"].format(hoje_str=hoje_str),
                template["colunas"],
                dados_tabela
            )

            logging.info(f"Enviando e-mail diário (nascimento) para o gestor {gestor} ({email_gestor}) com {len(dados_tabela)} aniversariantes.")
            self.utilitariosComuns.enviar_email_formatado([email_gestor], assunto, body)