import pyodbc
from pprint import pprint


def retorna_processos():
    conn = pyodbc.connect("DSN=ContabilPBI;UID=PBI;PWD=Pbi")
    cursor=conn.cursor()
    query="""
            SELECT 
                A.I_ATIVIDADE, A.NOME, M.NOME
            FROM 
                bethadba.PCATIVIDADE A
            LEFT JOIN 
                bethadba.PCATIVIDADE_MODULO M
            ON
                A.I_MODULO = M.I_MODULO
            
            """
    query_teste = """
            SELECT 
                G.COMPETENCIA, u.i_usuario, G.DATAHORACONCLUSAO, A.NOME
            FROM 
                bethadba.GEGESTTA_ATIVIDADE G
            LEFT JOIN
                bethadba.usConfUsuario u
            ON
                G.USUARIO = u.CONTACTID
            LEFT JOIN
                bethadba.PCATIVIDADE A
            ON
                A.I_ATIVIDADE = G.ATIVIDADE  
            """
    cursor.execute(query_teste)
    resultado = cursor.fetchall()
    conn.close()
    return resultado

pprint(retorna_processos())