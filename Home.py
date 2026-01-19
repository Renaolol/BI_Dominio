import streamlit as st
st.set_page_config(layout="wide")

st.title("BI Gcont gestão")
st.divider()
st.header("Bem Vindo(a)")
st.write("Para acessar as diferentes abas do BI, utilize o menu lateral")
st.write("Ou clique em um dos links abaixo")
st.link_button("Administrar","Administrar")
st.link_button("AliqSimples","AliqSimples")
st.link_button("Contabil","Contabil")
st.link_button("Empresas","Empresas")