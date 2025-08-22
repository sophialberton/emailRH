# emailRH
Automação de envio de emails para o RH da FGM Dental Group.

# Atual Versão: Apenas Aniversariantes de Tempo de Casa
- [x] E-mails para RH: mensal de *aniversariantes tempo de casa* (todo dia 27 do mês)
- [x] E-mails para gestores: mensal *aniversariantes tempo de casa* (todo dia 27 do mês)
---

# Implementar na Versão tempo de casa
- [ ] E-mails para gestores: diário *aniversariantes de casa*
- [ ] E-mails individuais para os *aniversariantes de casa* no dia do seu aniversário
- [ ] E-mails individuais para os *aniversariantes ESTRELAS de casa* no dia do seu aniversário
---
# Implementar para inegrar aniversários de nascimento
- [ ] E-mails para RH: mensal de *aniversariantes nascimento* (todo dia 27 do mês)
- [ ] E-mails para gestores: mensal de *aniversariantes nascimento* (todo dia 27 do mês)
- [ ] E-mails para gestores: diário *aniversariantes nascimento*
- [ ] E-mails individuais para os *aniversariantes nascimento* no dia do seu aniversário

#### Estrutura/Arquitetura Atual
```
├───data
│   │   conexaoGraph.py - Funções que conectam com a API Graph
│   │   conexaoSenior.py - Funções que conectam com o Banco de Dados Senior
│   └───
├───email
│   │   emailEmpresa.py - Funções relacionadas aos emails de aniversário de tempo de empresa
│   └───
|
├───gerenciadores
│   │   gerenciarAniversariantes.py - Funções que calculam/filtram aniversáriantes
│   │   gerenciarColaboradores.py - Funções que válidam cadastro de colaborador para calculos
│   └───
|
├───script
│   │   main.py - Orquestra as principais funções para executar
│   └───
├───utils
│   │   config.py - Dados de acesso
│   │   utilitariosComuns.py - Funções utilizadas em todo projeto
|   └───
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
