# %%
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

# ==============================================================================
# IMPORTAÇÕES DE FUNÇÕES E DADOS
# ==============================================================================
from src.views.home import show_page_home
from src.views.emprego import show_page_emprego
from src.views.comercio_exterior import show_page_comex
from src.views.seguranca import show_page_seguranca
from src.views.assistencia_social import show_page_assistencia_social
from src.views.financas import show_page_financas
from src.views.empresas_ativas import show_page_empresas_ativas
from src.views.educacao import show_page_educacao
from src.views.saude import show_page_saude


from src.utils import carregar_css
from src.utils import manter_posicao_scroll

from src.data_loader import (
    carregar_dados_comex_mensal,
    carregar_dados_emprego_municipios,
    carregar_dados_emprego_cnae,
    carregar_dados_emprego_faixa_etaria,
    carregar_dados_emprego_raca_cor,
    carregar_dados_emprego_grau_instrucao,
    carregar_dados_emprego_sexo,
    carregar_dados_comex_anual,
    carregar_dados_comex_municipio,
    carregar_dados_siconfi_rreo,
    carregar_dados_seguranca,
    carregar_dados_seguranca_taxa,
    carregar_dados_CAD,
    carregar_dados_bolsa_familia,
    carregar_dados_cnpj_total,
    carregar_dados_cnpj_cnae,
    carregar_dados_mei_total,
    carregar_dados_mei_cnae,
    carregar_dados_educacao_matriculas,
    carregar_dados_educacao_rendimento,
    carregar_dados_educacao_ideb_escolas,
    carregar_dados_educacao_ideb_municipio,
    carregar_dados_saude_mensal,
)
from src.config import (
    municipio_de_interesse,
    municipios_de_interesse,
    anos_de_interesse,
    anos_comex,
    CORES_MUNICIPIOS,
)

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(layout="wide", page_title="Dashboard CEI ", page_icon="📊")
carregar_css("assets/style.css")

# ==============================================================================
# INICIALIZAÇÃO DO SESSION STATE
# ==============================================================================
if "emprego_expander_state" not in st.session_state:
    st.session_state.emprego_expander_state = False


# ==============================================================================
# CARREGAMENTO DE DADOS
# ==============================================================================

# Emprego
df_caged = carregar_dados_emprego_municipios(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)
df_caged_cnae = carregar_dados_emprego_cnae(
    municipio=municipio_de_interesse, anos=anos_de_interesse
)

df_caged_faixa_etaria = carregar_dados_emprego_faixa_etaria(
    municipio=municipio_de_interesse, anos=anos_de_interesse
)

df_caged_grau_instrucao = carregar_dados_emprego_grau_instrucao(
    municipio=municipio_de_interesse, anos=anos_de_interesse
)

df_caged_raca_cor = carregar_dados_emprego_raca_cor(
    municipio=municipio_de_interesse, anos=anos_de_interesse
)

df_caged_sexo = carregar_dados_emprego_sexo(
    municipio=municipio_de_interesse, anos=anos_de_interesse
)
# Comércio Exterior
df_comex_ano = carregar_dados_comex_anual(
    municipios=municipios_de_interesse, anos=anos_comex
)

df_comex_mensal = carregar_dados_comex_mensal(
    municipios=municipios_de_interesse, anos=anos_comex
)

df_comex_municipio = carregar_dados_comex_municipio(
    municipio=municipio_de_interesse, anos=anos_comex
)

df_siconfi_rreo = carregar_dados_siconfi_rreo()

df_seguranca = carregar_dados_seguranca(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

df_seguranca_taxa = carregar_dados_seguranca_taxa(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

df_cad = carregar_dados_CAD(municipios=municipios_de_interesse, anos=anos_de_interesse)

df_bolsa_familia = carregar_dados_bolsa_familia(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

df_cnpj_total = carregar_dados_cnpj_total(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

df_cnpj_cnae = carregar_dados_cnpj_cnae(
    municipio=municipio_de_interesse, anos=anos_de_interesse
)

df_mei_total = carregar_dados_mei_total(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

df_mei_cnae = carregar_dados_mei_cnae(
    municipio=municipio_de_interesse, anos=anos_de_interesse
)

df_educacao_matriculas = carregar_dados_educacao_matriculas(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

df_educacao_rendimento = carregar_dados_educacao_rendimento(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

df_educacao_ideb_municipio = carregar_dados_educacao_ideb_municipio(
    municipios=municipios_de_interesse
)

df_educacao_ideb_escolas = carregar_dados_educacao_ideb_escolas(
    municipios=municipios_de_interesse
)

df_saude_mensal = carregar_dados_saude_mensal(
    municipios=municipios_de_interesse, anos=anos_de_interesse
)

# ==============================================================================
# BARRA LATERAL E NAVEGAÇÃO ENTRE PÁGINAS
# ==============================================================================

municipios_para_comparacao = [
    m for m in municipios_de_interesse if m != municipio_de_interesse
]

with st.sidebar:
    st.title("Filtros Globais")

    cor_foco = CORES_MUNICIPIOS.get(municipio_de_interesse, "#888888")

    st.markdown(
        f"""
        <label style="font-size: 14px; color: rgba(255, 255, 255, 0.6);">Município Principal:</label>
        <div style="
            background-color: {cor_foco}; 
            color: white; 
            padding: 8px 12px; 
            border-radius: 8px; 
            font-weight: 600;
            margin-bottom: 10px;
        ">
            {municipio_de_interesse}
        </div>
        """,
        unsafe_allow_html=True,
    )

    municipios_comparados = st.multiselect(
        "Adicionar municípios para comparação:",
        options=municipios_para_comparacao,
        # Você pode escolher um default se quiser, ou deixar vazio
        default=municipios_para_comparacao,
    )
    municipios_selecionados_global = [municipio_de_interesse] + municipios_comparados

    st.markdown("---")
    pagina_selecionada = option_menu(
        menu_title="Menu",
        options=[
            "Início",
            "Emprego",
            "Empresas Ativas",
            "Comércio Exterior",
            "Segurança",
            "Assistência Social",
            "Educação",
            "Saúde",
            "Finanças",
        ],
        icons=[
            "house-door-fill",
            "briefcase-fill",
            "building-fill",
            "globe2",
            "shield-shaded",
            "people-fill",
            "mortarboard-fill",
            "mortarboard-fill",
            "piggy-bank-fill",
        ],
        menu_icon="cast",
        default_index=0,
    )

    # ==============================================================================
# FILTRAGEM GLOBAL DOS DADOS
# ==============================================================================

df_caged_filtrado = df_caged[df_caged["municipio"].isin(municipios_selecionados_global)]
df_caged_cnae_filtrado = df_caged_cnae[
    df_caged_cnae["municipio"].isin(municipios_selecionados_global)
]
df_caged_sexo_filtrado = df_caged_sexo[
    df_caged_sexo["municipio"].isin(municipios_selecionados_global)
]
df_caged_faixa_etaria_filtrado = df_caged_faixa_etaria[
    df_caged_faixa_etaria["municipio"].isin(municipios_selecionados_global)
]
df_caged_grau_instrucao_filtrado = df_caged_grau_instrucao[
    df_caged_grau_instrucao["municipio"].isin(municipios_selecionados_global)
]
df_caged_raca_cor_filtrado = df_caged_raca_cor[
    df_caged_raca_cor["municipio"].isin(municipios_selecionados_global)
]
df_comex_ano_filtrado = df_comex_ano[
    df_comex_ano["municipio"].isin(municipios_selecionados_global)
]
df_comex_mensal_filtrado = df_comex_mensal[
    df_comex_mensal["municipio"].isin(municipios_selecionados_global)
]
df_seguranca_filtrado = df_seguranca[
    df_seguranca["municipio"].isin(municipios_selecionados_global)
]
df_seguranca_taxa_filtrado = df_seguranca_taxa[
    df_seguranca_taxa["municipio"].isin(municipios_selecionados_global)
]
df_siconfi_filtrado = df_siconfi_rreo[
    df_siconfi_rreo["municipio"].isin(municipios_selecionados_global)
]
df_cad_filtrado = df_cad[df_cad["municipio"].isin(municipios_selecionados_global)]

df_bolsa_familia_filtrado = df_bolsa_familia[
    df_bolsa_familia["municipio"].isin(municipios_selecionados_global)
]

df_cnpj_total_filtrado = df_cnpj_total[
    df_cnpj_total["municipio"].isin(municipios_selecionados_global)
]

df_mei_total_filtrado = df_mei_total[
    df_mei_total["municipio"].isin(municipios_selecionados_global)
]
df_cnpj_cnae_filtrado = df_cnpj_cnae[
    df_cnpj_cnae["municipio"].isin(municipios_selecionados_global)
]
df_mei_cnae_filtrado = df_mei_cnae[
    df_mei_cnae["municipio"].isin(municipios_selecionados_global)
]

df_educacao_rendimento_filtrado = df_educacao_rendimento[
    df_educacao_rendimento["municipio"].isin(municipios_selecionados_global)
]

df_educacao_matriculas_filtrado = df_educacao_matriculas[
    df_educacao_matriculas["municipio"].isin(municipios_selecionados_global)
]

df_educacao_ideb_municipio_filtrado = df_educacao_ideb_municipio[
    df_educacao_ideb_municipio["municipio"].isin(municipios_selecionados_global)
]

df_educacao_ideb_escolas_filtrado = df_educacao_ideb_escolas[
    df_educacao_ideb_escolas["municipio"].isin(municipios_selecionados_global)
]

df_saude_mensal_filtrado = df_saude_mensal[
    df_saude_mensal["municipio"].isin(municipios_selecionados_global)
]
# ==============================================================================
# PÁGINAS
# ==============================================================================
if pagina_selecionada == "Início":
    show_page_home(
        df_emprego=df_caged_filtrado,
        df_comex=df_comex_mensal_filtrado,
        df_seguranca=df_seguranca_filtrado,
        df_assistencia_cad=df_cad_filtrado,
        df_assistencia_bolsa=df_bolsa_familia_filtrado,
        df_financas=df_siconfi_filtrado,
        df_empresas=df_cnpj_total_filtrado,
        df_educacao_ideb=df_educacao_ideb_municipio_filtrado,
        df_educacao_matriculas=df_educacao_matriculas_filtrado,
    )
if pagina_selecionada == "Emprego":
    show_page_emprego(
        df_caged=df_caged_filtrado,
        df_caged_cnae=df_caged_cnae_filtrado,
        df_caged_faixa_etaria=df_caged_faixa_etaria_filtrado,
        df_caged_grau_instrucao=df_caged_grau_instrucao_filtrado,
        df_caged_raca_cor=df_caged_raca_cor_filtrado,
        df_caged_sexo=df_caged_sexo_filtrado,
        municipio_de_interesse=municipio_de_interesse,
    )

elif pagina_selecionada == "Empresas Ativas":
    show_page_empresas_ativas(
        df_cnpj=df_cnpj_total_filtrado,
        df_cnpj_cnae=df_cnpj_cnae_filtrado,
        df_mei=df_mei_total_filtrado,
        df_mei_cnae=df_mei_cnae_filtrado,
        municipio_de_interesse=municipio_de_interesse,
    )

elif pagina_selecionada == "Comércio Exterior":
    show_page_comex(
        df_comex_ano_filtrado,
        df_comex_mensal_filtrado,
        df_comex_municipio,
        municipios_selecionados_global,
        municipio_de_interesse,
    )

elif pagina_selecionada == "Segurança":
    show_page_seguranca(df_seguranca_filtrado, df_seguranca_taxa_filtrado)

elif pagina_selecionada == "Assistência Social":
    show_page_assistencia_social(
        df_cad=df_cad_filtrado,
        df_bolsa=df_bolsa_familia_filtrado,
        municipio_interesse=municipio_de_interesse,
    )

elif pagina_selecionada == "Educação":
    show_page_educacao(
        df_matriculas=df_educacao_matriculas_filtrado,
        df_rendimento=df_educacao_rendimento_filtrado,
        df_ideb_municipio=df_educacao_ideb_municipio_filtrado,
        df_ideb_escolas=df_educacao_ideb_escolas_filtrado,
        municipios_selecionados_global=municipios_selecionados_global,
    )

elif pagina_selecionada == "Saúde":
    show_page_saude(df_saude_mensal=df_saude_mensal_filtrado)

elif pagina_selecionada == "Finanças":
    show_page_financas(df_siconfi_filtrado, municipio_de_interesse)

manter_posicao_scroll()

# %%
