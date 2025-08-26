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
# EMAIL_TESTE = os.getenv("EMAIL_TESTE", "vanessa.boing@fgmdentalgroup.com")
EMAIL_TESTE = [
    os.getenv("EMAIL_TESTE", "vanessa.boing@fgmdentalgroup.com"),
    "sophia.alberton@fgmdentalgroup.com"
]
AMBIENTE = os.getenv("AMBIENTE", "QAS")

class aniversarioEmpresa:
    def __init__(self):
        self.utilitariosComuns = utilitariosComuns()
        self.conexaoGraph = conexaoGraph()
    # Mensal RH 
    def enviar_email_rh_aniversariante_empresa(self, aniversariantes_df, data_simulada=None):
        """Envia o e-mail consolidado para o RH."""
        data_referencia = data_simulada or datetime.now()
        if AMBIENTE == "PRD" and data_referencia.day != 27:
            logging.info("Hoje nao e dia 27. E-mail para RH nao sera enviado.")
            return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa para o proximo mes. E-mail para o RH nao enviado.")
            return

        template = EMAIL_TEMPLATES["RH_ANIVERSARIANTES_EMPRESA"]
        mes_seguinte = (data_referencia + relativedelta(months=1)).strftime("%B").title()
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
        self.utilitariosComuns.enviar_email_formatado([EMAIL_RH], assunto, body)
    # Mensal Gestores
    def enviar_emails_gestores_aniversariante_empresa(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails individuais para cada gestor com seus liderados."""
        data_referencia = data_simulada or datetime.now()
        if AMBIENTE == "PRD" and data_referencia.day != 27:
            logging.info("Hoje nao e dia 27. E-mails para gestores nao serao enviados.")
            return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante para notificar os gestores.")
            return

        template = EMAIL_TEMPLATES["GESTOR_ANIVERSARIANTES_EMPRESA"]
        mes_seguinte = (data_referencia + relativedelta(months=1)).strftime("%B").title()
        assunto = template["assunto"].format(mes_seguinte=mes_seguinte)
        
        for gestor, grupo in aniversariantes_df.groupby('Superior'):
            email_gestor = grupo['Email_superior'].iloc[0]
            if not email_gestor or pd.isna(email_gestor):
                logging.warning(f"Gestor {gestor} nao possui e-mail cadastrado. Pulando notificacao.")
                continue
            
            nome_gestor_formatado = self.utilitariosComuns.formatar_nome(gestor)
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
            self.utilitariosComuns.enviar_email_formatado([email_gestor], assunto, body)
    # Dia do aniversário aniversariante
    def enviar_email_individual_aniversariante_empresa(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails individuais para cada colaborador aniversariante de tempo de empresa no dia."""
        data_referencia = data_simulada or datetime.now()
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa hoje.")
            return
        template = EMAIL_TEMPLATES["INDIVIDUAL_ANIVERSARIANTE_EMPRESA"]
        hoje = data_simulada if data_simulada else data_referencia
        hoje_str = hoje.strftime('%d/%m/%Y')

        for _, row in aniversariantes_df.iterrows():
            nome = self.utilitariosComuns.formatar_nome(row['Nome'])
            anos = row['Anos_de_casa']
            destinatarios = [email for email in [row.get('Email_corporativo'), row.get('Email_pessoal')] if email and not pd.isna(email)]

            if not destinatarios:
                logging.warning(f"{nome} não possui e-mail válido cadastrado. Pulando envio.")
                continue

            
            assunto = template["assunto"].format(nome=nome, anos_de_casa=row['Anos_de_casa'])
            
            imagem_src = f"https://fgmdentalgroup.com/wp-content/uploads/2025/02/{anos}-anos.jpg"
            link_redirect = "https://fgmdentalgroup.com/Endomarketing/Tempo%20de%20casa/Geral/index.html"

            corpo_email = self.utilitariosComuns.gerar_email_com_imagem(
                imagem_src=imagem_src,
                texto_alt=f"{row['Anos_de_casa']} anos de FGM!",
                link=link_redirect
            )
            logging.info(f"Enviando e-mail de parabéns (tempo de empresa) para {nome} ({', '.join(destinatarios)}).")
            self.utilitariosComuns.enviar_email_formatado(destinatarios, assunto, corpo_email)
    # Dia do aniversário gestores de aniversariantes
    def enviar_email_diario_gestor_aniversariante_empresa(self, aniversariantes_df, data_simulada=None):
        """Envia e-mail diário para o gestor com os aniversariantes de tempo de empresa do dia."""
        data_referencia = data_simulada or datetime.now()
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa hoje para notificar gestores.")
            return

        template = EMAIL_TEMPLATES["GESTOR_DIARIO_ANIVERSARIANTE_EMPRESA"]
        hoje = data_simulada if data_simulada else data_referencia
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
            self.utilitariosComuns.enviar_email_formatado([email_gestor], assunto, body)
    # Dia do aniversario aniversariante estrela
    def enviar_email_individual_aniversariante_empresa_star(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails individuais para colaboradores que fazem aniversário de tempo de casa (Star)."""
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de casa hoje.")
            return

        aniversariantes_df['Data_aniversario_empresa'] = pd.to_datetime(aniversariantes_df['Data_admissao']).dt.strftime('%d/%m')

        template = EMAIL_TEMPLATES["INDIVIDUAL_ANIVERSARIANTE_EMPRESA"]
        for _, row in aniversariantes_df.iterrows():
            nome = self.utilitariosComuns.formatar_nome(row['Nome'])
            anos = row['Anos_de_casa']

            destinatarios = [email for email in [row.get('Email_corporativo'), row.get('Email_pessoal')] if email and not pd.isna(email)]
            if not destinatarios:
                logging.warning(f"{nome} não possui e-mail válido cadastrado. Pulando envio.")
                continue
            assunto = template["assunto"].format(nome=nome, anos_de_casa=row['Anos_de_casa'])
            imagem_src = f"https://fgmdentalgroup.com/wp-content/uploads/2025/02/{anos}-anos-estrela.jpg"
            link_redirect = f"https://fgmdentalgroup.com/Endomarketing/Tempo%20de%20casa/{anos}%20anos/index.html"

            body = self.utilitariosComuns.gerar_email_com_imagem(
                imagem_src=imagem_src,
                texto_alt=f"{anos} anos de FGM!",
                link=link_redirect
            )

            logging.info(f"Enviando e-mail de aniversário de tempo de casa para {nome} ({', '.join(destinatarios)}).")
            self.utilitariosComuns.enviar_email_formatado(destinatarios, assunto, body)
