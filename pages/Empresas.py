import streamlit as st
import pandas as pd
from dependencies import *
import datetime
from datetime import timedelta, time
st.set_page_config(layout="wide")
st.title("Empresas")
st.header("Comparar estatísticas das empresas")
opt_datas = st.radio("Selecione como deseja filtrar as datas", options=["Anos","Períodos"],horizontal=True)
col1,col2,col3 = st.columns(3)
if opt_datas == "Períodos":
    with col1:
        dt_init = st.date_input("Insira a data inicial",format="DD/MM/YYYY",value=(datetime.date.today() - datetime.timedelta(60)),width=300)
    with col2:
        dt_fim = st.date_input("Insira a data final",width=300,format="DD/MM/YYYY")
    with col3:
        cod = st.number_input("Insira o código da empresa",step=0,width=300)
else:
    with col1:
        opt_anos = st.radio("Anos:",options=[2021,2022,2023,2024,2025],horizontal=True)
        if opt_anos == 2021:
            dt_init = '2021-01-01'
            dt_fim = '2021-12-31'
        elif opt_anos == 2022:
            dt_init = '2022-01-01'
            dt_fim = '2022-12-31'
        elif opt_anos == 2023:
            dt_init = '2023-01-01'
            dt_fim = '2023-12-31' 
        elif opt_anos == 2024:
            dt_init = '2024-01-01'
            dt_fim = '2024-12-31' 
        elif opt_anos == 2025:
            dt_init = '2025-01-01'
            dt_fim = '2025-12-31'
    with col2:        
        cod = st.number_input("Insira o código da empresa",step=0,width=300)                                            

nome_empresa = retorna_nome_empresa(cod)
try:
    st.subheader(f"Empresa : {nome_empresa[0][0]}")
    impostos = retorna_faturamento_por_imposto(dt_init,cod)
    impostos_list = []
    for x in impostos:
        impostos_list.append([x[0],x[1],x[2],x[3],x[4],x[5].strftime("%m/%Y")])
    impostos_df = pd.DataFrame(impostos_list,columns=["Imposto","Saldo Devedor","Saldo Credor","Valor Saídas","Valor Serviços","Competencia"])    
    #st.write(impostos_df)
except:
    st.error("Insira o código de uma empresa válida")    
#Apresentação dos dados    
tempo_gasto_empresa = retorna_tempo_trabalho_empresa(cod,dt_init,dt_fim)  
tempo_gasto_list = []
for x in tempo_gasto_empresa:
    tempo_gasto_list.append([x[0],x[1].strftime("%d/%m/%Y"),x[2].strftime("%H:%M:%S"),x[3].strftime("%H:%M:%S"),
                             ((time_to_timedelta(x[3])-time_to_timedelta(x[2])).total_seconds()/60),x[5]])
tempo_gasto_df=pd.DataFrame(tempo_gasto_list,columns=["Usuário","Data","Hora Inicial","Hora Final","Tempo gasto","Módulo ID"])

modulo = retorna_modulo()
modulo_list = []
for x in modulo:
    modulo_list.append([x[0],x[1]])
modulo_df = pd.DataFrame(modulo_list,columns=["Módulo", "Módulo ID"])
tempo_gasto_merged = pd.merge(tempo_gasto_df,modulo_df, on='Módulo ID')
with st.container(border=True,horizontal_alignment="center"):
    st.subheader(f'Total de tempo gasto para a empresa *{formata_horas_min_seg((tempo_gasto_df["Tempo gasto"].sum()))}*')
#st.write(tempo_gasto_merged[["Usuário","Data","Tempo gasto","Módulo"]])  
col_dados1, col_dados2, col_dados3 = st.columns(3)
with col_dados1:
    with st.container(border=True):
        st.header("TEMPO")
        tempo_agrupado = pd.DataFrame(columns=["Tempo gasto"])
        tempo_agrupado["Tempo gasto"] = (tempo_gasto_merged.groupby("Módulo")["Tempo gasto"].sum()).sort_values(ascending=False)
        tempo_agrupado["Tempo gasto"] = tempo_agrupado["Tempo gasto"].apply(formata_horas_min_seg)

        st.write(tempo_agrupado)
with col_dados2:
    with st.container(border=True):
        st.header("FOLHA")
        admissoes = retorna_admissoes(cod,dt_init,dt_fim)
        admissoes_nomes = retorna_nome_admissoes(cod,dt_init,dt_fim)
        demissoes = retorna_demitidos(cod,dt_init,dt_fim)
        demissoes_nomes = retorna_nome_demitidos(cod,dt_init,dt_fim)
        total_funcionarios = retorna_total_funcionarios(cod)
        nomes_funcionarios = retorna_nome_funcionarios(cod)
        st.write(f'Admissões do período: {admissoes[0][0]}')
        with st.expander("Admitidos"):
            for x in admissoes_nomes:
                st.write(x[0])
        st.write(f'Demissões do período: {demissoes[0][0]}')
        with st.expander("Demitidos"):
            for x in demissoes_nomes:
                st.write(x[0])
        st.write(f'Funcionários totais: {total_funcionarios[0][0]}')
        with st.expander("Funcionários"):
            for x in nomes_funcionarios:
                st.write(x[0])
with col_dados3:
    with st.container(border=True):
        st.write("Aqui vai a variação de faturamento")                