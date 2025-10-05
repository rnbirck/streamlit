# %%
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

# ==============================================================================
# IMPORTAÇÕES DE FUNÇÕES E DADOS
# ==============================================================================
from src.utils import carregar_css
from src.utils import (
    MESES_DIC,
    checar_ult_ano_completo,
    filtrar_municipio_ult_mes_ano,
    criar_grafico_barras,
    criar_tabela_formatada,
    manter_posicao_scroll,
    destacar_percentuais,
    criar_tabela_comex,
)
from src.data_loader import (
    carregar_dados_comex_mensal,
    carregar_dados_emprego_municipios,
    carregar_dados_emprego_cnae,
    carregar_dados_comex_anual,
    carregar_dados_comex_municipio,
    carregar_dados_siconfi_rreo,
    carregar_dados_seguranca,
    carregar_dados_seguranca_taxa,
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
# FUNÇÕES DA PÁGINA HOME
# ==============================================================================


def show_page_home():
    """
    Renderiza a página inicial do dashboard com instruções e informações.
    """
    st.title("📊 Dashboard de Indicadores Municipais")
    st.markdown("---")

    st.markdown(
        """
        Bem-vindo(a) ao painel de visualização de dados! 
        
        Este dashboard foi desenvolvido para centralizar e apresentar diversos indicadores socioeconômicos 
        para os municípios selecionados, permitindo uma análise ágil e comparativa.
        
        Utilize as ferramentas de navegação e filtragem para explorar as informações.
        """
    )

    st.subheader("🧭 Como Navegar e Filtrar")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            #### 1. Navegue pelas Páginas
            No menu à esquerda, você pode alternar entre as diferentes seções do dashboard:
            - **Início:** Esta página de boas-vindas.
            - **Emprego:** Dados do mercado de trabalho formal.
            - **Comércio Exterior:** Infomações de exportação dos municípios.
            - **Segurança:** Indicadores de criminalidade.
            - **Finanças:** Dados fiscais dos municípios.
            """
        )

    with col2:
        st.markdown(
            """
            #### 2. Filtre por Municípios
            Também na barra lateral, no topo, você encontrará o filtro global de municípios. 
            
            As cidades que você selecionar aqui serão aplicadas a **todas** as páginas e gráficos 
            do dashboard, permitindo uma análise comparativa direta e eficiente.
            """
        )

    st.markdown("---")
    st.subheader("📂 Sobre as Páginas e Atualizações")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            #### 💼 Emprego
            Analisa o mercado de trabalho formal através dos dados do **CAGED** (Cadastro Geral de Empregados e Desempregados). Explore o saldo de admissões e demissões e a análise por setor econômico (CNAE).
            
            *Frequência de Atualização: **Mensal***
            """
        )
        st.markdown("---")
        st.markdown(
            """
            #### 🛡️ Segurança Pública
            Reúne os principais indicadores de criminalidade divulgados pela **Secretaria de Segurança Pública**. Os dados são agrupados em categorias como crimes contra a vida, crimes patrimoniais e violência contra a mulher, com visualização em números absolutos e taxas por 10 mil habitantes.
            
            *Frequência de Atualização: **Mensal***
            """
        )

    with col2:
        st.markdown(
            """
            #### ✈️ Comércio Exterior
            Apresenta os dados de exportação dos municípios com base nos dados divulgados pelo Comexstat. É possível analisar os valores totais, os principais produtos exportados e os países de destino.
            
            *Frequência de Atualização: **Mensal***
            """
        )
        st.markdown("---")
        st.markdown(
            """
            #### 💰 Finanças Públicas
            Apresenta dados fiscais dos municípios com base nos relatórios do **SICONFI** (Sistema de Informações Contábeis e Fiscais do Setor Público Brasileiro). Explore indicadores como Receitas Correntes e Total de Receitas.
            
            *Frequência de Atualização: **Bimestral***
            """
        )


# ==============================================================================
# FUNÇÕES DA PÁGINA DE EMPREGO
# ==============================================================================


def display_emprego_kpi_cards(df, municipio_interesse):
    """Exibe os cards de KPI de Emprego para um município específico."""
    st.markdown(f"""#### Saldo de Admissões e Demissões em {municipio_interesse}:""")

    with st.container(border=False):
        filtro_municipio = df["municipio"] == municipio_interesse
        df_municipio = df[filtro_municipio]
        ano_completo = checar_ult_ano_completo(df_municipio)

        ult_ano = df_municipio["ano"].max()
        ult_mes = df_municipio[df_municipio["ano"] == ult_ano]["mes"].max()

        saldo_ult_mes = df_municipio[
            (df_municipio["ano"] == ult_ano) & (df_municipio["mes"] == ult_mes)
        ]["saldo_movimentacao"].sum()

        saldo_acu_ano = df_municipio[
            (df_municipio["ano"] == ult_ano) & (df_municipio["mes"] <= ult_mes)
        ]["saldo_movimentacao"].sum()

        saldo_ano_completo = df_municipio[df_municipio["ano"] == ano_completo][
            "saldo_movimentacao"
        ].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric(
            label=f"{MESES_DIC[ult_mes]} de {ult_ano}",
            value=f"{saldo_ult_mes:,.0f}".replace(",", "."),
            delta=None,
            border=True,
        )
        col2.metric(
            label=f"Acumulado de Jan a {MESES_DIC[ult_mes][:3]} de {ult_ano}",
            value=f"{saldo_acu_ano:,.0f}".replace(",", "."),
            delta=None,
            border=True,
        )
        col3.metric(
            label=f"{ano_completo}",
            value=f"{saldo_ano_completo:,.0f}".replace(",", "."),
            delta=None,
            border=True,
        )


def expander_emprego_callback():
    """Garante que o expander de emprego permaneça aberto após a interação."""
    st.session_state.emprego_expander_state = True


@st.cache_data
def preparar_dados_graficos_emprego(df_filtrado):
    """
    Recebe um DataFrame filtrado e retorna todos os DataFrames pivotados e prontos
    para os gráficos do expander de emprego. Esta função é cacheada para performance.
    """
    # Histórico Mensal
    df_hist = (
        df_filtrado.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            columns="municipio",
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    # Mês Atual
    ult_ano = df_filtrado["ano"].max()
    ult_mes = df_filtrado[df_filtrado["ano"] == ult_ano]["mes"].max()

    df_mes = (
        df_filtrado[df_filtrado["mes"] == ult_mes]
        .pivot_table(
            index="ano",
            columns="municipio",
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    df_mes.index = MESES_DIC[ult_mes] + "/" + df_mes.index.astype(str).str.slice(-2)

    # Acumulado no Ano
    df_acum = (
        df_filtrado[df_filtrado["mes"] <= ult_mes]
        .pivot_table(
            index="ano",
            columns="municipio",
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    df_acum.index = (
        "Jan-" + MESES_DIC[ult_mes][:3] + "/" + df_acum.index.astype(str).str.slice(-2)
    )

    # Anual
    ano_completo = checar_ult_ano_completo(df_filtrado)
    df_anual = (
        df_filtrado[df_filtrado["ano"] <= ano_completo]
        .pivot_table(
            index="ano",
            columns="municipio",
            values="saldo_movimentacao",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index(ascending=False)
    )

    return df_hist, df_mes, df_acum, df_anual, ult_ano, ult_mes


def display_emprego_municipios_expander(df, municipio_interesse):
    """Exibe o expander com análise de saldo de emprego para múltiplos municípios."""
    with st.expander(
        "Saldo de Emprego por Município",
        expanded=st.session_state.emprego_expander_state,
    ):
        df_hist, df_mes, df_acum, df_anual, ult_ano, ult_mes = (
            preparar_dados_graficos_emprego(df)
        )
        anos_disponiveis = sorted(df["ano"].unique().tolist(), reverse=True)

        tab_hist, tab_mes, tab_acum, tab_anual = st.tabs(
            ["Histórico Mensal", "Mês Atual", "Acumulado no Ano", "Anual"],
        )

        with tab_hist:
            ANO_SELECIONADO = st.selectbox(
                "Selecione o ano para o gráfico:",
                options=anos_disponiveis,
                index=0,
                key="hist_ano_emprego",
            )

            df_hist = df_hist[df_hist.index.year == ANO_SELECIONADO]
            st.markdown(f"##### Saldo de Emprego Mensal em {ANO_SELECIONADO}")

            fig_hist = criar_grafico_barras(
                df=df_hist,
                titulo="",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=450,
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_map=CORES_MUNICIPIOS,
            )
            st.plotly_chart(fig_hist, width="stretch")

        with tab_mes:
            st.markdown(f"##### Saldo Mensal de Emprego em {MESES_DIC[ult_mes]}")
            fig_mes = criar_grafico_barras(
                df=df_mes,
                titulo="",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=450,
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_map=CORES_MUNICIPIOS,
            )
            st.plotly_chart(fig_mes, width="stretch")

        with tab_acum:
            st.markdown(
                f"##### Saldo Acumulado de Emprego de Janeiro a {MESES_DIC[ult_mes]}",
            )
            fig_acum = criar_grafico_barras(
                df=df_acum,
                titulo="",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=450,
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_map=CORES_MUNICIPIOS,
            )
            st.plotly_chart(fig_acum, width="stretch")

        with tab_anual:
            st.markdown(
                "##### Saldo Anual de Emprego",
            )
            fig_anual = criar_grafico_barras(
                df=df_anual,
                titulo="",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=450,
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_map=CORES_MUNICIPIOS,
            )
            st.plotly_chart(fig_anual, width="stretch")


def display_emprego_cnae_expander(df, ult_ano, ult_mes):
    """Exibe o expander com análise de saldo de emprego por Setor e CNAE."""
    with st.expander("Saldo de Emprego por Setor Econômico", expanded=False):
        tab_grupo_ibge, tab_grupo_cnae, tab_subclasse_cnae = st.tabs(
            ["Setor", "CNAE Grupo", "CNAE Subclasse"],
        )

        with tab_grupo_ibge:
            df_tabela_grupo_ibge = criar_tabela_formatada(
                df=df, index_col="grupo_ibge", ult_ano=ult_ano, ult_mes=ult_mes
            )
            st.markdown(
                f"##### Saldo Acumulado de Admissões e Demissões por Setor Econômico - {municipio_de_interesse}"
            )

            fig_grupo_ibge = criar_grafico_barras(
                df=df_tabela_grupo_ibge.T,
                titulo="",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=450,
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_map=CORES_MUNICIPIOS,
            )
            st.plotly_chart(fig_grupo_ibge, width="stretch")

        with tab_grupo_cnae:
            df_tabela_grupo_cnae = (
                criar_tabela_formatada(
                    df=df, index_col="grupo", ult_ano=ult_ano, ult_mes=ult_mes
                )
                .style.format(lambda x: f"{x:,.0f}".replace(",", "."))
                .background_gradient(cmap="coolwarm_r")
            )
            st.dataframe(df_tabela_grupo_cnae, width="stretch")

        with tab_subclasse_cnae:
            df_tabela_subclasse_cnae = (
                criar_tabela_formatada(
                    df=df, index_col="subclasse", ult_ano=ult_ano, ult_mes=ult_mes
                )
                .style.format(lambda x: f"{x:,.0f}".replace(",", "."))
                .background_gradient(cmap="coolwarm_r")
            )
            st.dataframe(df_tabela_subclasse_cnae, width="stretch")


def show_page_emprego(
    df_caged,
    df_caged_cnae,
    municipio_de_interesse,
):
    """Função principal que renderiza a página de Emprego."""
    st.title("Dashboard de Emprego")
    st.markdown("### Análise de Saldo de Emprego")

    display_emprego_kpi_cards(df_caged, municipio_de_interesse)
    st.markdown("##### Clique nos menus abaixo para explorar os dados")

    display_emprego_municipios_expander(
        df_caged,
        municipio_de_interesse,
    )

    if not df_caged_cnae.empty:
        ult_ano = int(df_caged_cnae["ano"].max())
        ult_mes = int(df_caged_cnae[df_caged_cnae["ano"] == ult_ano]["mes"].max())
        display_emprego_cnae_expander(df_caged_cnae, ult_ano, ult_mes)


# ==============================================================================
# FUNÇÕES DA PÁGINA DE COMÉRCIO EXTERIOR
# ==============================================================================


def display_comex_kpi_cards(df_ano, df_mes, municipio_interesse):
    """Exibe os cards de KPI de Comércio Exterior para um município específico."""

    st.markdown(f"""#### Exportações de {municipio_de_interesse} (Milhões de US$):""")

    with st.container(border=False):
        # Ultimo mês disponível
        ult_ano = df_mes["ano"].max()
        ult_mes = df_mes[df_mes["ano"] == ult_ano]["mes"].max()
        exp_mun_ult_mes = filtrar_municipio_ult_mes_ano(df_mes, municipio_interesse)[
            "total_exp_mensal"
        ].sum()

        taxa_var_ult_mes = filtrar_municipio_ult_mes_ano(df_mes, municipio_interesse)[
            "perc_var_mes_ano_anterior"
        ].sum()

        # Acumulado no ano
        exp_mun_acu_ano = filtrar_municipio_ult_mes_ano(df_mes, municipio_interesse)[
            "total_exp_acumulado"
        ].sum()

        taxa_var_acu_ano = filtrar_municipio_ult_mes_ano(df_mes, municipio_interesse)[
            "perc_var_acum_ano_anterior"
        ].sum()

        # Último ano completo
        ano_completo = checar_ult_ano_completo(df_mes)
        exp_mun_ano_completo = df_ano[
            (df_ano["municipio"] == municipio_interesse)
            & (df_ano["ano"] == ano_completo)
        ]["total_exp_anual"].sum()

        tx_var_ano_completo = df_ano[
            (df_ano["municipio"] == municipio_interesse)
            & (df_ano["ano"] == ano_completo)
        ]["perc_var_ano_anterior"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            label=f"{MESES_DIC[ult_mes]} de {ult_ano}",
            value=f"{exp_mun_ult_mes / 1000000:,.1f}".replace(".", ","),
            delta=f"{taxa_var_ult_mes}%".replace(".", ","),
            help="Taxa de Variação percentual em relação ao mesmo mês do ano anterior",
            border=True,
        )
        col2.metric(
            label=f"Acumulado de Jan a {MESES_DIC[ult_mes][:3]} de {ult_ano}",
            value=f"{exp_mun_acu_ano / 1000000:,.1f}".replace(".", ","),
            delta=f"{taxa_var_acu_ano}%".replace(".", ","),
            help="Taxa de Variação percentual em relação ao mesmo período do ano anterior",
            border=True,
        )

        col3.metric(
            label=f"Exportação em {ano_completo}",
            value=f"{exp_mun_ano_completo / 1000000:,.1f}".replace(".", ","),
            delta=f"{tx_var_ano_completo}%".replace(".", ","),
            help="Taxa de Variação percentual em relação ao ano anterior",
            border=True,
        )


@st.cache_data
def prepara_dados_graficos_comex(df_filtrado, anos_de_interesse):
    """
    Recebe um DataFrame de comex filtrado e retorna todos os DataFrames pivotados
    e o último ano/mês para os títulos dos gráficos.
    """

    ult_ano_comex, ult_mes_comex = None, None
    df_comex_hist, df_comex_hist_perc, df_comex_mes, df_comex_acum, df_comex_ano = (
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
    )

    if not df_filtrado.empty:
        ult_ano_comex = df_filtrado["ano"].max()
        ult_mes_comex = df_filtrado[df_filtrado["ano"] == ult_ano_comex]["mes"].max()

        # Histórico Mensal - Valor
        df_comex_hist = (
            df_filtrado.assign(
                date=lambda x: pd.to_datetime(
                    x["ano"].astype(str)
                    + "-"
                    + x["mes"].astype(str).str.zfill(2)
                    + "-01"
                ),
                exp_milhoes=lambda x: x["total_exp_mensal"] / 1_000_000,
            )
            .pivot_table(
                index="date",
                columns="municipio",
                values="exp_milhoes",
                aggfunc="sum",
                fill_value=0,
            )
            .sort_index()
            .apply(lambda x: x.round(2))
        )
        # Historico Mensal - Percentual
        df_comex_hist_perc = (
            df_filtrado.assign(
                date=lambda x: pd.to_datetime(
                    x["ano"].astype(str)
                    + "-"
                    + x["mes"].astype(str).str.zfill(2)
                    + "-01"
                ),
            )
            .pivot_table(
                index="date",
                columns="municipio",
                values="perc_var_mes_ano_anterior",
                aggfunc="sum",
                fill_value=0,
            )
            .sort_index()
            .apply(lambda x: x.round(2))
        )

        # Mês Atual
        df_comex_mes = (
            df_filtrado[df_filtrado["mes"] == ult_mes_comex]
            .assign(exp_milhoes=lambda x: x["total_exp_mensal"] / 1_000_000)
            .pivot_table(
                index="ano",
                columns="municipio",
                values="exp_milhoes",
                aggfunc="sum",
                fill_value=0,
            )
            .sort_index()
            .apply(lambda x: x.round(2))
        )

        # Acumulado no Ano
        df_comex_acum = (
            df_filtrado[df_filtrado["mes"] <= ult_mes_comex]
            .assign(exp_milhoes=lambda x: x["total_exp_acumulado"] / 1_000_000)
            .pivot_table(
                index="ano",
                columns="municipio",
                values="exp_milhoes",
                aggfunc="sum",
                fill_value=0,
            )
            .sort_index()
        )

        # Anual
        ano_completo_comex = checar_ult_ano_completo(df_filtrado)
        df_comex_ano = (
            df_filtrado[df_filtrado["ano"] <= ano_completo_comex]
            .assign(exp_milhoes=lambda x: x["total_exp_mensal"] / 1_000_000)
            .pivot_table(
                index="ano",
                columns="municipio",
                values="exp_milhoes",
                aggfunc="sum",
                fill_value=0,
            )
            .sort_index()
        )

    return (
        df_comex_hist,
        df_comex_hist_perc,
        df_comex_mes,
        df_comex_acum,
        df_comex_ano,
        ult_ano_comex,
        ult_mes_comex,
    )


def display_comex_municipios_expander(df_mes):
    """Exibe o expander com análise de exportações para múltiplos municípios."""
    with st.expander("Comércio Exterior por Município", expanded=False):
        tab_hist, tab_mes, tab_acum, tab_anual = st.tabs(
            ["Histórico Mensal", "Mês Atual", "Acumulado no Ano", "Anual"],
        )

        df_filtrado = df_mes[(df_mes["ano"].isin(anos_de_interesse))]

        (
            df_comex_hist,
            df_comex_hist_perc,
            df_comex_mes,
            df_comex_acum,
            df_comex_ano,
            ult_ano_comex,
            ult_mes_comex,
        ) = prepara_dados_graficos_comex(df_filtrado, anos_de_interesse)

        anos_disponiveis = sorted(df_filtrado["ano"].unique().tolist(), reverse=True)

        with tab_hist:
            ANO_SELECIONADO = st.selectbox(
                "Selecione o ano para o gráfico:",
                options=anos_disponiveis,
                index=0,
                key="hist_ano_comex",
            )
            df_comex_hist_filtrado_ano = df_comex_hist[
                df_comex_hist.index.year == ANO_SELECIONADO
            ]

            df_comex_hist_perc_filtrado_ano = df_comex_hist_perc[
                df_comex_hist_perc.index.year == ANO_SELECIONADO
            ]

            if not ANO_SELECIONADO:
                st.warning("Por favor, selecione ao menos um ano.")

            fig_hist = criar_grafico_barras(
                df=df_comex_hist_filtrado_ano,
                titulo="",
                label_y="(Milhões de US$)",
                barmode="group",
                height=450,
                data_label_format=".1f",
                hover_label_format=",.2f",
                color_map=CORES_MUNICIPIOS,
            )

            fig_hist_perc = criar_grafico_barras(
                df=df_comex_hist_perc_filtrado_ano,
                titulo="",
                label_y="Variação em relação ao mesmo mês do ano anterior (%)",
                barmode="group",
                height=450,
                data_label_format=".1f",
                hover_label_format=",.2f",
                color_map=CORES_MUNICIPIOS,
            )

            view_mode = st.radio(
                "Selecione o modo de Visualização:",
                options=["Valor (Milhões de US$)", "Variação YoY (%)"],
                horizontal=True,
                label_visibility="collapsed",
                key="view_mode_comex_municipios_hist",
            )

            if view_mode == "Valor (Milhões de US$)":
                st.markdown(f"##### Exportações em {ANO_SELECIONADO}")
                st.plotly_chart(fig_hist, width="stretch")

            elif view_mode == "Variação YoY (%)":
                if fig_hist_perc:
                    st.markdown(
                        f"##### Variação Percentual das Exportações em {ANO_SELECIONADO}"
                    )
                    st.plotly_chart(fig_hist_perc, use_container_width=True)
                else:
                    st.warning("Nenhum dado disponível para o gráfico.")

        with tab_mes:
            nome_mes = MESES_DIC[ult_mes_comex]

            df_comex_mes.index = (
                nome_mes + "/" + df_comex_mes.index.astype(str).str.slice(-2)
            )
            fig_mes = criar_grafico_barras(
                df=df_comex_mes,
                titulo="",
                label_y="(Milhões de US$)",
                barmode="group",
                height=450,
                data_label_format=".1f",
                hover_label_format=",.2f",
                color_map=CORES_MUNICIPIOS,
            )
            st.markdown(f"##### Exportações em {MESES_DIC[ult_mes_comex]}")
            st.plotly_chart(fig_mes, width="stretch")

        with tab_acum:
            df_comex_acum.index = (
                "Jan-"
                + MESES_DIC[ult_mes_comex][:3]
                + "/"
                + df_comex_acum.index.astype(str).str.slice(-2)
            )
            fig_acum = criar_grafico_barras(
                df=df_comex_acum,
                titulo="",
                label_y="(Milhões de US$)",
                barmode="group",
                height=450,
                data_label_format=".1f",
                hover_label_format=",.2f",
                color_map=CORES_MUNICIPIOS,
            )
            st.markdown(f"##### Exportações de Janeiro a {MESES_DIC[ult_mes_comex]}")
            st.plotly_chart(fig_acum, width="stretch")

        with tab_anual:
            fig_anual = criar_grafico_barras(
                df=df_comex_ano,
                titulo="",
                label_y="(Milhões de US$)",
                barmode="group",
                height=450,
                data_label_format=",.1f",
                hover_label_format=",.2f",
                color_map=CORES_MUNICIPIOS,
            )
            st.markdown("##### Exportações Anuais")
            st.plotly_chart(fig_anual, width="stretch")


@st.cache_data
def preparar_dados_comex_produto_pais(df, anos_selecionados, tipo_agg):
    """
    Função cacheada e genérica para preparar os dados para as abas de Comex.
    'tipo_agg' pode ser 'pais', 'produto', ou 'pais_produto'.
    """
    if not anos_selecionados:
        return pd.DataFrame()

    df_filtrado = df[df["ano"].isin(anos_selecionados)]

    if tipo_agg == "pais":
        return criar_tabela_comex(df_filtrado, ["pais"], ["País"], anos_selecionados)

    if tipo_agg == "produto":
        return criar_tabela_comex(
            df_filtrado, ["produto"], ["Produto"], anos_selecionados
        )

    if tipo_agg == "pais_produto":
        return criar_tabela_comex(
            df_filtrado, ["pais", "produto"], ["País", "Produto"], anos_selecionados
        )

    return pd.DataFrame()


@st.cache_data
def preparar_grafico_comex(df_filtrado_exibicao):
    """
    Recebe o DataFrame já filtrado pela UI e retorna a figura do gráfico cacheada.
    """
    if df_filtrado_exibicao.empty:
        return None

    df_grafico = (
        df_filtrado_exibicao.assign(
            date=lambda x: pd.to_datetime(
                x["Ano"].astype(str) + "-" + x["Mês"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            columns=["País"],
            values="Valor Exportado no Mês (US$)",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )
    if not df_grafico.empty:
        df_grafico.index = df_grafico.index.strftime("%Y-%m")

    return criar_grafico_barras(
        df=df_grafico,
        titulo="",
        label_y="Valor Exportado (US$)",
        barmode="stack",
        height=450,
        data_label_format=",.0f",
        hover_label_format=",.0f",
        color_map=CORES_MUNICIPIOS,
    )


def display_comex_produto_pais_expander(df, municipio_interesse):
    """Exibe o expander com análise de exportações por Produto e País do Municipio Selecionado."""
    with st.expander(
        f"Comércio Exterior de {municipio_interesse} por Destino e Produto",
        expanded=False,
    ):
        anos_disponiveis = sorted(df["ano"].unique().tolist(), reverse=True)
        ANOS_SELECIONADOS = st.multiselect(
            "Selecione o(s) ano(s) para a tabela:",
            options=anos_disponiveis,
            default=anos_de_interesse[-1],
            key="anos_comex_pais_multiselect",
        )

        if not ANOS_SELECIONADOS:
            st.warning("Por favor, selecione ao menos um ano.")

        tab_pais, tab_produto, tab_pais_produto = st.tabs(
            ["País", "Produto", "País - Produto"],
        )

        format_dict = {
            "Valor Exportado no Mês (US$)": lambda x: f"{x:,.0f}".replace(",", "."),
            "Valor Acumulado no Ano (US$)": lambda x: f"{x:,.0f}".replace(",", "."),
            "Variação YoY no Mês (%)": lambda x: f"{x:.1f}%".replace(".", ","),
            "Variação YoY Acumulada (%)": lambda x: f"{x:.1f}%".replace(".", ","),
        }

        with tab_pais:
            df_comex_pais = preparar_dados_comex_produto_pais(
                df=df,
                anos_selecionados=ANOS_SELECIONADOS,
                tipo_agg="pais",
            )

            paises_options = sorted(df_comex_pais["País"].unique().tolist())

            paises_selecionados_filtro = st.multiselect(
                label="Filtrar a tabela por país (opcional):",
                options=paises_options,
                key="filtro_tabela_comex_pais",
            )

            df_comex_pais_exibir = (
                df_comex_pais[df_comex_pais["País"].isin(paises_selecionados_filtro)]
                if paises_selecionados_filtro
                else df_comex_pais
            )

            st.dataframe(
                df_comex_pais_exibir.style.map(
                    destacar_percentuais,
                    subset=["Variação YoY no Mês (%)", "Variação YoY Acumulada (%)"],
                ).format(format_dict),
                hide_index=True,
                width="stretch",
            )

        with tab_produto:
            df_comex_produto = preparar_dados_comex_produto_pais(
                df=df, anos_selecionados=ANOS_SELECIONADOS, tipo_agg="produto"
            )

            produtos_options = sorted(df_comex_produto["Produto"].unique().tolist())

            produtos_selecionados_filtro = st.multiselect(
                label="Filtrar a tabela por produto (opcional):",
                options=produtos_options,
                key="filtro_tabela_comex_produto",
            )
            df_comex_produto_exibir = (
                df_comex_produto[
                    df_comex_produto["Produto"].isin(produtos_selecionados_filtro)
                ]
                if produtos_selecionados_filtro
                else df_comex_produto
            )

            st.dataframe(
                df_comex_produto_exibir.style.map(
                    destacar_percentuais,
                    subset=["Variação YoY no Mês (%)", "Variação YoY Acumulada (%)"],
                ).format(format_dict),
                hide_index=True,
                width="stretch",
            )

        with tab_pais_produto:
            df_comex_pais_produto = preparar_dados_comex_produto_pais(
                df=df, anos_selecionados=ANOS_SELECIONADOS, tipo_agg="pais_produto"
            )

            paises_options = sorted(df_comex_pais_produto["País"].unique().tolist())
            paises_default = (
                df_comex_pais_produto.groupby(["País"], as_index=False)[
                    "Valor Exportado no Mês (US$)"
                ]
                .sum()
                .sort_values(by="Valor Exportado no Mês (US$)", ascending=False)
                .head(5)["País"]
                .tolist()
            )
            paises_selecionados = st.multiselect(
                "Filtrar por País:",
                options=paises_options,
                default=paises_default,
                key="filtro_pp_pais",
            )

            if paises_selecionados:
                df_filtrado_temp = df_comex_pais_produto[
                    df_comex_pais_produto["País"].isin(paises_selecionados)
                ]
                produtos_options = sorted(df_filtrado_temp["Produto"].unique().tolist())
            else:
                produtos_options = sorted(
                    df_comex_pais_produto["Produto"].unique().tolist()
                )

            produtos_selecionados = st.multiselect(
                "Filtrar por Produto:",
                options=produtos_options,
                default=produtos_options,
                key="filtro_pp_produto",
            )

            df_pais_produto_exibir = df_comex_pais_produto.copy()
            if paises_selecionados:
                df_pais_produto_exibir = df_pais_produto_exibir[
                    df_pais_produto_exibir["País"].isin(paises_selecionados)
                ]
            if produtos_selecionados:
                df_pais_produto_exibir = df_pais_produto_exibir[
                    df_pais_produto_exibir["Produto"].isin(produtos_selecionados)
                ]

            styled_df = df_pais_produto_exibir.style.map(
                destacar_percentuais,
                subset=["Variação YoY no Mês (%)", "Variação YoY Acumulada (%)"],
            ).format(format_dict)

            fig_pp = preparar_grafico_comex(df_pais_produto_exibir)

            view_mode = st.radio(
                "Selecione o modo de Visualização:",
                options=["Tabela", "Gráfico"],
                horizontal=True,
                label_visibility="collapsed",
                key="view_mode_comex_pp",
            )

            if view_mode == "Tabela":
                st.dataframe(styled_df, hide_index=True, width="stretch")

            elif view_mode == "Gráfico":
                if fig_pp:
                    st.markdown("##### Exportações Anuais")
                    st.plotly_chart(fig_pp, use_container_width=True)
                else:
                    st.warning("Nenhum dado disponível para o gráfico.")


def show_page_comex(df_comex_ano, df_comex_mensal, municipio_de_interesse):
    """Função principal que renderiza a página de Comércio Exterior."""

    display_comex_kpi_cards(
        df_comex_ano, df_comex_mensal, municipio_interesse=municipio_de_interesse
    )
    st.markdown("##### Clique nos menus abaixo para explorar os dados")

    display_comex_municipios_expander(
        df_mes=df_comex_mensal,
    )
    display_comex_produto_pais_expander(
        df=df_comex_municipio, municipio_interesse=municipio_de_interesse
    )


# ==============================================================================
# FUNÇÕES DA PÁGINA DE SEGURANÇA
# ==============================================================================


@st.cache_data
def preparar_dados_graficos_seguranca(df_filtrado, coluna_selecionada, is_taxa=False):
    """
    Prepara os DataFrames pivotados para as abas da página de segurança.
    Agora aceita um parâmetro 'is_taxa' para saber qual coluna de valor usar.
    """
    df_hist, df_acum, df_anual = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    ult_ano, ult_mes = None, None

    # Define o nome da coluna de valor com base no tipo de dado (absoluto ou taxa)
    coluna_valor = f"taxa_{coluna_selecionada}" if is_taxa else coluna_selecionada

    if not df_filtrado.empty and coluna_valor in df_filtrado.columns:
        ult_ano = df_filtrado["ano"].max()
        ult_mes = df_filtrado[df_filtrado["ano"] == ult_ano]["mes"].max()

        # Histórico Mensal
        df_hist = (
            df_filtrado.assign(
                date=lambda x: pd.to_datetime(
                    x["ano"].astype(str)
                    + "-"
                    + x["mes"].astype(str).str.zfill(2)
                    + "-01"
                )
            )
            .pivot_table(
                index="date",
                columns="municipio",
                values=coluna_valor,
                aggfunc="sum",
                fill_value=0,
            )
            .sort_index()
        )

        # Acumulado no Ano
        df_acum_temp = df_filtrado[df_filtrado["mes"] <= ult_mes]
        df_acum = df_acum_temp.pivot_table(
            index="ano",
            columns="municipio",
            values=coluna_valor,
            aggfunc="sum",
            fill_value=0,
        ).sort_index()

        # Anual
        ano_completo = checar_ult_ano_completo(df_filtrado)
        df_anual_temp = df_filtrado[df_filtrado["ano"] <= ano_completo]
        df_anual = df_anual_temp.pivot_table(
            index="ano",
            columns="municipio",
            values=coluna_valor,
            aggfunc="sum",
            fill_value=0,
        ).sort_index(ascending=False)

    return df_hist, df_acum, df_anual, ult_ano, ult_mes


def display_secao_seguranca(
    df_seguranca, df_seguranca_taxa, titulo_expander, dicionario_indicadores, key_prefix
):
    """Função genérica para exibir uma seção de indicadores de segurança com opção de taxa."""
    with st.expander(titulo_expander, expanded=False):
        # --- WIDGETS DE FILTRO ---

        indicador_selecionado = st.selectbox(
            "Selecione um indicador:",
            options=list(dicionario_indicadores.keys()),
            key=f"{key_prefix}_selectbox",
        )
        coluna_selecionada = dicionario_indicadores[indicador_selecionado]

        # --- BOTÕES PARA ALTERNAR VISUALIZAÇÃO ---
        view_mode = st.radio(
            "Visualizar por:",
            options=["Número de Ocorrências", "Taxa por 10 mil hab."],
            horizontal=True,
            label_visibility="collapsed",
            key=f"view_mode_{key_prefix}",
        )

        # --- PREPARAÇÃO DOS DADOS COM BASE NA ESCOLHA DO USUÁRIO ---
        is_taxa = view_mode == "Taxa por 10 mil hab."
        df_ativo = df_seguranca_taxa if is_taxa else df_seguranca
        label_y_grafico = "Taxa por 10 mil hab." if is_taxa else "Ocorrências"
        data_label_format = ",.1f" if is_taxa else ",.0f"
        hover_label_format = ",.2f" if is_taxa else ",.0f"

        df_hist, df_acum, df_anual, ult_ano, ult_mes = (
            preparar_dados_graficos_seguranca(df_ativo, coluna_selecionada, is_taxa)
        )

        anos_disponiveis = sorted(df_ativo["ano"].unique().tolist(), reverse=True)

        # --- RENDERIZAÇÃO DAS ABAS ---
        tab_hist, tab_acum, tab_anual = st.tabs(
            ["Histórico Mensal", "Acumulado no Ano", "Anual"]
        )

        with tab_hist:
            if not anos_disponiveis:
                st.warning("Nenhum dado disponível para os filtros selecionados.")
            else:
                ANO_SELECIONADO = st.selectbox(
                    "Selecione o ano para o gráfico:",
                    options=anos_disponiveis,
                    index=0,
                    key=f"{key_prefix}_hist_ano",
                )
                st.markdown(
                    f"##### {indicador_selecionado} - Histórico Mensal em {ANO_SELECIONADO}"
                )

                df_hist_ano = df_hist[df_hist.index.year == ANO_SELECIONADO]
                df_hist_ano.index = df_hist_ano.index.strftime("%Y-%m")

                fig = criar_grafico_barras(
                    df=df_hist_ano,
                    titulo="",
                    label_y=label_y_grafico,
                    barmode="group",
                    height=450,
                    data_label_format=data_label_format,
                    color_map=CORES_MUNICIPIOS,
                    hover_label_format=hover_label_format,
                )
                st.plotly_chart(fig, use_container_width=True)

        if ult_mes:
            with tab_acum:
                df_acum.index = (
                    "Jan-"
                    + MESES_DIC[ult_mes][:3]
                    + "/"
                    + df_acum.index.astype(str).str.slice(-2)
                )
                st.markdown(
                    f"##### {indicador_selecionado} - Acumulado de Janeiro a {MESES_DIC[ult_mes]}"
                )
                fig = criar_grafico_barras(
                    df=df_acum,
                    titulo="",
                    label_y=label_y_grafico,
                    barmode="group",
                    height=450,
                    data_label_format=data_label_format,
                    color_map=CORES_MUNICIPIOS,
                    hover_label_format=hover_label_format,
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab_anual:
            st.markdown("##### Total Anual de Ocorrências")
            fig = criar_grafico_barras(
                df=df_anual,
                titulo="",
                label_y=label_y_grafico,
                barmode="group",
                height=450,
                data_label_format=data_label_format,
                color_map=CORES_MUNICIPIOS,
                hover_label_format=hover_label_format,
            )
            st.plotly_chart(fig, use_container_width=True)


def show_page_seguranca(df_seguranca, df_seguranca_taxa):
    # Dicionário de Indicadores Gerais
    INDICADORES_GERAIS = {
        "Homicídio Doloso": "homicidio_doloso",
        "Vítimas de Homicídio Doloso": "total_vitimas_homicidio_doloso",
        "Latrocínio": "latrocinio",
        "Furtos": "furtos",
        "Roubos": "roubos",
        "Furto de Veículo": "furto_veiculo",
        "Roubo de Veículo": "roubo_veiculo",
        "Estelionato": "estelionato",
    }

    # Dicionário de Violência Contra a Mulher
    INDICADORES_VIOLENCIA_MULHER = {
        "Feminicídio Consumado": "feminicidio_consumado",
        "Feminicídio Tentado": "feminicidio_tentado",
        "Ameaça": "ameaca",
        "Estupro": "estupro",
        "Lesão Corporal": "lesao_corporal",
    }

    # Dicionário de Drogas e Armas
    INDICADORES_DROGAS_ARMAS = {
        "Delitos com Armas e Munições": "delitos_armas_municoes",
        "Posse de Entorpecentes": "entorpecentes_posse",
        "Tráfico de Entorpecentes": "entorpecentes_trafico",
    }

    # Chama a função de display para cada seção
    display_secao_seguranca(
        df_seguranca,
        df_seguranca_taxa,
        "Indicadores Gerais",
        INDICADORES_GERAIS,
        "geral",
    )
    display_secao_seguranca(
        df_seguranca,
        df_seguranca_taxa,
        "Violência Contra a Mulher",
        INDICADORES_VIOLENCIA_MULHER,
        "mulher",
    )
    display_secao_seguranca(
        df_seguranca,
        df_seguranca_taxa,
        "Crimes Relacionados à Drogas e Armas",
        INDICADORES_DROGAS_ARMAS,
        "drogas",
    )


# ==============================================================================
# FUNÇÕES DA PÁGINA DE FINANÇAS
# ==============================================================================
@st.cache_data
def preparar_dados_siconfi(df, municipio_de_interesse, cod_conta):
    return (
        df[(df["municipio"] == municipio_de_interesse) & (df["cod_conta"] == cod_conta)]
        .sort_values(by=["municipio", "coluna", "periodo", "exercicio"])
        .assign(
            valor_milhoes=lambda x: x["valor"] / 1000000,
            valor_ano_anterior=lambda x: x.groupby(["municipio", "coluna", "periodo"])[
                "valor"
            ].shift(1),
        )
        .pipe(
            lambda x: x.assign(
                variacao_yoy=lambda x: np.where(
                    x["valor_ano_anterior"].notna() & x["valor_ano_anterior"] != 0,
                    (x["valor"] / x["valor_ano_anterior"] - 1) * 100,
                    np.nan,
                )
            )
        )
    )


def display_expander_siconfi(df, municipio_de_interesse, cod_conta, conta, expanded):
    df_siconfi_mun = preparar_dados_siconfi(
        df=df,
        municipio_de_interesse=municipio_de_interesse,
        cod_conta=f"{cod_conta}",
    )

    with st.expander(f"{conta} de {municipio_de_interesse} ", expanded=expanded):
        df_siconfi_mun_bimestre = df_siconfi_mun.query(
            "coluna == 'No Bimestre (b)'"
        ).pivot_table(
            index=["exercicio", "periodo"],
            columns="municipio",
            values="valor_milhoes",
            aggfunc="sum",
            fill_value=0,
        )
        df_siconfi_mun_bimestre.index = (
            df_siconfi_mun_bimestre.index.get_level_values("periodo")
            .astype(str)
            .str.zfill(2)
            + "-"
            + df_siconfi_mun_bimestre.index.get_level_values("exercicio")
            .astype(str)
            .str.slice(-2)
        )

        fig_siconfi = criar_grafico_barras(
            df=df_siconfi_mun_bimestre,
            titulo="",
            label_y=f"{conta} (Milhões R$)",
            barmode="group",
            height=450,
            data_label_format=".1f",
            hover_label_format=",.2f",
            color_map=CORES_MUNICIPIOS,
        )

        df_siconfi_mun_acum = df_siconfi_mun.query(
            "coluna == 'Até o Bimestre (c)'"
        ).pivot_table(
            index=["exercicio", "periodo"],
            columns="municipio",
            values="valor_milhoes",
            aggfunc="sum",
            fill_value=0,
        )
        df_siconfi_mun_acum.index = (
            df_siconfi_mun_acum.index.get_level_values("periodo")
            .astype(str)
            .str.zfill(2)
            + "-"
            + df_siconfi_mun_acum.index.get_level_values("exercicio")
            .astype(str)
            .str.slice(-2)
        )

        fig_siconfi_acum = criar_grafico_barras(
            df=df_siconfi_mun_acum,
            titulo="",
            label_y=f"{conta} Acumuladas (Milhões R$)",
            barmode="group",
            height=450,
            data_label_format=".1f",
            hover_label_format=",.2f",
            color_map=CORES_MUNICIPIOS,
        )

        df_siconfi_mun_yoy = df_siconfi_mun.query(
            "coluna == 'No Bimestre (b)'"
        ).pivot_table(
            index=["exercicio", "periodo"],
            columns="municipio",
            values="variacao_yoy",
            aggfunc="mean",
            fill_value=0,
        )
        df_siconfi_mun_yoy.index = (
            df_siconfi_mun_yoy.index.get_level_values("periodo")
            .astype(str)
            .str.zfill(2)
            + "-"
            + df_siconfi_mun_yoy.index.get_level_values("exercicio")
            .astype(str)
            .str.slice(-2)
        )

        fig_siconfi_yoy = criar_grafico_barras(
            df=df_siconfi_mun_yoy,
            titulo="",
            label_y="Variação Anual (%)",
            barmode="group",
            height=450,
            data_label_format=".1f",
            hover_label_format=",.2f",
            color_map=CORES_MUNICIPIOS,
        )

        df_siconfi_mun_acum_yoy = df_siconfi_mun.query(
            "coluna == 'Até o Bimestre (c)'"
        ).pivot_table(
            index=["exercicio", "periodo"],
            columns="municipio",
            values="variacao_yoy",
            aggfunc="mean",
            fill_value=0,
        )
        df_siconfi_mun_acum_yoy.index = (
            df_siconfi_mun_acum_yoy.index.get_level_values("periodo")
            .astype(str)
            .str.zfill(2)
            + "-"
            + df_siconfi_mun_acum_yoy.index.get_level_values("exercicio")
            .astype(str)
            .str.slice(-2)
        )

        fig_siconfi_acum_yoy = criar_grafico_barras(
            df=df_siconfi_mun_acum_yoy,
            titulo="",
            label_y="Variação Anual (%)",
            barmode="group",
            height=450,
            data_label_format=".1f",
            hover_label_format=",.2f",
            color_map=CORES_MUNICIPIOS,
        )

        view_mode = st.radio(
            "Selecione o modo de Visualização:",
            options=["No bimestre", "Até o bimestre"],
            horizontal=True,
            label_visibility="collapsed",
            key=f"view_mode_siconfi_{cod_conta}_yoy_mun",
        )
        if view_mode == "No bimestre":
            st.markdown(
                f"##### {conta} de {municipio_de_interesse} no Bimestre (Milhões R$)"
            )
            st.plotly_chart(fig_siconfi, width="stretch")
            st.markdown(
                f"##### {conta} Acumuladas até o Bimestre de {municipio_de_interesse} (Milhões R$)"
            )
            st.plotly_chart(fig_siconfi_yoy, width="stretch")

        elif view_mode == "Até o bimestre":
            if fig_siconfi_acum:
                st.markdown(
                    f"##### {conta} no Bimestre de {municipio_de_interesse} (Variação Anual %)"
                )
                st.plotly_chart(fig_siconfi_acum, width="stretch")
                st.markdown(
                    f"##### {conta} Acumuladas até o Bimestre de {municipio_de_interesse} (Variação Anual %)"
                )
                st.plotly_chart(fig_siconfi_acum_yoy, width="stretch")
            else:
                st.warning("Nenhum dado disponível para o gráfico.")


def show_page_financas(df, municipio_de_interesse):
    """Função principal que renderiza a página de Finanças Públicas."""

    # Receitas Correntes
    display_expander_siconfi(
        df=df,
        municipio_de_interesse=municipio_de_interesse,
        cod_conta="ReceitasCorrentes",
        conta="Receitas Correntes",
        expanded=False,
    )

    # Total de Receitas
    display_expander_siconfi(
        df=df,
        municipio_de_interesse=municipio_de_interesse,
        cod_conta="TotalReceitas",
        conta="Total de Receitas",
        expanded=False,
    )

    # Transferencias Correntes
    display_expander_siconfi(
        df=df,
        municipio_de_interesse=municipio_de_interesse,
        cod_conta="TransferenciasCorrentes",
        conta="Transferências Correntes",
        expanded=False,
    )

    # Impostos
    display_expander_siconfi(
        df=df,
        municipio_de_interesse=municipio_de_interesse,
        cod_conta="Impostos",
        conta="Impostos",
        expanded=False,
    )


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

# ==============================================================================
# BARRA LATERAL E NAVEGAÇÃO ENTRE PÁGINAS
# ==============================================================================

with st.sidebar:
    st.title("Filtros Globais")

    # --- FILTRO GLOBAL DE MUNICÍPIOS ---
    municipios_selecionados_global = st.multiselect(
        "Selecione o(s) município(s):",
        options=municipios_de_interesse,
        default=municipios_de_interesse,
        key="filtro_global_municipios",
    )

    st.markdown("---")
    pagina_selecionada = option_menu(
        menu_title="Menu",
        options=["Início", "Emprego", "Comércio Exterior", "Segurança", "Finanças"],
        icons=[
            "house-door-fill",
            "briefcase-fill",
            "globe2",
            "shield-shaded",
            "piggy-bank-fill",
        ],
        menu_icon="cast",
        default_index=0,
    )

    # ==============================================================================
# FILTRAGEM GLOBAL DOS DADOS
# ==============================================================================
# Filtra todos os dataframes necessários com base na seleção global da sidebar
df_caged_filtrado = df_caged[df_caged["municipio"].isin(municipios_selecionados_global)]
df_caged_cnae_filtrado = df_caged_cnae[
    df_caged_cnae["municipio"].isin(municipios_selecionados_global)
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
# ==============================================================================
# PÁGINAS
# ==============================================================================
if pagina_selecionada == "Início":
    show_page_home()

if pagina_selecionada == "Emprego":
    show_page_emprego(df_caged_filtrado, df_caged_cnae_filtrado, municipio_de_interesse)

elif pagina_selecionada == "Comércio Exterior":
    show_page_comex(
        df_comex_ano_filtrado,
        df_comex_mensal_filtrado,
        municipio_de_interesse=municipio_de_interesse,
    )

elif pagina_selecionada == "Segurança":
    st.title("Dashboard de Segurança")
    st.markdown("### Indicadores de Segurança Pública")
    show_page_seguranca(df_seguranca_filtrado, df_seguranca_taxa_filtrado)

elif pagina_selecionada == "Finanças":
    st.title("Dashboard de Finanças Públicas")
    st.markdown("### Indicadores de Finanças Públicas")
    show_page_financas(df_siconfi_filtrado, municipio_de_interesse)


manter_posicao_scroll()

# %%
