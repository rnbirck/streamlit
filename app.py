# %%
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# ==============================================================================
# IMPORTAÇÕES DE FUNÇÕES E DADOS
# ==============================================================================
from utils import carregar_css
from utils import (
    MESES_DIC,
    checar_ult_ano_completo,
    filtrar_municipio_ult_mes_ano,
    criar_grafico_barras,
    criar_tabela_formatada,
    manter_posicao_scroll,
    destacar_percentuais,
)
from data_loader import (
    carregar_dados_comex_mensal,
    carregar_dados_emprego_municipios,
    carregar_dados_emprego_cnae,
    carregar_dados_comex_anual,
    carregar_dados_comex_municipio,
)

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(layout="wide", page_title="Dashboard CEI ", page_icon="📊")
carregar_css("style.css")

# ==============================================================================
# DEFINIÇÕES GERAIS
# ==============================================================================
municipio_de_interesse = "São Leopoldo"
municipios_de_interesse = [
    "Porto Alegre",
    "Canoas",
    "Novo Hamburgo",
    "São Leopoldo",
    "Gravataí",
]
anos_de_interesse = range(2021, 2026)

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


def display_emprego_municipios_expander(df, municipios_interesse, municipio_interesse):
    """Exibe o expander com análise de saldo de emprego para múltiplos municípios."""
    with st.expander("Saldo de Emprego por Município", expanded=False):
        municipios_selecionados = st.multiselect(
            "Selecione o(s) município(s):",
            options=municipios_interesse,
            default=municipio_interesse,
            key="emprego_municipios_multiselect",
        )

        if not municipios_selecionados:
            st.warning("Por favor, selecione ao menos um município.")
            return None

        tab_hist, tab_mes, tab_acum, tab_anual = st.tabs(
            ["Histórico Mensal", "Mês Atual", "Acumulado no Ano", "Anual"],
        )

        df_filtrado = df[df["municipio"].isin(municipios_selecionados)]
        anos_disponiveis = sorted(df_filtrado["ano"].unique().tolist(), reverse=True)

        with tab_hist:
            ANO_SELECIONADO = st.selectbox(
                "Selecione o ano para o gráfico:",
                options=anos_disponiveis,
                index=0,
                key="hist_ano_emprego",
            )
            df_hist = df_filtrado[df_filtrado["ano"] == ANO_SELECIONADO]

            df_hist = (
                df_hist.assign(
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
                    values="saldo_movimentacao",
                    aggfunc="sum",
                    fill_value=0,
                )
                .sort_index()
            )

            fig_hist = criar_grafico_barras(
                df=df_hist,
                titulo=f"Saldo de Emprego Mensal em {ANO_SELECIONADO}",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=500,
                data_label_format=",.0f",
                hover_label_format=",.0f",
            )
            st.plotly_chart(fig_hist, width="stretch")

        with tab_mes:
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
            nome_mes = MESES_DIC[ult_mes]
            df_mes.index = nome_mes + "/" + df_mes.index.astype(str).str.slice(-2)
            fig_mes = criar_grafico_barras(
                df=df_mes,
                titulo=f"Saldo Mensal de Emprego em {MESES_DIC[ult_mes]}",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=500,
                data_label_format=",.0f",
                hover_label_format=",.0f",
            )
            st.plotly_chart(fig_mes, width="stretch")

        with tab_acum:
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
                "Jan-"
                + MESES_DIC[ult_mes][:3]
                + "/"
                + df_acum.index.astype(str).str.slice(-2)
            )
            fig_acum = criar_grafico_barras(
                df=df_acum,
                titulo=f"Saldo Acumulado de Emprego de Janeiro a {MESES_DIC[ult_mes]}",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=500,
                data_label_format=",.0f",
                hover_label_format=",.0f",
            )
            st.plotly_chart(fig_acum, width="stretch")

        with tab_anual:
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
            fig_anual = criar_grafico_barras(
                df=df_anual,
                titulo="Saldo Anual de Emprego",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=500,
                data_label_format=",.0f",
                hover_label_format=",.0f",
            )
            st.plotly_chart(fig_anual, width="stretch")

        return municipios_selecionados


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

            fig_grupo_ibge = criar_grafico_barras(
                df=df_tabela_grupo_ibge.T,
                titulo=f"Saldo Acumulado de Admissões e Demissões por Setor Econômico - {municipio_de_interesse}",
                label_y="Saldo de Admissões e Demissões",
                barmode="group",
                height=500,
                data_label_format=",.0f",
                hover_label_format=",.0f",
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
    municipios_de_interesse,
):
    """Função principal que renderiza a página de Emprego."""
    st.title("Dashboard de Emprego")
    st.markdown("### Análise de Saldo de Emprego")

    display_emprego_kpi_cards(df_caged, municipio_de_interesse)
    st.markdown("##### Clique nos menus abaixo para explorar os dados")

    display_emprego_municipios_expander(
        df_caged,
        municipios_de_interesse,
        municipio_de_interesse,
    )

    if not df_caged_cnae.empty:
        ult_ano = int(df_caged_cnae["ano"].max())
        ult_mes = int(df_caged_cnae[df_caged_cnae["ano"] == ult_ano]["mes"].max())
        display_emprego_cnae_expander(df_caged_cnae, ult_ano, ult_mes)


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


def display_comex_municipios_expander(
    df_mes, municipio_interesse, municipios_interesse
):
    """Exibe o expander com análise de exportações para múltiplos municípios."""
    with st.expander("Comércio Exterior por Município", expanded=False):
        municipios_selecionados = st.multiselect(
            "Selecione o(s) município(s):",
            options=municipios_interesse,
            default=municipio_interesse,
            key="comex_municipios_multiselect",
        )
        if not municipios_selecionados:
            st.warning("Por favor, selecione ao menos um município.")

        tab_hist, tab_mes, tab_acum, tab_anual = st.tabs(
            ["Histórico Mensal", "Mês Atual", "Acumulado no Ano", "Anual"],
        )

        df_filtrado = df_mes[
            (
                df_mes["municipio"].isin(municipios_selecionados)
                & df_mes["ano"].isin(anos_de_interesse)
            )
        ]
        anos_disponiveis = sorted(df_filtrado["ano"].unique().tolist(), reverse=True)

        with tab_hist:
            ANO_SELECIONADO = st.selectbox(
                "Selecione o ano para o gráfico:",
                options=anos_disponiveis,
                index=0,
                key="hist_ano_comex",
            )
            df_comex_hist = df_filtrado[df_filtrado["ano"] == ANO_SELECIONADO]
            if not ANO_SELECIONADO:
                st.warning("Por favor, selecione ao menos um ano.")
            df_comex_hist = (
                df_comex_hist.assign(
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

            fig_hist = criar_grafico_barras(
                df=df_comex_hist,
                titulo=f"Exportações em {ANO_SELECIONADO}",
                label_y="(Milhões de US$)",
                barmode="group",
                height=500,
                data_label_format=".1f",
                hover_label_format=",.2f",
            )
            st.plotly_chart(fig_hist, width="stretch")

        with tab_mes:
            ult_ano = df_filtrado["ano"].max()
            ult_mes = df_filtrado[df_filtrado["ano"] == ult_ano]["mes"].max()
            df_comex_mes = (
                df_filtrado[df_filtrado["mes"] == ult_mes]
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
            nome_mes = MESES_DIC[ult_mes]
            df_comex_mes.index = (
                nome_mes + "/" + df_comex_mes.index.astype(str).str.slice(-2)
            )
            fig_mes = criar_grafico_barras(
                df=df_comex_mes,
                titulo=f"Exportações em {MESES_DIC[ult_mes]}",
                label_y="(Milhões de US$)",
                barmode="group",
                height=500,
                data_label_format=".1f",
                hover_label_format=",.2f",
            )
            st.plotly_chart(fig_mes, width="stretch")

        with tab_acum:
            df_acum = (
                df_filtrado[df_filtrado["mes"] == ult_mes]
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
            df_acum.index = (
                "Jan-"
                + MESES_DIC[ult_mes][:3]
                + "/"
                + df_acum.index.astype(str).str.slice(-2)
            )
            fig_acum = criar_grafico_barras(
                df=df_acum,
                titulo=f"Exportações de Janeiro a {MESES_DIC[ult_mes]}",
                label_y="(Milhões de US$)",
                barmode="group",
                height=500,
                data_label_format=".1f",
                hover_label_format=",.2f",
            )
            st.plotly_chart(fig_acum, width="stretch")

        with tab_anual:
            ano_completo = checar_ult_ano_completo(df_filtrado)
            df_comex_ano = (
                df_filtrado[df_filtrado["ano"] <= ano_completo]
                .assign(exp_milhoes=lambda x: x["total_exp_mensal"] / 1_000_000)
                .pivot_table(
                    index="ano",
                    columns="municipio",
                    values="exp_milhoes",
                    aggfunc="sum",
                    fill_value=0,
                )
                .sort_index(ascending=False)
            )
            fig_anual = criar_grafico_barras(
                df=df_comex_ano,
                titulo="Exportações Anuais",
                label_y="(Milhões de US$)",
                barmode="group",
                height=500,
                data_label_format=",.1f",
                hover_label_format=",.2f",
            )
            st.plotly_chart(fig_anual, width="stretch")


def show_page_comex(
    df_comex_ano,
    df_comex_mensal,
    municipio_de_interesse,
    municipios_de_interesse,
):
    """Função principal que renderiza a página de Comércio Exterior."""

    display_comex_kpi_cards(df_comex_ano, df_comex_mensal, municipio_de_interesse)
    st.markdown("##### Clique nos menus abaixo para explorar os dados")

    display_comex_municipios_expander(
        df_mes=df_comex_mensal,
        municipio_interesse=municipio_de_interesse,
        municipios_interesse=municipios_de_interesse,
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
anos_comex = range(min(anos_de_interesse) - 1, max(anos_de_interesse) + 1)
df_comex_ano = carregar_dados_comex_anual(
    municipios=municipios_de_interesse, anos=anos_comex
)

df_comex_mensal = carregar_dados_comex_mensal(
    municipios=municipios_de_interesse, anos=anos_comex
)

df_comex_municipio = carregar_dados_comex_municipio(
    municipio=municipio_de_interesse, anos=anos_comex
)
# ==============================================================================
# BARRA LATERAL E NAVEGAÇÃO ENTRE PÁGINAS
# ==============================================================================

with st.sidebar:
    pagina_selecionada = option_menu(
        menu_title="Menu",
        options=["Emprego", "Comércio Exterior"],
        icons=["briefcase-fill", "globe2"],
        menu_icon="cast",
        default_index=0,
    )
# ==============================================================================
# PÁGINA DE EMPREGO
# ==============================================================================

if pagina_selecionada == "Emprego":
    # Chama a função principal da página de emprego, passando os dados e configurações
    show_page_emprego(
        df_caged, df_caged_cnae, municipio_de_interesse, municipios_de_interesse
    )

elif pagina_selecionada == "Comércio Exterior":
    st.title("Dashboard de Comércio Exterior")
    st.markdown("### Análise de Exportações")
    show_page_comex(
        df_comex_ano, df_comex_mensal, municipio_de_interesse, municipios_de_interesse
    )

    with st.expander(
        f"Comércio Exterior de {municipio_de_interesse} por Destino e Produto",
        expanded=False,
    ):
        tab_pais, tab_produto = st.tabs(
            ["País", "Produto"],
        )

        format_dict = {
            "Valor Exportado no Mês (US$)": lambda x: f"{x:,.0f}".replace(",", "."),
            "Valor Exportado Acumulado no Ano (US$)": lambda x: f"{x:,.0f}".replace(
                ",", "."
            ),
            "Variação YoY no Mês (%)": lambda x: f"{x:.1f}%".replace(".", ","),
            "Variação YoY Acumulada (%)": lambda x: f"{x:.1f}%".replace(".", ","),
        }

        with tab_pais:
            anos_disponiveis = sorted(
                df_comex_municipio["ano"].unique().tolist(), reverse=True
            )
            ANOS_SELECIONADOS = st.multiselect(
                "Selecione o(s) ano(s) para a tabela:",
                options=anos_disponiveis,
                default=anos_de_interesse[-1],
                key="anos_comex_pais_multiselect",
            )
            df_comex_pais = df_comex_municipio[
                df_comex_municipio["ano"].isin(ANOS_SELECIONADOS)
            ]
            if not ANOS_SELECIONADOS:
                st.warning("Por favor, selecione ao menos um ano.")

            df_comex_pais = (
                df_comex_pais.groupby(["ano", "mes", "pais"], as_index=False)
                .agg(
                    {
                        "valor_exp_mensal": "sum",
                        "valor_exp_mensal_ano_anterior": "sum",
                        "valor_acumulado_ano": "sum",
                        "valor_acumulado_ano_anterior": "sum",
                    }
                )
                .assign(
                    yoy_mensal=lambda x: (
                        x["valor_exp_mensal"] - x["valor_exp_mensal_ano_anterior"]
                    )
                    / x["valor_exp_mensal_ano_anterior"]
                    * 100,
                    yoy_acumulado=lambda x: (
                        x["valor_acumulado_ano"] - x["valor_acumulado_ano_anterior"]
                    )
                    / x["valor_acumulado_ano_anterior"]
                    * 100,
                )
                .sort_values(
                    by=["ano", "mes", "valor_exp_mensal"],
                    ascending=[False, False, False],
                )
                .query("ano in @anos_de_interesse")
                .drop(
                    columns=[
                        "valor_exp_mensal_ano_anterior",
                        "valor_acumulado_ano_anterior",
                    ]
                )
                .replace([float("inf"), -float("inf")], float("nan"))[
                    [
                        "ano",
                        "mes",
                        "pais",
                        "valor_exp_mensal",
                        "yoy_mensal",
                        "valor_acumulado_ano",
                        "yoy_acumulado",
                    ]
                ]
                .set_axis(
                    [
                        "Ano",
                        "Mês",
                        "País",
                        "Valor Exportado no Mês (US$)",
                        "Variação YoY no Mês (%)",
                        "Valor Exportado Acumulado no Ano (US$)",
                        "Variação YoY Acumulada (%)",
                    ],
                    axis=1,
                )
            )

            paises_options = sorted(df_comex_pais["País"].unique().tolist())

            paises_selecionados_filtro = st.multiselect(
                label="Filtrar a tabela por país (opcional):",
                options=paises_options,
                key="filtro_tabela_comex_pais",
            )

            df_comex_pais_exibir = df_comex_pais.copy()
            if paises_selecionados_filtro:
                df_comex_pais_exibir = df_comex_pais_exibir[
                    df_comex_pais_exibir["País"].isin(paises_selecionados_filtro)
                ]

            styled_df_pais = df_comex_pais_exibir.style.map(
                destacar_percentuais,
                subset=["Variação YoY no Mês (%)", "Variação YoY Acumulada (%)"],
            ).format(format_dict)

            st.dataframe(styled_df_pais, hide_index=True, use_container_width=True)

        with tab_produto:
            anos_disponiveis = sorted(
                df_comex_municipio["ano"].unique().tolist(), reverse=True
            )
            ANOS_SELECIONADOS = st.multiselect(
                "Selecione o(s) ano(s) para a tabela:",
                options=anos_disponiveis,
                default=anos_de_interesse[-1],
                key="anos_comex_produto_multiselect",
            )
            df_comex_produto = df_comex_municipio[
                df_comex_municipio["ano"].isin(ANOS_SELECIONADOS)
            ]
            if not ANOS_SELECIONADOS:
                st.warning("Por favor, selecione ao menos um ano.")
            df_comex_produto = (
                df_comex_produto.groupby(["ano", "mes", "desc_sh4"], as_index=False)
                .agg(
                    {
                        "valor_exp_mensal": "sum",
                        "valor_exp_mensal_ano_anterior": "sum",
                        "valor_acumulado_ano": "sum",
                        "valor_acumulado_ano_anterior": "sum",
                    }
                )
                .assign(
                    yoy_mensal=lambda x: (
                        x["valor_exp_mensal"] - x["valor_exp_mensal_ano_anterior"]
                    )
                    / x["valor_exp_mensal_ano_anterior"]
                    * 100,
                    yoy_acumulado=lambda x: (
                        x["valor_acumulado_ano"] - x["valor_acumulado_ano_anterior"]
                    )
                    / x["valor_acumulado_ano_anterior"]
                    * 100,
                )
                .sort_values(
                    by=["ano", "mes", "valor_exp_mensal"],
                    ascending=[False, False, False],
                )
                .query("ano in @anos_de_interesse")
                .drop(
                    columns=[
                        "valor_exp_mensal_ano_anterior",
                        "valor_acumulado_ano_anterior",
                    ]
                )
                .replace([float("inf"), -float("inf")], float("nan"))[
                    [
                        "ano",
                        "mes",
                        "desc_sh4",
                        "valor_exp_mensal",
                        "yoy_mensal",
                        "valor_acumulado_ano",
                        "yoy_acumulado",
                    ]
                ]
                .set_axis(
                    [
                        "Ano",
                        "Mês",
                        "Produto",
                        "Valor Exportado no Mês (US$)",
                        "Variação YoY no Mês (%)",
                        "Valor Exportado Acumulado no Ano (US$)",
                        "Variação YoY Acumulada (%)",
                    ],
                    axis=1,
                )
            )

            produtos_options = sorted(df_comex_produto["Produto"].unique().tolist())

            produtos_selecionados_filtro = st.multiselect(
                label="Filtrar a tabela por produto (opcional):",
                options=produtos_options,
                key="filtro_tabela_comex_produto",
            )

            df_comex_produto_exibir = df_comex_produto.copy()
            if produtos_selecionados_filtro:
                df_comex_produto_exibir = df_comex_produto_exibir[
                    df_comex_produto_exibir["Produto"].isin(
                        produtos_selecionados_filtro
                    )
                ]

            styled_df_produto = df_comex_produto_exibir.style.map(
                destacar_percentuais,
                subset=["Variação YoY no Mês (%)", "Variação YoY Acumulada (%)"],
            ).format(format_dict)

            st.dataframe(styled_df_produto, hide_index=True, use_container_width=True)

    # col1, col2 = st.columns([1, 2])
    # with col1:
    #     select_all_paises = st.checkbox(
    #         "Selecionar todos os países", value=False, key="select_all_paises"
    #     )
    #     if select_all_paises:
    #         default_selection_paises = paises_options
    #     else:
    #         default_selection_paises = []

    #     pais_selecionado = st.multiselect(
    #         "Selecione o(s) país(es):",
    #         options=paises_options,
    #         default=default_selection_paises,
    #         key="comex_paises_multiselect",
    #     )
    #     if not pais_selecionado:
    #         st.warning("Por favor, selecione ao menos um país.")

    # with col2:
    #     produtos_selecionados = []
    #     if pais_selecionado:
    #         df_comex_filtrado_pais = df_comex_municipio[
    #             df_comex_municipio["pais"].isin(pais_selecionado)
    #         ]
    #         produtos_filtrados_options = sorted(
    #             df_comex_filtrado_pais["desc_sh4"].unique().tolist()
    #         )
    #         select_all_produtos = st.checkbox(
    #             "Selecionar todos os produtos",
    #             value=False,
    #             key="select_all_produtos",
    #         )
    #         if select_all_produtos:
    #             default_selection_produtos = produtos_filtrados_options
    #         else:
    #             default_selection_produtos = []

    #         produtos_selecionados = st.multiselect(
    #             "Selecione o(s) produto(s):",
    #             options=produtos_filtrados_options,
    #             default=default_selection_produtos,
    #             key="comex_produtos_multiselect",
    #         )
    #         if not produtos_selecionados:
    #             st.warning("Por favor, selecione ao menos um produto.")

    # with tab_hist:
    #     ANO_SELECIONADO = st.selectbox(
    #         "Selecione o ano para o gráfico:",
    #         options=anos_de_interesse,
    #         index=len(anos_de_interesse) - 1,
    #         key="hist_ano_comex_mun",
    #     )

    #     if not pais_selecionado or not produtos_selecionados:
    #         st.warning("Por favor, selecione ao menos um país e um produto.")

    #     elif ANO_SELECIONADO:
    #         df_comex_hist = df_comex_municipio[
    #             (df_comex_municipio["ano"] == ANO_SELECIONADO)
    #             & (df_comex_municipio["pais"].isin(pais_selecionado))
    #             & (df_comex_municipio["desc_sh4"].isin(produtos_selecionados))
    #         ]
    #         df_comex_hist = (
    #             df_comex_hist.assign(
    #                 date=lambda x: pd.to_datetime(
    #                     x["ano"].astype(str)
    #                     + "-"
    #                     + x["mes"].astype(str).str.zfill(2)
    #                     + "-01"
    #                 ),
    #             )
    #             .pivot_table(
    #                 index="date",
    #                 # columns="pais",
    #                 values="valor_exp_mensal",
    #                 aggfunc="sum",
    #                 fill_value=0,
    #             )
    #             .sort_index()
    #             .apply(lambda x: x.round(2))
    #         )

    #         # st.dataframe(df_comex_hist)

    #         fig_hist = criar_grafico_barras(
    #             df=df_comex_hist,
    #             titulo=f"Exportações em {ANO_SELECIONADO}",
    #             label_y="(Milhões de US$)",
    #             barmode="group",
    #             height=500,
    #             data_label_format=",.0f",
    #             hover_label_format=",.0f",
    #         )
    #         st.plotly_chart(fig_hist, width="stretch")

    # with tab_produto:
    #     if not pais_selecionado or not produtos_selecionados:
    #         st.warning("Por favor, selecione ao menos um país e um produto.")

    #     df_comex_prod = (
    #         df_comex_municipio[
    #             (df_comex_municipio["pais"].isin(pais_selecionado))
    #             & (df_comex_municipio["desc_sh4"].isin(produtos_selecionados))
    #         ]
    #         .assign(
    #             yoy_mensal=lambda x: (
    #                 x["valor_exp_mensal"] / x["valor_exp_mensal_ano_anterior"] - 1
    #             )
    #             * 100,
    #             yoy_acumulado=lambda x: (
    #                 x["valor_acumulado_ano"] / x["valor_acumulado_ano_anterior"] - 1
    #             )
    #             * 100,
    #         )
    #         .drop(
    #             columns=[
    #                 "municipio",
    #                 "valor_exp_mensal_ano_anterior",
    #                 "valor_acumulado_ano_anterior",
    #             ]
    #         )
    #         .sort_values(
    #             by=["ano", "mes", "valor_exp_mensal"],
    #             ascending=[False, False, False],
    #         )
    #         .rename(
    #             columns={
    #                 "desc_sh4": "Produto",
    #                 "pais": "País",
    #                 "ano": "Ano",
    #                 "mes": "Mês",
    #                 "valor_exp_mensal": "Valor Exportado (US$)",
    #                 "yoy_mensal": "Variação Anual Mensal (%)",
    #                 "valor_acumulado_ano": "Valor Acumulado no Ano (US$)",
    #                 "yoy_acumulado": "Variação Anual Acumulada (%)",
    #             }
    #         )
    #     )
    #     st.dataframe(df_comex_prod.style.background_gradient(cmap="coolwarm_r"))

    # st.dataframe(
    #     df_comex_mun_filtrado := df_comex_municipio[
    #         (
    #             df_comex_municipio["pais"].isin(pais_selecionado)
    #             & df_comex_municipio["desc_sh4"].isin(produtos_selecionados)
    #         )
    #     ]
    # )
    # anos_disponiveis = sorted(df_filtrado["ano"].unique().tolist(), reverse=True)

    # with tab_hist:
    #     ANO_SELECIONADO = st.selectbox(
    #         "Selecione o ano para o gráfico:",
    #         options=anos_disponiveis,
    #         index=0,
    #         key="hist_ano_comex",
    #     )
    #     df_comex_hist = df_filtrado[df_filtrado["ano"] == ANO_SELECIONADO]
    #     if not ANO_SELECIONADO:
    #         st.warning("Por favor, selecione ao menos um ano.")
    #     df_comex_hist = (
    #         df_comex_hist.assign(
    #             date=lambda x: pd.to_datetime(
    #                 x["ano"].astype(str)
    #                 + "-"
    #                 + x["mes"].astype(str).str.zfill(2)
    #                 + "-01"
    #             ),
    #             exp_milhoes=lambda x: x["total_exp_mensal"] / 1_000_000,
    #         )
    #         .pivot_table(
    #             index="date",
    #             columns="municipio",
    #             values="exp_milhoes",
    #             aggfunc="sum",
    #             fill_value=0,
    #         )
    #         .sort_index()
    #         .apply(lambda x: x.round(2))
    #     )

    #     fig_hist = criar_grafico_barras(
    #         df=df_comex_hist,
    #         titulo=f"Exportações em {ANO_SELECIONADO}",
    #         label_y="(Milhões de US$)",
    #         barmode="group",
    #         height=500,
    #         data_label_format=".1f",
    #         hover_label_format=",.2f",
    #     )
    #     st.plotly_chart(fig_hist, width="stretch")

    # with tab_mes:
    #     ult_ano = df_filtrado["ano"].max()
    #     ult_mes = df_filtrado[df_filtrado["ano"] == ult_ano]["mes"].max()
    #     df_comex_mes = (
    #         df_filtrado[df_filtrado["mes"] == ult_mes]
    #         .assign(exp_milhoes=lambda x: x["total_exp_mensal"] / 1_000_000)
    #         .pivot_table(
    #             index="ano",
    #             columns="municipio",
    #             values="exp_milhoes",
    #             aggfunc="sum",
    #             fill_value=0,
    #         )
    #         .sort_index()
    #         .apply(lambda x: x.round(2))
    #     )
    #     nome_mes = MESES_DIC[ult_mes]
    #     df_comex_mes.index = (
    #         nome_mes + "/" + df_comex_mes.index.astype(str).str.slice(-2)
    #     )
    #     fig_mes = criar_grafico_barras(
    #         df=df_comex_mes,
    #         titulo=f"Exportações em {MESES_DIC[ult_mes]}",
    #         label_y="(Milhões de US$)",
    #         barmode="group",
    #         height=500,
    #         data_label_format=".1f",
    #         hover_label_format=",.2f",
    #     )
    #     st.plotly_chart(fig_mes, width="stretch")

    # with tab_acum:
    #     df_acum = (
    #         df_filtrado[df_filtrado["mes"] == ult_mes]
    #         .assign(exp_milhoes=lambda x: x["total_exp_acumulado"] / 1_000_000)
    #         .pivot_table(
    #             index="ano",
    #             columns="municipio",
    #             values="exp_milhoes",
    #             aggfunc="sum",
    #             fill_value=0,
    #         )
    #         .sort_index()
    #     )
    #     df_acum.index = (
    #         "Jan-"
    #         + MESES_DIC[ult_mes][:3]
    #         + "/"
    #         + df_acum.index.astype(str).str.slice(-2)
    #     )
    #     fig_acum = criar_grafico_barras(
    #         df=df_acum,
    #         titulo=f"Exportações de Janeiro a {MESES_DIC[ult_mes]}",
    #         label_y="(Milhões de US$)",
    #         barmode="group",
    #         height=500,
    #         data_label_format=".1f",
    #         hover_label_format=",.2f",
    #     )
    #     st.plotly_chart(fig_acum, width="stretch")

    # with tab_anual:
    #     ano_completo = checar_ult_ano_completo(df_filtrado)
    #     df_comex_ano = (
    #         df_filtrado[df_filtrado["ano"] <= ano_completo]
    #         .assign(exp_milhoes=lambda x: x["total_exp_mensal"] / 1_000_000)
    #         .pivot_table(
    #             index="ano",
    #             columns="municipio",
    #             values="exp_milhoes",
    #             aggfunc="sum",
    #             fill_value=0,
    #         )
    #         .sort_index(ascending=False)
    #     )
    #     fig_anual = criar_grafico_barras(
    #         df=df_comex_ano,
    #         titulo="Exportações Anuais",
    #         label_y="(Milhões de US$)",
    #         barmode="group",
    #         height=500,
    #         data_label_format=",.1f",
    #         hover_label_format=",.2f",
    #     )
    #     st.plotly_chart(fig_anual, width="stretch")

manter_posicao_scroll()
# %%
