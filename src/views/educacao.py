import pandas as pd
import streamlit as st

from src.config import CORES_MUNICIPIOS
from src.utils import (
    criar_grafico_barras,
    titulo_centralizado,
)


@st.cache_data
def preparar_dados_grafico_educacao(
    df_filtrado, coluna_selecionada, dependencia, municipios_selecionados
):
    if df_filtrado.empty:
        return pd.DataFrame()

    df_processed = pd.DataFrame()

    if dependencia == "total":
        total_pre_calculado = df_filtrado[df_filtrado["dependencia"] == "total"]

        if not total_pre_calculado.empty:
            df_processed = total_pre_calculado
        else:
            df_processed = df_filtrado.groupby(
                ["ano", "municipio"], as_index=False
            ).agg({coluna_selecionada: "sum"})
    else:
        df_processed = df_filtrado[df_filtrado["dependencia"] == dependencia]

    if df_processed.empty:
        return pd.DataFrame()

    anos = sorted(df_filtrado["ano"].unique())

    df_grid = pd.MultiIndex.from_product(
        [anos, municipios_selecionados], names=["ano", "municipio"]
    ).to_frame(index=False)

    df_completo = pd.merge(
        df_grid, df_processed, on=["ano", "municipio"], how="left"
    ).fillna(0)

    df_graf = df_completo.pivot_table(
        index="ano",
        columns="municipio",
        values=coluna_selecionada,
        aggfunc="sum",
        fill_value=0,
    ).sort_index()

    return df_graf


@st.cache_data
def preparar_dados_grafico_ideb_municipio(
    df, indicador, categoria, dependencia, municipios_selecionados
):
    df_filtrado = df[
        (df["dependencia"] == dependencia)
        & (df["indicador"] == indicador)
        & (df["categoria"] == categoria)
    ]

    anos = sorted(df_filtrado["ano"].unique())

    df_grid = pd.MultiIndex.from_product(
        [anos, municipios_selecionados], names=["ano", "municipio"]
    ).to_frame(index=False)

    df_completo = pd.merge(
        df_grid, df_filtrado, on=["ano", "municipio"], how="left"
    ).fillna(0)

    df_graf = df_completo.pivot_table(
        index="ano",
        columns="municipio",
        values="valor",
        aggfunc="sum",
        fill_value=0,
    ).sort_index()

    return df_graf


@st.cache_data
def preparar_dados_tabela_ideb_escolas(df, categoria, dependencia):
    df_filtrado = df[
        (df["dependencia"] == dependencia) & (df["categoria"] == categoria)
    ]

    df_tab = (
        df_filtrado.pivot_table(
            index=["ano", "municipio", "escola"],
            columns="indicador",
            values="valor",
            aggfunc="sum",
        ).assign(nota_media=lambda x: (x["nota_mat"] + x["nota_port"]) / 2)
    ).sort_values(by="nota_media", ascending=False)

    return df_tab


def display_educacao(
    df_filtrado,
    municipios_selecionados,
    titulo_expander,
    key_prefix,
    dicionario_indicadores,
    dicionario_dependencia,
    label_y,
    data_label_format,
    hover_label_format,
):
    """Função genérica para exibir a seção de educacao matriculas e rendimento."""

    with st.expander(f"{titulo_expander}", expanded=False):
        titulo_centralizado(f"Indicadores de {titulo_expander}", 5)

        indicador_selecionado = st.selectbox(
            "Selecione um indicador:",
            options=list(dicionario_indicadores.keys()),
            key=f"{key_prefix}_selectbox_indicadores",
        )

        dependecia_selecionada = st.selectbox(
            "Selecione uma dependência:",
            options=list(dicionario_dependencia.keys()),
            key=f"{key_prefix}_selectbox_dependencia",
        )

        coluna_selecionada = dicionario_indicadores[indicador_selecionado]

        dependencia_selecionada = dicionario_dependencia[dependecia_selecionada]

        df_graf = preparar_dados_grafico_educacao(
            df_filtrado=df_filtrado,
            coluna_selecionada=coluna_selecionada,
            dependencia=dependencia_selecionada,
            municipios_selecionados=municipios_selecionados,
        )

        titulo_centralizado(
            f"{titulo_expander} - {indicador_selecionado} - {dependecia_selecionada}", 5
        )
        fig = criar_grafico_barras(
            df=df_graf,
            titulo="",
            label_y=f"{label_y}",
            barmode="group",
            height=500,
            data_label_format=f"{data_label_format}",
            hover_label_format=f"{hover_label_format}",
            color_map=CORES_MUNICIPIOS,
        )
        st.plotly_chart(fig, use_container_width=False)


def display_ideb_mun(
    df_filtrado,
    municipios_selecionados,
    titulo_expander,
    key_prefix,
    dicionario_indicadores,
    dicionario_dependencia,
    dicionario_categoria,
):
    """Função genérica para exibir a seção de IDEB MUNCIPIOS."""

    with st.expander(f"{titulo_expander}", expanded=False):
        titulo_centralizado(f"Indicadores do {titulo_expander}", 5)
        titulo_centralizado(
            "O Índice de Desenvolvimento da Educação Básica (Ideb) reúne, em um só indicador, os resultados de dois conceitos igualmente importantes para a qualidade da educação: o fluxo escolar e as médias de desempenho nas avaliações. O Ideb é calculado a partir dos dados sobre aprovação escolar, obtidos no Censo Escolar, e das médias de desempenho no Sistema de Avaliação da Educação Básica (Saeb).",
            6,
        )

        categoria_selecionada = st.selectbox(
            "Selecione uma etapa de ensino:",
            options=list(dicionario_categoria.keys()),
            key=f"{key_prefix}_selectbox_categoria",
        )

        indicador_selecionado = st.selectbox(
            "Selecione um indicador:",
            options=list(dicionario_indicadores.keys()),
            key=f"{key_prefix}_selectbox_indicadores",
        )

        dependencia_selecionada = st.selectbox(
            "Selecione uma dependência:",
            options=list(dicionario_dependencia.keys()),
            key=f"{key_prefix}_selectbox_dependencia",
        )

        categoria = dicionario_categoria[categoria_selecionada]

        indicador = dicionario_indicadores[indicador_selecionado]

        dependencia = dicionario_dependencia[dependencia_selecionada]

        df_graf = preparar_dados_grafico_ideb_municipio(
            df=df_filtrado,
            categoria=categoria,
            indicador=indicador,
            dependencia=dependencia,
            municipios_selecionados=municipios_selecionados,
        )

        if not df_graf.empty:
            df_graf.index = df_graf.index.astype(str)

        titulo_centralizado(
            f"{indicador_selecionado} - {dependencia_selecionada}",
            5,
        )
        fig = criar_grafico_barras(
            df=df_graf,
            titulo="",
            label_y=f"{indicador_selecionado}",
            barmode="group",
            height=500,
            data_label_format=",.1f",
            hover_label_format=",.1f",
            color_map=CORES_MUNICIPIOS,
        )
        st.plotly_chart(fig, use_container_width=False)


def display_ideb_escolas(
    df_filtrado,
    titulo_expander,
    key_prefix,
    dicionario_dependencia,
    dicionario_categoria,
):
    with st.expander(f"{titulo_expander}", expanded=False):
        titulo_centralizado(f"Indicadores do {titulo_expander}", 5)
        titulo_centralizado(
            "O Índice de Desenvolvimento da Educação Básica (Ideb) reúne, em um só indicador, os resultados de dois conceitos igualmente importantes para a qualidade da educação: o fluxo escolar e as médias de desempenho nas avaliações. O Ideb é calculado a partir dos dados sobre aprovação escolar, obtidos no Censo Escolar, e das médias de desempenho no Sistema de Avaliação da Educação Básica (Saeb).",
            6,
        )

        anos_disponiveis = sorted(df_filtrado["ano"].unique().tolist(), reverse=True)

        ANO_SELECIONADO = st.selectbox(
            "Selecione o ano para a tabela:",
            options=anos_disponiveis,
            index=0,
            key="hist_ano_escolas",
        )

        df_filtrado = df_filtrado[df_filtrado["ano"] == ANO_SELECIONADO]

        categoria_selecionada = st.selectbox(
            "Selecione uma etapa de ensino:",
            options=list(dicionario_categoria.keys()),
            key=f"{key_prefix}_selectbox_categoria",
        )

        dependencia_selecionada = st.selectbox(
            "Selecione uma dependência:",
            options=list(dicionario_dependencia.keys()),
            key=f"{key_prefix}_selectbox_dependencia",
        )

        categoria = dicionario_categoria[categoria_selecionada]

        dependencia = dicionario_dependencia[dependencia_selecionada]

        df_tab = preparar_dados_tabela_ideb_escolas(
            df_filtrado, categoria=categoria, dependencia=dependencia
        ).query("ideb != 0")

        df_tab_renomeado = (
            df_tab.rename_axis(
                index={"ano": "Ano", "municipio": "Município", "escola": "Escola"}
            )
            .rename(
                columns={
                    "ideb": "IDEB",
                    "nota_mat": "Nota SAEB Matemática",
                    "nota_port": "Nota SAEB Português",
                    "nota_media": "Nota SAEB Média",
                }
            )
            .style.format(lambda x: f"{x:,.2f}".replace(".", ","))
            .background_gradient(cmap="GnBu")
        )

        st.dataframe(df_tab_renomeado, width="stretch")


def show_page_educacao(
    df_matriculas,
    df_rendimento,
    df_ideb_municipio,
    df_ideb_escolas,
    municipios_selecionados_global,
):
    titulo_centralizado("Dashboard de Educação", 1)

    DEPENDENCIA = {
        "Total": "total",
        "Municipal": "municipal",
        "Estadual": "estadual",
        "Privada": "privada",
    }

    DEPENDENCIA_RENDIMENTO = {
        "Total": "total",
        "Pública": "publica",
        "Municipal": "municipal",
        "Estadual": "estadual",
        "Privada": "privada",
    }

    DEPENDENCIA_IDEB = {
        "Pública": "publica",
        "Municipal": "municipal",
        "Estadual": "estadual",
    }

    DEPENDENCIA_ESCOLAS = {
        "Municipal": "municipal",
        "Estadual": "estadual",
    }

    CATEGORIA_IDEB = {"Anos Iniciais": "anos_iniciais", "Anos Finais": "anos_finais"}

    INDICADOR_MATRICULA = {
        "Creche": "mat_infantil_creche",
        "Taxa - Creche": "taxa_matricula_creche",
        "Educação Básica": "mat_basico",
        "Educação Infantil": "mat_infantil",
        "Ensino Fundamental": "mat_fundamental",
        "Ensino Médio": "mat_medio",
        "Ensino Profissional": "mat_profissional",
        "EJA (Educação de Jovens e Adultos)": "mat_eja",
    }

    INDICADOR_DOCENTES = {
        "Educação Básica": "docentes_basico",
        "Educação Infantil": "docentes_infantil",
        "Ensino Fundamental": "docentes_fundamental",
        "Ensino Médio": "docentes_medio",
        "Ensino Profissional": "docentes_profissional",
        "EJA (Educação de Jovens e Adultos)": "docentes_eja",
    }

    INDICADOR_TURMAS = {
        "Educação Básica": "turmas_basico",
        "Educação Infantil": "turmas_infantil",
        "Ensino Fundamental": "turmas_fundamental",
        "Ensino Médio": "turmas_medio",
        "Ensino Profissional": "turmas_profissional",
        "EJA (Educação de Jovens e Adultos)": "turmas_eja",
    }

    INDICADORES_RENDIMENTO = {
        # --- Taxas de Aprovação ---
        "Taxa de Aprovação - Ensino Fundamental": "taxa_aprovacao_fundamental",
        "Taxa de Aprovação - Anos Iniciais do Ensino Fundamental": "taxa_aprovacao_fundamental_anos_iniciais",
        "Taxa de Aprovação - Anos Finais do Ensino Fundamental": "taxa_aprovacao_fundamental_anos_finais",
        # --- Taxas de Reprovação ---
        "Taxa de Reprovação - Ensino Fundamental": "taxa_reprovacao_fundamental",
        "Taxa de Reprovação - Anos Iniciais do Ensino Fundamental": "taxa_reprovacao_fundamental_anos_iniciais",
        "Taxa de Reprovação - Anos Finais do Ensino Fundamental": "taxa_reprovacao_fundamental_anos_finais",
        # --- Taxas de Abandono ---
        "Taxa de Abandono - Ensino Fundamental": "taxa_abandono_fundamental",
        "Taxa de Abandono - Anos Iniciais do Ensino Fundamental": "taxa_abandono_fundamental_anos_iniciais",
        "Taxa de Abandono - Anos Finais do Ensino Fundamental": "taxa_abandono_fundamental_anos_finais",
        # --- Taxas de Distorção Idade-Série ---
        "Taxa de Distorção Idade-Série - Ensino Fundamental": "taxa_distorcao_fundamental",
        "Taxa de Distorção Idade-Série - Anos Iniciais do Ensino Fundamental": "taxa_distorcao_fundamental_anos_iniciais",
        "Taxa de Distorção Idade-Série - Anos Finais do Ensino Fundamental": "taxa_distorcao_fundamental_anos_finais",
    }

    INDICADOR_ESCOLAS = {"Número de Escolas": "qntd_escolas"}

    INDICADOR_IDEB = {
        "Nota SAEB Português": "nota_port",
        "Nota SAEB Matemática": "nota_mat",
        "IDEB": "ideb",
    }

    titulo_centralizado("Clique nos menus abaixo para explorar os dados", 5)

    display_educacao(
        df_filtrado=df_matriculas,
        titulo_expander="Escolas",
        municipios_selecionados=municipios_selecionados_global,
        dicionario_dependencia=DEPENDENCIA,
        dicionario_indicadores=INDICADOR_ESCOLAS,
        key_prefix="escolas",
        label_y="Número de Escolas",
        hover_label_format=",.0f",
        data_label_format=",.0f",
    )

    display_educacao(
        df_filtrado=df_matriculas,
        titulo_expander="Matrículas",
        municipios_selecionados=municipios_selecionados_global,
        dicionario_dependencia=DEPENDENCIA,
        dicionario_indicadores=INDICADOR_MATRICULA,
        key_prefix="matriculas",
        label_y="Número de Matrículas",
        hover_label_format=",.0f",
        data_label_format=",.0f",
    )

    display_educacao(
        df_filtrado=df_matriculas,
        titulo_expander="Docentes",
        municipios_selecionados=municipios_selecionados_global,
        dicionario_dependencia=DEPENDENCIA,
        dicionario_indicadores=INDICADOR_DOCENTES,
        key_prefix="docentes",
        label_y="Número de Docentes",
        hover_label_format=",.0f",
        data_label_format=",.0f",
    )

    display_educacao(
        df_filtrado=df_matriculas,
        titulo_expander="Turmas",
        municipios_selecionados=municipios_selecionados_global,
        dicionario_dependencia=DEPENDENCIA,
        dicionario_indicadores=INDICADOR_TURMAS,
        key_prefix="turmas",
        label_y="Número de Turmas",
        hover_label_format=",.0f",
        data_label_format=",.0f",
    )

    display_educacao(
        df_filtrado=df_rendimento,
        titulo_expander="Taxas de Rendimento",
        municipios_selecionados=municipios_selecionados_global,
        dicionario_dependencia=DEPENDENCIA_RENDIMENTO,
        dicionario_indicadores=INDICADORES_RENDIMENTO,
        key_prefix="rendimento",
        label_y="Taxa",
        hover_label_format=",.1f",
        data_label_format=",.1f",
    )

    display_ideb_mun(
        df_filtrado=df_ideb_municipio,
        titulo_expander="IDEB - Municípios",
        municipios_selecionados=municipios_selecionados_global,
        dicionario_dependencia=DEPENDENCIA_IDEB,
        dicionario_indicadores=INDICADOR_IDEB,
        dicionario_categoria=CATEGORIA_IDEB,
        key_prefix="ideb",
    )

    display_ideb_escolas(
        df_filtrado=df_ideb_escolas,
        titulo_expander="IDEB - Escolas",
        dicionario_dependencia=DEPENDENCIA_ESCOLAS,
        dicionario_categoria=CATEGORIA_IDEB,
        key_prefix="ideb_escolas",
    )
