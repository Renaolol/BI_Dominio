import streamlit as st
import pandas as pd
from dependencies import *
import datetime
from datetime import timedelta, time
import altair as alt
st.set_page_config(layout="wide")
st.title("Empresas")
login = st.text_input("Login")
senha = st.text_input("Senha")

if login == "Vera" and senha == "VeraGcont":
    opt_datas = st.sidebar.radio("Selecione como deseja filtrar as datas", options=["Anos","Períodos"],horizontal=True)
    if opt_datas == "Períodos":
        dt_init = st.sidebar.date_input("Insira a data inicial",format="DD/MM/YYYY",value=(datetime.date.today() - datetime.timedelta(60)),width=300)
        dt_fim = st.sidebar.date_input("Insira a data final",width=300,format="DD/MM/YYYY")
        cod = st.sidebar.number_input("Insira o código da empresa",step=0,width=300)
    else:
        opt_anos = st.sidebar.radio("Anos:",options=[2021,2022,2023,2024,2025,2026],horizontal=True,index=4)
        if opt_anos == 2021:
            dt_init = '2021-01-01'
            dt_fim = '2021-12-31'
        elif opt_anos == 2022:
            dt_init = '2022-01-01'
            dt_fim = '2022-12-31'
        elif opt_anos == 2023:
            dt_init = '2023-01-01'
            dt_fim = '2023-12-31' 
        elif opt_anos == 2024:
            dt_init = '2024-01-01'
            dt_fim = '2024-12-31' 
        elif opt_anos == 2025:
            dt_init = '2025-01-01'
            dt_fim = '2025-12-31'
        elif opt_anos == 2026:
            dt_init = '2026-01-01'
            dt_fim = '2026-12-31'                   
        cod = st.sidebar.number_input("Insira o código da empresa",step=0,width=300)                                            

    nome_empresa = retorna_nome_empresa(cod)
    try:
        st.subheader(f"Empresa : {nome_empresa[0][0]}")
            
        #Apresentação dos dados    
        tempo_gasto_empresa = retorna_tempo_trabalho_empresa(cod,dt_init,dt_fim)  
        tempo_gasto_list = []
        for x in tempo_gasto_empresa:
            tempo_gasto_list.append([x[0],x[1].strftime("%d/%m/%Y"),x[2].strftime("%H:%M:%S"),x[3].strftime("%H:%M:%S"),
                                    ((time_to_timedelta(x[3])-time_to_timedelta(x[2])).total_seconds()/60),x[5]])
        tempo_gasto_df=pd.DataFrame(tempo_gasto_list,columns=["Usuário","Data","Hora Inicial","Hora Final","Tempo gasto","Módulo ID"])

        modulo = retorna_modulo()
        modulo_list = []
        for x in modulo:
            modulo_list.append([x[0],x[1]])
        modulo_df = pd.DataFrame(modulo_list,columns=["Módulo", "Módulo ID"])
        tempo_gasto_merged = pd.merge(tempo_gasto_df,modulo_df, on='Módulo ID')
        valor_honorario = retorna_valor_hono(cod)
        valor_honorario_num = 0
        if valor_honorario[0][7] is None:
            valor_honorario_num = valor_honorario[0][5]
        else:
            y = 0
            for x in valor_honorario:
                y+=1
            valor_honorario_num = valor_honorario[y-1][7]   

        col_hono1, col_hono2 = st.columns(2)
        with col_hono1:
            with st.container(border=True,horizontal_alignment="center"):
                try: 
                    st.header(f'Total de tempo gasto para a empresa *{formata_horas_min_seg((tempo_gasto_df["Tempo gasto"].sum()))}*')
                    if opt_datas == "Períodos":
                        st.subheader(f'Valor dos honorários mensais {formata_valor((valor_honorario_num))}')
                    else:
                        if opt_anos == 2025: 
                            st.subheader(f'Valor dos honorários anuais {formata_valor((valor_honorario_num)*12)}')
                            st.subheader(f'Valor dos honorários mensais {formata_valor((valor_honorario_num))}')
                            st.subheader(f'Valor por Hora {formata_valor(float(((valor_honorario_num)*12))/(tempo_gasto_df["Tempo gasto"].sum()/60))}')
                        else:
                            pass
                except Exception as e:
                    st.info(f"Erro: {e}")
        with col_hono2:
            with st.container(border=True,horizontal_alignment="center",height=320):
                with st.expander("Ajustes de Honorários"):
                    st.write(f"Valor do primeiro contrato {formata_valor(valor_honorario[0][5])}")
                    if valor_honorario[0][7] is None:
                        st.write("Sem reajustes de Honorários")
                    else:
                        for x in valor_honorario:
                            st.write(f'Reajuste para o valor de {formata_valor(x[7])} em {x[8].strftime("%d/%m/%Y")}')
        col_dados1, col_dados2, col_dados3, col_dados4 = st.columns(4)
        with col_dados1:
            with st.container(border=True,height=500):
                st.header("TEMPO")
                tempo_agrupado = pd.DataFrame(columns=["Tempo gasto"])
                tempo_agrupado["Tempo gasto"] = (tempo_gasto_merged.groupby("Módulo")["Tempo gasto"].sum()).sort_values(ascending=False)
                tempo_agrupado["Tempo gasto"] = tempo_agrupado["Tempo gasto"].apply(formata_horas_min_seg)

                st.write(tempo_agrupado)
        with col_dados2:
            with st.container(border=True,height=500):
                st.header("FOLHA")
                admissoes = retorna_admissoes(cod,dt_init,dt_fim)
                admissoes_nomes = retorna_nome_admissoes(cod,dt_init,dt_fim)
                demissoes = retorna_demitidos(cod,dt_init,dt_fim)
                demissoes_nomes = retorna_nome_demitidos(cod,dt_init,dt_fim)
                total_funcionarios = retorna_total_funcionarios(cod)
                nomes_funcionarios = retorna_nome_funcionarios(cod)
                st.write(f'Admissões do período: {admissoes[0][0]}')
                with st.expander("Admitidos"):
                    for x in admissoes_nomes:
                        st.write(x[0])
                st.write(f'Demissões do período: {demissoes[0][0]}')
                with st.expander("Demitidos"):
                    for x in demissoes_nomes:
                        st.write(x[0])
                st.write(f'Funcionários totais: {total_funcionarios[0][0]}')
                with st.expander("Funcionários"):
                    for x in nomes_funcionarios:
                        st.write(x[0])
        with col_dados3:
            with st.container(border=True,height=500):
                st.header("FISCAL")
                contagem_notas_entrada = retorna_contagem_entradas(cod,dt_init,dt_fim)
                contagem_notas_entrada_list = []
                for x in contagem_notas_entrada:
                    contagem_notas_entrada_list.append([x[0]])
                contagem_notas_saida = retorna_contagem_saidas(cod,dt_init,dt_fim)
                contagem_notas_saida_list = []
                for x in contagem_notas_saida:
                    contagem_notas_saida_list.append([x[0]])
                contagem_notas_servico = retorna_contagem_servico(cod,dt_init,dt_fim)
                contagem_notas_servico_list=[]
                for x in contagem_notas_servico:
                    contagem_notas_servico_list.append([x[0]])    
                st.write(f"Contagem de lançamentos de Entrada: *{contagem_notas_entrada_list[0][0]}* ")
                contagem_acum_entrada=retorna_contagem_acumulador_entrada(cod,dt_init,dt_fim)
                with st.expander("Acumuladores Entradas: "):
                    for x in contagem_acum_entrada:
                        st.write(f'{x[1]} -  {x[0]}')    
                st.write(f"Contagem de lançamentos de Saída: *{contagem_notas_saida_list[0][0]}* ")
                contagem_acum_saida=retorna_contagem_acumulador_saida(cod,dt_init,dt_fim)
                with st.expander("Acumuladores Saídas: "):
                    for x in contagem_acum_saida:
                        st.write(f'{x[1]} -  {x[0]}')        
                st.write(f"Contagem de lançamentos de Serviço: *{contagem_notas_servico_list[0][0]}* ")
                contagem_acum_servico=retorna_contagem_acumulador_servico(cod,dt_init,dt_fim)
                with st.expander("Acumuladores Serviços: "):
                    for x in contagem_acum_servico:
                        st.write(f'{x[1]} -  {x[0]}')         
        with col_dados4:
            with st.container(border=True,height=500):
                st.header("CONTABIL")
                contagem_lancto_contabil = retorna_contagem_lanctos_contabil(cod,dt_init,dt_fim)
                st.write(f"Contagem de lançamentos Contabeis : {contagem_lancto_contabil[0][0]}")
                contagem_lancto_contabil_origem = retorna_contagem_tipo_lancto(cod,dt_init,dt_fim)
                contagem_lancto_extrato = retorna_lancto_extrato(cod,dt_init,dt_fim)
                with st.expander("Origem dos lançamentos"):
                    for x in contagem_lancto_contabil_origem:
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
                        st.write(f'{origem} - {x[0]}')
        st.divider()
        st.header(f"Total de Lançamentos  --------- {(contagem_lancto_contabil[0][0]+contagem_notas_servico_list[0][0]+
                                          contagem_notas_saida_list[0][0]+contagem_notas_entrada_list[0][0]):,.0f}".replace(",","."))
    #Parte do Faturamento
        st.divider()
        col_faturamento1, col_faturamento2,col_faturamento3 = st.columns([0.5,1.5,1])
        impostos_empresa = retorna_impostos_empresa(cod,dt_init,dt_fim)
        impostos_empresa_list = []
        for x in impostos_empresa:
            impostos_empresa_list.append(x[0])
        with col_faturamento1:       
            opt_imposto = st.radio("Selecione o imposto", options=impostos_empresa_list)
        valores_impostos = retorna_debito_credito_imposto(cod,dt_init,dt_fim,opt_imposto)
        valores_impostos_list = []
        for x in valores_impostos:
            valores_impostos_list.append([x[0],x[1],x[2],x[3],x[4]])
        valores_impostos_df = pd.DataFrame(valores_impostos_list,columns=["Valor Débito","Valor Crédito","Competência","Vlr Saídas","Vlr Serviços"])
        valores_impostos_df["Faturamento"] = valores_impostos_df["Vlr Saídas"] + valores_impostos_df["Vlr Serviços"]
        valores_impostos_df_visual = valores_impostos_df.copy()
        valores_impostos_df_visual["Faturamento"] = valores_impostos_df_visual["Faturamento"].map(formata_valor)
        valores_impostos_df_visual["Competência"] = pd.to_datetime(valores_impostos_df_visual["Competência"]).dt.strftime("%m/%Y")
        with col_faturamento2:
            st.write(valores_impostos_df_visual[["Competência","Faturamento"]])
        with col_faturamento3:   
            #COMPARATIVO ENTRE ANOS 
            opt_comparativo = st.radio("Selecione o ano para comparar!", options=[2021,2022,2023,2024,2025,2026],horizontal=True,index=4)
            if opt_comparativo == 2021:
                dt_init_comparativo = '2021-01-01'
                dt_fim_comparativo = '2021-12-31'
            elif opt_comparativo == 2022:
                dt_init_comparativo = '2022-01-01'
                dt_fim_comparativo = '2022-12-31'
            elif opt_comparativo == 2023:
                dt_init_comparativo = '2023-01-01'
                dt_fim_comparativo = '2023-12-31' 
            elif opt_comparativo == 2024:
                dt_init_comparativo = '2024-01-01'
                dt_fim_comparativo = '2024-12-31' 
            elif opt_comparativo == 2025:
                dt_init_comparativo = '2025-01-01'
                dt_fim_comparativo = '2025-12-31'
            elif opt_comparativo == 2026:
                dt_init_comparativo = '2026-01-01'
                dt_fim_comparativo = '2026-12-31' 
            comparativo = retorna_impostos_empresa(cod,dt_init_comparativo,dt_fim_comparativo)
            comparativo_list = []
            for x in impostos_empresa:
                comparativo_list.append(x[0])     
            valores_impostos_comparativo = retorna_debito_credito_imposto(cod,dt_init_comparativo,dt_fim_comparativo,opt_imposto)
            valores_impostos_comparativo_list = []
            for x in valores_impostos_comparativo:
                valores_impostos_comparativo_list.append([x[0],x[1],x[2],x[3],x[4]])
            valores_impostos_df_comparativo = pd.DataFrame(valores_impostos_comparativo_list,columns=["Valor Débito","Valor Crédito","Competência","Vlr Saídas","Vlr Serviços"])
            valores_impostos_df_comparativo["Faturamento"] = valores_impostos_df_comparativo["Vlr Saídas"] + valores_impostos_df_comparativo["Vlr Serviços"]
            faturamento_comparado = valores_impostos_df_comparativo["Faturamento"].sum()
            faturamento_total =  valores_impostos_df["Faturamento"].sum()
            evolucao = round(((faturamento_total/faturamento_comparado)-1)*100,4)
            #Demonstração dos valores comparativos.
            st.metric("Total de Faturamento",formata_valor(faturamento_total))
            st.metric("Faturamento ano comparado",formata_valor(faturamento_comparado))
            st.metric("Evolução",formata_porcentagem(evolucao))
    #Parte de Resultados por Hora
        st.divider()
        st.header("RESULTADO POR EMPRESA")
        st.header("Custo")
        tempo_agrupado_empresa = pd.DataFrame(columns=["Tempo gasto"])
        tempo_agrupado_empresa["Tempo gasto"] = (tempo_gasto_merged.groupby("Usuário")["Tempo gasto"].sum().div(60)).sort_values(ascending=False)
        tempo_agrupado_empresa.reset_index(inplace=True)
        col_sal1, col_sal2 = st.columns(2)
        with col_sal1:
            eduardo = st.number_input("Eduardo")
            gabi = st.number_input("Gabi")
            adri = st.number_input("Adri")
            dani = st.number_input("Dani")
            josi = st.number_input("Josi")
            izabel = st.number_input("Izabel")
        with col_sal2:
            renan = st.number_input("Renan")
            andre = st.number_input("André")
            leticia = st.number_input("Letícia")
            gio = st.number_input("Giovana")
            djeuri = st.number_input("Djeuriston")
            vera = st.number_input("Vera")
        st.divider()
        total_de_horas = tempo_agrupado_empresa["Tempo gasto"].sum()
        custo_eduardo_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='MISTER']['Tempo gasto'].sum()*(eduardo/220)
        custo_gabi_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='GABI']['Tempo gasto'].sum()*(gabi/220)
        custo_adri_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='ADRI']['Tempo gasto'].sum()*(adri/220)
        custo_dani_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='DANI']['Tempo gasto'].sum()*(dani/220)
        custo_josi_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='JOSI']['Tempo gasto'].sum()*(josi/220)
        custo_izabel_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='IZABEL']['Tempo gasto'].sum()*(izabel/220)
        custo_renan_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='RENAN']['Tempo gasto'].sum()*(renan/220)
        custo_andre_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='ANDRE']['Tempo gasto'].sum()*(andre/220)
        custo_leticia_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='GCONT']['Tempo gasto'].sum()*(leticia/220)
        custo_gio_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='GIO']['Tempo gasto'].sum()*(gio/220)
        custo_djeuri_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='FISCAL']['Tempo gasto'].sum()*(djeuri/220)
        custo_vera_horas = tempo_agrupado_empresa[tempo_agrupado_empresa['Usuário']=='VERA']['Tempo gasto'].sum()*(vera/220)
        total_custo = float(custo_eduardo_horas+custo_gabi_horas+custo_adri_horas+custo_dani_horas+custo_josi_horas+custo_izabel_horas+custo_renan_horas+custo_andre_horas+custo_leticia_horas+custo_gio_horas+custo_djeuri_horas+custo_vera_horas)
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            with st.container(border=True):
                st.header(f'Total de custo por hora: {formata_valor(total_custo)}')
                if opt_datas == "Anos":
                    receita_hora = (float(valor_honorario_num*12)/float(total_de_horas))
                else:
                    receita_hora = (float(valor_honorario_num)/float(total_de_horas))
                lucro_hora = receita_hora - total_custo
                st.header(f'Receita por hora: {formata_valor(receita_hora)}')
                st.header(f'Resultado por hora: {formata_valor(lucro_hora)}')
        with col_res2:
            with st.container(border=True):
                st.header(f'Percentual de resultado: {round((lucro_hora/receita_hora),2)*100}%')

        st.write(f"Bases de Cálculo: ")
        if opt_datas == "Anos":
            st.write(f'Honorário: {formata_valor(valor_honorario_num*12)}')
        else:
            st.write(f'Honorário: {formata_valor(valor_honorario_num)}')
        st.write(f'Horas trabalhadas por funcionario:')
        with st.expander("Funcionários"):
            st.write(tempo_agrupado_empresa)
        st.divider()


    except Exception as e:
        st.info(f"Insira o código de uma empresa {e}")
else:
    st.error("Credenciais inválidas")