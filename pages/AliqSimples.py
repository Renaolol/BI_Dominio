import streamlit as st
from datetime import date
import altair as alt
from dependencies import *
import pandas as pd

st.set_page_config(layout="wide")
st.title("B.I | Alíquotas do Simples Nacional")
#Sidebar
opt_datas = st.sidebar.radio("Selecione como deseja filtrar as datas", options=["Anos","Períodos"],horizontal=True)
cod = st.sidebar.number_input("Insira o código da empresa",step=0,width=300)
opt_anos = st.sidebar.radio("Anos:",options=[2021,2022,2023,2024,2025,2026],horizontal=True,index=4)
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


st.header("Defina as propriedades dos gráficos")
with st.container(border=True):
    prop_col1,prop_col2,prop_col3,prop_col4,prop_col5 = st.columns(5)
    with prop_col1:
        largura = st.slider("Defina a largura das barras",1,100,value=35)
    with prop_col2:
        rotulos = st.radio("Rotulos visiveis?",["Sim","Não"],horizontal=True)
    with prop_col3:
        tamanho_rotulos = st.slider("Defina o tamanho dos rotulos",1,20,value=10)
    with prop_col4:
        cor_primaria = st.color_picker("Selecione a cor primária",value="#fad32b")
    with prop_col5:
        cor_rotulos = st.color_picker("Selecione a cor dos rotulos",value="#c0c0c0")
st.divider()
faturamento=retorna_faturamento_simples(cod,dt_init,dt_fim)
faturamento_list = [[x[0],x[1],x[2],x[3]] for x in faturamento]
faturamento_df = pd.DataFrame(faturamento_list,columns=["Faturamento","Impostos","Aliquota Ef float","Competência"])

#aliquota ef formatada para float
faturamento_df["Aliquota Ef float"]=faturamento_df["Aliquota Ef float"].apply(float)

#aliquota ef formatada para porcentagem
faturamento_df["Aliquota EF"]=faturamento_df["Aliquota Ef float"].apply(formata_porcentagem)

#Faturamento e impostos formatados para Floats
faturamento_df["Faturamento float"]=faturamento_df["Faturamento"].apply(float)
faturamento_df["Impostos float"]=faturamento_df["Impostos"].apply(float)

#Faturamento e impostos formatados em R$
faturamento_df["Faturamento"]=faturamento_df["Faturamento"].apply(formata_valor)
faturamento_df["Impostos"]=faturamento_df["Impostos"].apply(formata_valor)

#Áreas de plotagem
col1,col2 = st.columns([1,2])
with col1:
    with st.container(border=True):
        st.altair_chart(alt.Chart(faturamento_df)
                            .mark_line(point=True,interpolate="monotone",color=cor_primaria,)
                            .encode(x=alt.X("Competência",scale=alt.Scale(paddingOuter=0.5)),y=alt.Y("Aliquota Ef float",scale=alt.Scale(paddingOuter=0.5)),tooltip=["Faturamento","Impostos","Aliquota EF"],) +
                        alt.Chart(faturamento_df)
                            .mark_text(dy=-25,angle=35,align="center",baseline='middle',color=cor_rotulos,size=(tamanho_rotulos))
                            .encode(text="Aliquota EF",x="Competência",y=alt.Y("Aliquota Ef float",title="Aliquota"),tooltip=["Faturamento","Impostos","Aliquota EF"])
                        if rotulos =="Sim" #Caso os rótulos forem "Sim" o código acima é posto, caso contrário o código abaixo
                        else
                        alt.Chart(faturamento_df)
                            .mark_line(point=True,interpolate="monotone",color=cor_primaria,)
                            .encode(x="Competência",y="Aliquota Ef float",tooltip=["Faturamento","Impostos","Aliquota EF"]))
with col2:
    with st.container(border=True):
        st.altair_chart(alt.Chart(faturamento_df)
                            .mark_bar(color=cor_primaria,size=(largura))
                            .encode(x=alt.X("Competência"),
                                    y=alt.Y("Faturamento float"),
                                    tooltip=["Faturamento","Impostos","Aliquota EF"]) +
                        alt.Chart(faturamento_df)
                            .mark_text(dy=-25,angle=0,align="center",baseline='middle',color=cor_rotulos,size=(tamanho_rotulos))
                            .encode(text="Faturamento",x="Competência",y="Faturamento float",tooltip=["Faturamento","Impostos","Aliquota EF"])
                        if rotulos =="Sim" #Caso os rótulos forem "Sim" o código acima é posto, caso contrário o código abaixo
                        else 
                        alt.Chart(faturamento_df) 
                            .mark_bar(color=cor_primaria,size=(largura))
                            .encode(x="Competência",y="Faturamento float",tooltip=["Faturamento","Impostos","Aliquota EF"]))
st.divider()

try:
    #COMPARATIVO ENTRE ANOS 
    st.title("Comparativo entre Anos")
    with st.container(border=True):
        valores_impostos = retorna_faturamento_simples(cod,dt_init,dt_fim)
        valores_impostos_list = []
        for x in valores_impostos:
            valores_impostos_list.append([x[0],x[1],x[2],x[3]])
        valores_impostos_df = pd.DataFrame(valores_impostos_list,columns=["Faturamento","Imposto","Aliquota EF","Competência"])
        opt_comparativo = st.radio("Selecione o ano para comparar!", options=[2021,2022,2023,2024,2025,2026],horizontal=True,index=3)
        if opt_comparativo == 2021:
            dt_init_comparativo = '2021-01-01'
            dt_fim_comparativo = '2021-12-31'
        elif opt_comparativo == 2022:
            dt_init_comparativo = '2022-01-01'
            dt_fim_comparativo = '2022-12-31'
        elif opt_comparativo == 2023:
            dt_init_comparativo = '2023-01-01'
            dt_fim_comparativo = '2023-12-31' 
        elif opt_comparativo == 2024:
            dt_init_comparativo = '2024-01-01'
            dt_fim_comparativo = '2024-12-31' 
        elif opt_comparativo == 2025:
            dt_init_comparativo = '2025-01-01'
            dt_fim_comparativo = '2025-12-31'
        elif opt_comparativo == 2026:
            dt_init_comparativo = '2026-01-01'
            dt_fim_comparativo = '2026-12-31' 
        valores_impostos_comparativo = retorna_faturamento_simples(cod,dt_init_comparativo,dt_fim_comparativo)
        valores_impostos_comparativo_list = []
        for x in valores_impostos_comparativo:
            valores_impostos_comparativo_list.append([x[0],x[1],x[2],x[3]])
        valores_impostos_df_comparativo = pd.DataFrame(valores_impostos_comparativo_list,columns=["Faturamento","Imposto","Aliquota EF","Competência"])
        faturamento_comparado = valores_impostos_df_comparativo["Faturamento"].sum()
        faturamento_total =  valores_impostos_df["Faturamento"].sum()
        evolucao = round(((faturamento_total/faturamento_comparado)-1)*100,4)
    #Demonstração dos valores comparativos.
        st.metric("Total de Faturamento",formata_valor(faturamento_total))
        st.metric("Faturamento ano comparado",formata_valor(faturamento_comparado))
        st.metric("Evolução",formata_porcentagem(evolucao))
except:
    pass