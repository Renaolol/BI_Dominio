import pandas as pd
import pyodbc
import datetime
import streamlit as st
import altair as alt
from time import sleep
import plotly.express as px
import geopandas as gpd
from dependencies import formata_valor
st.set_page_config(layout="wide")


codigo = st.session_state.get("empresa_codigo")
nome = st.session_state.get("name")

if not codigo:  # sem empresa na sessão -> bloqueia
    codigo = st.text_input("Insira o código da empresa")
    st.info("Acesso de Administrador.")

# se seu banco espera número, tente converter:
try:
    codigo_int = int(str(codigo).strip())
except Exception:
    # se o banco aceita STRING, você pode manter como está e usar direto
    codigo_int = codigo  # fallback

conexao = ("DSN=ContabilPBI;UID=PBI;PWD=Pbi")


ano = st.radio("Selecione o ano!",options=["2026","2027-2028","2029","2030","2031","2032","2033"],horizontal=True)
abadespesas,aba1=st.tabs(["Despesas","Analise"])
#Função para buscar a contagem de produtos nas notas
def get_cte(codigo,data_inicio,data_final):
    conn = pyodbc.connect(conexao)
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

data_inicio = st.sidebar.date_input("Insira a data Incial",value='2025-01-01',format="DD/MM/YYYY", width=150)   
data_final = st.sidebar.date_input("Insira a data Final",value='2025-12-31',format="DD/MM/YYYY", width=150)
ctes = get_cte(codigo_int,data_inicio, data_final)
if not ctes:
    st.title(f"Dashboard do Faturamento")
    st.warning(f"Nenhum dado encontrado para a empresa")
    st.stop()

df_ctes = pd.DataFrame(ctes,columns=["DATA SAÍDA","NUMERO CTE", "CFOP", "MUNICIPIO SAÍDA","ESTADO SAÍDA","MUNICIPIO DE DESTINO","ESTADO DESTINO","VALOR DO PEDÁGIO","VALOR DO FRETE","TOTAL DO CTE"])
df_ctes["DATA SAÍDA"] = pd.to_datetime(df_ctes["DATA SAÍDA"], dayfirst=True, errors="coerce")
df_ctes["VALOR DO PEDÁGIO"] = pd.to_numeric(df_ctes["VALOR DO PEDÁGIO"], errors="coerce")
df_ctes["VALOR DO FRETE"] = pd.to_numeric(df_ctes["VALOR DO FRETE"], errors="coerce")
df_ctes["TOTAL DO CTE"] = pd.to_numeric(df_ctes["TOTAL DO CTE"], errors="coerce")

estados = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS",
           "MG","PA","PB","PR","PE","PI","RN","RS","RJ","RO","RR","SC","SP","SE","TO"]
# Dados da tabela (extraídos manualmente da imagem)
dados = [
[19,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,21,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,18,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,20,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,20.5,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,20,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,5,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,19,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,23,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,12,17,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,12,12,17,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12],
[7,7,7,7,7,7,7,7,7,7,7,7,18,7,7,12,7,7,7,12,12,7,7,12,12,7,7],
[12,12,12,12,12,12,12,12,12,12,12,12,12,19,12,12,12,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,20,12,12,12,12,12,12,12,12,12,12,12,12],
[7,7,7,7,7,7,7,7,7,7,7,7,12,7,7,12,7,7,7,12,12,7,7,12,12,7,7],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,20.5,12,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,21,12,12,12,12,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,20,12,12,12,12,12,12,12,12],
[7,7,7,7,7,7,7,7,7,7,7,7,12,7,7,12,7,7,7,12,12,7,7,12,12,7,7],
[7,7,7,7,7,7,7,7,7,7,7,7,12,7,7,12,7,7,7,12,22,7,7,12,12,7,7],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,19.5,12,12,12,12,12],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,20,12,12,12,12],
[7,7,7,7,7,7,7,7,7,7,7,7,12,7,7,12,7,7,7,12,12,7,7,17,12,7,7],
[7,7,7,7,7,7,7,7,7,7,7,7,12,7,7,12,7,7,7,12,12,7,7,12,12,7,7],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,20,12],
[12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12,20]
]
# Criar DataFrame
df_aliquotas = pd.DataFrame(dados, index=estados, columns=estados)
# Mapear posições (índices) de origem e destino na matriz
lin_idx = df_aliquotas.index.get_indexer(df_ctes["ESTADO SAÍDA"])
col_idx = df_aliquotas.columns.get_indexer(df_ctes["ESTADO DESTINO"])

# Pegar valores diretamente do array subjacente
mat = df_aliquotas.to_numpy()
df_ctes["ALIQUOTA"] = mat[lin_idx, col_idx]

df_ctes["VALOR ICMS"]=df_ctes["TOTAL DO CTE"]*(df_ctes["ALIQUOTA"]/100)
df_ctes["PIS"] = (df_ctes["TOTAL DO CTE"]-df_ctes["VALOR ICMS"])*(1.65/100)
df_ctes["COFINS"] = (df_ctes["TOTAL DO CTE"]-df_ctes["VALOR ICMS"])*(7.6/100)

#Variaveis Globais
total_icms = df_ctes["VALOR ICMS"].sum()
total_pis = df_ctes["PIS"].sum()
total_cofins = df_ctes["COFINS"].sum()
total_fretes = df_ctes["TOTAL DO CTE"].sum()
aliquota_estatica_ibs = (17.7/100)
aliq_cbs = 8.8/100
bc_debito_iva = total_fretes-total_cofins-total_icms-total_pis
total_icms_reforma = total_icms
with abadespesas:
    st.title("Elencar despesas do período")
    col1,col2,col3 = st.columns(3)
    with col1:
        combustivel_valor = st.number_input("COMBUSTÍVEL",width=200,value=100.10,help="Considerado 1,12 p/litro")
        preco_medio_combustivel = st.number_input("P/M litro",width=200,value=6.10)
        litros_comb = combustivel_valor/preco_medio_combustivel
        credito_monofasico = litros_comb*1.12
        manutencao_veiculos = st.number_input("MANUTENÇÃO DE VEÍCULOS",width=200)
        pneus_pecas = st.number_input("PNEUS E PEÇAS",width=200)
        rastreamento = st.number_input("RASTREAMENTO",width=200)
        seguros = st.number_input("SEGUROS",width=200)
        pedagio = st.number_input("PEDÁGIO",width=200)
    with col2:
        assistencia_veiculo = st.number_input("ASSISTÊNCIA A VEÍCULOS",width=200)
        despesas_veiculos = st.number_input("DESPESAS DE VEÍCULOS",width=200)
        telefone = st.number_input("TELEFONE",width=200)
        depreciacao = st.number_input("DEPRECIAÇÃO",width=200)
        sistemas = st.number_input("SISTEMAS GERENCIAIS",width=200)
        internet = st.number_input("INTERNET",width=200)
    with col3:
        honorarios_adv = st.number_input("HONORÁRIOS ADVOCATÍCIOS",width=200)
        uso_consumo = st.number_input("USO E CONSUMO",width=200)
        honorarios_cont_vlr = st.number_input("HONORÁRIOS CONTÁBEIS",width=200,help="Redução de 30% - Art.127 da LC 214/2025")
        honorarios_cont = honorarios_cont_vlr*0.70
        juros_pagos = st.number_input("JUROS E COMISSÕES",width=200,help="Apenas juros sobre operações financeiras, sobre impostos não pode considerar")
        despesas_diversas = st.number_input("DESPESAS DIVERSAS",width=200) 
        soma_bc_creditos_reforma = (
            manutencao_veiculos+pneus_pecas+rastreamento+seguros+pedagio+
            assistencia_veiculo+despesas_veiculos+telefone+depreciacao+sistemas+internet+
            honorarios_adv+uso_consumo+honorarios_cont+despesas_diversas+juros_pagos)
        bc_creditos=(soma_bc_creditos_reforma*((100-1.65-7.6-12)/100))+credito_monofasico

        st.write(f"Total {formata_valor(soma_bc_creditos_reforma)}")  
with aba1:
    aliq_ibs=0
    if ano == "2026":
        aliq_ibs = 0.1/100
        aliq_cbs = 0.9/100
    elif ano == "2027-2028":
        aliq_ibs = 0.1/100
        aliq_cbs = 8.7/100
    elif ano == "2029":
        aliq_ibs = aliquota_estatica_ibs*0.10
        total_icms_reforma = total_icms*0.90
    elif ano == "2030":
        aliq_ibs = aliquota_estatica_ibs*0.20
        total_icms_reforma = total_icms*0.80
    elif ano == "2031":
        aliq_ibs = aliquota_estatica_ibs*0.30
        total_icms_reforma = total_icms*0.70
    elif ano == "2032":
        aliq_ibs = aliquota_estatica_ibs*0.40
        total_icms_reforma = total_icms*0.60
    elif ano == "2033":
        aliq_ibs = aliquota_estatica_ibs
        total_icms_reforma = 0
    if ano !="2026":
        total_pis = 0
        total_cofins = 0

    #Valor dos créditos
    creditos = bc_creditos*(aliq_ibs+aliq_cbs)

    debito_ibs = bc_debito_iva*aliq_ibs
    debito_cbs = bc_debito_iva*aliq_cbs
    total_debitos = debito_cbs+debito_ibs
    valor_a_pagar = total_debitos-creditos
    aliquota_ef_iva = valor_a_pagar/bc_debito_iva
    with st.container(border=True):
        col1,col2,col3,col4 = st.columns(4)
        with col1:
            st.header("Débitos IVA")
            st.write(f' IBS {formata_valor(debito_ibs)}')
            st.write(f' CBS {formata_valor(debito_cbs)}')
            st.write(f' Total de Débitos {formata_valor(total_debitos)}')
        with col2:
            st.header("Créditos IVA")
            st.write(f' Valor créditos {formata_valor(bc_creditos)}')
            st.write(f' Créditos {formata_valor(creditos)}')
        with col3:
            st.header("A pagar IVA")
            st.write(f' Valor a Pagar {formata_valor(valor_a_pagar)}')
            st.write(f' Aliquota Efetiva de IVA {round(aliquota_ef_iva*100,4)}%')
        with col4:
            st.header("Impostos antigos")
            st.write(f" ICMS {formata_valor(total_icms_reforma)}")
            st.write(f' PIS {formata_valor(total_pis)}')
            st.write(f' COFINS {formata_valor(total_cofins)}')
    df_ctes["BC_IVA"] = df_ctes["TOTAL DO CTE"] - df_ctes["VALOR ICMS"] - df_ctes["PIS"] - df_ctes["COFINS"]
    df_ctes["IBS 26"] = df_ctes["BC_IVA"]*(0.1/100)
    df_ctes["CBS 26"] = df_ctes["BC_IVA"]*(0.9/100)
    st.dataframe(df_ctes[["NUMERO CTE","TOTAL DO CTE","BC_IVA","IBS 26", "CBS 26"]])