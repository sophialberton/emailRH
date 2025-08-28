# src/utils/utilitariosComuns.py
from datetime import datetime
import locale
import os
from data.conexaoGraph import conexaoGraph
import logging

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

EMAIL_RH = os.getenv("EMAIL_RH", "comunicacaointerna@fgmdentalgroup.com")
EMAIL_TESTE = os.getenv("EMAIL_TESTE", "sophia.alberton@fgmdentalgroup.com")
AMBIENTE = os.getenv("AMBIENTE", "QAS")

class utilitariosComuns:
    def __init__(self):
        self.conexaoGraph = conexaoGraph()

    def formatar_nome(self, nome):
        """Formata o nome com a primeira letra maiúscula de cada palavra."""
        return ' '.join(word.capitalize() for word in nome.split()) if nome else ""

    def _gerar_tabela_html(self, colunas, dados, emojis=None):
        """Gera a estrutura de uma tabela HTML a partir de colunas e dados."""
        tabela = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
        tabela += "<tr style='background-color: #d3d3d3; color: black;'>"
        for coluna in colunas:
            tabela += f"<th>{coluna}</th>"
        tabela += "</tr>"
        for linha in dados:
            tabela += "<tr>"
            for i, valor in enumerate(linha):
                emoji = emojis[i] if emojis and i < len(emojis) else ""
                tabela += f"<td>{emoji} {valor}</td>"
            tabela += "</tr>"
        tabela += "</table>"
        return tabela

    def gerar_corpo_email_aniversariantes_duplicados(self, saudacao, mensagem, colunas, dados, emojis=None):
        """Gera apenas a tabela HTML do email de aniversariantes, sem assinatura final."""
        corpo = f"<strong>{saudacao}</strong><br>{mensagem}<br><br>"
        corpo += self._gerar_tabela_html(colunas, dados, emojis)
        return corpo

    def gerar_corpo_email_aniversariantes(self, saudacao, mensagem, colunas, dados, emojis=None):
        """Gera o corpo HTML do email de aniversariantes."""
        corpo = f"<strong>{saudacao}</strong><br>{mensagem}<br><br>"
        corpo += self._gerar_tabela_html(colunas, dados, emojis)
        corpo += "<br>Atenciosamente,<br>Equipe de Gestão de Pessoas"
        return corpo

    def gerar_email_com_imagem(self, imagem_src, texto_alt, link=None):
        """Gera um email com imagem centralizada, com ou sem link."""
        link_tag = f'<a href="{link}" style="display: flex; justify-content: center; align-items: center;">' if link else '<a style="display: flex; justify-content: center; align-items: center;">'
        return f"""<html><body style="display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
                    {link_tag}
                        <img src="{imagem_src}" alt="{texto_alt}">
                    </a></body></html>"""

    def enviar_email_formatado(self, destinatarios, assunto, body):
        """Função auxiliar para enviar e-mails, tratando ambiente de QAS/PRD."""
        if not destinatarios:
            logging.warning("Nenhum destinatário para o e-mail.")
            return

        email_para_envio = destinatarios
        if AMBIENTE == "QAS":
            email_para_envio = EMAIL_TESTE.split(',') if isinstance(EMAIL_TESTE, str) else [EMAIL_TESTE]

        self.conexaoGraph.enviar_email(email_para_envio, assunto, body)