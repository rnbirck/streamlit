# %%
import streamlit as st
from streamlit_option_menu import option_menu

# ==============================================================================
# IMPORTAÇÕES DAS PÁGINAS (VIEWS)
# ==============================================================================
from src.views.home import show_page_home
from src.views.emprego import show_page_emprego
from src.views.comercio_exterior import show_page_comex
from src.views.seguranca import show_page_seguranca
from src.views.assistencia_social import show_page_assistencia_social
from src.views.financas import show_page_financas
from src.views.empresas import show_page_empresas_ativas
from src.views.educacao import show_page_educacao
from src.views.saude import show_page_saude
from src.views.pib import show_page_pib
from src.views.demografia import show_page_demografia


from src.utils import carregar_css
from src.utils import manter_posicao_scroll

# ==============================================================================
# IMPORTAÇÕES DOS DATA LOADERS
# ==============================================================================
from src.data_loader import (
    # Loaders Essenciais (para a Página Início)
    carregar_dados_emprego_municipios,
    carregar_dados_vinculos_municipios,
    carregar_dados_comex_mensal,
    carregar_dados_seguranca,
    carregar_dados_CAD,
    carregar_dados_bolsa_familia,
    carregar_dados_financas,
    carregar_dados_indicadores_financeiros,
    carregar_pdf_indicadores_financeiros,
    carregar_dados_cnpj_total,
    carregar_dados_educacao_matriculas,
    carregar_dados_educacao_ideb_municipio,
    carregar_dados_pib_municipios,
    carregar_dados_saude_mensal,
    carregar_dados_populacao_densidade,
    carregar_dados_populacao_sexo_idade,
    # Loaders Secundários (serão chamados depois)
    carregar_dados_emprego_cnae,
    carregar_dados_emprego_faixa_etaria,
    carregar_dados_emprego_raca_cor,
    carregar_dados_emprego_grau_instrucao,
    carregar_dados_emprego_sexo,
    carregar_dados_vinculos_cnae,
    carregar_dados_vinculos_sexo,
    carregar_dados_vinculos_faixa_etaria,
    carregar_dados_vinculos_grau_instrucao,
    carregar_dados_vinculos_raca_cor,
    carregar_dados_renda_municipios,
    carregar_dados_renda_cnae,
    carregar_dados_renda_sexo,
    carregar_dados_estabelecimentos_municipios,
    carregar_dados_estabelecimentos_cnae,
    carregar_dados_estabelecimentos_tamanho,
    carregar_dados_comex_anual,
    carregar_dados_comex_municipio,
    carregar_dados_seguranca_taxa,
    carregar_dados_cnpj_cnae,
    carregar_dados_mei_total,
    carregar_dados_mei_cnae,
    carregar_dados_educacao_rendimento,
    carregar_dados_educacao_ideb_escolas,
    carregar_dados_saude_despesas,
    carregar_dados_saude_leitos,
    carregar_dados_saude_medicos,
    carregar_dados_saude_vacinas,
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
# Flags para controlar o carregamento lazy de cada página
if "emprego_dados_carregados" not in st.session_state:
    st.session_state.emprego_dados_carregados = False
if "empresas_dados_carregados" not in st.session_state:
    st.session_state.empresas_dados_carregados = False
if "comex_dados_carregados" not in st.session_state:
    st.session_state.comex_dados_carregados = False
if "seguranca_dados_carregados" not in st.session_state:
    st.session_state.seguranca_dados_carregados = False
if "educacao_dados_carregados" not in st.session_state:
    st.session_state.educacao_dados_carregados = False
if "saude_dados_carregados" not in st.session_state:
    st.session_state.saude_dados_carregados = False
if "emprego_expander_state" not in st.session_state:
    st.session_state.emprego_expander_state = False

# ==============================================================================
# CARREGAMENTO DE DADOS ESSENCIAIS (PARA PÁGINA INÍCIO)
# ==============================================================================
# Carrega apenas os DFs mínimos necessários para a página 'Início' funcionar
# (para mostrar as datas de atualização)
with st.spinner("Carregando dados essenciais... Por favor, aguarde."):
    df_caged = carregar_dados_emprego_municipios(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_comex_mensal = carregar_dados_comex_mensal(
        municipios=municipios_de_interesse, anos=anos_comex
    )
    df_seguranca = carregar_dados_seguranca(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_cad = carregar_dados_CAD(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_bolsa_familia = carregar_dados_bolsa_familia(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_financas = carregar_dados_financas(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_indicadores_financeiros = carregar_dados_indicadores_financeiros(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    pdf_indicadores = carregar_pdf_indicadores_financeiros()
    df_cnpj_total = carregar_dados_cnpj_total(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_educacao_matriculas = carregar_dados_educacao_matriculas(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_educacao_ideb_municipio = carregar_dados_educacao_ideb_municipio(
        municipios=municipios_de_interesse
    )
    df_vinculos = carregar_dados_vinculos_municipios(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_pib_municipios = carregar_dados_pib_municipios(
        municipios=municipios_de_interesse
    )
    df_saude_mensal = carregar_dados_saude_mensal(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_populacao_densidade = carregar_dados_populacao_densidade(
        municipios=municipios_de_interesse, anos=anos_de_interesse
    )
    df_populacao_sexo_idade = carregar_dados_populacao_sexo_idade(
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
        default=municipios_para_comparacao,
    )
    municipios_selecionados_global = [municipio_de_interesse] + municipios_comparados

    st.markdown("---")
    pagina_selecionada = option_menu(
        menu_title="Menu",
        options=[
            "Início",
            "Emprego",
            "Empresas",
            "Comércio Exterior",
            "Segurança",
            "Assistência Social",
            "Educação",
            "Saúde",
            "PIB",
            "Demografia",
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
            "heart-pulse-fill",
            "graph-up",
            "person-lines-fill",
            "piggy-bank-fill",
        ],
        menu_icon="cast",
        default_index=0,
        key="selected_page",
    )

# ==============================================================================
# FILTRAGEM GLOBAL DOS DADOS ESSENCIAIS
# ==============================================================================
# Filtra apenas os DFs essenciais que são usados em múltiplas páginas

df_caged_filtrado = df_caged[df_caged["municipio"].isin(municipios_selecionados_global)]
df_vinculos_filtrado = df_vinculos[
    df_vinculos["municipio"].isin(municipios_selecionados_global)
]
df_comex_mensal_filtrado = df_comex_mensal[
    df_comex_mensal["municipio"].isin(municipios_selecionados_global)
]
df_seguranca_filtrado = df_seguranca[
    df_seguranca["municipio"].isin(municipios_selecionados_global)
]
df_financas_filtrado = df_financas[
    df_financas["municipio"].isin(municipios_selecionados_global)
]
df_indicadores_financeiros_filtrado = df_indicadores_financeiros[
    df_indicadores_financeiros["municipio"].isin(municipios_selecionados_global)
]
df_cad_filtrado = df_cad[df_cad["municipio"].isin(municipios_selecionados_global)]
df_bolsa_familia_filtrado = df_bolsa_familia[
    df_bolsa_familia["municipio"].isin(municipios_selecionados_global)
]
df_cnpj_total_filtrado = df_cnpj_total[
    df_cnpj_total["municipio"].isin(municipios_selecionados_global)
]
df_educacao_matriculas_filtrado = df_educacao_matriculas[
    df_educacao_matriculas["municipio"].isin(municipios_selecionados_global)
]
df_educacao_ideb_municipio_filtrado = df_educacao_ideb_municipio[
    df_educacao_ideb_municipio["municipio"].isin(municipios_selecionados_global)
]
df_saude_mensal_filtrado = df_saude_mensal[
    df_saude_mensal["municipio"].isin(municipios_selecionados_global)
]
df_pib_municipios_filtrado = df_pib_municipios[
    df_pib_municipios["municipio"].isin(municipios_selecionados_global)
]
df_populacao_densidade_filtrado = df_populacao_densidade[
    df_populacao_densidade["municipio"].isin(municipios_selecionados_global)
]
df_populacao_sexo_idade_filtrado = df_populacao_sexo_idade[
    df_populacao_sexo_idade["municipio"].isin(municipios_selecionados_global)
]


# ==============================================================================
# PÁGINAS (COM CARREGAMENTO HÍBRIDO/LAZY)
# ==============================================================================
placeholder = st.empty()

with placeholder.container():
    # O spinner agora cobre o carregamento 'lazy' de cada página
    with st.spinner(f"A carregar a página de {pagina_selecionada}..."):
        if pagina_selecionada == "Início":
            show_page_home(
                df_emprego=df_caged_filtrado,
                df_comex=df_comex_mensal_filtrado,
                df_seguranca=df_seguranca_filtrado,
                df_assistencia_cad=df_cad_filtrado,
                df_assistencia_bolsa=df_bolsa_familia_filtrado,
                df_financas=df_financas_filtrado,
                df_indicadores_financeiros=df_indicadores_financeiros_filtrado,
                df_empresas=df_cnpj_total_filtrado,
                df_educacao_ideb=df_educacao_ideb_municipio_filtrado,
                df_educacao_matriculas=df_educacao_matriculas_filtrado,
                df_vinculos=df_vinculos_filtrado,
                df_pib=df_pib_municipios_filtrado,
                df_saude_mensal=df_saude_mensal_filtrado,  # Corrigido (passava df_saude_mensal)
                df_populacao_densidade=df_populacao_densidade_filtrado,
                df_populacao_sexo_idade=df_populacao_sexo_idade_filtrado,
            )

        if pagina_selecionada == "Emprego":
            # --- Carregamento Lazy (Dados Secundários de Emprego) ---
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
            df_vinculos_cnae = carregar_dados_vinculos_cnae(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_vinculos_faixa_etaria = carregar_dados_vinculos_faixa_etaria(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_vinculos_grau_instrucao = carregar_dados_vinculos_grau_instrucao(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_vinculos_raca_cor = carregar_dados_vinculos_raca_cor(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_vinculos_sexo = carregar_dados_vinculos_sexo(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_renda = carregar_dados_renda_municipios(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )
            df_renda_cnae = carregar_dados_renda_cnae(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_renda_sexo = carregar_dados_renda_sexo(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )

            # --- Filtragem Lazy (Dados Secundários de Emprego) ---
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
                df_caged_grau_instrucao["municipio"].isin(
                    municipios_selecionados_global
                )
            ]
            df_caged_raca_cor_filtrado = df_caged_raca_cor[
                df_caged_raca_cor["municipio"].isin(municipios_selecionados_global)
            ]
            df_vinculos_cnae_filtrado = df_vinculos_cnae[
                df_vinculos_cnae["municipio"].isin(municipios_selecionados_global)
            ]
            df_vinculos_sexo_filtrado = df_vinculos_sexo[
                df_vinculos_sexo["municipio"].isin(municipios_selecionados_global)
            ]
            df_vinculos_faixa_etaria_filtrado = df_vinculos_faixa_etaria[
                df_vinculos_faixa_etaria["municipio"].isin(
                    municipios_selecionados_global
                )
            ]
            df_vinculos_grau_instrucao_filtrado = df_vinculos_grau_instrucao[
                df_vinculos_grau_instrucao["municipio"].isin(
                    municipios_selecionados_global
                )
            ]
            df_vinculos_raca_cor_filtrado = df_vinculos_raca_cor[
                df_vinculos_raca_cor["municipio"].isin(municipios_selecionados_global)
            ]
            df_renda_filtrado = df_renda[
                df_renda["municipio"].isin(municipios_selecionados_global)
            ]
            df_renda_cnae_filtrado = df_renda_cnae[
                df_renda_cnae["municipio"].isin(municipios_selecionados_global)
            ]
            df_renda_sexo_filtrado = df_renda_sexo[
                df_renda_sexo["municipio"].isin(municipios_selecionados_global)
            ]

            show_page_emprego(
                df_caged=df_caged_filtrado,
                df_caged_cnae=df_caged_cnae_filtrado,
                df_caged_faixa_etaria=df_caged_faixa_etaria_filtrado,
                df_caged_grau_instrucao=df_caged_grau_instrucao_filtrado,
                df_caged_raca_cor=df_caged_raca_cor_filtrado,
                df_caged_sexo=df_caged_sexo_filtrado,
                municipio_de_interesse=municipio_de_interesse,
                df_vinculos=df_vinculos_filtrado,
                df_vinculos_cnae=df_vinculos_cnae_filtrado,
                df_vinculos_faixa_etaria=df_vinculos_faixa_etaria_filtrado,
                df_vinculos_grau_instrucao=df_vinculos_grau_instrucao_filtrado,
                df_vinculos_raca_cor=df_vinculos_raca_cor_filtrado,
                df_vinculos_sexo=df_vinculos_sexo_filtrado,
                df_renda_mun=df_renda_filtrado,
                df_renda_cnae=df_renda_cnae_filtrado,
                df_renda_sexo=df_renda_sexo_filtrado,
            )

        elif pagina_selecionada == "Empresas":
            # --- Carregamento Lazy (Dados Secundários de Empresas) ---
            df_cnpj_cnae = carregar_dados_cnpj_cnae(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_mei_total = carregar_dados_mei_total(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )
            df_mei_cnae = carregar_dados_mei_cnae(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_estabelecimentos = carregar_dados_estabelecimentos_municipios(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )
            df_estabelecimentos_cnae = carregar_dados_estabelecimentos_cnae(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )
            df_estabelecimentos_tamanho = carregar_dados_estabelecimentos_tamanho(
                municipio=municipio_de_interesse, anos=anos_de_interesse
            )

            # --- Filtragem Lazy ---
            df_mei_total_filtrado = df_mei_total[
                df_mei_total["municipio"].isin(municipios_selecionados_global)
            ]
            df_cnpj_cnae_filtrado = df_cnpj_cnae[
                df_cnpj_cnae["municipio"].isin(municipios_selecionados_global)
            ]
            df_mei_cnae_filtrado = df_mei_cnae[
                df_mei_cnae["municipio"].isin(municipios_selecionados_global)
            ]
            df_estabelecimentos_filtrado = df_estabelecimentos[
                df_estabelecimentos["municipio"].isin(municipios_selecionados_global)
            ]
            df_estabelecimentos_cnae_filtrado = df_estabelecimentos_cnae[
                df_estabelecimentos_cnae["municipio"].isin(
                    municipios_selecionados_global
                )
            ]
            df_estabelecimentos_tamanho_filtrado = df_estabelecimentos_tamanho[
                df_estabelecimentos_tamanho["municipio"].isin(
                    municipios_selecionados_global
                )
            ]

            show_page_empresas_ativas(
                df_cnpj=df_cnpj_total_filtrado,
                df_cnpj_cnae=df_cnpj_cnae_filtrado,
                df_mei=df_mei_total_filtrado,
                df_mei_cnae=df_mei_cnae_filtrado,
                municipio_de_interesse=municipio_de_interesse,
                df_estabelecimentos_cnae=df_estabelecimentos_cnae_filtrado,
                df_estabelecimentos_mun=df_estabelecimentos_filtrado,
                df_estabelecimentos_tamanho=df_estabelecimentos_tamanho_filtrado,
            )

        elif pagina_selecionada == "Comércio Exterior":
            df_comex_ano = carregar_dados_comex_anual(
                municipios=municipios_de_interesse, anos=anos_comex
            )
            df_comex_municipio = carregar_dados_comex_municipio(
                municipio=municipio_de_interesse, anos=anos_comex
            )

            df_comex_ano_filtrado = df_comex_ano[
                df_comex_ano["municipio"].isin(municipios_selecionados_global)
            ]

            show_page_comex(
                df_comex_ano_filtrado,
                df_comex_mensal_filtrado,
                df_comex_municipio,
                municipios_selecionados_global,
                municipio_de_interesse,
            )

        elif pagina_selecionada == "Segurança":
            df_seguranca_taxa = carregar_dados_seguranca_taxa(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )

            df_seguranca_taxa_filtrado = df_seguranca_taxa[
                df_seguranca_taxa["municipio"].isin(municipios_selecionados_global)
            ]

            show_page_seguranca(df_seguranca_filtrado, df_seguranca_taxa_filtrado)

        elif pagina_selecionada == "Assistência Social":
            show_page_assistencia_social(
                df_cad=df_cad_filtrado,
                df_bolsa=df_bolsa_familia_filtrado,
                municipio_interesse=municipio_de_interesse,
            )

        elif pagina_selecionada == "Educação":
            df_educacao_rendimento = carregar_dados_educacao_rendimento(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )
            df_educacao_ideb_escolas = carregar_dados_educacao_ideb_escolas(
                municipios=municipios_de_interesse
            )

            df_educacao_rendimento_filtrado = df_educacao_rendimento[
                df_educacao_rendimento["municipio"].isin(municipios_selecionados_global)
            ]
            df_educacao_ideb_escolas_filtrado = df_educacao_ideb_escolas[
                df_educacao_ideb_escolas["municipio"].isin(
                    municipios_selecionados_global
                )
            ]

            show_page_educacao(
                df_matriculas=df_educacao_matriculas_filtrado,
                df_rendimento=df_educacao_rendimento_filtrado,
                df_ideb_municipio=df_educacao_ideb_municipio_filtrado,
                df_ideb_escolas=df_educacao_ideb_escolas_filtrado,
                municipios_selecionados_global=municipios_selecionados_global,
            )

        elif pagina_selecionada == "Saúde":
            df_saude_vacinas = carregar_dados_saude_vacinas(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )
            df_saude_despesas = carregar_dados_saude_despesas(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )
            df_saude_leitos = carregar_dados_saude_leitos(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )
            df_saude_medicos = carregar_dados_saude_medicos(
                municipios=municipios_de_interesse, anos=anos_de_interesse
            )

            # --- Filtragem Lazy ---
            df_saude_vacinas_filtrado = df_saude_vacinas[
                df_saude_vacinas["municipio"].isin(municipios_selecionados_global)
            ]
            df_saude_despesas_filtrado = df_saude_despesas[
                df_saude_despesas["municipio"].isin(municipios_selecionados_global)
            ]
            df_saude_leitos_filtrado = df_saude_leitos[
                df_saude_leitos["municipio"].isin(municipios_selecionados_global)
            ]
            df_saude_medicos_filtrado = df_saude_medicos[
                df_saude_medicos["municipio"].isin(municipios_selecionados_global)
            ]

            show_page_saude(
                df_saude_mensal=df_saude_mensal_filtrado,
                df_saude_vacinas=df_saude_vacinas_filtrado,
                df_saude_leitos=df_saude_leitos_filtrado,
                df_saude_medicos=df_saude_medicos_filtrado,
                df_saude_despesas=df_saude_despesas_filtrado,
            )

        elif pagina_selecionada == "PIB":
            show_page_pib(df_pib=df_pib_municipios_filtrado)

        elif pagina_selecionada == "Demografia":
            show_page_demografia(
                df_populacao_densidade=df_populacao_densidade_filtrado,
                df_populacao_sexo_idade=df_populacao_sexo_idade_filtrado,
            )

        elif pagina_selecionada == "Finanças":
            show_page_financas(
                df_financas=df_financas_filtrado,
                df_indicadores_financeiros=df_indicadores_financeiros_filtrado,
                municipio_de_interesse=municipio_de_interesse,  # Adicionado argumento
                pdf_indicadores=pdf_indicadores,
            )

    manter_posicao_scroll()

# %%
