### Requisitos do Script

#### Requisitos Funcionais (O que o sistema FAZ)

São as funcionalidades e comportamentos específicos do sistema; as ações que ele executa.

- [ ] **RF01 - Extração de Dados:** O sistema deve se conectar a um banco de dados Oracle (Senior) e extrair uma lista de colaboradores com seus dados (nome, CPF, datas, e-mails, gestor, etc.).

- [ ] **RF02 - Classificação de Colaboradores:** O sistema deve processar a lista de colaboradores e classificá-los como "válidos" para o processo, ignorando demitidos, colaboradores sem e-mail ou sem gestor definido.

- [ ] **RF03 - Envio de E-mail Individual de Aniversário de Empresa:** O sistema deve enviar um e-mail de parabenização para cada colaborador no dia exato do seu aniversário de tempo de empresa.

- [ ] **RF04 - Envio de E-mail Individual de Aniversário de Nascimento:** O sistema deve enviar um e-mail de parabenização para cada colaborador no dia exato do seu aniversário de nascimento.

- [ ] **RF05 - Notificação Diária para Gestores:** O sistema deve enviar um e-mail diário para cada gestor, listando os membros da sua equipe que fazem aniversário (de empresa ou de nascimento) naquele dia.

- [ ] **RF06 - Relatório Mensal para o RH:** O sistema deve, todo dia 27 do mês, enviar um relatório por e-mail para o RH com a lista completa de aniversariantes (de empresa e de nascimento) do próximo mês.

- [ ] **RF07 - Relatório Mensal para Gestores:** O sistema deve, todo dia 27 do mês, enviar um relatório por e-mail para cada gestor com a lista de aniversariantes (de empresa e de nascimento) da sua equipe para o próximo mês.

- [ ] **RF08 - Geração de Logs:** O sistema deve registrar todas as suas operações, sucessos, avisos e erros em arquivos de log diários.

---

#### Requisitos Não-Funcionais (Como o sistema É)

São os critérios de qualidade, restrições e atributos de operação do sistema. Eles não descrevem uma funcionalidade, mas sim como o sistema deve operar.

- [ ] **RNF01 - Segurança:** O sistema não deve expor credenciais de acesso (senhas de banco de dados, chaves de API) em seu código-fonte. As informações sensíveis devem ser gerenciadas através de variáveis de ambiente (.env).

- [ ] **RNF02 - Confiabilidade:** O sistema deve ser robusto a falhas de conexão com o banco de dados, implementando um sistema de tentativas de reconexão antes de falhar completamente.

- [ ] **RNF03 - Manutenibilidade:** O código deve ser organizado em módulos com responsabilidades claras (conexão de dados, regras de negócio, utilitários, etc.), facilitando futuras alterações e correções.

- [ ] **RNF04 - Configurabilidade:**
  - [ ] O sistema deve permitir alternar facilmente entre um ambiente de teste (que envia e-mails para um endereço de debug) e produção (que envia para os destinatários reais).
  - [ ] Os textos e formatos dos e-mails devem ser facilmente customizáveis sem a necessidade de alterar a lógica principal do programa.

- [ ] **RNF05 - Automação:** O sistema deve ser projetado para ser executado de forma autônoma e agendada (por exemplo, uma vez por dia), sem necessidade de intervenção manual.

- [ ] **RNF06 - Portabilidade:** As dependências do projeto devem ser claramente definidas em um arquivo (requirements.txt), garantindo que ele possa ser facilmente instalado e executado em diferentes máquinas.
