import calendar
from datetime import date

import pandas as pd
import streamlit as st

from dependencies import *

st.set_page_config(layout="wide")


def _formata_data_exibicao(data_registro):
    if hasattr(data_registro, "strftime"):
        return data_registro.strftime("%d/%m/%Y")
    return str(data_registro)


def _data_para_widget(data_registro):
    data_convertida = pd.to_datetime(data_registro, errors="coerce")
    if pd.isna(data_convertida):
        return pd.Timestamp.today().date()
    return data_convertida.date()


def _inicio_fim_mes(data_ref):
    inicio = data_ref.replace(day=1)
    ultimo_dia = calendar.monthrange(data_ref.year, data_ref.month)[1]
    fim = data_ref.replace(day=ultimo_dia)
    return inicio, fim


def _carrega_mapa_empresas():
    try:
        empresas = retorna_codigos_empresas()
        mapa = {}
        for item in empresas:
            if len(item) >= 2:
                mapa[item[0]] = str(item[1])
        return mapa
    except Exception:
        return {}


st.title("Central GCONT", "GCONT")
st.divider()
st.header("Bem Vindo(a)")
pagina = st.segmented_control(
    "Selecione a pagina desejada",
    ["Controle de Notas", "Resumo Mensal de Notas", "Por enquanto Pag.Vazia"],
)

if pagina == "Controle de Notas":
    st.subheader("Contorle de notas emitidas no escritorio")
    empresa = st.selectbox(
        "Selecione a empresa que foi lancado Notas",
        retorna_codigos_empresas(),
        width=350,
    )

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            date_doc = st.date_input(
                "Selecione a data de emissao", width=250, format="DD/MM/YYYY"
            )
        with c2:
            user = st.text_input("Usuario")
        with c3:
            tipo = st.radio("Documento", ["NF-e", "NFC-e", "CT-e", "NFS-e"], horizontal=True)
        with c4:
            quantidade = st.number_input("Quantidade", step=0, width=250)
    save = st.button("Salvar")

    if save:
        if registra_nota(date_doc, empresa[0], user, tipo, quantidade):
            st.success("Lancamento Efetuado!")
    st.divider()
    pesquisa = st.radio("Selecione o Tipo de pesquisa", ["Geral", "Por periodo"], horizontal=True)
    if pesquisa == "Por periodo":
        col_data1, col_data2, col_sem_uso = st.columns([1, 1, 4])
        with col_data1:
            dt_init = st.date_input("Selecione a Data Inicial", format="DD/MM/YYYY")
        with col_data2:
            dt_fim = st.date_input("Selecione a Data Final", format="DD/MM/YYYY")
    else:
        dt_init = 0
        dt_fim = 0
    col1, col2 = st.columns(2)
    with col1:
        st.header("Notas emitidas para esse cliente")
        resultado = retorna_contagem_notas_emitidas(empresa[0], dt_init, dt_fim, pesquisa)
        st.subheader(f"Total de notas emitidas para o cliente: {resultado[0][0]}")
    with col2:
        st.header("Listagem das notas")
        listagem_notas = []
        notas = retorna_listagem_notas_emitidas(empresa[0], dt_init, dt_fim, pesquisa)
        for registro in notas:
            data_exibicao = _formata_data_exibicao(registro[1])
            listagem_notas.append(
                [registro[0], data_exibicao, registro[2], registro[3], registro[4], registro[5]]
            )
        df_notas = pd.DataFrame(
            listagem_notas, columns=["ID", "Data", "Empresa", "Emissor", "Tipo", "Quantidade"]
        )
        st.dataframe(df_notas[["ID", "Data", "Emissor", "Tipo", "Quantidade"]])

        if notas:
            st.subheader("Atualizar ou excluir lancamento")
            tipos_documento = ["NF-e", "NFC-e", "CT-e", "NFS-e"]

            nota_selecionada = st.selectbox(
                "Selecione o lancamento",
                notas,
                format_func=lambda registro: (
                    f"ID {registro[0]} | {_formata_data_exibicao(registro[1])} | "
                    f"{registro[3]} | {registro[4]} | Qtd {registro[5]}"
                ),
            )

            nota_id = nota_selecionada[0]
            data_edicao = _data_para_widget(nota_selecionada[1])
            tipo_atual = (
                nota_selecionada[4]
                if nota_selecionada[4] in tipos_documento
                else tipos_documento[0]
            )

            e1, e2, e3, e4 = st.columns(4)
            with e1:
                nova_data = st.date_input(
                    "Data do lancamento",
                    value=data_edicao,
                    format="DD/MM/YYYY",
                    key=f"edit_data_{nota_id}",
                )
            with e2:
                novo_emissor = st.text_input(
                    "Emissor",
                    value=str(nota_selecionada[3]),
                    key=f"edit_emissor_{nota_id}",
                )
            with e3:
                novo_tipo = st.selectbox(
                    "Tipo",
                    tipos_documento,
                    index=tipos_documento.index(tipo_atual),
                    key=f"edit_tipo_{nota_id}",
                )
            with e4:
                nova_quantidade = st.number_input(
                    "Quantidade",
                    min_value=0.0,
                    step=1.0,
                    value=float(nota_selecionada[5]),
                    key=f"edit_quantidade_{nota_id}",
                )

            b1, b2 = st.columns(2)
            with b1:
                if st.button("Atualizar lancamento", key=f"btn_atualizar_{nota_id}"):
                    atualizado = atualiza_nota_emitida(
                        nota_id,
                        empresa[0],
                        nova_data,
                        novo_emissor,
                        novo_tipo,
                        nova_quantidade,
                    )
                    if atualizado:
                        st.success("Lancamento atualizado com sucesso.")
                        st.rerun()
                    else:
                        st.warning("Nao foi possivel atualizar o lancamento selecionado.")

            with b2:
                confirmar_exclusao = st.checkbox(
                    "Confirmar exclusao deste lancamento",
                    key=f"confirmar_exclusao_{nota_id}",
                )
                if st.button("Excluir lancamento", key=f"btn_excluir_{nota_id}"):
                    if not confirmar_exclusao:
                        st.warning("Marque a confirmacao para excluir o lancamento.")
                    else:
                        excluido = exclui_nota_emitida(nota_id, empresa[0])
                        if excluido:
                            st.success("Lancamento excluido com sucesso.")
                            st.rerun()
                        else:
                            st.warning("Nao foi possivel excluir o lancamento selecionado.")

elif pagina == "Resumo Mensal de Notas":
    st.subheader("Resumo mensal de notas emitidas (todas as empresas)")
    col_comp, col_periodo = st.columns([1, 3])
    with col_comp:
        competencia = st.date_input("Selecione o mes de referencia", value=date.today())
    dt_inicio, dt_fim = _inicio_fim_mes(competencia)
    with col_periodo:
        st.caption(
            f"Periodo considerado: {dt_inicio.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}"
        )

    notas_mes = retorna_listagem_notas_geral(dt_inicio, dt_fim)
    if not notas_mes:
        st.info("Nao ha lancamentos para o mes selecionado.")
    else:
        df_mes = pd.DataFrame(
            notas_mes, columns=["ID", "Data", "Cliente", "Emissor", "Tipo", "Quantidade"]
        )
        df_mes["Data"] = pd.to_datetime(df_mes["Data"], errors="coerce").dt.date
        df_mes["Quantidade"] = pd.to_numeric(df_mes["Quantidade"], errors="coerce").fillna(0.0)
        df_mes["Cliente"] = pd.to_numeric(df_mes["Cliente"], errors="coerce").fillna(0).astype(int)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total de notas", f"{df_mes['Quantidade'].sum():.2f}")
        c2.metric("Lancamentos", f"{len(df_mes)}")
        c3.metric("Emissores", f"{df_mes['Emissor'].nunique()}")
        c4.metric("Tipos de documento", f"{df_mes['Tipo'].nunique()}")

        soma_emissor = (
            df_mes.groupby("Emissor", as_index=False)["Quantidade"]
            .sum()
            .sort_values("Quantidade", ascending=False)
        )
        soma_tipo = (
            df_mes.groupby("Tipo", as_index=False)["Quantidade"]
            .sum()
            .sort_values("Quantidade", ascending=False)
        )

        col_emissor, col_tipo = st.columns(2)
        with col_emissor:
            st.markdown("**Somatorio por emissor**")
            st.dataframe(soma_emissor, use_container_width=True, hide_index=True)
            st.bar_chart(soma_emissor.set_index("Emissor"))
        with col_tipo:
            st.markdown("**Somatorio por tipo de documento**")
            st.dataframe(soma_tipo, use_container_width=True, hide_index=True)
            st.bar_chart(soma_tipo.set_index("Tipo"))

        st.markdown("**Evolucao diaria do mes**")
        evolucao_diaria = (
            df_mes.groupby("Data", as_index=False)["Quantidade"]
            .sum()
            .sort_values("Data")
        )
        st.line_chart(evolucao_diaria.set_index("Data"))

        st.markdown("**Top clientes por quantidade emitida**")
        mapa_empresas = _carrega_mapa_empresas()
        if mapa_empresas:
            df_mes["Empresa"] = df_mes["Cliente"].map(mapa_empresas).fillna("Nao identificado")
            top_clientes = (
                df_mes.groupby(["Cliente", "Empresa"], as_index=False)["Quantidade"]
                .sum()
                .sort_values("Quantidade", ascending=False)
                .head(10)
            )
            top_clientes["Cliente"] = top_clientes["Cliente"].astype(str) + " - " + top_clientes["Empresa"]
            st.dataframe(
                top_clientes[["Cliente", "Quantidade"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            top_clientes = (
                df_mes.groupby("Cliente", as_index=False)["Quantidade"]
                .sum()
                .sort_values("Quantidade", ascending=False)
                .head(10)
            )
            st.dataframe(top_clientes, use_container_width=True, hide_index=True)

        st.markdown("**Cruzamento emissor x tipo**")
        cruzamento = pd.pivot_table(
            df_mes,
            values="Quantidade",
            index="Emissor",
            columns="Tipo",
            aggfunc="sum",
            fill_value=0,
        )
        st.dataframe(cruzamento, use_container_width=True)

        with st.expander("Ver detalhes dos lancamentos do mes"):
            df_detalhes = df_mes.copy()
            df_detalhes["Data"] = pd.to_datetime(df_detalhes["Data"], errors="coerce").dt.strftime(
                "%d/%m/%Y"
            )
            st.dataframe(
                df_detalhes[["ID", "Data", "Cliente", "Emissor", "Tipo", "Quantidade"]],
                use_container_width=True,
                hide_index=True,
            )
else:
    st.info("Pagina em construcao.")
