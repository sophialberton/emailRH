import oracledb
import logging
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import time

class conexaoSenior:
    def __init__(self, **kwargs):
        load_dotenv(find_dotenv())
        self.connection = None
        self.cursor = None
        self.user_senior = kwargs.get("user_senior")
        self.password_senior = kwargs.get("password_senior")
        self.host_senior = kwargs.get("host_senior")
        self.port_senior = kwargs.get("port_senior")
        self.service_name_senior = kwargs.get("service_name_senior")

    def conexaoBancoSenior(self, tentativas=3, atraso=5):
        """
        Tenta conectar ao banco de dados com um número definido de tentativas.
        """
        dsn_str = oracledb.makedsn(self.host_senior, self.port_senior, service_name=self.service_name_senior)
        
        for tentativa in range(tentativas):
            try:
                self.connection = oracledb.connect(
                    user=self.user_senior,
                    password=self.password_senior,
                    dsn=dsn_str
                )
                self.cursor = self.connection.cursor()
                logging.info("-------------->>>Informacoes da Database--------------")
                logging.info(">Conexao com o banco de dados estabelecida com sucesso")
                return True
            except oracledb.DatabaseError as e:
                logging.error(f">Erro ao estabelecer conexão (tentativa {tentativa + 1}/{tentativas}): {e}")
                if tentativa < tentativas - 1:
                    logging.info(f"Tentando novamente em {atraso} segundos...")
                    time.sleep(atraso)
                else:
                    logging.error("Não foi possível conectar ao banco de dados após várias tentativas.")
                    return False
        return False

    def desconectar(self):
        """Fecha o cursor e a conexão com o banco de dados de forma segura."""
        if self.cursor:
            try:
                self.cursor.close()
                logging.info(">Cursor fechado.")
            except oracledb.DatabaseError as e:
                logging.error(f">Erro ao fechar o cursor: {e}")
            finally:
                self.cursor = None
        
        if self.connection:
            try:
                self.connection.close()
                logging.info(">Conexão com o banco de dados fechada.")
            except oracledb.DatabaseError as e:
                logging.error(f">Erro ao fechar a conexão: {e}")
            finally:
                self.connection = None

    def consultaDadosSenior(self):
        """
        Executa a consulta e retorna um DataFrame.
        Usa pd.read_sql_query para simplificar a obtenção de dados.
        """
        if not self.connection:
            logging.error("> Conexao com o banco de dados não foi estabelecida.")
            return pd.DataFrame() # Retorna DataFrame vazio

        query = """
                SELECT
                    FUN.NUMCPF AS "Cpf",
                    FUN.NOMFUN AS "Nome",
                    FUN.SITAFA AS "Situacao",
                    FUN.NUMCAD AS "Matricula",
                    EM.EMAPAR AS "Email_pessoal",
                    EM.EMACOM AS "Email_corporativo",
                    FUN.DATADM AS "Data_admissao",
                    FUN.DATAFA AS "Data_demissao",
                    FUN.DATNAS AS "Data_nascimento",
                    TO_CHAR(ROUND((CASE 
                    WHEN FUN.DATAFA = TO_DATE('1900-12-31', 'YYYY-MM-DD') THEN SYSDATE
                    ELSE FUN.DATAFA
                    END - FUN.DATADM ) / 365.25, 2)) AS "Tempo_FGM",
                    O.GESTOR AS "Superior",
                    EMG.EMACOM AS "Email_superior",
                    ORN.NOMLOC AS "Local",
                    GEST.SITAFA AS "Situacao_superior"
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
                    LEFT JOIN SENIOR.R017HIE B ON
                        SUBSTR(A.POSPOS, 1, LENGTH(A.POSPOS)-2) = B.POSPOS
                            AND A.ESTPOS = B.ESTPOS
                            AND A.CODTHP = B.CODTHP
                            AND A.REVHIE = B.REVHIE
                        LEFT JOIN SENIOR.R034FUN C ON
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
        try:
            logging.info("-------------->>>Query---------------------------------")
            # Usando read_sql_query para mais eficiência
            df = pd.read_sql_query(query, self.connection)
            # Renomeia as colunas para o padrão do projeto
            df.columns = [
                'Cpf','Nome','Situacao','Matricula','Email_pessoal','Email_corporativo',
                'Data_admissao','Data_demissao','Data_nascimento','Tempo_FGM','Superior', 'Email_superior',
                'Local','Situacao_superior'
            ]
            logging.info(f">Consulta executada com sucesso. {len(df)} registros encontrados.")
            return df
        except (oracledb.DatabaseError, pd.io.sql.DatabaseError) as e:
            logging.error(f">Erro ao executar query: {e}")
            return pd.DataFrame() # Retorna DataFrame vazio em caso de erro
        finally:
            logging.info("-------------->>>Script Rodando------------------------")