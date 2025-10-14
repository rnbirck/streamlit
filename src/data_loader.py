import streamlit as st
import pandas as pd

# ID PLANILHAS GOOGLE SHEETS
ID_EMPREGO_MUNICIPIOS = "1R-ehxIUZnRZLetEL0b2SgvkK-YQdtBBl1ff_dtgAYpg"
ID_EMPREGO_CNAE = "1scPanyLdRKBLkWSwhxQiZryS1wVinfQ6vCqZakbkDmg"
ID_EMPREGO_GRAU_INSTRUCAO = "1WlBPJMbgMkAReFFeraqhHPHeIMA0oPoJ3A2d7sF52ns"
ID_EMPREGO_FAIXA_ETARIA = "18vXZaCkc8so4rO5jUN9XKzJDdumPCm7RdaVNmIBAFQ0"
ID_EMPREGO_RACA_COR = "10aStpcwC9qG8SGHIuloLxVaW_uCJR6TfGsnckPkeA5E"
ID_EMPREGO_SEXO = "1qwztnxdlIsK7DaIqbCNcFmTbFf9GR6ARJCgT00wE83o"
ID_COMEX_ANUAL = "1j4Xx0_PPHwDDvC9ybKhcbBovk3HpXUGVKnBfS5JxxEo"
ID_COMEX_MENSAL = "1I_d1n1KoU3VbHr5FVCX7oGp6VezgAgQQVvMnTFApbRU"
ID_COMEX_MUNICIPIO = "1DC89QdcB5GxuZgZamHH8xOSlp-BP_5oayKa5jsjl2c8"
ID_SICONFI_RREO = "1zGPeIXTfikqDN_n_-EGy0UZYCmeLTqZYGrx4TwpepO0"
ID_SEGURANCA = "1cPzaMIrHk-T5oJQKPxlFepHf63_-nQjHIFTf2xZzsog"
ID_SEGURANCA_TAXA = "1GUiqyYyXVleSNfkhdi0R36EFTAGw_hafeKylmMDRb4c"
ID_CAD = "15TiAHgFeM2gJ6NARrDfezJRRJt-TY64ksN4l7MMMrQE"
ID_BOLSA_FAMILIA = "1xuBjiv3in12U_xrdScGExMXTjfOlt3-shK_FiVT9E0o"
ID_CNPJ_TOTAL = "1S34HnK0wG4h9ifWnm066RQsubEMsrN5y6ZsHI8yvd_s"
ID_CNPJ_CNAE = "1LlGELAUNFBAg3gIKyZjJ5tE1VfQVAr5tqzGBVtvwLXg"
ID_MEI_TOTAL = "1x4gKWVJNOo13hH-2AchgrA6YIntZJphOlOjhhCDrO5s"
ID_MEI_CNAE = "1IaWCby0TmW-h9vBmqhvjZm-8CwayYAFS5xCVz_TeQLM"
ID_EDUCACAO_MATRICULAS = "1V2_LK6KmHWRS9G3dTDuvyseH4VK51V_h-WqyKo1vC2g"
ID_EDUCACAO_RENDIMENTO = "1eXvWso6qsqhAxuIp3_LJ8mxIDtuhnMhGFOgx_wB-G4E"
ID_EDUCACAO_IDEB_MUNICIPIOS = "1hRIaMp9NUkEJuv8-1B3o4tnBokPMecFlAUO_43eyEBI"
ID_EDUCACAO_IDEB_ESCOLAS = "1ckSLZvqznbCOcgNEnah3UGW5L4nraIU24RRKF79JKIg"
ID_SAUDE_MENSAL = "1zxQ37QD7zmLR-dZhsjtYG-ihpMhD9Pr1gxyX5ZDS2hA"


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
def carregar_dados_emprego_grau_instrucao(municipio, anos):
    url = construir_url_gsheet(ID_EMPREGO_GRAU_INSTRUCAO)
    df = pd.read_csv(url)
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_emprego_faixa_etaria(municipio, anos):
    url = construir_url_gsheet(ID_EMPREGO_FAIXA_ETARIA)
    df = pd.read_csv(url)
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_emprego_raca_cor(municipio, anos):
    url = construir_url_gsheet(ID_EMPREGO_RACA_COR)
    df = pd.read_csv(url)
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_emprego_sexo(municipio, anos):
    url = construir_url_gsheet(ID_EMPREGO_SEXO)
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


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_seguranca(municipios, anos):
    """Lê os dados de seguranca da planilha Google."""
    url = construir_url_gsheet(ID_SEGURANCA)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_seguranca_taxa(municipios, anos):
    """Lê os dados de taxa de seguranca da planilha Google."""
    url = construir_url_gsheet(ID_SEGURANCA_TAXA)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_CAD(municipios, anos):
    """Lê os dados do cadastro único da planilha Google."""
    url = construir_url_gsheet(ID_CAD)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_bolsa_familia(municipios, anos):
    """Lê os dados do novo bolsa família da planilha Google."""
    url = construir_url_gsheet(ID_BOLSA_FAMILIA)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_cnpj_total(municipios, anos):
    """Lê os dados de CNPJ total da planilha Google."""
    url = construir_url_gsheet(ID_CNPJ_TOTAL)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_cnpj_cnae(municipio, anos):
    """Lê os dados de CNPJ CNAE da planilha Google."""
    url = construir_url_gsheet(ID_CNPJ_CNAE)
    df = pd.read_csv(url)
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_mei_total(municipios, anos):
    """Lê os dados de MEI total da planilha Google."""
    url = construir_url_gsheet(ID_MEI_TOTAL)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_mei_cnae(municipio, anos):
    """Lê os dados de MEI CNAE da planilha Google."""
    url = construir_url_gsheet(ID_MEI_CNAE)
    df = pd.read_csv(url)
    return df[(df["municipio"] == municipio) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_educacao_matriculas(municipios, anos):
    """Lê os dados de Educacao Matriculas da planilha Google."""
    url = construir_url_gsheet(ID_EDUCACAO_MATRICULAS)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_educacao_rendimento(municipios, anos):
    """Lê os dados de Educacao Rendimento da planilha Google."""
    url = construir_url_gsheet(ID_EDUCACAO_RENDIMENTO)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_educacao_ideb_municipio(municipios):
    """Lê os dados de Educacao de IDEB Municipio da planilha Google."""
    url = construir_url_gsheet(ID_EDUCACAO_IDEB_MUNICIPIOS)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_educacao_ideb_escolas(municipios):
    """Lê os dados de Educacao de IDEB Escola da planilha Google."""
    url = construir_url_gsheet(ID_EDUCACAO_IDEB_ESCOLAS)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios))]


@st.cache_data(ttl=CACHE_TTL)
def carregar_dados_saude_mensal(municipios, anos):
    """Lê os dados de Saúde Mensal da planilha Google."""
    url = construir_url_gsheet(ID_SAUDE_MENSAL)
    df = pd.read_csv(url)
    return df[(df["municipio"].isin(municipios)) & (df["ano"].isin(anos))]
