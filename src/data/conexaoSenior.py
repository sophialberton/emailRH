import oracledb
import logging
import pandas as pd
from dotenv import load_dotenv, find_dotenv

class conexaoSenior:
    def __init__(self,**kwargs):
        load_dotenv(find_dotenv())
        self.connection = None  # Declara conexão como None
        self.cursor = None # Declara cursor como None
        self.user_senior = kwargs.get("user_senior")
        self.password_senior = kwargs.get("password_senior")
        self.host_senior = kwargs.get("host_senior")
        self.port_senior = kwargs.get("port_senior")
        self.service_name_senior = kwargs.get("service_name_senior")

    def conexaoBancoSenior(self):
        dsn = {
            'host_senior': self.host_senior,
            'port_senior': self.port_senior,
            'service_name_senior': self.service_name_senior,
            'user_senior': self.user_senior,
            'password_senior': self.password_senior
        }
        # Verifica se as variaveis de ambiente foram carregadas 
        if None in dsn.values():
            logging.error("Faltando uma ou mais variaveis de ambiente.")
            return False
        try:
            self.connection = oracledb.connect( 
                user=dsn['user_senior'],
                password=dsn['password_senior'],
                dsn=oracledb.makedsn(dsn['host_senior'],dsn['port_senior'],service_name=dsn['service_name_senior'])
            )
            self.cursor = self.connection.cursor()
            logging.info(f"-------------->>>Informacoes da Database--------------")
            logging.info(">Conexao com o banco de dados estabelecida com sucesso")
            return self.cursor
        except oracledb.DatabaseError as e:
            logging.error(">Erro ao estabelecer conexão: %s", e)
            return False
    
    def consultaDadosSenior(self):
        if self.connection is None:
            logging.error("> Conexao om banco de dados não foi estabelecida.")
            return []
        df = pd.DataFrame()
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute(
                """
                SELECT
                    FUN.NUMCPF AS "Cpf",
                    FUN.NOMFUN AS "Nome",
                    FUN.SITAFA AS "Situacao",
                    FUN.NUMCAD AS "Matricula",
                    EM.EMAPAR AS "Email Pessoal",
                    EM.EMACOM AS "Email Corporativo",
                    FUN.DATADM AS "Data de Admissao",
                    FUN.DATAFA AS "Data de Demissão",
                    FUN.DATNAS AS "Data de Nascimento",
                    O.GESTOR AS "Superior Responsável Pelo Setor",
                    EMG.EMACOM AS "Email do Superior",
                    ORN.NOMLOC AS "Local de Trabalho",
                    GEST.SITAFA AS "Situacao do Superior"
                FROM
                    SENIOR.R034FUN FUN
                INNER JOIN SENIOR.R030EMP EMP ON
                    FUN.NUMEMP = EMP.NUMEMP
                INNER JOIN SENIOR.R024CAR CAR ON
                    FUN.CODCAR = CAR.CODCAR
                    AND FUN.ESTCAR = CAR.ESTCAR
                INNER JOIN SENIOR.R034CPL EM ON
                    FUN.NUMCAD = EM.NUMCAD
                    AND FUN.NUMEMP = EM.NUMEMP
                INNER JOIN SENIOR.R016ORN ORN ON
                    ORN.NUMLOC = FUN.NUMLOC
                INNER JOIN SENIOR.R030FIL FIL ON
                    FUN.CODFIL = FIL.CODFIL
                    AND FUN.NUMEMP = FIL.NUMEMP
                LEFT JOIN (
                    SELECT
                        A.ESTPOS,
                        A.POSTRA,
                        C.NUMCAD AS NUMCAD_GESTOR,
                        C.NUMEMP AS NUMEMP_GESTOR,
                        C.NOMFUN AS GESTOR
                    FROM
                        SENIOR.R017HIE A
                    LEFT JOIN SENIOR.R017HIE B 
                        ON
                        SUBSTR(A.POSPOS, 1, LENGTH(A.POSPOS)-2) = B.POSPOS
                            AND A.ESTPOS = B.ESTPOS
                            AND A.CODTHP = B.CODTHP
                            AND A.REVHIE = B.REVHIE
                        LEFT JOIN SENIOR.R034FUN C 
                        ON
                            B.ESTPOS = C.ESTPOS
                            AND B.POSTRA = C.POSTRA
                        WHERE
                            A.CODTHP = 1
                ) O ON
                    FUN.ESTPOS = O.ESTPOS
                    AND FUN.POSTRA = O.POSTRA
                LEFT JOIN SENIOR.R034CPL EMG ON
                    O.NUMCAD_GESTOR = EMG.NUMCAD
                    AND O.NUMEMP_GESTOR = EMG.NUMEMP
                LEFT JOIN SENIOR.R034FUN GEST ON
                    O.NUMCAD_GESTOR = GEST.NUMCAD
                    AND O.NUMEMP_GESTOR = GEST.NUMEMP
                WHERE
                    FUN.TIPCOL = 1
                    AND CAR.TITCAR <> 'PENSIONISTA'
                    AND FUN.NUMEMP <> 100
                ORDER BY
                    FUN.NUMCPF,
                    FUN.DATADM
                """
            )
            colunas = ['Cpf','Nome','Situacao','Matricula','Email_pessoal','Email_corporativo','Data_admissao','Data_demissao','Data_nascimento','Superior', 'Email_superior','Local','Situacao_superior']
            # Definindo os nomes das colunas
            # Criando o DataFrame
            df = pd.DataFrame(self.cursor.fetchall(), columns=colunas)
            logging.info("-------------->>>Query---------------------------------")
            logging.info(">Consulta executada com sucesso.")
            # logging.info("------------------------------------------------------------------------------------")            
        except oracledb.DatabaseError as e:
            logging.error("Erro ao executar query: %s", e)
        finally:
            if self.cursor:
                self.cursor.close()
            logging.info(">Cursor fechado")
            logging.info("-------------->>>Script Rodandno------------------------")
            # print(self.row_data_list)
        return df