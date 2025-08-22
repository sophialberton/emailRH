from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import logging

class utilitariosComuns:
    def formatar_nome(self, nome):
        """Formata o nome com a primeira letra maiúscula de cada palavra."""
        return ' '.join(word.capitalize() for word in nome.split()) if nome else ""

    def converter_para_datetime(data_str):
        """Converte uma string para datetime, se necessário."""
        return data_str if isinstance(data_str, datetime) else datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")

    def converter_data_dd_mm(data_str):
        """Converte uma data no formato dd/mm para datetime, assumindo o ano como 2024."""
        return datetime.strptime(f"{data_str}/2024", "%d/%m/%Y")

    def extrair_datas_aniversario(aniversariantes):
        """Extrai todas as datas de aniversário da estrutura de aniversariantes."""
        return [funcionario[1] for info in aniversariantes.values() for funcionario in info["funcionarios"]]

    def extrair_dados_colaborador(colaborador):
        """Extrai os dados relevantes de um colaborador."""
        return {
            "cpf": str(colaborador.NUMCPF).zfill(11),
            "nome": utilitariosComuns.formatar_nome(colaborador.NOMFUN),
            "email_corporativo": colaborador.EMACOM,
            "email_pessoal": colaborador.EMAPAR,
            "nome_usuario": colaborador.NOMUSU,
            "situacao": colaborador.SITAFA,
            "data_admissao": utilitariosComuns.converter_para_datetime(colaborador.DATADM),
            "data_nascimento": utilitariosComuns.converter_para_datetime(colaborador.DATNAS),
            "data_demissao": utilitariosComuns.converter_para_datetime(getattr(colaborador, "DATAFA", None)) if hasattr(colaborador, "DATAFA") else None,
            "local": getattr(colaborador, "NOMLOCAL", None),
            "estpos": getattr(colaborador, "ESTPOS", None),
            "postra": getattr(colaborador, "POSTRA", None),
            "supervisor_usuario": getattr(colaborador, "USERSUP", None)
        }

    def verificar_eventos_hoje(dados):
        """Verifica se hoje é aniversário ou admissão do colaborador."""
        hoje = datetime.now()
        admissao_hoje = dados["data_admissao"].strftime("%d/%m/%y") == hoje.strftime("%d/%m/%y")
        aniversario_hoje = dados["data_nascimento"].strftime("%d/%m") == hoje.strftime("%d/%m")
        return admissao_hoje, aniversario_hoje

    def gerar_corpo_email_aniversariantes(self, saudacao, mensagem, colunas, dados, emojis=None):
        """Gera o corpo HTML do email de aniversariantes."""
        body = f"<strong>{saudacao}</strong><br>{mensagem}<br><br>"
        body += "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
        body += "<tr style='background-color: #d3d3d3; color: black;'>"
        for coluna in colunas:
            body += f"<th>{coluna}</th>"
        body += "</tr>"
        for linha in dados:
            body += "<tr>"
            for i, valor in enumerate(linha):
                emoji = emojis[i] if emojis and i < len(emojis) else ""
                body += f"<td>{emoji} {valor}</td>"
            body += "</tr>"
        body += "</table><br>Atenciosamente,<br>Equipe de Gestão de Pessoas"
        return body

    def gerar_email_com_imagem(self, imagem_src, texto_alt, link=None):
        """Gera um email com imagem centralizada, com ou sem link."""
        link_tag = f"""<a href="{link}" style="display: flex; justify-content: center; align-items: center;">""" if link else "<a style='display: flex; justify-content: center; align-items: center;'>"
        return f"""<html><body style="display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
                    {link_tag}
                        <img src="{imagem_src}" alt="{texto_alt}">
                    </a></body></html>"""