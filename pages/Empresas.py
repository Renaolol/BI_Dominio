import streamlit as st
import pandas as pd
from dependencies import *
import datetime
from datetime import timedelta, time
import altair as alt
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
        opt_anos = st.radio("Anos:",options=[2021,2022,2023,2024,2025,2026],horizontal=True)
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
        elif opt_anos == 2026:
            dt_init = '2026-01-01'
            dt_fim = '2026-12-31'            
    with col2:        
        cod = st.number_input("Insira o código da empresa",step=0,width=300)                                            

nome_empresa = retorna_nome_empresa(cod)
try:
    st.subheader(f"Empresa : {nome_empresa[0][0]}")
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
col_dados1, col_dados2, col_dados3, col_dados4 = st.columns(4)
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
        st.header("FISCAL")
        contagem_notas_entrada = retorna_contagem_entradas(cod,dt_init,dt_fim)
        contagem_notas_entrada_list = []
        for x in contagem_notas_entrada:
            contagem_notas_entrada_list.append([x[0]])
        contagem_notas_saida = retorna_contagem_saidas(cod,dt_init,dt_fim)
        contagem_notas_saida_list = []
        for x in contagem_notas_saida:
            contagem_notas_saida_list.append([x[0]])
        contagem_notas_servico = retorna_contagem_servico(cod,dt_init,dt_fim)
        contagem_notas_servico_list=[]
        for x in contagem_notas_servico:
            contagem_notas_servico_list.append([x[0]])    
        st.write(f"Contagem de lançamentos de Entrada: *{contagem_notas_entrada_list[0][0]}* ")
        contagem_acum_entrada=retorna_contagem_acumulador_entrada(cod,dt_init,dt_fim)
        with st.expander("Acumuladores Entradas: "):
            for x in contagem_acum_entrada:
                st.write(f'{x[1]} -  {x[0]}')    
        st.write(f"Contagem de lançamentos de Saída: *{contagem_notas_saida_list[0][0]}* ")
        contagem_acum_saida=retorna_contagem_acumulador_saida(cod,dt_init,dt_fim)
        with st.expander("Acumuladores Saídas: "):
            for x in contagem_acum_saida:
                st.write(f'{x[1]} -  {x[0]}')        
        st.write(f"Contagem de lançamentos de Serviço: *{contagem_notas_servico_list[0][0]}* ")
        contagem_acum_servico=retorna_contagem_acumulador_servico(cod,dt_init,dt_fim)
        with st.expander("Acumuladores Serviços: "):
            for x in contagem_acum_servico:
                st.write(f'{x[1]} -  {x[0]}')         
with col_dados4:
    with st.container(border=True):
        st.header("CONTABIL")
        st.write("Aqui vai vir as coisas do Contabil")
 
st.divider()
col_faturamento1, col_faturamento2,col_faturamento3 = st.columns([0.5,1,2])
 
impostos_empresa = retorna_impostos_empresa(cod,dt_init,dt_fim)
impostos_empresa_list = []
for x in impostos_empresa:
    impostos_empresa_list.append(x[0])
with col_faturamento1:       
    opt_imposto = st.radio("Selecione o imposto", options=impostos_empresa_list)
valores_impostos = retorna_debito_credito_imposto(cod,dt_init,dt_fim,opt_imposto)
valores_impostos_list = []
for x in valores_impostos:
    valores_impostos_list.append([x[0],x[1],x[2],x[3],x[4]])
valores_impostos_df = pd.DataFrame(valores_impostos_list,columns=["Valor Débito","Valor Crédito","Competência","Vlr Saídas","Vlr Serviços"])
valores_impostos_df["Faturamento"] = valores_impostos_df["Vlr Saídas"] + valores_impostos_df["Vlr Serviços"]
grafico_linha = pd.DataFrame(columns=["Faturamento"])  
grafico_linha= valores_impostos_df.groupby("Competência")["Faturamento"].sum().reset_index(name="Faturamento") 
grafico_linha["Faturamento"] = pd.to_numeric(grafico_linha["Faturamento"])
with col_faturamento2:
    st.write(valores_impostos_df[["Competência","Faturamento"]])
with col_faturamento3:    
    st.altair_chart(altair_chart=(alt.Chart(grafico_linha).mark_line(color="#Fad32b",interpolate="linear",
                                                                     line={'color':'gray'}).encode(x="Competência", y="Faturamento")))
