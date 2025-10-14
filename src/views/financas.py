import streamlit as st
import numpy as np

# ==============================================================================
# IMPORTAÇÕES DE FUNÇÕES E DADOS
# ==============================================================================

from src.utils import criar_grafico_barras, titulo_centralizado

from src.config import (
    CORES_MUNICIPIOS,
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
    titulo_centralizado("Dashboard de Finanças Públicas", 1)
    titulo_centralizado("Indicadores de Finanças Públicas", 3)
    titulo_centralizado("Clique nos menus abaixo para explorar os dados", 5)

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
