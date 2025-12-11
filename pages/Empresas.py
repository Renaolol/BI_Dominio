import streamlit as st
import pandas as pd
from dependencies import *
import datetime
st.title("Empresas")
st.header("Comparar estatísticas das empresas")
dt_init = st.date_input("Insira a data inicial",format="DD/MM/YYYY",value=(datetime.date.today() - datetime.timedelta(60)))
cod = st.number_input("Insira o código da empresa",step=0)
nome_empresa = retorna_nome_empresa(cod)
st.subheader(f"Empresa : {nome_empresa[0][0]}")
impostos = retorna_faturamento_por_imposto(dt_init,cod)
impostos_list = []
for x in impostos:
    impostos_list.append([x[0],x[1],x[2],x[3],x[4],x[5]])
impostos_df = pd.DataFrame(impostos_list)    
st.write(impostos_list)