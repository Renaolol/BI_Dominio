import streamlit as st
from dependencies import *
import pandas as pd
st.set_page_config(layout="wide")

st.title("Central GCONT","GCONT")
st.divider()
st.header("Bem Vindo(a)")
pagina = st.segmented_control("Selecione a página desejada",["Controle de Notas","Por enquanto Pág.Vazia"])

if pagina == "Controle de Notas":
    st.subheader("Contorle de notas emitidas no escritório")
    empresa = st.selectbox("Selecione a empresa que foi lançado Notas"
                           ,retorna_codigos_empresas(),width=350)

    with st.container(border=True):
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            date_doc = st.date_input("Selecione a data de emissão",width=250,format="DD/MM/YYYY")
        with c2:
            user = st.text_input("Usuário")
        with c3:
            tipo = st.radio("Documento",["NF-e","NFC-e","CT-e","NFS-e"],horizontal=True)
        with c4:
            quantidade = st.number_input("Quantidade",step=0,width=250)    
    save = st.button("Salvar")

    if save:
        if registra_nota(date_doc,empresa[0],user,tipo,quantidade):
            st.success("Lançamento Efetuado!")
    st.divider()
    pesquisa = st.radio("Selecione o Tipo de pesquisa",["Geral","Por período"],horizontal=True)
    if pesquisa =="Por período":
        col_data1,col_data2,col_sem_uso = st.columns([1,1,4])
        with col_data1:
            dt_init = st.date_input("Selecione a Data Inicial",format="DD/MM/YYYY")
        with col_data2:
            dt_fim = st.date_input("Selecione a Data Final",format="DD/MM/YYYY")
    else:
        dt_init=0
        dt_fim=0
    col1,col2=st.columns(2)
    with col1:
        st.header("Notas emitidas para esse cliente")
        resultado = retorna_contagem_notas_emitidas(empresa[0],dt_init,dt_fim,pesquisa)
        st.subheader(f'Total de notas emitidas para o cliente: {resultado[0][0]}')
    with col2:
        st.header("Listagem das notas")
        listagem_notas = []
        notas= retorna_listagem_notas_emitidas(empresa[0],dt_init,dt_fim,pesquisa)
        for registro in notas:
            data_registro = registro[1]
            if hasattr(data_registro, "strftime"):
                data_exibicao = data_registro.strftime("%d/%m/%Y")
            else:
                data_exibicao = str(data_registro)
            listagem_notas.append([registro[0],data_exibicao,registro[2]
                                   ,registro[3],registro[4],registro[5]])
        df_notas = pd.DataFrame(listagem_notas,columns=["ID","Data","Empresa","Emissor","Tipo","Quantidade"])
        st.dataframe(df_notas[["Data","Emissor","Tipo","Quantidade"]])
