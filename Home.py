import calendar
from datetime import date, datetime, time, timedelta

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


def _formata_minutos_exibicao(minutos):
    try:
        return formata_horas_min_seg(float(minutos))
    except Exception:
        return "00:00:00"


def _para_minutos_seguro(valor):
    if valor is None:
        return 0.0

    if isinstance(valor, timedelta):
        return max(float(valor.total_seconds() / 60), 0.0)

    if isinstance(valor, datetime):
        return max(float(valor.hour * 60 + valor.minute + (valor.second / 60)), 0.0)

    if isinstance(valor, time):
        return max(float(valor.hour * 60 + valor.minute + (valor.second / 60)), 0.0)

    try:
        return max(float(valor), 0.0)
    except (TypeError, ValueError):
        texto = str(valor).strip()
        if ":" in texto:
            partes = texto.split(":")
            if len(partes) >= 2:
                try:
                    horas = float(partes[0])
                    minutos = float(partes[1])
                    segundos = float(partes[2]) if len(partes) >= 3 else 0.0
                    return max((horas * 60) + minutos + (segundos / 60), 0.0)
                except ValueError:
                    return 0.0
        return 0.0


def _extrai_tempo_registro(registro):
    if not registro or len(registro) <= 6:
        return 0.0

    # Prioriza o indice esperado (tempo_minutos) quando o schema estiver alinhado.
    valor_indice_6 = registro[6]
    if isinstance(valor_indice_6, (int, float, str, timedelta, datetime, time)):
        minutos = _para_minutos_seguro(valor_indice_6)
        if minutos > 0 or str(valor_indice_6).strip() in ("0", "0.0"):
            return minutos

    # Fallback para bases legadas em que existam colunas extras entre quantidade e tempo.
    for indice in range(len(registro) - 1, 5, -1):
        valor = registro[indice]
        if isinstance(valor, (int, float, str, timedelta, datetime, time)):
            minutos = _para_minutos_seguro(valor)
            if minutos > 0 or str(valor).strip() in ("0", "0.0"):
                return minutos

    return 0.0


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
        c1, c2, c3, c4, c5 = st.columns(5)
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
        with c5:
            tempo_gasto_min = st.number_input(
                "Tempo gasto (min)", min_value=0.0, step=1.0, width=250
            )
    save = st.button("Salvar")

    if save:
        if registra_nota(date_doc, empresa[0], user, tipo, quantidade, tempo_gasto_min):
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
    notas = retorna_listagem_notas_emitidas(empresa[0], dt_init, dt_fim, pesquisa)
    listagem_notas = []
    for registro in notas:
        data_exibicao = _formata_data_exibicao(registro[1])
        tempo_minutos = _extrai_tempo_registro(registro)
        listagem_notas.append(
            [
                registro[0],
                data_exibicao,
                registro[2],
                registro[3],
                registro[4],
                registro[5],
                tempo_minutos,
            ]
        )
    df_notas = pd.DataFrame(
        listagem_notas,
        columns=["ID", "Data", "Empresa", "Emissor", "Tipo", "Quantidade", "Tempo (min)"],
    )
    if df_notas.empty:
        total_notas = 0.0
        total_tempo_min = 0.0
    else:
        df_notas["Quantidade"] = pd.to_numeric(df_notas["Quantidade"], errors="coerce").fillna(0.0)
        df_notas["Tempo (min)"] = pd.to_numeric(df_notas["Tempo (min)"], errors="coerce").fillna(0.0)
        total_notas = float(df_notas["Quantidade"].sum())
        total_tempo_min = float(df_notas["Tempo (min)"].sum())
    tempo_medio_min = (total_tempo_min / total_notas) if total_notas > 0 else 0.0

    col1, col2 = st.columns(2)
    with col1:
        st.header("Notas emitidas para esse cliente")
        st.metric("Total de notas emitidas", f"{total_notas:.2f}")
        st.metric("Tempo total gasto", _formata_minutos_exibicao(total_tempo_min))
        st.metric("Tempo medio por nota", _formata_minutos_exibicao(tempo_medio_min))
    with col2:
        st.header("Listagem das notas")
        st.dataframe(df_notas[["ID", "Data", "Emissor", "Tipo", "Quantidade", "Tempo (min)"]])

        if not df_notas.empty:
            st.markdown("**Tempo medio por funcionario na empresa selecionada**")
            resumo_tempo = (
                df_notas.groupby(["Empresa", "Emissor"], as_index=False)
                .agg({"Quantidade": "sum", "Tempo (min)": "sum"})
                .sort_values("Quantidade", ascending=False)
            )
            resumo_tempo.rename(
                columns={
                    "Empresa": "Codigo Empresa",
                    "Quantidade": "Notas Emitidas",
                    "Tempo (min)": "Tempo Total (min)",
                },
                inplace=True,
            )
            resumo_tempo["Tempo Medio (min/nota)"] = resumo_tempo.apply(
                lambda linha: (
                    linha["Tempo Total (min)"] / linha["Notas Emitidas"]
                    if linha["Notas Emitidas"] > 0
                    else 0
                ),
                axis=1,
            )
            resumo_tempo["Tempo Total"] = resumo_tempo["Tempo Total (min)"].apply(_formata_minutos_exibicao)
            resumo_tempo["Tempo Medio"] = resumo_tempo["Tempo Medio (min/nota)"].apply(
                _formata_minutos_exibicao
            )
            st.dataframe(
                resumo_tempo[
                    [
                        "Codigo Empresa",
                        "Emissor",
                        "Notas Emitidas",
                        "Tempo Total (min)",
                        "Tempo Medio (min/nota)",
                        "Tempo Total",
                        "Tempo Medio",
                    ]
                ],
                hide_index=True,
                use_container_width=True,
            )

        if notas:
            st.subheader("Atualizar ou excluir lancamento")
            tipos_documento = ["NF-e", "NFC-e", "CT-e", "NFS-e"]

            nota_selecionada = st.selectbox(
                "Selecione o lancamento",
                notas,
                format_func=lambda registro: (
                    f"ID {registro[0]} | {_formata_data_exibicao(registro[1])} | "
                    f"{registro[3]} | {registro[4]} | Qtd {registro[5]} | "
                    f"Tempo {_extrai_tempo_registro(registro):.2f} min"
                ),
            )

            nota_id = nota_selecionada[0]
            data_edicao = _data_para_widget(nota_selecionada[1])
            tempo_atual = _extrai_tempo_registro(nota_selecionada)
            tipo_atual = (
                nota_selecionada[4]
                if nota_selecionada[4] in tipos_documento
                else tipos_documento[0]
            )

            e1, e2, e3, e4, e5 = st.columns(5)
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
            with e5:
                novo_tempo_min = st.number_input(
                    "Tempo gasto (min)",
                    min_value=0.0,
                    step=1.0,
                    value=tempo_atual,
                    key=f"edit_tempo_{nota_id}",
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
                        novo_tempo_min,
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
            notas_mes,
            columns=["ID", "Data", "Cliente", "Emissor", "Tipo", "Quantidade", "Tempo (min)"],
        )
        df_mes["Data"] = pd.to_datetime(df_mes["Data"], errors="coerce").dt.date
        df_mes["Quantidade"] = pd.to_numeric(df_mes["Quantidade"], errors="coerce").fillna(0.0)
        df_mes["Tempo (min)"] = pd.to_numeric(df_mes["Tempo (min)"], errors="coerce").fillna(0.0)
        df_mes["Cliente"] = pd.to_numeric(df_mes["Cliente"], errors="coerce").fillna(0).astype(int)
        tempo_medio_mes = (
            df_mes["Tempo (min)"].sum() / df_mes["Quantidade"].sum()
            if df_mes["Quantidade"].sum() > 0
            else 0
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total de notas", f"{df_mes['Quantidade'].sum():.2f}")
        c2.metric("Lancamentos", f"{len(df_mes)}")
        c3.metric("Emissores", f"{df_mes['Emissor'].nunique()}")
        c4.metric("Tipos de documento", f"{df_mes['Tipo'].nunique()}")
        c5.metric("Tempo medio por nota", _formata_minutos_exibicao(tempo_medio_mes))

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
                df_detalhes[
                    ["ID", "Data", "Cliente", "Emissor", "Tipo", "Quantidade", "Tempo (min)"]
                ],
                use_container_width=True,
                hide_index=True,
            )
else:
    st.info("Pagina em construcao.")
