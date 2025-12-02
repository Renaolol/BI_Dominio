import pyodbc
import pandas as pd
from pprint import pprint
CONEXAO = "DSN=ContabilPBI;UID=PBI;PWD=Pbi"

def conecta_odbc():
    return pyodbc.connect(CONEXAO)

def retorna_lanctos(codi_emp,data_lancto):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
    SELECT
		ctlancto.codi_emp,
		geempre.razao_emp,
		ctlancto.codi_lote,
		efentradas.nume_ent,
		ctlancto.data_lan,
		ctlancto.vlor_lan,
		ctlancto.cdeb_lan,
		cdeb_ctcontas.nome_cta AS cdeb_nome_cta,
		ctlancto.ccre_lan,
		ccre_ctcontas.nome_cta AS ccre_nome_cta,
		ctlancto.chis_lan,
		ctlancto.codi_usu,
		ctlancto.orig_lan,
		ctlancto.origem_reg
    FROM
		bethadba.ctlancto
		LEFT JOIN
		bethadba.efentradas_lancto
		ON ctlancto.codi_emp = efentradas_lancto.codi_emp
		AND ctlancto.nume_lan = efentradas_lancto.nume_lan
		LEFT JOIN
		bethadba.efentradas
		ON efentradas_lancto.codi_emp = efentradas.codi_emp
		AND efentradas_lancto.codi_ent = efentradas.codi_ent
		LEFT JOIN
		bethadba.geempre
		ON ctlancto.codi_emp = geempre.codi_emp
		LEFT JOIN
		bethadba.ctcontas AS cdeb_ctcontas
		ON ctlancto.cdeb_lan = cdeb_ctcontas.codi_cta
		AND ctlancto.codi_emp = cdeb_ctcontas.codi_emp
		LEFT JOIN
		bethadba.ctcontas AS ccre_ctcontas
		ON ctlancto.ccre_lan = ccre_ctcontas.codi_cta
		AND ctlancto.codi_emp = ccre_ctcontas.codi_emp
    WHERE
        ctlancto.codi_emp = ? AND ctlancto.data_lan >=?
            """
    cursor.execute(query, (codi_emp,data_lancto))
    lanctos = cursor.fetchall()
    conn.close()
    return lanctos
#lanctos = retorna_lanctos(1, "2025-11-01")

def retorna_menor_salario_min(competencia):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
			SELECT f.salario, e.nome, emp.NOME, f.competencia, f.vencto_ferias, f.tipo
            FROM 
            bethadba.foprovisoes f
            LEFT JOIN
            bethadba.foempregados e
            ON f.i_empregados = e.i_empregados
            AND f.codi_emp = e.codi_emp
            LEFT JOIN
            bethadba.PRVCLIENTES emp
            ON f.codi_emp = emp.CODIGO
            WHERE f.salario < 1518 AND f.salario > 0 AND f.competencia >= ? AND f.tipo = 1
			"""
    cursor.execute(query,(competencia))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_prox_ferias(competencia):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
			SELECT e.nome, f.GOZO_INICIO, f.GOZO_FIM, f.ABONO_PAGA, f.ABONO_INICIO, f.ABONO_FIM, emp.nome,f.TIPO
            FROM 
            bethadba.foempregados e
            LEFT JOIN
            bethadba.FOFERIAS_GOZO f
            ON f.I_EMPREGADOS = e.i_empregados
            AND f.CODI_EMP = e.codi_emp
            LEFT JOIN
            bethadba.PRVCLIENTES emp
            ON e.codi_emp = emp.CODIGO
            WHERE f.GOZO_INICIO >= ?
			"""
    cursor.execute(query, (competencia))
    resultado = cursor.fetchall()
    conn.close()
    return resultado 

