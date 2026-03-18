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
            SELECT
                proventos, competencia
                from 
                bethadba.fobasesserv
            WHERE
            codi_emp = 32
            AND
            i_empregados = 8
               """
    cursor.execute(query)
    resultado = cursor.fetchall()
    conn.close()
    return resultado
pprint(teste())



