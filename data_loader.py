import streamlit as st
import pandas as pd
from sqlalchemy import text
from queries import (
    QUERY_EMPREGO_MUNICIPIOS,
    QUERY_EMPREGO_CNAE,
    QUERY_EXP_ANUAL,
    QUERY_EXP_MENSAL,
    QUERY_EXP_MUN_SELECIONADO,
)


@st.cache_data
def carregar_dados_emprego_municipios(_engine, municipios, anos):
    """Executa a query de emprego para os municípios selecionados."""
    return pd.read_sql_query(
        text(QUERY_EMPREGO_MUNICIPIOS),
        _engine,
        params={"lista_municipios": tuple(municipios), "lista_anos": tuple(anos)},
    )


@st.cache_data
def carregar_dados_emprego_cnae(_engine, municipio, anos):
    """Executa a query de emprego por CNAE para os municípios selecionados."""
    return pd.read_sql_query(
        text(QUERY_EMPREGO_CNAE),
        _engine,
        params={"municipio": municipio, "lista_anos": tuple(anos)},
    )


@st.cache_data
def carregar_dados_comex_anual(_engine, municipios, anos):
    """Executa a query de comércio exterior anual para os municípios selecionados."""
    return pd.read_sql_query(
        text(QUERY_EXP_ANUAL),
        _engine,
        params={"lista_municipios": tuple(municipios), "lista_anos": tuple(anos)},
    )


@st.cache_data
def carregar_dados_comex_mensal(_engine, municipios, anos):
    """Executa a query de comércio exterior mensal para os municípios selecionados."""
    return pd.read_sql_query(
        text(QUERY_EXP_MENSAL),
        _engine,
        params={"lista_municipios": tuple(municipios), "lista_anos": tuple(anos)},
    )


@st.cache_data
def carregar_dados_comex_municipio(_engine, municipio, anos):
    """Executa a query de comércio exterior mensal para os municípios selecionados."""
    return pd.read_sql_query(
        text(QUERY_EXP_MUN_SELECIONADO),
        _engine,
        params={"municipio": municipio, "lista_anos": tuple(anos)},
    )
