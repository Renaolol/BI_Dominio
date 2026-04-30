import streamlit as st
from dependencies import *
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import altair as alt
from io import BytesIO

def formata_valor(valor):
    return f"R$ {valor:,.2f}".replace(',','X').replace('.',',').replace('X','.')
st.set_page_config(layout="wide")

st.title("DEPARTAMENTO PESSOAL - ADRIANE E GABRIELA")
with st.expander("Férias"):
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
            ferias_list.append([x[0],x[1].strftime("%d/%m/%Y"),x[2],x[3]]) 
        ferias_df=pd.DataFrame(ferias_list,columns=["Nome","Fim Aquisitivo","Empresa","Tipo"])       
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

with st.expander("Admissões e Demissões"):
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

    if demitidos_lista == [] and admitidos_lista == []:
        pass
    else:
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
        
        st.divider()
        st.subheader("Ficha Cadastral Admitidos/Demitidos")
        with st.expander("Admissões"):
            ficha_cadastral_adm_list=[]
            ficha_adm = retorna_ficha_cadastral_admissoes(data_init,data_fin)
            for x in ficha_adm:
                ficha_cadastral_adm_list.append([x[0],x[1],x[2].strftime("%d/%m/%Y"),x[3],x[4]])
            ficha_cadastral_adm_df = pd.DataFrame(ficha_cadastral_adm_list,columns=["Nome","CPF","Data Admissão","Cod E-social","Empresa"])
            st.table(ficha_cadastral_adm_df)


        with st.expander("Demissões"):
            ficha_cadastral_demitidos_list=[]
            ficha_dem = retorna_ficha_cadastral_demissoes(data_init,data_fin)
            for x in ficha_dem:
                ficha_cadastral_demitidos_list.append([x[0],x[1],x[2].strftime("%d/%m/%Y"),x[3],x[4]])
            ficha_cadastral_demissoes_df = pd.DataFrame(ficha_cadastral_demitidos_list,columns=["Nome","CPF","Data Demissão","Cod E-social","Empresa"])
            st.table(ficha_cadastral_demissoes_df)
        df_merged = pd.concat([ficha_cadastral_adm_df,ficha_cadastral_demissoes_df])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer,engine="xlsxwriter") as writer:
            df_merged.to_excel(writer,sheet_name="funcionarios")
            writer.close()
        @st.fragment()
        def baixa_excel():
            st.download_button("Baixar Excel",buffer,
                               file_name="admissoes_e_demissoes.xlsx")
        baixa_excel()

with st.expander("Validação de Salários"):
    st.subheader("Comparativo de Salário por Competência")
    st.caption("Até o dia 26: atual = mês anterior e anterior = 2 meses atrás. Após o dia 26: atual = mês corrente e anterior = mês anterior.")

    dados_diferenca = retorna_dif_salarios()
    diferenca_list = []
    for x in dados_diferenca:
        salario_atual = float(x[0]) if x[0] is not None else 0.0
        salario_anterior = float(x[1]) if x[1] is not None else 0.0
        diferenca_salario = float(x[2]) if x[2] is not None else 0.0
        funcionario = x[3]
        empresa = x[4]
        competencia_atual_data = x[5]
        competencia_atual = competencia_atual_data.strftime("%m/%Y") if competencia_atual_data else ""
        competencia_anterior = (
            (competencia_atual_data - relativedelta(months=1)).strftime("%m/%Y")
            if competencia_atual_data
            else ""
        )

        linha = [
            funcionario,
            empresa,
            competencia_anterior,
            competencia_atual,
            salario_anterior,
            salario_atual,
            diferenca_salario,
        ]
        if abs(diferenca_salario) > 1.0:
            diferenca_list.append(linha)

    diferenca_df = pd.DataFrame(
        diferenca_list,
        columns=[
            "Funcionário",
            "Empresa",
            "Competência Anterior",
            "Competência Atual",
            "Salário Anterior",
            "Salário Atual",
            "Diferença",
        ],
    )

    if diferenca_df.empty:
        st.info("Nenhuma diferença encontrada")
    else:
        filtro_empresa = st.text_input(
            "Filtrar empresa",
            placeholder="Digite o nome da empresa",
        ).strip()

        diferenca_filtrada_df = diferenca_df
        if filtro_empresa:
            diferenca_filtrada_df = diferenca_df[
                diferenca_df["Empresa"].fillna("").str.contains(
                    filtro_empresa, case=False, na=False
                )
            ]

        st.metric("Qtd. com diferença", len(diferenca_filtrada_df))
        if diferenca_filtrada_df.empty:
            st.info("Nenhuma empresa encontrada para o filtro informado.")
        else:
            st.dataframe(
                diferenca_filtrada_df.style.format(
                    {
                        "Salário Anterior": lambda v: formata_valor(v),
                        "Salário Atual": lambda v: formata_valor(v),
                        "Diferença": lambda v: formata_valor(v),
                    }
                ),
                use_container_width=True,
            )
