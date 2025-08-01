# app.py

import streamlit as st
import pandas as pd
import random
from faker import Faker
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
# Usar st.set_page_config() como o primeiro comando do Streamlit
st.set_page_config(
    page_title="Dashboard de Análise de Alunos",
    page_icon="🎓",
    layout="wide"
)

# --- FUNÇÕES COM CACHE ---
# O cache faz com que as funções pesadas rodem apenas uma vez.
@st.cache_data
def gerar_dados():
    """Gera um DataFrame com dados fictícios de 540 alunos."""
    time.sleep(2) # Simula um carregamento de dados
    fake = Faker('pt_BR')
    ruas_sao_mateus = [
        "Avenida Mateo Bei", "Avenida Ragueb Chohfi", "Avenida Aricanduva", "Avenida Maria Cursi",
        "Rua Professor João de Oliveira Torres", "Rua Forte do Rio Negro", "Rua Dr. Felice Buscaglia",
        "Rua Senador Amaral Furlan", "Rua Baixada de Santa Cruz", "Rua Vintém de Prata"
    ]
    dados_alunos = []
    for serie in [f"{i}º ano" for i in range(1, 10)]:
        for turma in ['A', 'B', 'C']:
            for i in range(1, 21):
                dados_alunos.append({
                    'Nome': fake.name(), 'Série': serie, 'Turma': turma,
                    'Endereço': f"{random.choice(ruas_sao_mateus)}, {random.randint(50, 2000)}, São Mateus, São Paulo - SP",
                    'Média': round(random.uniform(3.0, 10.0), 1)
                })
    df = pd.DataFrame(dados_alunos)
    # Adicionando colunas de coordenadas vazias para preencher depois
    df['lat'] = None
    df['lon'] = None
    return df

@st.cache_data
def geocodificar_enderecos(df):
    """Converte endereços em coordenadas. Apenas para demonstração, pois é muito lento."""
    # NOTA: A geocodificação real de 540 endereços é muito lenta para um app web.
    # Em um projeto real, os dados já viriam com lat/lon do banco de dados
    # ou seriam processados offline. Aqui, vamos simular com coordenadas aleatórias
    # na região de São Mateus para que o app seja rápido.
    for index, row in df.iterrows():
        df.at[index, 'lat'] = random.uniform(-23.605, -23.585)
        df.at[index, 'lon'] = random.uniform(-46.475, -46.445)
    return df

def obter_cor_da_nota(media):
    """Retorna uma cor em formato RGB para a nota."""
    if media >= 7.0:
        return [0, 200, 0]    # Verde
    elif media >= 5.0:
        return [255, 165, 0] # Laranja
    else:
        return [255, 0, 0]     # Vermelho

# --- TÍTULO E INTRODUÇÃO ---
st.title("🎓 Dashboard de Análise de Alunos")
st.write("Use os filtros na barra lateral para explorar os dados dos alunos.")

# --- CARREGAMENTO DOS DADOS ---
with st.spinner("Gerando e processando dados dos alunos... Isso pode levar um momento na primeira vez."):
    df_original = gerar_dados()
    df_geocodificado = geocodificar_enderecos(df_original)
    df_geocodificado['cor'] = df_geocodificado['Média'].apply(obter_cor_da_nota)

# --- BARRA LATERAL COM FILTROS (SIDEBAR) ---
st.sidebar.header("Filtros")
filtro_serie = st.sidebar.multiselect(
    "Selecione a Série:",
    options=df_geocodificado['Série'].unique(),
    default=df_geocodificado['Série'].unique()
)

filtro_media = st.sidebar.slider(
    "Selecione a faixa de Média:",
    min_value=0.0,
    max_value=10.0,
    value=(0.0, 10.0) # Um slider de intervalo
)

# Aplicando os filtros ao DataFrame
df_filtrado = df_geocodificado[
    (df_geocodificado['Série'].isin(filtro_serie)) &
    (df_geocodificado['Média'].between(filtro_media[0], filtro_media[1]))
]

# --- LAYOUT PRINCIPAL COM MÉTRICAS, GRÁFICOS E MAPA ---
# Métricas principais
total_alunos = len(df_filtrado)
media_geral = round(df_filtrado['Média'].mean(), 2) if total_alunos > 0 else 0

col1, col2 = st.columns(2)
col1.metric("Total de Alunos Selecionados", f"{total_alunos}")
col2.metric("Média Geral do Grupo", f"{media_geral}")

st.markdown("---")

# Mapa e Tabela de dados
st.header("🗺️ Distribuição Geográfica e Dados dos Alunos")
st.map(df_filtrado, latitude='lat', longitude='lon', color='cor', size=30)
st.write("A legenda de cores do mapa é: Verde (>=7), Laranja (>=5), Vermelho (<5).")

with st.expander("Ver tabela de dados dos alunos selecionados"):
    st.dataframe(df_filtrado[['Nome', 'Série', 'Turma', 'Média']].sort_values('Média', ascending=False))