import streamlit as st
import pandas as pd
import mysql.connector
import decimal
import numpy as np

def gerar_df_phoenix(base_luck, request_select):
    
    config = {
        'user': 'user_automation_jpa', 
        'password': 'luck_jpa_2024', 
        'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com', 
        'database': base_luck
        }

    conexao = mysql.connector.connect(**config)

    cursor = conexao.cursor()

    request_name = request_select

    cursor.execute(request_name)

    resultado = cursor.fetchall()
    
    cabecalho = [desc[0] for desc in cursor.description]

    cursor.close()

    conexao.close()

    df = pd.DataFrame(resultado, columns=cabecalho)

    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)

    return df

st.title('Comissões Hoteis')

st.divider()

if not 'df_comissoes_hoteis' in st.session_state:

    with st.spinner('Carregando dados do Phoenix...'):

        st.session_state.df_comissoes_hoteis = gerar_df_phoenix('test_phoenix_maceio', 'SELECT * FROM vw_comissoes_hoteis')

        st.session_state.df_comissoes_hoteis['Data_Venda'] = pd.to_datetime(st.session_state.df_comissoes_hoteis['Data_Venda']).dt.date

        st.session_state.df_comissoes_hoteis['Canal_de_Vendas'] = st.session_state.df_comissoes_hoteis['Canal_de_Vendas'].fillna('')

        st.session_state.df_comissoes_hoteis['Valor_Reembolso'] = st.session_state.df_comissoes_hoteis['Valor_Reembolso'].fillna(0)

row_filtros = st.columns(5)

st.divider()

with row_filtros[0]:

    data_inicio = st.date_input('Data Inicial', format='DD/MM/YYYY', value=None)

with row_filtros[1]:

    data_fim = st.date_input('Data Final', format='DD/MM/YYYY', value=None)

if data_inicio and data_fim:

    df_filtrado = st.session_state.df_comissoes_hoteis[(st.session_state.df_comissoes_hoteis['Data_Venda'] >= data_inicio) & 
                                                       (st.session_state.df_comissoes_hoteis['Data_Venda'] <= data_fim)].reset_index(drop=True)
    
    df_filtrado['Hotel'] = np.where(df_filtrado['Estabelecimento_Origem'].str.contains('AEROPORTO'), df_filtrado['Estabelecimento_Destino'], 
                                    df_filtrado['Estabelecimento_Origem'])

    with row_filtros[2]:

        filtro_cv = st.multiselect('Canal de Vendas', sorted(df_filtrado['Canal_de_Vendas'].dropna().unique()), default=None)

        if filtro_cv:

            df_filtrado = df_filtrado[df_filtrado['Canal_de_Vendas'].isin(filtro_cv)].reset_index(drop=True)

    with row_filtros[3]:

        filtro_vendedor = st.multiselect('Vendedor', sorted(df_filtrado['Vendedor'].dropna().unique()), default=None)

        if filtro_vendedor:

            df_filtrado = df_filtrado[df_filtrado['Vendedor'].isin(filtro_vendedor)].reset_index(drop=True)

    with row_filtros[4]:

        filtro_hotel = st.multiselect('Hotel', sorted(df_filtrado['Hotel'].dropna().unique()), default=None)

        if filtro_hotel:

            df_filtrado = df_filtrado[df_filtrado['Hotel'].isin(filtro_hotel)].reset_index(drop=True)

    df_filtrado['Venda Líquida de Reembolso'] = df_filtrado['Valor_Venda'] - df_filtrado['Valor_Reembolso']

    df_filtrado = df_filtrado[['Data_Venda', 'Reserva', 'Vendedor', 'Canal_de_Vendas', 'Servico', 'Valor_Venda', 'Valor_Reembolso', 'Venda Líquida de Reembolso', 
                               'Hotel']]
    
    df_filtrado.rename(columns={'Data_Venda': 'Data da Venda', 'Canal_de_Vendas': 'Canal de Vendas', 'Servico': 'Serviço', 
                                'Valor_Venda': 'Venda Líquida de Desconto', 'Valor_Reembolso': 'Reembolso'}, inplace=True)

    st.dataframe(df_filtrado, hide_index=True, use_container_width=True)
