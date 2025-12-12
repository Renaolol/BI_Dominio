import streamlit as st
import pandas as pd
from dependencies import *
from datetime import timedelta, time,datetime
import altair as alt
st.set_page_config(layout="wide")
st.title("B.I Administrativo")
st.header("Informativo sobre Usuários")

col1,col2,col3=st.columns(3)
with col1:
    dt_init = st.date_input("Insira a data inicial",width=300,value=(datetime.today() - timedelta(30)),format="DD/MM/YYYY")
with col2:    
    dt_fim = st.date_input("Insira a data final",width=300,format="DD/MM/YYYY")

if dt_init > dt_fim:
    st.warning("Data inicial não pode ser maior que a data final")
    st.stop()    
usuarios = retorna_usuarios(dt_init)
users_list =[]
for x in usuarios:
    users_list.append(x[0])
with col3:      
    user = st.selectbox("Selecione o usuário",options=users_list,width=300)
       
try:
    registro = registro_atividades(dt_init,dt_fim)
except:
    st.info("Informe a data inicial")

registro_list=[]
for x in registro:
    registro_list.append([x[0],x[1],x[2].strftime("%d/%m/%Y"),x[3].strftime("%H:%M:%S"),x[4].strftime("%H:%M:%S"),
                          (((time_to_timedelta(x[4])-time_to_timedelta(x[3])).total_seconds())/60),x[6]]) 
    
registro_df = pd.DataFrame(registro_list,columns=["Empresa","Usuário","Data","Tempo Inicial","Tempo Final","Tempo gasto","Módulo ID"])
registro_df["Tempo gasto"] = pd.to_numeric(registro_df["Tempo gasto"], errors="coerce")
registro_df_fil = registro_df[registro_df["Usuário"].str.contains(user)]
registro_df_fil["Tempo"] = registro_df_fil["Tempo gasto"].apply(formata_horas_min_seg)
modulo_utilizado = retorna_modulo()

modulo_list = []
for x in modulo_utilizado:
    modulo_list.append([x[0],x[1]])
modulo_df = pd.DataFrame(modulo_list,columns=["Módulo", "Módulo ID"])
registro_df_fil_merged = pd.merge(registro_df_fil,modulo_df,on="Módulo ID")
registro_df_fil_merged["Tempo gasto"] = pd.to_numeric(registro_df_fil_merged["Tempo gasto"])
registro_grafico_pizza = pd.DataFrame(columns=["Tempo gasto"])
registro_grafico_pizza = (
    registro_df_fil_merged
        .groupby("Módulo")["Tempo gasto"]
        .sum()
        .div(60)
        .reset_index(name="Tempo gasto")
)
#exibição dos dados
col_dados1, col_dados2 = st.columns([3,1])
with col_dados1:
    st.write(registro_df_fil_merged[["Empresa","Usuário","Data","Tempo Inicial","Tempo Final","Tempo","Módulo"]])
with col_dados2:
    st.altair_chart(altair_chart=(alt.Chart(registro_grafico_pizza).mark_arc().encode(theta="Tempo gasto",color="Módulo")),theme='streamlit')
with st.container(border=True,horizontal=True):
    st.subheader(f'Total de horas trabalhadas no Sistema Domínio: ')
    st.subheader(f'{formata_horas_min_seg(registro_df_fil["Tempo gasto"].sum())}')
st.divider()

#Gráfico
st.header("Gráfico de usuários (Horas Acumuladas)")
registro_grafico = pd.DataFrame(columns=["Tempo gasto"])
registro_grafico["Tempo gasto"] = (registro_df.groupby("Usuário")["Tempo gasto"].sum().div(60).sort_values(ascending=False))
st.bar_chart(registro_grafico.sort_values(by="Tempo gasto"),y="Tempo gasto",color="#fad32b")
st.divider()
#Conexões Ativas
coluna_usuarios1, coluna_usuarios2 = st.columns(2)
with coluna_usuarios1:
    st.header("Usuários Ociosos")
    conexoes=retorna_ociosos()
    ociosos_list=[]
    for x in conexoes:
        ociosos_list.append([x[0],x[1].strftime("%d/%m/%Y - %H:%M:%S"),x[2],x[3]])

    ociosos_df=pd.DataFrame(ociosos_list,columns=["Usuário","Data/Hora","Empresa","Ocioso Inicial"])
    ociosos_df["Ocioso Inicial"] = ociosos_df["Ocioso Inicial"].fillna("")
    ociosos_df["Ocioso Inicial"] = pd.to_datetime(ociosos_df["Ocioso Inicial"])
    ociosos_df["Tempo Ocioso"] = ociosos_df["Ocioso Inicial"] - datetime.now()
    st.dataframe(ociosos_df)
with coluna_usuarios2:
    st.header("Usuários Ativos")
    conexoes=retorna_conectado()
    conectados_list=[]
    for x in conexoes:
        conectados_list.append([x[0],x[1].strftime("%d/%m/%Y - %H:%M:%S"),x[2]])

    conectados_df=pd.DataFrame(conectados_list,columns=["Usuário","Data/Hora","Empresa"])
    st.dataframe(conectados_df)