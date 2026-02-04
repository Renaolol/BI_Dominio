import streamlit as st
from dependencies import *
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import altair as alt
import locale

def formata_valor(valor):
    return f"R$ {valor:,.2f}".replace(',','X').replace('.',',').replace('X','.')
st.set_page_config(layout="wide")

st.title("")
col1,col2 = st.columns(2)
with col1:
    st.subheader("Funcionários que recebem menos de 1 sal. Min")
    compt=st.date_input("insira a competencia",format='DD/MM/YYYY')
    salario = retorna_menor_salario_min(competencia=compt)
    salario_list = []
    for x in salario:
        salario_list.append([formata_valor(x[0]),x[1],x[2]])

    salario_df = pd.DataFrame(salario_list,columns=['Salário','Nome','Empresa'])
    st.write(salario_df)

with col2:
    st.subheader("Ferias")
    compt2=st.date_input("Competencia 2",format='DD/MM/YYYY')
    proximas_ferias = retorna_prox_ferias(compt2)
    ferias_list=[]
    
    for x in proximas_ferias:
        ferias_list.append([x[0],x[1].strftime("%d/%m/%Y"),x[2].strftime("%d/%m/%Y"),x[3],
                            x[4].strftime("%d/%m/%y"),x[5].strftime("%d/%m/%y"),x[6],x[7]]) 
    ferias_df=pd.DataFrame(ferias_list,columns=["Nome","Inicio Gozo","Fim Gozo","Abono?","Inicio Abono","Fim Abono","Empresa","Tipo"])       
    st.write(ferias_df)
    
st.divider()

st.subheader("Vencimento das Férias em dobro")
hoje = datetime.date.today()
prox_tres_meses = hoje + relativedelta(months=3)
ferias = vencimento_ferias(hoje,prox_tres_meses)
ferias_list = []
for x in ferias:
    ferias_list.append([x[1],x[2],x[3].strftime("%d/%m/%Y"),
                        (x[5]+relativedelta(months=12)).strftime("%d/%m/%Y"),
                        (x[3]-(x[5]+relativedelta(months=12))).days*(-1)+1])
ferias_df = pd.DataFrame(ferias_list,columns=["Empresa","Funcionário","Data Limite",
                                              "Aquisitivo","Dias"])    
st.write(ferias_df)

st.divider()
with st.container(border=True,horizontal=True,gap='medium'):
    data_init= st.date_input("Selecione a Data Inicial",format="DD/MM/YYYY",width=150)
    data_fin = st.date_input("Selecione a Data Final",format="DD/MM/YYYY",width=150)
    admitidos = retorna_admissoes_todas_empresas(data_init,data_fin)
    demitidos = retorna_demitidos_todas_empresas(data_init,data_fin)
    st.metric("Contagem de admissões",admitidos[0][0],width=200)
    st.metric("Contagem de demissões",demitidos[0][0],width=200)
    st.metric("Somatório Geral",(admitidos[0][0]+demitidos[0][0]))

#Busca no banco de dados
demitidos_base = retorna_demitidos_com_data(data_init,data_fin)
admitidos_base = retorna_admissoes_com_data(data_init,data_fin)

#Formação do primeiro DATAFRAME (Demitidos)
demitidos_lista=[]
for x in demitidos_base:
    demitidos_lista.append([x[0],x[1].strftime("%m/%Y")])
demitidos_df = pd.DataFrame(demitidos_lista,columns=["Demissoes","Date"])
demitidos_mes = demitidos_df.groupby("Date")["Demissoes"].sum().reset_index()
demitidos_mes["Date"]=pd.to_datetime(demitidos_mes["Date"])

#Formação do segundo DATAFRAME (Admitidos)
admitidos_lista=[]
for x in admitidos_base:
    admitidos_lista.append([x[0],x[1].strftime("%m/%Y")])
admitidos_df = pd.DataFrame(admitidos_lista,columns=["Admissoes","Date"])
admitidos_mes = admitidos_df.groupby("Date")["Admissoes"].sum().reset_index()
admitidos_mes["Date"]=pd.to_datetime(admitidos_mes["Date"])


#Visulalização em um gráfico de Linhas combinado
st.altair_chart(alt.Chart(demitidos_mes)
                    .mark_line(color="#Fad32b",
                               point=alt.OverlayMarkDef(filled=True,fill="#9e9e9e"))
                    .encode(x=alt.X("Date"),
                            y=alt.Y("Demissoes"))
                            +
                alt.Chart(admitidos_mes)
                    .mark_line(color="#c0c0c0",
                               point=alt.OverlayMarkDef(filled=True,fill="#9E9E9E"))
                    .encode(x=alt.X("Date",type="temporal"),
                            y=alt.Y("Admissoes"))
                            )