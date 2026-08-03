import pyodbc
import pandas as pd
from pprint import pprint
from datetime import timedelta, time, date, datetime
import calendar
import streamlit as st
import psycopg2
import os
import sqlite3
import socket
from io import BytesIO
CONEXAO = "DSN=ContabilPBI;UID=PBI;PWD=Pbi"

def conecta_odbc():
    return pyodbc.connect(CONEXAO)

def retorna_lanctos(codi_emp,data_lancto):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
    SELECT
		l.codi_emp,
		geempre.razao_emp,
		l.codi_lote,
		efentradas.nume_ent,
		l.data_lan,
		l.vlor_lan,
		l.cdeb_lan,
		cdeb_ctcontas.nome_cta AS cdeb_nome_cta,
		l.ccre_lan,
		ccre_ctcontas.nome_cta AS ccre_nome_cta,
		l.chis_lan,
		l.codi_usu,
		l.orig_lan,
		l.origem_reg
    FROM
		bethadba.ctlancto
		LEFT JOIN
		bethadba.efentradas_lancto
		ON l.codi_emp = efentradas_lancto.codi_emp
		AND l.nume_lan = efentradas_lancto.nume_lan
		LEFT JOIN
		bethadba.efentradas
		ON efentradas_lancto.codi_emp = efentradas.codi_emp
		AND efentradas_lancto.codi_ent = efentradas.codi_ent
		LEFT JOIN
		bethadba.geempre
		ON l.codi_emp = geempre.codi_emp
		LEFT JOIN
		bethadba.ctcontas AS cdeb_ctcontas
		ON l.cdeb_lan = cdeb_ctcontas.codi_cta
		AND l.codi_emp = cdeb_ctcontas.codi_emp
		LEFT JOIN
		bethadba.ctcontas AS ccre_ctcontas
		ON l.ccre_lan = ccre_ctcontas.codi_cta
		AND l.codi_emp = ccre_ctcontas.codi_emp
    WHERE
        l.codi_emp = ? AND l.data_lan >=?
            """
    cursor.execute(query, (codi_emp,data_lancto))
    lanctos = cursor.fetchall()
    conn.close()
    return lanctos
#lanctos = retorna_lanctos(1, "2025-11-01")
def retorna_menor_salario_min(competencia):
    compe=date(competencia.year,competencia.month,1)
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
        SELECT 
            s.SALARIO, e.nome, emp.NOME
        FROM 
            bethadba.fobasesserv s
        LEFT JOIN
            bethadba.foempregados e
        ON
            s.codi_emp = e.codi_emp AND s.i_empregados = e.i_empregados
        LEFT JOIN
            bethadba.PRVCLIENTES emp
        ON
            s.codi_emp = emp.CODIGO
        WHERE
            competencia >=? AND s.SALARIO < 1621 AND s.tipo_process = 11 AND s.rateio=0
			"""
    cursor.execute(query,(compe))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_prox_ferias(competencia:date) -> list :
    inicio_mes =f"{competencia.year}-{(competencia.month)if len(str(competencia.month))>=2 else ('0'+str(competencia.month))}-01" 
    ultimo_dia = calendar.monthrange(competencia.year,competencia.month)[1]
    fim_mes = date(competencia.year,competencia.month,ultimo_dia)


    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
			SELECT 
                e.nome,f.DATA_FIM, emp.nome,f.TIPO
            FROM 
                bethadba.foempregados e
            LEFT JOIN
                bethadba.FOFERIAS_AQUISITIVOS f
            ON 
                f.I_EMPREGADOS = e.i_empregados
            AND 
                f.CODI_EMP = e.codi_emp
            LEFT JOIN
                bethadba.PRVCLIENTES emp
            ON 
                e.codi_emp = emp.CODIGO
            LEFT JOIN
                bethadba.forescisoes r
            ON
                e.codi_emp = r.codi_emp 
            AND 
                e.i_empregados = r.i_empregados
            AND 
                emp.CODIGO = r.codi_emp    
            WHERE 
                f.DATA_FIM >= ? 
            AND 
                f.DATA_FIM <=? 
            AND 
                r.demissao is NULL
            ORDER BY 
                f.DATA_FIM
			"""
    cursor.execute(query, (inicio_mes, fim_mes))
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
            f.CODI_EMP, emp.NOME, e.nome, f.LIMITE_PARA_GOZO, f.SITUACAO, f.DATA_FIM
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
            ORDER BY
            f.DATA_FIM
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
            ORDER BY usua_log
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
    valor = f'{valor:,.2f}'
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
        segundos = (valor - (horas*60) - minutos)*60
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

def retorna_impostos_empresa(cod,data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT DISTINCT(i.nome_imp) FROM
            bethadba.efsdoimp s
            LEFT JOIN 
            bethadba.EFIMPOSTO i
            ON
            s.codi_emp = i.codi_emp AND s.codi_imp = i.codi_imp
            WHERE
            s.codi_emp = ? AND s.data_sim >= ? AND s.data_sim <= ? AND (s.sdev_sim > 0 OR scre_sim >0)
            ORDER BY i.nome_imp
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_debito_credito_imposto(cod, data_inicial,data_final, imposto):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                s.sdev_sim, s.scre_sim, s.data_sim, s.vcos_sim, s.vcov_sim
            FROM
                bethadba.efsdoimp s
            LEFT JOIN bethadba.EFIMPOSTO i
            ON
                s.codi_imp = i.codi_imp AND s.codi_emp = i.codi_emp
            WHERE
                s.codi_emp = ? AND s.data_sim >=? AND s.data_sim <=? AND i.nome_imp = ? 
            """
    cursor.execute(query,(cod, data_inicial,data_final,imposto))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_debito_credito_imposto_simples(cod, data_inicial,data_final, imposto):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                s.sdev_sim, s.scre_sim, s.data_sim, s.vcos_sim, s.vcov_sim
            FROM
                bethadba.efsdoimp s
            LEFT JOIN bethadba.EFIMPOSTO i
            ON
                s.codi_imp = i.codi_imp AND s.codi_emp = i.codi_emp
            WHERE
                s.codi_emp = ? AND s.data_sim >=? AND s.data_sim <=? AND i.codi_imp = ? 
            """
    cursor.execute(query,(cod, data_inicial,data_final,imposto))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_contagem_entradas(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(nume_ent)
            FROM
                bethadba.efentradas
            WHERE
                codi_emp = ? AND ddoc_ent >= ? AND ddoc_ent <= ? 
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_contagem_saidas(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(nume_sai)
            FROM
                bethadba.efsaidas
            WHERE
                codi_emp = ? AND ddoc_sai >= ? AND ddoc_sai <= ? 
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_contagem_servico(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(nume_ser)
            FROM
                bethadba.efservicos
            WHERE
                codi_emp = ? AND ddoc_ser >= ? AND ddoc_ser <= ? 
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_contagem_acumulador_entrada(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(e.nume_ent), a.nome_acu
            FROM
                bethadba.efentradas e
            LEFT JOIN bethadba.EFACUMULADOR a 
            ON
            e.codi_emp = a.codi_emp AND e.codi_acu = a.codi_acu   
            WHERE
                e.codi_emp = ? AND e.ddoc_ent >= ? AND e.ddoc_ent <= ?
            GROUP BY 
            a.nome_acu                
             
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_contagem_acumulador_saida(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(e.nume_sai), a.nome_acu
            FROM
                bethadba.efsaidas e
            LEFT JOIN bethadba.EFACUMULADOR a 
            ON
            e.codi_emp = a.codi_emp AND e.codi_acu = a.codi_acu   
            WHERE
                e.codi_emp = ? AND e.ddoc_sai >= ? AND e.ddoc_sai <= ?
            GROUP BY 
            a.nome_acu                
             
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado   

def retorna_contagem_acumulador_servico(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(e.nume_ser), a.nome_acu
            FROM
                bethadba.efservicos e
            LEFT JOIN bethadba.EFACUMULADOR a 
            ON
            e.codi_emp = a.codi_emp AND e.codi_acu = a.codi_acu   
            WHERE
                e.codi_emp = ? AND e.ddoc_ser >= ? AND e.ddoc_ser <= ?
            GROUP BY 
            a.nome_acu                
             
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado   

def retorna_contagem_lanctos_contabil(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(nume_lan)
            FROM
                bethadba.ctlancto
            WHERE
                codi_emp = ? AND data_lan >= ? AND data_lan <= ?
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado      

def retorna_contagem_tipo_lancto(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(nume_lan), orig_lan
            FROM
                bethadba.ctlancto
            WHERE
                codi_emp = ? AND data_lan >= ? AND data_lan <= ?
            GROUP BY orig_lan
            """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_lancto_tipo(cod, data_inicial,data_final,tipo):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
        SELECT 
            l.data_lan,
            l.vlor_lan,
            d.nome_cta as conta_debito,
            c.nome_cta as conta_credito,
            l.codi_his,
            l.chis_lan,
            l.codi_usu,
            l.orig_lan,
            l.codi_lote
        FROM 
            bethadba.ctlancto l
        LEFT JOIN
            bethadba.ctcontas d
        ON
            l.codi_emp = d.codi_emp AND d.codi_cta = l.cdeb_lan
        LEFT JOIN
            bethadba.ctcontas c
        ON
            l.codi_emp = c.codi_emp AND c.codi_cta = l.ccre_lan
        WHERE
            l.codi_emp = ? AND l.data_lan >=? AND l.data_lan <=? AND l.orig_lan = ?            
"""
    cursor.execute(query,(cod, data_inicial,data_final,tipo))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_lancto_extrato(cod, data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT 
                COUNT(codi_emp)
            FROM
                bethadba.CTEXTRATO_BANCARIO_LANCAMENTO_ITEM
            WHERE codi_emp = ? AND DATA_ITEM >= ? AND DATA_ITEM <= ?
             """
    cursor.execute(query,(cod, data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_valor_hono(cod):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""
        SELECT
            e.codi_emp, c.I_CLIENTE,c.I_CONTRATO, cli.APELIDO, c.DATA_EMISSAO, c.VALOR_CONTRATO, c.DATA_INICIO, nv.VALOR_APLICADO, nv.DATA_REAJUSTE
        FROM
            bethadba.HRCONTRATO c
        LEFT JOIN bethadba.HRCLIENTE cli
        ON
            c.I_CLIENTE = cli.I_CLIENTE
        LEFT JOIN bethadba.geempre e
        ON
            cli.INSCRICAO = e.cgce_emp
        LEFT JOIN bethadba.HRREAJUSTE_CONTRATO nv
        ON
            c.I_CONTRATO = nv.I_CONTRATO
        WHERE
            c.DATA_TERMINO IS NULL AND e.codi_emp = ?
        """
    cursor.execute(query, (cod))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_tempo_empresa_geral(data_inicial, data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
            l.usua_log, l.data_log, l.tini_log, l.tfim_log, dfim_log, l.sist_log
            FROM
            bethadba.geloguser l
            WHERE l.data_log >= ?  AND l.data_log <=?
            ORDER BY l.data_log
            """
    cursor.execute(query,(data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def retorna_codigos_empresas():
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT CODIGO, NOME FROM bethadba.PRVCLIENTES WHERE SITUACAO = 'A'            """
    cursor.execute(query)
    empresa = cursor.fetchall()
    conn.close()
    return empresa 

def retorna_faturamento_simples(cod, data_inicial, data_final):
    conn = conecta_odbc()
    cursor=conn.cursor()
    query='''
        SELECT SUM(bcal_sim), SUM(sdev_sim),((SUM(sdev_sim)/SUM(bcal_sim))*100),data_sim
        FROM bethadba.efsdoimp
        WHERE codi_emp = ? AND data_sim >= ? AND data_sim <= ? and codi_imp = '44' and bcal_sim > 0
        GROUP BY data_sim
        '''
    
    cursor.execute(query,(cod,data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def formata_porcentagem(valor):
    return f'{valor:,.2f} %'

def get_cte(codigo,data_inicio,data_final):
    conn = pyodbc.connect(CONEXAO)
    cursor = conn.cursor()
    query = """
        SELECT
            c.dsai_sai,
            c.nume_sai,
            c.codi_nat,
            m.nome_municipio,
            c.sigl_est,
            md.nome_municipio,
            e.sigla_uf,
            c.PEDAGIO_SAI,
            c.vprod_sai,
            c.vcon_sai
        FROM bethadba.efsaidas AS c
        JOIN bethadba.gemunicipio AS m
        ON m.codigo_municipio = c.codigo_municipio
        JOIN bethadba.gemunicipio AS md
        ON md.codigo_municipio = c.CODIGO_MUNICIPIO_DESTINO
        JOIN bethadba.geestado AS e
        ON md.codigo_uf = e.codigo_uf  
        WHERE c.codi_esp = 38
        AND c.codi_emp = ?
        AND dsai_sai BETWEEN ? AND ?
            """
    cursor.execute(query, (codigo,data_inicio, data_final, ))
    rows = cursor.fetchall()
    lista=[]
    for row in rows:
        lista.append((row[0], row[1], row[2], row[3],row[4], row[5], row[6], row[7], row[8], row[9]))

    cursor.close()
    conn.close()       
    return lista

@st.cache_data()
def retorna_admissoes_todas_empresas(data_inicial, data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                COUNT(nome)
            FROM
                bethadba.foempregados
            WHERE admissao >= ? AND admissao <= ?
            """
    cursor.execute(query,( data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
   
    return resultado

@st.cache_data()
def retorna_demitidos_todas_empresas(data_inicial,data_final):
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
            WHERE 
                r.demissao >= ? and r.demissao <= ?
            """
    cursor.execute(query,( data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

@st.cache_data()
def retorna_demitidos_com_data(data_inicial,data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                COUNT(e.nome), r.demissao
            FROM
                bethadba.foempregados e
            LEFT JOIN 
                bethadba.forescisoes r
            ON
                e.codi_emp = r.codi_emp AND e.i_empregados = r.i_empregados
            WHERE
                r.demissao >= ? and r.demissao <= ?
            GROUP BY
                r.demissao
            """
    cursor.execute(query,( data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

@st.cache_data()
def retorna_admissoes_com_data( data_inicial, data_final):
    conn=conecta_odbc()
    cursor=conn.cursor()
    query="""SELECT
                COUNT(nome), admissao
            FROM
                bethadba.foempregados
            WHERE
                admissao >= ? AND admissao <= ?
            GROUP BY
                admissao
            """
    cursor.execute(query,( data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
   
    return resultado

@st.cache_data()
def retorna_ficha_cadastral_admissoes(data_inicial, data_final):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
        SELECT 
            e.nome,e.cpf, e.admissao, e.CODIGO_ESOCIAL, emp.NOME
        FROM 
            bethadba.foempregados e
        LEFT JOIN 
            bethadba.PRVCLIENTES emp
        ON
            e.codi_emp = emp.CODIGO
        WHERE
            e.codi_emp = emp.CODIGO AND e.admissao >=? AND e.admissao <=?
        ORDER BY emp.NOME
        
        """
    cursor.execute(query,(data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

@st.cache_data()
def retorna_ficha_cadastral_demissoes(data_inicial, data_final):
    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
        SELECT 
            e.nome,e.cpf, r.demissao, e.CODIGO_ESOCIAL, emp.NOME
        FROM 
            bethadba.foempregados e
        LEFT JOIN 
            bethadba.PRVCLIENTES emp
        ON
            e.codi_emp = emp.CODIGO
        LEFT JOIN 
            bethadba.forescisoes r
        ON
            e.codi_emp = r.codi_emp AND e.i_empregados = r.i_empregados
        WHERE
            e.codi_emp = emp.CODIGO AND r.demissao >=? AND r.demissao <=?
        ORDER BY emp.NOME
        
        """
    cursor.execute(query,(data_inicial,data_final))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

PG_NOTAS_CONN_PARAMS = {
    "dbname": os.getenv("NOTAS_DB_NAME", "notas_emitidas"),
    "user": os.getenv("NOTAS_DB_USER", "postgres"),
    "password": os.getenv("NOTAS_DB_PASSWORD", "0176"),
    "host": os.getenv("NOTAS_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("NOTAS_DB_PORT", "5432")),
    "connect_timeout": 5,
}
PG_NOTAS_ENCODINGS = ("UTF8", "WIN1252", "LATIN1")
SQLITE_NOTAS_DB_PATH = os.getenv(
    "NOTAS_SQLITE_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "notas_emitidas.sqlite3"),
)


def _safe_exc_message(exc: Exception) -> str:
    if exc is None:
        return "erro desconhecido"
    try:
        return str(exc)
    except Exception:
        return repr(exc)


def _to_iso_date(valor):
    if isinstance(valor, datetime):
        return valor.date().isoformat()
    if isinstance(valor, date):
        return valor.isoformat()
    return str(valor)


def _to_date_obj(valor):
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str):
        try:
            return datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            return valor
    return valor


def _pesquisa_por_periodo(tipo):
    if tipo is None:
        return False
    tipo_normalizado = str(tipo).strip().lower()
    return tipo_normalizado in ("por periodo", "por período")


def _aviso_fallback_sqlite(exc_pg):
    try:
        chave = "_notas_db_fallback_sqlite_exibido"
        if not st.session_state.get(chave, False):
            st.warning(
                "PostgreSQL indisponivel no momento. "
                "A tela de notas esta usando banco local SQLite em "
                f"`{SQLITE_NOTAS_DB_PATH}`. Detalhe: {_safe_exc_message(exc_pg)}"
            )
            st.session_state[chave] = True
    except Exception:
        pass


def _validar_porta_postgres():
    host = PG_NOTAS_CONN_PARAMS["host"]
    port = PG_NOTAS_CONN_PARAMS["port"]
    timeout = min(PG_NOTAS_CONN_PARAMS.get("connect_timeout", 5), 5)
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return
    except Exception as exc:
        raise ConnectionError(
            "Servico PostgreSQL indisponivel em "
            f"{host}:{port}. Verifique se o servico esta iniciado "
            "e se host/porta estao corretos. "
            f"Erro TCP: {_safe_exc_message(exc)}"
        ) from exc


def conecta_postgres_notas():
    _validar_porta_postgres()

    ultimo_erro = None
    for encoding in PG_NOTAS_ENCODINGS:
        try:
            return psycopg2.connect(
                **PG_NOTAS_CONN_PARAMS,
                options=f"-c client_encoding={encoding}",
            )
        except UnicodeDecodeError as exc:
            # Retry with another client encoding on Windows locales.
            ultimo_erro = exc
            continue
        except psycopg2.Error as exc:
            ultimo_erro = exc
            break

    raise ConnectionError(
        "Falha ao autenticar/conectar no PostgreSQL "
        f"({PG_NOTAS_CONN_PARAMS['dbname']}): "
        f"{_safe_exc_message(ultimo_erro)}"
    )


def conecta_sqlite_notas():
    conn = sqlite3.connect(SQLITE_NOTAS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            cod_cliente INTEGER NOT NULL,
            emissor TEXT NOT NULL,
            tipo TEXT NOT NULL,
            tipo_nota_emitida TEXT NOT NULL DEFAULT '',
            quantidade REAL NOT NULL,
            tempo_minutos REAL NOT NULL DEFAULT 0
        )
        """
    )
    conn.commit()
    return conn


def _garante_schema_notas(conn, engine):
    cursor = conn.cursor()
    if engine == "postgres":
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS registros (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                cod_cliente INTEGER NOT NULL,
                emissor TEXT NOT NULL,
                tipo TEXT NOT NULL,
                tipo_nota_emitida TEXT NOT NULL DEFAULT '',
                quantidade DOUBLE PRECISION NOT NULL,
                tempo_minutos DOUBLE PRECISION NOT NULL DEFAULT 0
            )
            """
        )
        cursor.execute(
            "ALTER TABLE registros ADD COLUMN IF NOT EXISTS tipo_nota_emitida TEXT"
        )
        cursor.execute(
            "UPDATE registros SET tipo_nota_emitida = '' WHERE tipo_nota_emitida IS NULL"
        )
        cursor.execute(
            "ALTER TABLE registros ALTER COLUMN tipo_nota_emitida SET DEFAULT ''"
        )
        cursor.execute(
            "ALTER TABLE registros ALTER COLUMN tipo_nota_emitida SET NOT NULL"
        )
        cursor.execute(
            "ALTER TABLE registros ADD COLUMN IF NOT EXISTS tempo_minutos DOUBLE PRECISION"
        )
        cursor.execute("UPDATE registros SET tempo_minutos = 0 WHERE tempo_minutos IS NULL")
        cursor.execute("ALTER TABLE registros ALTER COLUMN tempo_minutos SET DEFAULT 0")
        cursor.execute("ALTER TABLE registros ALTER COLUMN tempo_minutos SET NOT NULL")
    else:
        cursor.execute("PRAGMA table_info(registros)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        if "tipo_nota_emitida" not in colunas:
            cursor.execute(
                "ALTER TABLE registros ADD COLUMN tipo_nota_emitida TEXT NOT NULL DEFAULT ''"
            )
        if "tempo_minutos" not in colunas:
            cursor.execute(
                "ALTER TABLE registros ADD COLUMN tempo_minutos REAL NOT NULL DEFAULT 0"
            )
        cursor.execute(
            "UPDATE registros SET tipo_nota_emitida = '' WHERE tipo_nota_emitida IS NULL"
        )
        cursor.execute("UPDATE registros SET tempo_minutos = 0 WHERE tempo_minutos IS NULL")
    conn.commit()


def _conecta_notas():
    conn_pg = None
    try:
        conn_pg = conecta_postgres_notas()
        _garante_schema_notas(conn_pg, "postgres")
        return conn_pg, "postgres"
    except Exception as exc_pg:
        if conn_pg is not None:
            conn_pg.close()
        conn_sqlite = conecta_sqlite_notas()
        _garante_schema_notas(conn_sqlite, "sqlite")
        _aviso_fallback_sqlite(exc_pg)
        return conn_sqlite, "sqlite"


def registra_nota(
    date,
    cod_cliente,
    emissor,
    tipo_documento,
    tipo_nota_emitida,
    quantidade,
    tempo_minutos,
):
    conn = None
    try:
        conn, engine = _conecta_notas()
        cursor = conn.cursor()
        if engine == "postgres":
            query = """
                    INSERT INTO registros (
                        date,
                        cod_cliente,
                        emissor,
                        tipo,
                        tipo_nota_emitida,
                        quantidade,
                        tempo_minutos
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """
            cursor.execute(
                query,
                (
                    date,
                    cod_cliente,
                    emissor,
                    tipo_documento,
                    tipo_nota_emitida,
                    quantidade,
                    tempo_minutos,
                ),
            )
        else:
            query = """
                    INSERT INTO registros (
                        date,
                        cod_cliente,
                        emissor,
                        tipo,
                        tipo_nota_emitida,
                        quantidade,
                        tempo_minutos
                    )
                    VALUES (?,?,?,?,?,?,?)
                    """
            cursor.execute(
                query,
                (
                    _to_iso_date(date),
                    cod_cliente,
                    emissor,
                    tipo_documento,
                    tipo_nota_emitida,
                    quantidade,
                    tempo_minutos,
                ),
            )
        conn.commit()
        return True
    except Exception as exc:
        st.error(f"Conexao com banco de notas falhou: {_safe_exc_message(exc)}")
        return False
    finally:
        if conn is not None:
            conn.close()


def atualiza_nota_emitida(
    id_registro,
    cod_cliente,
    date_doc,
    emissor,
    tipo_documento,
    tipo_nota_emitida,
    quantidade,
    tempo_minutos,
):
    conn = None
    try:
        conn, engine = _conecta_notas()
        cursor = conn.cursor()
        if engine == "postgres":
            query = """
                    UPDATE registros
                    SET date = %s,
                        emissor = %s,
                        tipo = %s,
                        tipo_nota_emitida = %s,
                        quantidade = %s,
                        tempo_minutos = %s
                    WHERE id = %s AND cod_cliente = %s
                    """
            cursor.execute(
                query,
                (
                    date_doc,
                    emissor,
                    tipo_documento,
                    tipo_nota_emitida,
                    quantidade,
                    tempo_minutos,
                    id_registro,
                    cod_cliente,
                ),
            )
        else:
            query = """
                    UPDATE registros
                    SET date = ?,
                        emissor = ?,
                        tipo = ?,
                        tipo_nota_emitida = ?,
                        quantidade = ?,
                        tempo_minutos = ?
                    WHERE id = ? AND cod_cliente = ?
                    """
            cursor.execute(
                query,
                (
                    _to_iso_date(date_doc),
                    emissor,
                    tipo_documento,
                    tipo_nota_emitida,
                    quantidade,
                    tempo_minutos,
                    id_registro,
                    cod_cliente,
                ),
            )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        st.error(f"Falha ao atualizar lancamento: {_safe_exc_message(exc)}")
        return False
    finally:
        if conn is not None:
            conn.close()


def exclui_nota_emitida(id_registro,cod_cliente):
    conn = None
    try:
        conn, engine = _conecta_notas()
        cursor = conn.cursor()
        if engine == "postgres":
            query = "DELETE FROM registros WHERE id = %s AND cod_cliente = %s"
            cursor.execute(query, (id_registro, cod_cliente))
        else:
            query = "DELETE FROM registros WHERE id = ? AND cod_cliente = ?"
            cursor.execute(query, (id_registro, cod_cliente))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as exc:
        st.error(f"Falha ao excluir lancamento: {_safe_exc_message(exc)}")
        return False
    finally:
        if conn is not None:
            conn.close()


def retorna_contagem_notas_emitidas(cod_cliente,dt_inicial,dt_final,tipo):
    conn = None
    try:
        conn, engine = _conecta_notas()
        cursor = conn.cursor()

        if engine == "postgres":
            if _pesquisa_por_periodo(tipo):
                query="SELECT SUM(quantidade) FROM registros WHERE cod_cliente = %s AND date >= %s AND date <= %s"
                cursor.execute(query, (cod_cliente,dt_inicial,dt_final))
            else:
                query="SELECT SUM(quantidade) FROM registros WHERE cod_cliente = %s"
                cursor.execute(query, (cod_cliente, ))
        else:
            if _pesquisa_por_periodo(tipo):
                query="SELECT SUM(quantidade) FROM registros WHERE cod_cliente = ? AND date >= ? AND date <= ?"
                cursor.execute(query, (cod_cliente, _to_iso_date(dt_inicial), _to_iso_date(dt_final)))
            else:
                query="SELECT SUM(quantidade) FROM registros WHERE cod_cliente = ?"
                cursor.execute(query, (cod_cliente, ))

        resultado = cursor.fetchall()
        total = resultado[0][0] if resultado else 0
        if total is None:
            total = 0
        return [(total,)]
    except Exception as exc:
        st.error(f"Falha na consulta das notas emitidas: {_safe_exc_message(exc)}")
        return [(0,)]
    finally:
        if conn is not None:
            conn.close()


def retorna_listagem_notas_emitidas(cod_cliente,dt_inicial,dt_final,tipo):
    conn = None
    try:
        conn, engine = _conecta_notas()
        cursor = conn.cursor()

        if engine == "postgres":
            if _pesquisa_por_periodo(tipo):
                query = """
                        SELECT
                            id,
                            date,
                            cod_cliente,
                            emissor,
                            tipo,
                            tipo_nota_emitida,
                            quantidade,
                            tempo_minutos
                        FROM registros
                        WHERE cod_cliente = %s AND date >= %s AND date <= %s
                        ORDER BY date, id
                        """
                cursor.execute(query, (cod_cliente,dt_inicial,dt_final))
            else:
                query = """
                        SELECT
                            id,
                            date,
                            cod_cliente,
                            emissor,
                            tipo,
                            tipo_nota_emitida,
                            quantidade,
                            tempo_minutos
                        FROM registros
                        WHERE cod_cliente = %s
                        ORDER BY date, id
                        """
                cursor.execute(query, (cod_cliente, ))
        else:
            if _pesquisa_por_periodo(tipo):
                query = """
                        SELECT
                            id,
                            date,
                            cod_cliente,
                            emissor,
                            tipo,
                            tipo_nota_emitida,
                            quantidade,
                            tempo_minutos
                        FROM registros
                        WHERE cod_cliente = ? AND date >= ? AND date <= ?
                        ORDER BY date, id
                        """
                cursor.execute(query, (cod_cliente, _to_iso_date(dt_inicial), _to_iso_date(dt_final)))
            else:
                query = """
                        SELECT
                            id,
                            date,
                            cod_cliente,
                            emissor,
                            tipo,
                            tipo_nota_emitida,
                            quantidade,
                            tempo_minutos
                        FROM registros
                        WHERE cod_cliente = ?
                        ORDER BY date, id
                        """
                cursor.execute(query, (cod_cliente, ))

        resultado = cursor.fetchall()
        if engine == "sqlite":
            normalizado = []
            for registro in resultado:
                normalizado.append(
                    (
                        registro[0],
                        _to_date_obj(registro[1]),
                        registro[2],
                        registro[3],
                        registro[4],
                        registro[5],
                        registro[6],
                        registro[7],
                    )
                )
            return normalizado
        return resultado
    except Exception as exc:
        st.error(f"Falha na listagem das notas emitidas: {_safe_exc_message(exc)}")
        return []
    finally:
        if conn is not None:
            conn.close()


def retorna_listagem_notas_geral(dt_inicial,dt_final):
    conn = None
    try:
        conn, engine = _conecta_notas()
        cursor = conn.cursor()

        if engine == "postgres":
            query = """
                    SELECT
                        id,
                        date,
                        cod_cliente,
                        emissor,
                        tipo,
                        tipo_nota_emitida,
                        quantidade,
                        tempo_minutos
                    FROM registros
                    WHERE date >= %s AND date <= %s
                    ORDER BY date, id
                    """
            cursor.execute(query, (dt_inicial, dt_final))
        else:
            query = """
                    SELECT
                        id,
                        date,
                        cod_cliente,
                        emissor,
                        tipo,
                        tipo_nota_emitida,
                        quantidade,
                        tempo_minutos
                    FROM registros
                    WHERE date >= ? AND date <= ?
                    ORDER BY date, id
                    """
            cursor.execute(query, (_to_iso_date(dt_inicial), _to_iso_date(dt_final)))

        resultado = cursor.fetchall()
        if engine == "sqlite":
            normalizado = []
            for registro in resultado:
                normalizado.append(
                    (
                        registro[0],
                        _to_date_obj(registro[1]),
                        registro[2],
                        registro[3],
                        registro[4],
                        registro[5],
                        registro[6],
                        registro[7],
                    )
                )
            return normalizado
        return resultado
    except Exception as exc:
        st.error(f"Falha na consulta geral de notas: {_safe_exc_message(exc)}")
        return []
    finally:
        if conn is not None:
            conn.close()

def retorna_dif_salarios():
    hoje = date.today()
    competencia_atual_inicio = hoje.replace(day=1)
    if hoje.day <= 26:
        competencia_atual_inicio = (competencia_atual_inicio - timedelta(days=1)).replace(day=1)
    competencia_anterior_inicio = (competencia_atual_inicio - timedelta(days=1)).replace(day=1)

    conn = conecta_odbc()
    cursor = conn.cursor()
    query = """
        SELECT
            s_atual.proventos AS salario_atual,
            s_anterior.proventos AS salario_anterior,
            ABS(s_atual.proventos - s_anterior.proventos) AS diferenca,
            e.nome AS funcionario,
            emp.NOME AS empresa,
            s_atual.competencia
        FROM bethadba.fobasesserv s_atual
        INNER JOIN bethadba.fobasesserv s_anterior
            ON s_anterior.codi_emp = s_atual.codi_emp
            AND s_anterior.i_empregados = s_atual.i_empregados
            AND s_anterior.competencia = ?
            AND s_anterior.tipo_process = 11
            AND s_anterior.rateio = 0
        LEFT JOIN bethadba.foempregados e
            ON s_atual.codi_emp = e.codi_emp
            AND s_atual.i_empregados = e.i_empregados
        LEFT JOIN bethadba.PRVCLIENTES emp
            ON s_atual.codi_emp = emp.CODIGO
        WHERE
            s_atual.competencia = ?
            AND s_atual.tipo_process = 11
            AND s_atual.rateio = 0
            AND ABS(s_atual.proventos - s_anterior.proventos) > 1
        ORDER BY
            emp.NOME, e.nome, s_atual.competencia;

    """
    cursor.execute(
        query,
        (
            competencia_anterior_inicio,
            competencia_atual_inicio,
        ),
    )
    resultado = cursor.fetchall()
    conn.close()
    return resultado
