import streamlit as st
import pandas as pd


from src.utils import (
    MESES_DIC,
    checar_ult_ano_completo,
    criar_grafico_barras,
    criar_tabela_formatada,
    criar_tabela_formatada_mes,
    criar_tabela_formatada_ano,
    titulo_centralizado,
)

from src.config import municipio_de_interesse, CORES_MUNICIPIOS, ordem_instrucao

# ==============================================================================
# FUNÇÕES DA PÁGINA DE EMPREGO
# ==============================================================================


def display_emprego_kpi_cards(df, municipio_interesse):
    """Exibe os cards de KPI de Emprego para um município específico."""

    titulo_centralizado(f"Saldo de Admissões e Demissões em {municipio_interesse}", 3)

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
    if df_filtrado.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), None, None

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

    ult_ano = df_filtrado["ano"].max()
    ult_mes = df_filtrado[df_filtrado["ano"] == ult_ano]["mes"].max()

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

    return df_hist, df_acum, df_anual, ult_ano, ult_mes


def display_emprego_municipios_expander(df, municipio_interesse):
    """Exibe o expander com análise de saldo de emprego para múltiplos municípios."""
    with st.expander(
        "Saldo de Emprego por Município",
        expanded=st.session_state.emprego_expander_state,
    ):
        df_hist, df_acum, df_anual, ult_ano, ult_mes = preparar_dados_graficos_emprego(
            df
        )
        anos_disponiveis = sorted(df["ano"].unique().tolist(), reverse=True)

        tab_hist, tab_acum, tab_anual = st.tabs(
            ["Histórico Mensal", "Acumulado no Ano", "Anual"],
        )

        with tab_hist:
            ANO_SELECIONADO = st.selectbox(
                "Selecione o ano para o gráfico:",
                options=anos_disponiveis,
                index=0,
                key="hist_ano_emprego",
            )

            df_hist = df_hist[df_hist.index.year == ANO_SELECIONADO]
            if not df_hist.empty:
                df_hist.index = [
                    f"{MESES_DIC[date.month][:3]}/{str(date.year)[2:]}"
                    for date in df_hist.index
                ]

            titulo_centralizado(f"Saldo de Emprego Mensal em {ANO_SELECIONADO}", 5)

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

        with tab_acum:
            titulo_centralizado(
                f"Saldo de Emprego de Janeiro a {MESES_DIC[ult_mes]}", 5
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
            titulo_centralizado("Saldo Emprego Anual", 5)

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


@st.cache_data
def preparar_dados_categoria_emprego(df_categoria, index_col, sort_order=None):
    """
    Prepara os DataFrames de Mês, Acumulado e Ano para uma categoria de emprego.
    Aplica ordenação customizada se fornecida.
    """
    if df_categoria.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Aplica ordenação categórica se uma ordem for especificada
    if sort_order:
        df_categoria[index_col] = pd.Categorical(
            df_categoria[index_col], categories=sort_order, ordered=True
        )
        df_categoria = df_categoria.dropna(subset=[index_col])

    ult_ano = int(df_categoria["ano"].max())
    ult_mes = int(df_categoria[df_categoria["ano"] == ult_ano]["mes"].max())

    # Delega a criação das tabelas para as funções já cacheadas de utils
    df_mes = criar_tabela_formatada_mes(
        df=df_categoria, index_col=index_col, ult_ano=ult_ano, ult_mes=ult_mes
    ).sort_index()
    df_acum = criar_tabela_formatada(
        df=df_categoria, index_col=index_col, ult_ano=ult_ano, ult_mes=ult_mes
    ).sort_index()
    df_anual = criar_tabela_formatada_ano(
        df=df_categoria, index_col=index_col
    ).sort_index()

    return df_mes, df_acum, df_anual


def display_emprego_categoria_expander(
    df_sexo, df_faixa_etaria, df_raca_cor, df_grau_instrucao, ult_mes
):
    """Exibe o expander com análise de saldo de emprego por categoria (versão otimizada)."""
    with st.expander(
        f"Saldo de Emprego por Categoria em {municipio_de_interesse}",
        expanded=False,
    ):
        tab_sexo, tab_raca_cor, tab_faixa_etaria, tab_grau_instrucao = st.tabs(
            ["Sexo", "Raça/Cor", "Faixa Etária", "Grau de Instrução"],
        )

        def render_categoria_tab(
            df, index_col, titulo, sort_order=None, color_map=None
        ):
            """Função interna para renderizar o conteúdo de cada aba de categoria."""
            df_mes, df_acum, df_anual = preparar_dados_categoria_emprego(
                df, index_col, sort_order
            )

            view_mode = st.radio(
                "Selecione a Análise:",
                options=["Último Mês", "Acumulado no Ano", "Anual"],
                horizontal=True,
                label_visibility="collapsed",
                key=f"view_mode_cat_{index_col}",
            )

            if view_mode == "Último Mês":
                titulo_centralizado(
                    f"Saldo de Emprego em {MESES_DIC[ult_mes]} por {titulo}",
                    5,
                )
                fig = criar_grafico_barras(
                    df=df_mes.T,
                    titulo="",
                    label_y="Saldo de Admissões e Demissões",
                    color_map=color_map,
                    data_label_format=",.0f",
                    hover_label_format=",.0f",
                )
                st.plotly_chart(fig, use_container_width=True)
            elif view_mode == "Acumulado no Ano":
                titulo_centralizado(
                    f"Saldo de Emprego de Janeiro a {MESES_DIC[ult_mes]} por {titulo}",
                    5,
                )
                fig = criar_grafico_barras(
                    df=df_acum.T,
                    titulo="",
                    label_y="Saldo de Admissões e Demissões",
                    color_map=color_map,
                    data_label_format=",.0f",
                    hover_label_format=",.0f",
                )
                st.plotly_chart(fig, use_container_width=True)
            elif view_mode == "Anual":
                titulo_centralizado(f"Saldo de Anual por {titulo}", 5)
                fig = criar_grafico_barras(
                    df=df_anual.T,
                    titulo="",
                    label_y="Saldo de Admissões e Demissões",
                    color_map=color_map,
                    data_label_format=",.0f",
                    hover_label_format=",.0f",
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab_sexo:
            render_categoria_tab(
                df_sexo,
                "sexo",
                "Sexo",
                color_map={"Masculino": "#4C82F7", "Feminino": "#FF6BE1"},
            )
        with tab_raca_cor:
            render_categoria_tab(df_raca_cor, "raca_cor", "Raça/Cor")
        with tab_faixa_etaria:
            render_categoria_tab(df_faixa_etaria, "faixa_etaria", "Faixa Etária")
        with tab_grau_instrucao:
            render_categoria_tab(
                df_grau_instrucao,
                "grau_instrucao",
                "Grau de Instrução",
                sort_order=ordem_instrucao,
            )


@st.cache_data
def preparar_dados_graficos_cnae(df_cnae, index_col):
    """
    Prepara os DataFrames para as visualizações de Mês, Acumulado e Ano para dados de CNAE.
    """
    df_mes, df_acum, df_anual = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    if not df_cnae.empty:
        ult_ano = df_cnae["ano"].max()
        ult_mes = df_cnae[df_cnae["ano"] == ult_ano]["mes"].max()

        df_mes = criar_tabela_formatada_mes(
            df=df_cnae, index_col=index_col, ult_ano=ult_ano, ult_mes=ult_mes
        )

        df_acum = criar_tabela_formatada(
            df=df_cnae, index_col=index_col, ult_ano=ult_ano, ult_mes=ult_mes
        )

        df_anual = criar_tabela_formatada_ano(df=df_cnae, index_col=index_col)

    return df_mes, df_acum, df_anual


def display_emprego_cnae_expander(df_cnae_foco):
    """Exibe o expander com análise de saldo de emprego por Setor e CNAE"""
    with st.expander(
        f"Saldo de Emprego por Setor Econômico em {municipio_de_interesse}",
        expanded=False,
    ):
        tab_setor, tab_grupo, tab_subclasse = st.tabs(
            ["Setor", "CNAE - Grupo", "CNAE - Subclasse"]
        )

        def render_cnae_content(index_col, titulo_categoria, show_graph=True):
            """Função interna para renderizar o conteúdo de cada aba de CNAE."""
            df_mes, df_acum, df_anual = preparar_dados_graficos_cnae(
                df_cnae_foco, index_col
            )

            ult_ano = int(df_cnae_foco["ano"].max())
            ult_mes = int(df_cnae_foco[df_cnae_foco["ano"] == ult_ano]["mes"].max())

            view_mode = st.radio(
                "Selecione a Análise:",
                options=["Último Mês", "Acumulado no Ano", "Anual"],
                horizontal=True,
                label_visibility="collapsed",
                key=f"view_mode_cnae_{index_col}",
            )

            df_map = {
                "Último Mês": df_mes,
                "Acumulado no Ano": df_acum,
                "Anual": df_anual,
            }
            df_selecionado = df_map[view_mode]

            if view_mode == "Último Mês":
                titulo_centralizado(
                    f"Saldo em {MESES_DIC[ult_mes]} por {titulo_categoria}", 5
                )
            elif view_mode == "Acumulado no Ano":
                titulo_centralizado(f"Saldo Acumulado no Ano por {titulo_categoria}", 5)
            elif view_mode == "Anual":
                titulo_centralizado(f"Saldo Anual por {titulo_categoria}", 5)

            # Lógica para exibir gráfico ou tabela
            if show_graph:
                fig = criar_grafico_barras(
                    df=df_selecionado.sort_index().T,
                    titulo="",
                    label_y="Saldo de Admissões e Demissões",
                    data_label_format=",.0f",
                    hover_label_format=",.0f",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(
                    df_selecionado.style.format("{:,.0f}").background_gradient(
                        cmap="coolwarm_r"
                    ),
                    use_container_width=True,
                )

        with tab_setor:
            render_cnae_content("grupo_ibge", show_graph=True, titulo_categoria="Setor")
        with tab_grupo:
            render_cnae_content(
                "grupo", show_graph=False, titulo_categoria="CNAE - Grupo"
            )
        with tab_subclasse:
            render_cnae_content(
                "subclasse", show_graph=False, titulo_categoria="CNAE - Subclasse"
            )


def show_page_emprego(
    df_caged,
    df_caged_cnae,
    df_caged_faixa_etaria,
    df_caged_raca_cor,
    df_caged_grau_instrucao,
    df_caged_sexo,
    municipio_de_interesse,
):
    """Função principal que renderiza a página de Emprego."""
    st.markdown(
        "<h1 style='text-align: center;'>Dashboard de Emprego</h1>",
        unsafe_allow_html=True,
    )
    ult_ano = int(df_caged["ano"].max())
    ult_mes = int(df_caged[df_caged["ano"] == ult_ano]["mes"].max())

    display_emprego_kpi_cards(df_caged, municipio_de_interesse)

    titulo_centralizado("Clique nos menus abaixo para explorar os dados", 5)

    display_emprego_municipios_expander(
        df_caged,
        municipio_de_interesse,
    )

    display_emprego_categoria_expander(
        df_faixa_etaria=df_caged_faixa_etaria,
        df_sexo=df_caged_sexo,
        df_raca_cor=df_caged_raca_cor,
        df_grau_instrucao=df_caged_grau_instrucao,
        ult_mes=ult_mes,
    )

    if not df_caged_cnae.empty:
        display_emprego_cnae_expander(df_caged_cnae)
