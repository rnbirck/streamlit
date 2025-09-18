import streamlit as st
import pandas as pd

# ID PLANILHAS GOOGLE SHEETS
ID_EMPREGO_MUNICIPIOS = "1R-ehxIUZnRZLetEL0b2SgvkK-YQdtBBl1ff_dtgAYpg"
ID_EMPREGO_CNAE = "1scPanyLdRKBLkWSwhxQiZryS1wVinfQ6vCqZakbkDmg"
ID_COMEX_ANUAL = "1j4Xx0_PPHwDDvC9ybKhcbBovk3HpXUGVKnBfS5JxxEo"
ID_COMEX_MENSAL = "1I_d1n1KoU3VbHr5FVCX7oGp6VezgAgQQVvMnTFApbRU"
ID_COMEX_MUNICIPIO = "1DC89QdcB5GxuZgZamHH8xOSlp-BP_5oayKa5jsjl2c8"
ID_SICONFI_RREO = "1zGPeIXTfikqDN_n_-EGy0UZYCmeLTqZYGrx4TwpepO0"


def construir_url_gsheet(sheet_id):
    """Constrói o URL de exportação CSV para uma planilha do Google Sheets."""
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"


CACHE_TTL = 86400  # 24 horas


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_emprego_municipios(municipios, anos):
    url = construir_url_gsheet(ID_EMPREGO_MUNICIPIOS)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_emprego_cnae(municipio, anos):
    url = construir_url_gsheet(ID_EMPREGO_CNAE)
    df = pd.read_csv(url)
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_comex_anual(municipios, anos):
    url = construir_url_gsheet(ID_COMEX_ANUAL)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_comex_mensal(municipios, anos):
    url = construir_url_gsheet(ID_COMEX_MENSAL)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_comex_municipio(municipio, anos):
    url = construir_url_gsheet(ID_COMEX_MUNICIPIO)
    df = pd.read_csv(url)
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_siconfi_rreo():
    """Lê os dados do SICONFI da planilha Google."""
    url = construir_url_gsheet(ID_SICONFI_RREO)
    df = pd.read_csv(url)
    return df
