import pyodbc
import pandas as pd
from pprint import pprint
from datetime import timedelta, time, date, datetime
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

def vencimento_ferias (competencia_incial, competencia_final):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query1 = """
            SELECT
            f.CODI_EMP, emp.NOME, e.nome, f.LIMITE_INICIO_GOZO, f.TIPO, f.GOZO_INICIO
            FROM
            bethadba.FOFERIAS_PROGRAMACAO f
            LEFT JOIN
            bethadba.foempregados e
            ON
            f.CODI_EMP = e.codi_emp
            AND
            f.I_EMPREGADOS = e.I_empregados
            LEFT JOIN
            bethadba.PRVCLIENTES emp
            ON
            e.codi_emp = emp.CODIGO
            WHERE
            f.LIMITE_INICIO_GOZO >= ? AND f.LIMITE_INICIO_GOZO <=? AND f.TIPO = 1
            """
    query2 = """
            SELECT
            f.CODI_EMP, emp.NOME, e.nome, f.LIMITE_PARA_GOZO, f.SITUACAO
            FROM
            bethadba.FOFERIAS_AQUISITIVOS f
            LEFT JOIN
            bethadba.foempregados e
            ON
            f.CODI_EMP = e.codi_emp
            AND
            f.I_EMPREGADOS = e.I_empregados
            LEFT JOIN
            bethadba.PRVCLIENTES emp
            ON
            e.codi_emp = emp.CODIGO
            WHERE
            f.LIMITE_PARA_GOZO >= ? AND f.LIMITE_PARA_GOZO <=? AND (f.SITUACAO = 1 OR f.SITUACAO = 2) AND emp.SITUACAO != 'I' AND emp.CODIGO <=999
            """
    cursor.execute(query2, (competencia_incial, competencia_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado 

def registro_atividades(data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
            e.nome_emp, l.usua_log, l.data_log, l.tini_log, l.tfim_log, dfim_log,l.sist_log
            FROM
            bethadba.geloguser l
            LEFT JOIN bethadba.geempre e
            ON l.codi_emp = e.codi_emp
            WHERE l.data_log >= ?  AND l.data_log <=?
            ORDER BY l.data_log
            """
    cursor.execute(query,(data_inicial,data_final))
    atividades = cursor.fetchall()
    conn.close()
    return atividades
  
def retorna_usuarios(data_inicial):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT DISTINCT
            usua_log
            FROM
            bethadba.geloguser
            WHERE
            data_log >=?
            """
    cursor.execute(query,(data_inicial))
    users = cursor.fetchall()
    conn.close()
    return users  

def time_to_timedelta(t):
    return timedelta(hours=t.hour,minutes=t.minute,seconds=t.second)
    
def retorna_modulo():
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT nome, codigo from bethadba.GEMODULOS
            """
    cursor.execute(query)
    modulo = cursor.fetchall()
    conn.close()
    return modulo          

def retorna_ociosos():
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT c.usuario, c.inicio_conexao, e.NOME, c.ocioso_inicial
            FROM
            bethadba.geconexoesativas c
            LEFT JOIN
            bethadba.PRVCLIENTES e
            ON
            c.empresa = e.CODIGO
            WHERE c.empresa >0 AND c.ocioso_inicial > '1900-01-01' 
            """
    cursor.execute(query)
    modulo = cursor.fetchall()
    conn.close()
    return modulo

def retorna_conectado():
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT c.usuario, c.inicio_conexao, e.NOME
            FROM
            bethadba.geconexoesativas c
            LEFT JOIN
            bethadba.PRVCLIENTES e
            ON
            c.empresa = e.CODIGO
            WHERE c.empresa > 0 AND (c.ocioso_inicial = '1900-01-01' OR c.ocioso_inicial IS NULL)
            """
    cursor.execute(query)
    modulo = cursor.fetchall()
    conn.close()
    return modulo

def retorna_faturamento_por_imposto(dt_init,cod):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT i.nome_imp, s.sdev_sim, s.scre_sim, s.vcos_sim, s.vcov_sim,s.data_sim
            FROM bethadba.efsdoimp s
            LEFT JOIN bethadba.geimposto i
            ON s.codi_emp = i.codi_emp AND s.codi_imp = i.codi_imp
            WHERE
            s.data_sim >= ? AND (s.sdev_sim > 0 OR s.scre_sim > 0) AND s.codi_emp =?
            """
    cursor.execute(query,(dt_init,cod))
    empresa = cursor.fetchall()
    conn.close()
    return empresa    

def retorna_nome_empresa(cod):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT NOME FROM bethadba.PRVCLIENTES WHERE CODIGO = ?
            """
    cursor.execute(query,(cod))
    empresa = cursor.fetchall()
    conn.close()
    return empresa 

def formata_valor(valor):
    if valor is None or "0":
        valor = "R$ 0,00"
    else:
        valor = str(valor)
        valor = f'R$ {valor.replace(",","X").replace(".",",").replace("X",".")}'
    return valor

def formata_horas_min_seg(valor):
    resultado = valor    
    if valor <= 0.99999999:
        valor = valor*60
        if valor < 10:
            resultado = f"00:00:{valor:.0f}0"
        else:    
            resultado = f"00:00:{valor:.0f}"
    elif valor >= 60.00:
        horas = int(valor)//60
        minutos = int(valor)-(horas*60)       
        segundos = (valor - horas - minutos)/60
        if horas >=10:
            horas = f'{horas:.0f}'
        else:    
            horas = f'0{horas:.0f}'
        if segundos <10 :
            segundos = f'{segundos:.0f}0'
        else:
            segundos = str(f'{segundos:.0f}')    
        if minutos < 10:
            resultado = str(f'{horas}:0{minutos:.0f}:{segundos}')    
        else:
            resultado = str(f'{horas}:{minutos:.0f}:{segundos}')        
    elif valor >= 1.0:
        minutos = int(valor)
        segundos = (valor - minutos)*60
        horas = '00'
        if segundos <10 :
            segundos = f'{segundos:.0f}0'
        else:
            segundos = f'{segundos:.0f}'    
        if minutos < 10:
            resultado = str(f'{horas}:0{minutos:.0f}:{segundos}')      
        else:
            resultado = str(f'{horas}:{minutos:.0f}:{segundos}')          
    return resultado

def retorna_tempo_trabalho_empresa(cod, data_inicial, data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
            l.usua_log, l.data_log, l.tini_log, l.tfim_log, dfim_log, l.sist_log
            FROM
            bethadba.geloguser l
            WHERE l.codi_emp = ? AND l.data_log >= ?  AND l.data_log <=?
            ORDER BY l.data_log
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_admissoes(cod, data_inicial, data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                COUNT(nome)
            FROM
                bethadba.foempregados
            WHERE codi_emp = ? AND admissao >= ? AND admissao <= ?
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
   
    return resultado

def retorna_nome_admissoes(cod, data_inicial, data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                nome
            FROM
                bethadba.foempregados
            WHERE codi_emp = ? AND admissao >= ? AND admissao <= ?
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_total_funcionarios(cod):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                COUNT(e.nome)
            FROM
                bethadba.foempregados e
            LEFT JOIN 
                bethadba.forescisoes r
            ON
                e.codi_emp = r.codi_emp AND e.i_empregados = r.i_empregados
            WHERE e.codi_emp = ? AND r.demissao IS NULL
            """
    cursor.execute(query,(cod))
    resultado = cursor.fetchall()
    conn.close()
    return resultado
def retorna_nome_funcionarios(cod):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                e.nome
            FROM
                bethadba.foempregados e
            LEFT JOIN 
                bethadba.forescisoes r
            ON
                e.codi_emp = r.codi_emp AND e.i_empregados = r.i_empregados
            WHERE e.codi_emp = ? AND r.demissao IS NULL
            """
    cursor.execute(query,(cod))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_demitidos(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                COUNT(e.nome)
            FROM
                bethadba.foempregados e
            LEFT JOIN 
                bethadba.forescisoes r
            ON
                e.codi_emp = r.codi_emp AND e.i_empregados = r.i_empregados
            WHERE e.codi_emp = ? AND r.demissao >= ? and r.demissao <= ?
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_nome_demitidos(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                e.nome
            FROM
                bethadba.foempregados e
            LEFT JOIN 
                bethadba.forescisoes r
            ON
                e.codi_emp = r.codi_emp AND e.i_empregados = r.i_empregados
            WHERE e.codi_emp = ? AND r.demissao >= ? and r.demissao <= ?
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado
