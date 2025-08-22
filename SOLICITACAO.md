# emailRH
Automação de envio de emails para o RH da FGM Dental Group.

# Atual Versão: Envio automatizado de aniversários de nascimento e tempo de casa
- [x] E-mails para RH: mensal de *aniversariantes tempo de casa* (todo dia 27 do mês)
- [x] E-mails para gestores: mensal *aniversariantes tempo de casa* (todo dia 27 do mês)
- [x] E-mails para gestores: diário *aniversariantes de casa*
- [x] E-mails individuais para os *aniversariantes de casa* no dia do seu aniversário
- [x] E-mails para RH: mensal de *aniversariantes nascimento* (todo dia 27 do mês)
- [x] E-mails para gestores: mensal de *aniversariantes nascimento* (todo dia 27 do mês)
- [x] E-mails para gestores: diário *aniversariantes nascimento*
- [x] E-mails individuais para os *aniversariantes nascimento* no dia do seu aniversário
---

# Implementar sobre o envio de tempo de casa
- [ ] E-mails individuais para os *aniversariantes ESTRELAS de casa* no dia do seu aniversário

#### Estrutura/Arquitetura Atual
```
├───data
│   ├─── conexaoGraph.py         # Responsável pela comunicação com a API da Microsoft (Graph) para enviar os e-mails.
│   ├─── conexaoSenior.py        # Gerencia a conexão e a extração de dados do banco de dados Oracle (Senior).
│   └─── __init__.py             # Transforma o diretório 'data' em um pacote Python.
│
├───email_utils
│   ├─── emailEmpresa.py         # Orquestra a criação e o envio de todos os tipos de e-mail (RH, gestores, individuais).
│   ├─── email_config.py         # Centraliza todos os textos e modelos dos e-mails (assuntos, mensagens, etc.).
│   └─── __init__.py             # Transforma o diretório 'email_utils' em um pacote Python.
│
├───gerenciadores
│   ├─── gerenciarAniversariantes.py # Contém a lógica para filtrar e identificar os aniversariantes (de empresa e de nascimento).
│   ├─── gerenciarColaboradores.py # Responsável por classificar os colaboradores em válidos e inválidos, aplicando as regras de negócio.
│   └─── __init__.py             # Transforma o diretório 'gerenciadores' em um pacote Python.
│
├───script
│   ├─── main.py                 # Ponto de entrada do programa; orquestra todo o fluxo de execução.
│   └─── __init__.py             # Transforma o diretório 'script' em um pacote Python.
│
└───utils
    ├─── config.py               # Carrega as variáveis de ambiente e credenciais (senhas, IDs, etc.) do arquivo .env.
    ├─── utilitariosComuns.py    # Fornece funções auxiliares usadas em várias partes do projeto (ex: formatar nome, gerar HTML).
    └─── __init__.py             # Transforma o diretório 'utils' em um pacote Python.V
```
---
### CARTÕES DE TEMPO DE CASA
Envio dos e-mails individuais para os colaboradores:
Os envios para as lideranças seguirão o mesmo modelo dos aniversários:
- 1 envio mensal no dia 27, com a relação dos colaboradores que farão aniversário de casa no mês seguinte;
- 1 envio mensal para cada líder, com a relação da sua equipe que faz aniversário de casa naquele mês;
- 1 envio diário com os nomes dos colaboradores que fazem aniversário de tempo de casa naquele dia.

#### O primeiro envio com a relação completa será realizado no dia 27/08.
Por enquanto:
Para colaboradores com mais de duas matrículas, os envios são feitos manualmente.
Os nomes são encaminhados para meu e-mail, eu realizo a consulta e solicito o envio ao Jovem Aprendiz.

Cartões de Aniversário dos Colaboradores (BIRTHMAIL)
O envio está ocorrendo normalmente:
- E-mails individuais para os aniversariantes no dia do seu aniversário;
- E-mails para as lideranças: mensal, da equipe e diário.
