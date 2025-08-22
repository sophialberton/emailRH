# src/utils/email_config.py

"""
Arquivo de configuração para centralizar os templates de e-mail.
Cada chave representa um tipo de e-mail e contém seu assunto,
saudação, mensagem e colunas (para e-mails com tabelas).
"""

EMAIL_TEMPLATES = {
    "RH_ANIVERSARIANTES_EMPRESA": {
        "assunto": "Aniversariantes de Tempo de Empresa - {mes_seguinte}",
        "saudacao": "Olá,",
        "mensagem": "Segue a lista de colaboradores que fazem aniversário de tempo de empresa no mês de {mes_seguinte}:",
        "colunas": ["🎉 Nome", "📅 Data de Admissão", "🏢 Anos de Empresa", "📍 Setor", "👤 Superior"],
    },
    "GESTOR_ANIVERSARIANTES_EMPRESA": {
        "assunto": "Aniversariantes de Tempo de Empresa da sua Equipe - {mes_seguinte}",
        "saudacao": "Olá, {nome_gestor}.",
        "mensagem": "Segue a lista dos seus liderados que fazem aniversário de tempo de empresa no mês de {mes_seguinte}:",
        "colunas": ["🎉 Nome", "📅 Data de Admissão", "🏢 Anos de Empresa"],
    },
    "INDIVIDUAL_ANIVERSARIANTE_EMPRESA": {
        "assunto": "🎉 Parabéns pelo seu aniversário de empresa!",
        "saudacao": "Olá, {nome}!",
        "mensagem": (
            "Hoje, {hoje_str}, você completa {anos_de_casa} ano(s) de empresa! 🎉<br><br>"
            "Queremos agradecer por todo o seu empenho e dedicação desde sua admissão em {data_admissao}.<br>"
            "Continue brilhando e contribuindo com seu talento. Parabéns por essa conquista!"
        ),
        "colunas": [],
    },
    "GESTOR_DIARIO_ANIVERSARIANTE_EMPRESA": {
        "assunto": "🎉 Aniversariantes de Tempo de Empresa - {hoje_str}",
        "saudacao": "Olá, {nome_gestor}!",
        "mensagem": "Hoje ({hoje_str}), os seguintes colaboradores da sua equipe completam aniversário de tempo de empresa:",
        "colunas": ["🎉 Nome", "📅 Data de Admissão", "🏢 Anos de Empresa"],
    },
    "INDIVIDUAL_ANIVERSARIANTE_NASCIMENTO": {
        "assunto": "🎉 Feliz Aniversário, {nome}!",
        "texto_alt_imagem": "Feliz Aniversário!"
    }
}