import streamlit as st
import pandas as pd


@st.cache_data
def carregar_dados_emprego_municipios(municipios, anos):
    """Lê os dados de emprego do arquivo CSV e filtra."""
    df = pd.read_csv("data/emprego/caged_municipios.csv", engine="pyarrow")
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data
def carregar_dados_emprego_cnae(municipio, anos):
    """Lê os dados de emprego por CNAE do arquivo CSV e filtra."""
    df = pd.read_csv("data/emprego/caged_cnae.csv", engine="pyarrow")
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data
def carregar_dados_comex_anual(municipios, anos):
    """Lê os dados de comex anual do arquivo CSV e filtra."""
    df = pd.read_csv("data/comex/comex_anual.csv", engine="pyarrow")
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data
def carregar_dados_comex_mensal(municipios, anos):
    """Lê os dados de comex mensal do arquivo CSV e filtra."""
    df = pd.read_csv("data/comex/comex_mensal.csv", engine="pyarrow")
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data
def carregar_dados_comex_municipio(municipio, anos):
    """Lê os dados de comex do município selecionado do arquivo CSV e filtra."""
    df = pd.read_csv("data/comex/comex_municipio.csv", engine="pyarrow")
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]
