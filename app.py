# %%

# ==============================================================================
# BLOCO 1: IMPORTS DE TERCEIROS (PIP)
# ==============================================================================
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
from dotenv import load_dotenv  # noqa: F811

load_dotenv()
# ==============================================================================
# BLOCO 2: IMPORTS DA APLICAÇÃO (SRC)
# ==============================================================================
from src.views.home import show_page_home  # noqa: E402
from src.views.emprego import show_page_emprego  # noqa: E402
from src.views.comercio_exterior import show_page_comex  # noqa: E402
from src.views.seguranca import show_page_seguranca  # noqa: E402
from src.views.assistencia_social import show_page_assistencia_social  # noqa: E402
from src.views.financas import show_page_financas  # noqa: E402
from src.views.empresas import show_page_empresas_ativas  # noqa: E402
from src.views.educacao import show_page_educacao  # noqa: E402
from src.views.saude import show_page_saude  # noqa: E402
from src.views.pib import show_page_pib  # noqa: E402
from src.views.demografia import show_page_demografia  # noqa: E402
from src.views.dados import show_page_dados  # noqa: E402

# noqa: E402
from src.utils import carregar_css  # noqa: E402
from src.utils import manter_posicao_scroll  # noqa: E402

# noqa: E402
from src.data_loader import (  # noqa: E402
    carregar_dados_emprego_municipios,  # noqa: E402
    carregar_dados_vinculos_municipios,  # noqa: E402
    carregar_dados_comex_mensal,  # noqa: E402
    carregar_dados_seguranca,  # noqa: E402
    carregar_dados_CAD,  # noqa: E402
    carregar_dados_bolsa_familia,  # noqa: E402
    carregar_dados_financas,  # noqa: E402
    carregar_dados_indicadores_financeiros,  # noqa: E402
    carregar_pdf_indicadores_financeiros,  # noqa: E402
    carregar_dados_cnpj_total,  # noqa: E402
    carregar_dados_educacao_matriculas,  # noqa: E402
    carregar_dados_educacao_ideb_municipio,  # noqa: E402
    carregar_dados_pib_municipios,  # noqa: E402
    carregar_dados_saude_mensal,  # noqa: E402
    carregar_dados_populacao_densidade,  # noqa: E402
    carregar_dados_populacao_sexo_idade,  # noqa: E402
    carregar_dados_emprego_cnae,  # noqa: E402
    carregar_dados_emprego_faixa_etaria,  # noqa: E402
    carregar_dados_emprego_raca_cor,  # noqa: E402
    carregar_dados_emprego_grau_instrucao,  # noqa: E402
    carregar_dados_emprego_sexo,  # noqa: E402
    carregar_dados_vinculos_cnae,  # noqa: E402
    carregar_dados_vinculos_sexo,  # noqa: E402
    carregar_dados_vinculos_faixa_etaria,  # noqa: E402
    carregar_dados_vinculos_grau_instrucao,  # noqa: E402
    carregar_dados_vinculos_raca_cor,  # noqa: E402
    carregar_dados_renda_municipios,  # noqa: E402
    carregar_dados_renda_cnae,  # noqa: E402
    carregar_dados_renda_sexo,  # noqa: E402
    carregar_dados_estabelecimentos_municipios,  # noqa: E402
    carregar_dados_estabelecimentos_cnae,  # noqa: E402
    carregar_dados_estabelecimentos_tamanho,  # noqa: E402
    carregar_dados_comex_anual,  # noqa: E402
    carregar_dados_comex_municipio,  # noqa: E402
    carregar_dados_seguranca_taxa,  # noqa: E402
    carregar_dados_cnpj_cnae,  # noqa: E402
    carregar_dados_cnpj_cnae_saldo,  # noqa: E402
    carregar_dados_mei_total,  # noqa: E402
    carregar_dados_mei_cnae,  # noqa: E402
    carregar_dados_mei_cnae_saldo,  # noqa: E402
    carregar_dados_educacao_rendimento,  # noqa: E402
    carregar_dados_educacao_ideb_escolas,  # noqa: E402
    carregar_dados_saude_despesas,  # noqa: E402
    carregar_dados_saude_leitos,  # noqa: E402
    carregar_dados_saude_medicos,  # noqa: E402
    carregar_dados_saude_vacinas,  # noqa: E402
)  # noqa: E402
from src.config import (  # noqa: E402
    municipio_de_interesse,  # noqa: E402
    municipios_de_interesse,  # noqa: E402
    anos_de_interesse,  # noqa: E402
    anos_comex,  # noqa: E402
    CORES_MUNICIPIOS,  # noqa: E402
)  # noqa: E402


def main():
    """Função principal que executa a aplicação Streamlit."""

    # ==============================================================================
    # BLOCO DE CARREGAMENTO DAS VARIÁVEIS DE AMBIENTE
    # ==============================================================================

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
    # CARREGAMENTO DE TODOS OS DADOS (UPFRONT)
    # ==============================================================================
    # Carrega TODOS os DFs necessários para a aplicação inteira de uma só vez.
    with st.spinner("Carregando todos os dados da aplicação... Por favor, aguarde."):
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

        # --- Dados Secundários (Página Emprego) ---
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

        # --- Dados Secundários (Página Empresas) ---
        df_cnpj_cnae = carregar_dados_cnpj_cnae(
            municipio=municipio_de_interesse, anos=anos_de_interesse
        )
        df_cnpj_cnae_saldo = carregar_dados_cnpj_cnae_saldo(
            municipio=municipio_de_interesse, anos=anos_de_interesse
        )
        df_mei_total = carregar_dados_mei_total(
            municipios=municipios_de_interesse, anos=anos_de_interesse
        )
        df_mei_cnae = carregar_dados_mei_cnae(
            municipio=municipio_de_interesse, anos=anos_de_interesse
        )
        df_mei_cnae_saldo = carregar_dados_mei_cnae_saldo(
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

        # --- Dados Secundários (Página Comércio Exterior) ---
        df_comex_ano = carregar_dados_comex_anual(
            municipios=municipios_de_interesse, anos=anos_comex
        )
        df_comex_municipio = carregar_dados_comex_municipio(
            municipio=municipio_de_interesse, anos=anos_comex
        )

        # --- Dados Secundários (Página Segurança) ---
        df_seguranca_taxa = carregar_dados_seguranca_taxa(
            municipios=municipios_de_interesse, anos=anos_de_interesse
        )

        # --- Dados Secundários (Página Educação) ---
        df_educacao_rendimento = carregar_dados_educacao_rendimento(
            municipios=municipios_de_interesse, anos=anos_de_interesse
        )
        df_educacao_ideb_escolas = carregar_dados_educacao_ideb_escolas(
            municipios=municipios_de_interesse
        )

        # --- Dados Secundários (Página Saúde) ---
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

    # ==============================================================================
    # BARRA LATERAL E NAVEGAÇÃO ENTRE PÁGINAS
    # ==============================================================================

    municipios_para_comparacao = [
        m for m in municipios_de_interesse if m != municipio_de_interesse
    ]

    with st.sidebar:
        with st.expander("Filtros Globais", expanded=True):
            cor_foco = CORES_MUNICIPIOS.get(municipio_de_interesse, "#888888")

            st.markdown(
                f"""
                <label style="font-size: 14px;">Município Principal:</label>
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
            municipios_selecionados_global = [
                municipio_de_interesse
            ] + municipios_comparados

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
                "Dados",
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
                "download",
            ],
            menu_icon="cast",
            default_index=0,
            key="selected_page",
            styles={
                "icon": {"font-size": "14px"},
                "nav-link": {
                    "font-size": "14px",
                    "padding": "8px 15px",
                },
                "nav-link-selected": {"background-color": "#d90429"},
            },
        )

    # ==============================================================================
    # FILTRAGEM GLOBAL DE TODOS OS DADOS
    # ==============================================================================
    # --- Filtros Essenciais (Mult-Município) ---
    df_caged_filtrado = df_caged[
        df_caged["municipio"].isin(municipios_selecionados_global)
    ]
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

    # --- Filtros Secundários (Multi-Município) ---
    df_renda_filtrado = df_renda[
        df_renda["municipio"].isin(municipios_selecionados_global)
    ]
    df_mei_total_filtrado = df_mei_total[
        df_mei_total["municipio"].isin(municipios_selecionados_global)
    ]
    df_estabelecimentos_filtrado = df_estabelecimentos[
        df_estabelecimentos["municipio"].isin(municipios_selecionados_global)
    ]
    df_comex_ano_filtrado = df_comex_ano[
        df_comex_ano["municipio"].isin(municipios_selecionados_global)
    ]
    df_seguranca_taxa_filtrado = df_seguranca_taxa[
        df_seguranca_taxa["municipio"].isin(municipios_selecionados_global)
    ]
    df_educacao_rendimento_filtrado = df_educacao_rendimento[
        df_educacao_rendimento["municipio"].isin(municipios_selecionados_global)
    ]
    df_educacao_ideb_escolas_filtrado = df_educacao_ideb_escolas[
        df_educacao_ideb_escolas["municipio"].isin(municipios_selecionados_global)
    ]
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

    # ==============================================================================
    # RENDERIZAÇÃO DAS PÁGINAS
    # ==============================================================================
    placeholder = st.empty()

    with placeholder.container():
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
                df_saude_mensal=df_saude_mensal_filtrado,
                df_populacao_densidade=df_populacao_densidade_filtrado,
                df_populacao_sexo_idade=df_populacao_sexo_idade_filtrado,
            )

        if pagina_selecionada == "Emprego":
            show_page_emprego(
                df_caged=df_caged_filtrado,
                df_caged_cnae=df_caged_cnae,
                df_caged_faixa_etaria=df_caged_faixa_etaria,
                df_caged_grau_instrucao=df_caged_grau_instrucao,
                df_caged_raca_cor=df_caged_raca_cor,
                df_caged_sexo=df_caged_sexo,
                municipio_de_interesse=municipio_de_interesse,
                df_vinculos=df_vinculos_filtrado,
                df_vinculos_cnae=df_vinculos_cnae,
                df_vinculos_faixa_etaria=df_vinculos_faixa_etaria,
                df_vinculos_grau_instrucao=df_vinculos_grau_instrucao,
                df_vinculos_raca_cor=df_vinculos_raca_cor,
                df_vinculos_sexo=df_vinculos_sexo,
                df_renda_mun=df_renda_filtrado,
                df_renda_cnae=df_renda_cnae,
                df_renda_sexo=df_renda_sexo,
            )

        elif pagina_selecionada == "Empresas":
            show_page_empresas_ativas(
                df_cnpj=df_cnpj_total_filtrado,
                df_cnpj_cnae=df_cnpj_cnae,
                df_cnpj_cnae_saldo=df_cnpj_cnae_saldo,
                df_mei=df_mei_total_filtrado,
                df_mei_cnae=df_mei_cnae,
                df_mei_cnae_saldo=df_mei_cnae_saldo,
                municipio_de_interesse=municipio_de_interesse,
                df_estabelecimentos_cnae=df_estabelecimentos_cnae,
                df_estabelecimentos_mun=df_estabelecimentos_filtrado,
                df_estabelecimentos_tamanho=df_estabelecimentos_tamanho,
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
                pdf_indicadores=pdf_indicadores,
            )

        elif pagina_selecionada == "Dados":
            with st.spinner("Carregando os dados para download..."):
                show_page_dados(
                    # --- Emprego ---
                    df_caged=df_caged_filtrado,
                    df_caged_cnae=df_caged_cnae,
                    df_caged_faixa_etaria=df_caged_faixa_etaria,
                    df_caged_raca_cor=df_caged_raca_cor,
                    df_caged_grau_instrucao=df_caged_grau_instrucao,
                    df_caged_sexo=df_caged_sexo,
                    df_vinculos=df_vinculos_filtrado,
                    df_vinculos_cnae=df_vinculos_cnae,
                    df_vinculos_faixa_etaria=df_vinculos_faixa_etaria,
                    df_vinculos_grau_instrucao=df_vinculos_grau_instrucao,
                    df_vinculos_raca_cor=df_vinculos_raca_cor,
                    df_vinculos_sexo=df_vinculos_sexo,
                    df_renda_mun=df_renda_filtrado,
                    df_renda_sexo=df_renda_sexo,
                    df_renda_cnae=df_renda_cnae,
                    municipio_de_interesse=municipio_de_interesse,
                    # --- Empresas ---
                    df_cnpj_mun=df_cnpj_total_filtrado,
                    df_cnpj_cnae=df_cnpj_cnae,
                    df_cnpj_cnae_saldo=df_cnpj_cnae_saldo,
                    df_mei_mun=df_mei_total_filtrado,
                    df_mei_cnae=df_mei_cnae,
                    df_mei_cnae_saldo=df_mei_cnae_saldo,
                    df_estabelecimentos_mun=df_estabelecimentos_filtrado,
                    df_estabelecimentos_cnae=df_estabelecimentos_cnae,
                    df_estabelecimentos_tamanho=df_estabelecimentos_tamanho,
                    # --- Comércio Exterior ---
                    df_comex_anual_mun=df_comex_ano_filtrado,
                    df_comex_mensal_mun=df_comex_mensal_filtrado,
                    df_comex_raw_municipio_foco=df_comex_municipio,
                    # --- Segurança ---
                    df_seguranca_mun=df_seguranca_filtrado,
                    df_seguranca_taxa_mun=df_seguranca_taxa_filtrado,
                    # --- Assistência Social ---
                    df_cad=df_cad_filtrado,
                    df_bolsa=df_bolsa_familia_filtrado,
                    # --- Educação ---
                    df_educacao_matriculas=df_educacao_matriculas,
                    df_educacao_rendimento=df_educacao_rendimento,
                    df_educacao_ideb_municipio=df_educacao_ideb_municipio,
                    df_educacao_ideb_escolas=df_educacao_ideb_escolas,
                    # --- Saúde ---
                    df_saude_mensal=df_saude_mensal,
                    df_saude_vacinas=df_saude_vacinas,
                    df_saude_despesas=df_saude_despesas,
                    df_saude_leitos=df_saude_leitos,
                    df_saude_medicos=df_saude_medicos,
                    # --- PIB ---
                    df_pib_municipios=df_pib_municipios_filtrado,
                    # --- Demografia ---
                    df_populacao_densidade=df_populacao_densidade_filtrado,
                    df_populacao_sexo_idade=df_populacao_sexo_idade_filtrado,
                    # --- Finanças ---
                    df_financas=df_financas_filtrado,
                    df_indicadores_financeiros=df_indicadores_financeiros_filtrado,
                    pdf_indicadores=pdf_indicadores,
                )

        manter_posicao_scroll()


# ==============================================================================
# PONTO DE ENTRADA DA APLICAÇÃO
# ==============================================================================
if __name__ == "__main__":
    main()
