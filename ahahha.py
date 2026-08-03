import pyodbc
import pandas as pd
from pprint import pprint
from datetime import timedelta, time, date, datetime
import calendar
import streamlit as st
import psycopg2
from io import BytesIO
CONEXAO = "DSN=ContabilPBI;UID=PBI;PWD=Pbi"

def conecta_odbc():
    return pyodbc.connect(CONEXAO)

def teste():

    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
            SELECT TOP 2 CONTEUDO_XML FROM bethadba.EFATENDIMENTO_NFE_XML_V2
               """
    cursor.execute(query)
    resultado = cursor.fetchall()
    conn.close()
    return resultado
pprint(teste())



