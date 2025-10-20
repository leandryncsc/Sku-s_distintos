import cx_Oracle
import pandas as pd
import configparser
import os
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo



class OracleConnection:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.connection = None
        # A conexão será aberta explicitamente via self.connect()
    
    def connect(self):
        try:
            os.environ['NLS_LANG'] = 'BRAZILIAN PORTUGUESE_BRAZIL.UTF8'

            host = self.config.get('ORACLE', 'host')
            port = self.config.getint('ORACLE', 'port')
            service_name = self.config.get('ORACLE', 'service_name')
            user = self.config.get('ORACLE', 'user')
            password = self.config.get('ORACLE', 'password')

            dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
            self.connection = cx_Oracle.connect(
                user=user,
                password=password, 
                dsn=dsn
            )
            return True
        except cx_Oracle.DatabaseError as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except cx_Oracle.DatabaseError as e:
                print(f"Erro ao fechar a conexão: {e}")



    def execute_query(self):
        nome_tabela = input("Digite o mes nesse formato ex: 202412: ")

        try:
            if not self.connection:
                print("Conexão não está aberta. Conecte antes de executar a consulta.")
                return

            cursor = self.connection.cursor()

            cursor.execute(f"""
            SELECT 
        FILIAL,
        COUNT(ITEM) AS ITENS,
        COUNT(DISTINCT ITEM) AS ITENS_DISTINTOS,
        COUNT(DISTINCT CLIENTES) AS CLIENTES,
        TRUNC(COUNT(ITEM)/COUNT(DISTINCT CLIENTES),2) AS ITENS_POR_CUPOM,
        TRUNC(COUNT(DISTINCT ITEM)/COUNT(DISTINCT CLIENTES),2) AS ITENS_DISTINTOS_POR_CUPOM
        FROM
        (
        SELECT 
        TRIM(B.TIP_NOME_FANTASIA) AS FILIAL,
        A.R60I_DTA||'.'||A.R60I_CXA||'.'||A.R60I_CUP AS CLIENTES,
        A.R60I_DTA||'.'||A.R60I_CXA||'.'||A.R60I_CUP||'.'||A.R60I_ITE AS ITEM
        FROM AA1FR60I_{nome_tabela} A, RMS.AA2CTIPO B
            WHERE A.R60I_FIL=B.TIP_CODIGO
            AND R60I_SIT     = ' '
        ) GROUP BY FILIAL
            """)

            colunas = [desc[0] for desc in cursor.description]  
            dados = cursor.fetchall()  
            df = pd.DataFrame(dados, columns=colunas)  

            print("Dados recuperados do banco de dados:")
            print(df)

            medias = df.select_dtypes(include='number').mean()

            
            # Adicionando uma linha para as médias
            df.loc[len(df)] = ['Média'] + medias.tolist()

            with pd.ExcelWriter('resultado_'+nome_tabela+'.xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Dados', index=False)

                workbook = writer.book
                worksheet = writer.sheets['Dados']

                tabela = Table(displayName="TabelaDados", ref=worksheet.dimensions)

                style = TableStyleInfo(
                    name="TableStyleMedium9", showFirstColumn=False,
                    showLastColumn=False, showRowStripes=True, showColumnStripes=True
                )
                tabela.tableStyleInfo = style

                worksheet.add_table(tabela)

            print("\nDados escritos na planilha 'resultado.xlsx' com sucesso.")

        except cx_Oracle.DatabaseError as e:
            print(f"Erro ao acessar o banco de dados: {e}")
        finally:
            try:
                if cursor:
                    cursor.close()
            except Exception:
                pass

            # Não fechar aqui; o ciclo de vida da conexão é gerido fora


if __name__ == "__main__":
    oracle = OracleConnection()
    conectado = oracle.connect()
    if conectado:
        try:
            oracle.execute_query()
        finally:
            oracle.close()
    else:
        print("Falha ao conectar. Verifique o arquivo de configuração e a rede.")