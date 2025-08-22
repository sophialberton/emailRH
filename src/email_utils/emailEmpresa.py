import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.utilitariosComuns import utilitariosComuns
from data.conexaoGraph import conexaoGraph
import pandas as pd
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')  # Define o locale para português do Brasil
import os
EMAIL_RH = os.getenv("EMAIL_RH", "comunicacaointerna@fgmdentalgroup.com")
EMAIL_TESTE = os.getenv("EMAIL_TESTE", "sophia.alberton@fgmdentalgroup.com")
AMBIENTE = os.getenv("AMBIENTE", "QAS")  # "QAS" é o valor padrão se a variável não estiver definida

class emailEmpresa:
    def __init__(self):
        self.utilitariosComuns = utilitariosComuns()
        self.conexaoGraph = conexaoGraph()
        self.email_teste = ["sophia.alberton@fgmdentalgroup.com"] # E-mail para testes

    def enviar_email_rh(self, aniversariantes_df):
        """Envia o e-mail consolidado para o RH."""
        if AMBIENTE == "PRD" and datetime.now().day != 27:
            if datetime.now().day != 27:
                logging.info("Hoje nao e dia 27. E-mails para RH nao sera enviado.")
                return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa no proximo mes. E-mail para o RH nao enviado.")
            return

        emojis = ["🎉", "📅", "🏢", "📍", "👤"]
        
        # Limpeza e formatação dos dados
        for coluna in ["Nome", "Local", "Superior"]:
            aniversariantes_df[coluna] = aniversariantes_df[coluna].apply(
                lambda x: self.utilitariosComuns.formatar_nome(
                    ''.join([c for c in x if c not in emojis]) if isinstance(x, str) else ''
                )
            )


        mes_seguinte = (datetime.now() + relativedelta(months=1)).strftime("%B").title()
        subject = f'Aniversariantes de Tempo de Empresa - {mes_seguinte}'
        
        saudacao = "Olá,"
        mensagem = f"Segue a lista de colaboradores que fazem aniversário de tempo de empresa no mês de {mes_seguinte}:"
        colunas = ["🎉 Nome", " 📅 Data de Admissão", "🏢 Anos de Empresa", "📍 Setor", "👤 Superior"]
        aniversariantes_df['DiaMes'] = aniversariantes_df['Data_admissao'].dt.strftime('%m-%d')
        aniversariantes_df = aniversariantes_df.sort_values(by='DiaMes')

        # Prepara os dados para a tabela
        dados_tabela = []
        for _, row in aniversariantes_df.iterrows():
            dados_tabela.append([
                row['Nome'],
                row['Data_admissao'].strftime('%d/%m/%Y'),
                row['Anos_de_casa'],
                row.get('Local', 'N/A'),
                row.get('Superior', 'N/A')
            ])
            
        body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(saudacao, mensagem, colunas, dados_tabela)

        logging.info(f"Enviando e-mail para o RH com {len(dados_tabela)} aniversariantes.")
        # self.conexaoGraph.enviar_email(self.email_rh_list, subject, body) # PRD
        # self.conexaoGraph.enviar_email(self.email_teste, subject, body) # QAS
        self.conexaoGraph.enviar_email(
            [EMAIL_TESTE] if AMBIENTE == "QAS" else [EMAIL_RH],
            subject,
            body
        )

    def enviar_emails_gestores(self, aniversariantes_df):
        """Envia e-mails individuais para cada gestor com seus liderados."""
        if AMBIENTE == "PRD" and datetime.now().day != 27:
            if datetime.now().day != 27:
                logging.info("Hoje nao e dia 27. E-mails para gestores nao serao enviados.")
                return
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante para notificar os gestores.")
            return

        mes_seguinte = (datetime.now() + relativedelta(months=1)).strftime("%B").title()
        
        for gestor, grupo in aniversariantes_df.groupby('Superior'):
            if not grupo.empty:
                email_gestor = grupo['Email_superior'].iloc[0]
                if not email_gestor or pd.isna(email_gestor):
                    logging.warning(f"Gestor {gestor} nao possui e-mail cadastrado. Pulando notificacao.")
                    continue
                emojis = ["🎉", "📅", "🏢"]
                # Limpeza e formatação dos dados
                for coluna in ["Nome", "Local", "Superior"]:
                    aniversariantes_df[coluna] = aniversariantes_df[coluna].apply(
                        lambda x: self.utilitariosComuns.formatar_nome(
                            ''.join([c for c in x if c not in emojis]) if isinstance(x, str) else ''
                        )
                    )
                subject = f'Aniversariantes de Tempo de Empresa da sua Equipe - {mes_seguinte}'
                saudacao = f"Olá, {self.utilitariosComuns.formatar_nome(gestor)}."
                mensagem = f"Segue a lista dos seus liderados que fazem aniversário de tempo de empresa no mês de {mes_seguinte}:"
                colunas = ["🎉 Nome", "📅 Data de Admissão", "🏢 Anos de Empresa"]
                grupo['DiaMes'] = grupo['Data_admissao'].dt.strftime('%m-%d')
                grupo = grupo.sort_values(by='DiaMes')
                dados_tabela = []
                for _, row in grupo.iterrows():
                    dados_tabela.append([
                        row['Nome'],
                        row['Data_admissao'].strftime('%d/%m/%Y'),
                        row['Anos_de_casa']
                    ])

                body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(saudacao, mensagem, colunas, dados_tabela)

                logging.info(f"Enviando e-mail para o gestor {gestor} ({email_gestor}) com {len(dados_tabela)} aniversariantes.")
                # self.conexaoGraph.enviar_email([email_gestor], subject, body) # Enviar para o e-mail do gestor PRD
                # self.conexaoGraph.enviar_email(self.email_teste, subject, body) # Enviar para o e-mail QAS
                self.conexaoGraph.enviar_email(
                    [EMAIL_TESTE] if AMBIENTE == "QAS" else [email_gestor],
                    subject,
                    body
                )

    def enviar_email_individual_aniversariante(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails individuais para cada colaborador aniversariante de tempo de empresa no dia."""
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa hoje.")
            return

        hoje = data_simulada if data_simulada else datetime.now()
        hoje_str = hoje.strftime('%d/%m/%Y')

        for _, row in aniversariantes_df.iterrows():
            nome = self.utilitariosComuns.formatar_nome(row['Nome'])
            data_admissao = row['Data_admissao'].strftime('%d/%m/%Y')
            anos_de_casa = row['Anos_de_casa']
            email_pessoal = row.get('Email_pessoal', '')
            email_corporativo = row.get('Email_corporativo', '')

            destinatarios = []
            if email_corporativo and not pd.isna(email_corporativo):
                destinatarios.append(email_corporativo)
            if email_pessoal and not pd.isna(email_pessoal):
                destinatarios.append(email_pessoal)

            if not destinatarios:
                logging.warning(f"{nome} não possui e-mail válido cadastrado. Pulando envio.")
                continue

            subject = f"🎉 Parabéns pelo seu aniversário de empresa!"
            saudacao = f"Olá, {nome}!"
            mensagem = (
                f"Hoje, {hoje_str}, você completa {anos_de_casa} ano(s) de empresa! 🎉\n\n"
                f"Queremos agradecer por todo o seu empenho e dedicação desde sua admissão em {data_admissao}.\n"
                f"Continue brilhando e contribuindo com seu talento. Parabéns por essa conquista!"
            )
            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(saudacao, mensagem, [], [])

            logging.info(f"Enviando e-mail de parabéns para {nome} ({', '.join(destinatarios)}).")
            self.conexaoGraph.enviar_email(
                [EMAIL_TESTE] if AMBIENTE == "QAS" else destinatarios,
                subject,
                body
            )


    def enviar_email_diario_gestor_aniversariante(self, aniversariantes_df, data_simulada=None):
        """Envia e-mail diário para o gestor com os aniversariantes de tempo de empresa do dia."""
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de tempo de empresa hoje.")
            return

        hoje = data_simulada if data_simulada else datetime.now()
        hoje_str = hoje.strftime('%d/%m/%Y')

        for gestor, grupo in aniversariantes_df.groupby('Superior'):
            email_gestor = grupo['Email_superior'].iloc[0]
            if not email_gestor or pd.isna(email_gestor):
                logging.warning(f"Gestor {gestor} não possui e-mail cadastrado. Pulando envio.")
                continue

            nome_gestor = self.utilitariosComuns.formatar_nome(gestor)
            saudacao = f"Olá, {nome_gestor}!"
            mensagem = f"Hoje ({hoje_str}), os seguintes colaboradores da sua equipe completam aniversário de tempo de empresa:"

            colunas = ["🎉 Nome", "📅 Data de Admissão", "🏢 Anos de Empresa"]
            grupo['DiaMes'] = grupo['Data_admissao'].dt.strftime('%m-%d')
            grupo = grupo.sort_values(by='DiaMes')

            dados_tabela = []
            for _, row in grupo.iterrows():
                dados_tabela.append([
                    row['Nome'],
                    row['Data_admissao'].strftime('%d/%m/%Y'),
                    row['Anos_de_casa']
                ])

            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(saudacao, mensagem, colunas, dados_tabela)

            logging.info(f"Enviando e-mail diário para o gestor {gestor} ({email_gestor}) com {len(dados_tabela)} aniversariantes.")
            assunto = f"🎉 Aniversariantes de Tempo de Empresa - {hoje_str}"
            destinatarios = [EMAIL_TESTE] if AMBIENTE == "QAS" else [email_gestor]
            self.conexaoGraph.enviar_email(destinatarios, assunto, body)
            
    def enviar_email_aniversariante_nascimento(self, aniversariantes_df, data_simulada=None):
        """Envia e-mails individuais para cada colaborador aniversariante de nascimento no dia."""
        if aniversariantes_df.empty:
            logging.info("Nenhum aniversariante de nascimento hoje.")
            return

        hoje = data_simulada if data_simulada else datetime.now()
        hoje_str = hoje.strftime('%d/%m/%Y')

        for _, row in aniversariantes_df.iterrows():
            nome = self.utilitariosComuns.formatar_nome(row['Nome'])
            email_pessoal = row.get('Email_pessoal', '')
            email_corporativo = row.get('Email_corporativo', '')

            destinatarios = []
            if email_corporativo and not pd.isna(email_corporativo):
                destinatarios.append(email_corporativo)
            if email_pessoal and not pd.isna(email_pessoal):
                destinatarios.append(email_pessoal)

            if not destinatarios:
                logging.warning(f"{nome} não possui e-mail válido cadastrado. Pulando envio.")
                continue

            subject = f"🎉 Feliz Aniversário, {nome}!"
            saudacao = f"Olá, {nome}!"
            mensagem = (
                f"Hoje é o seu dia! 🎉\n\n"
                f"Toda a equipe deseja a você um feliz aniversário, com muita saúde, paz e sucesso.\n"
                f"Aproveite muito o seu dia!"
            )
            body = self.utilitariosComuns.gerar_corpo_email_aniversariantes(saudacao, mensagem, [], [])

            logging.info(f"Enviando e-mail de feliz aniversário para {nome} ({', '.join(destinatarios)}).")
            self.conexaoGraph.enviar_email(
                [EMAIL_TESTE] if AMBIENTE == "QAS" else destinatarios,
                subject,
                body
            )