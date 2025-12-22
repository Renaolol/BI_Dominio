import pyodbc
import pandas as pd
import streamlit as st
from dependencies import *
import datetime

st.title("B.I Contábil")
st.header("Dev. Renan")
st.divider()
dt_init = st.sidebar.date_input("Insira a data inicial",format="DD/MM/YYYY",value=(datetime.date.today() - datetime.timedelta(60)),width=300)
dt_fim = st.sidebar.date_input("Insira a data final",width=300,format="DD/MM/YYYY")
cod = st.sidebar.number_input("Insira o código da empresa",step=0,width=300)
try:
    contagens = retorna_contagem_tipo_lancto(cod,dt_init,dt_fim)
    col1,col2 =st.columns([0.2,0.8])
    with col1:
        st.subheader(retorna_nome_empresa(cod)[0][0])
        for x in contagens:
                origem = ""
                if x [1] == 1:
                    origem = "Normal"
                elif x[1] == 2:
                    origem ="Zeramento"
                elif x[1] == 3:
                    origem = "Patrimônio"
                elif x[1] == 4:
                    origem = "Escrita"
                elif x[1] == 5:
                    origem = "Saida"
                elif x[1] == 6:
                    origem = "Entrada"
                elif x[1] == 7:
                    origem = "Serviço"
                elif x[1] == 8:
                    origem = "Ajustes EF"
                elif x[1] == 9:
                    origem = "Acumulador EF"
                elif x[1] == 10:
                    origem = "Apuração EF"
                elif x[1] == 11:
                    origem = "Pagto Guia"
                elif x[1] == 12:
                    origem = "Cliente"
                elif x[1] == 13:
                    origem = "Folha"
                elif x[1] == 39:
                    origem = "Extrato Bancário"
                elif x[1] == 66:
                    origem = "Pagto Guia Folha Pagto." 
                elif x[1] == 25:
                    origem = "Ajustes de PIS e COFINS"
                elif x[1] == 23:
                    origem = "Ajustes PIS e COFINS imob."       
                else:
                    origem = "Honorários"
                st.write(f'{x[0]} - {origem}')
    with col2:
        st.subheader("Lançamentos Normais")
        lanctos_normais = retorna_lancto_tipo(cod,dt_init,dt_fim,1)
        lanctos_list = []
        for x in lanctos_normais:
            lanctos_list.append([x[0].strftime('%d/%m/%Y'),x[1],x[2],x[3],x[5][:30],x[6],x[7],x[8]])
        lanctos_df=pd.DataFrame(lanctos_list,columns=['Data','Valor','Conta Déb','Conta Créd','Histórico','Usuário','Origem','lote'])
        lanctos_df['Conta Déb']=lanctos_df['Conta Déb'].fillna('0')
        lanctos_df['Conta Créd']=lanctos_df['Conta Créd'].fillna('0')
        st.write(lanctos_df)
    st.divider()
except Exception as e:
    st.info("Insira o código da empresa desejada no menu lateral")