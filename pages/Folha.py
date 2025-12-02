import streamlit as st
from dependencies import retorna_menor_salario_min, retorna_prox_ferias
import pandas as pd

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
        ferias_list.append([x[0],x[1].strftime("%d/%m/%Y"),x[2].strftime("%d/%m/%Y"),x[3],x[4].strftime("%d/%m/%y"),x[5].strftime("%d/%m/%y"),x[6],x[7]]) 
    ferias_df=pd.DataFrame(ferias_list,columns=["Nome","Inicio Gozo","Fim Gozo","Abono?","Inicio Abono","Fim Abono","Empresa","Tipo"])       
    st.write(ferias_df)
