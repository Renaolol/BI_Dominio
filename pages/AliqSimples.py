import streamlit as st
from datetime import date
import altair as alt
from dependencies import *
import pandas as pd

st.set_page_config(layout="wide")
st.title("B.I | Alíquotas do Simples nacional")
#Sidebar
dt_init = st.sidebar.date_input("Insira a data inicial",format="DD/MM/YYYY",width=300)
dt_fim = st.sidebar.date_input("Insira a data final",width=300,format="DD/MM/YYYY")
cod = st.sidebar.number_input("Insira o código da empresa",step=0,width=300)

st.header("Defina as propriedades dos gráficos")
with st.container(border=True):
    prop_col1,prop_col2,prop_col3,prop_col4,prop_col5 = st.columns(5)
    with prop_col1:
        largura = st.slider("Defina a largura das barras",1,100,value=35)
    with prop_col2:
        rotulos = st.radio("Rotulos visiveis?",["Sim","Não"],horizontal=True)
    with prop_col3:
        tamanho_rotulos = st.slider("Defina o tamanho dos rotulos",1,20,value=5)
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
col1,col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.altair_chart(alt.Chart(faturamento_df)
                            .mark_line(point=True,interpolate="monotone",color=cor_primaria,)
                            .encode(x=alt.X("Competência",scale=alt.Scale(paddingOuter=0.5)),y=alt.Y("Aliquota Ef float",scale=alt.Scale(paddingOuter=0.5)),tooltip=["Faturamento","Impostos","Aliquota EF"],) +
                        alt.Chart(faturamento_df)
                            .mark_text(dy=25,align="center",baseline='middle',color=cor_rotulos,size=(tamanho_rotulos))
                            .encode(text="Aliquota EF",x="Competência",y="Aliquota Ef float",tooltip=["Faturamento","Impostos","Aliquota EF"])
                        if rotulos =="Sim" #Caso os rótulos forem "Sim" o código acima é posto, caso contrário o código abaixo
                        else
                        alt.Chart(faturamento_df)
                            .mark_line(point=True,interpolate="monotone",color=cor_primaria,)
                            .encode(x="Competência",y="Aliquota Ef float",tooltip=["Faturamento","Impostos","Aliquota EF"])    )
with col2:
    with st.container(border=True):
        st.altair_chart(alt.Chart(faturamento_df)
                            .mark_bar(color=cor_primaria,size=(largura))
                            .encode(x=alt.X("Competência",scale=alt.Scale(padding=0.1)),
                                    y=alt.Y("Faturamento float",scale=alt.Scale(paddingOuter=0.1)),
                                    tooltip=["Faturamento","Impostos","Aliquota EF"]) +
                        alt.Chart(faturamento_df)
                            .mark_text(dy=-25,align="center",baseline='middle',color=cor_rotulos,size=(tamanho_rotulos))
                            .encode(text="Faturamento",x="Competência",y="Faturamento float",tooltip=["Faturamento","Impostos","Aliquota EF"])
                        if rotulos =="Sim" #Caso os rótulos forem "Sim" o código acima é posto, caso contrário o código abaixo
                        else 
                        alt.Chart(faturamento_df) 
                            .mark_bar(color=cor_primaria,size=(largura))
                            .encode(x="Competência",y="Faturamento float",tooltip=["Faturamento","Impostos","Aliquota EF"]))