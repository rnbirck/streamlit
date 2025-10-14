import streamlit as st
import pandas as pd

from src.utils import (
    MESES_DIC,
    titulo_centralizado,
    calcular_yoy,
    filtrar_municipio_ult_mes_ano,
    criar_grafico_barras,
    criar_tabela_formatada,
)

from src.config import (
    municipio_de_interesse,
    anos_de_interesse,
    CORES_MUNICIPIOS,
)


# ==============================================================================
# FUNÇÕES DA PÁGINA DE EMPRESAS ATIVAS
# ==============================================================================


def display_cnpj_kpi_cards(df_cnpj, df_mei, municipio_de_interesse):
    """Exibe os cards de KPI de Empresas Ativas para um município específico."""
    titulo_centralizado(f"Número de Empresas Ativas em {municipio_de_interesse}", 3)
    ult_ano = df_cnpj["ano"].max()
    ult_mes = df_cnpj[df_cnpj["ano"] == ult_ano]["mes"].max()

    cnpj_ativos_ult_mes = filtrar_municipio_ult_mes_ano(
        df_cnpj, municipio_de_interesse
    )["empresas_ativas"].sum()
    cnpj_ativos_yoy = calcular_yoy(
        df=df_cnpj,
        ultimo_ano=ult_ano,
        ultimo_mes=ult_mes,
        coluna="empresas_ativas",
        round=1,
    )
    mei_ativos_ult_mes = filtrar_municipio_ult_mes_ano(df_mei, municipio_de_interesse)[
        "empresas_ativas"
    ].sum()
    mei_ativos_yoy = calcular_yoy(
        df=df_mei,
        ultimo_ano=ult_ano,
        ultimo_mes=ult_mes,
        coluna="empresas_ativas",
        round=1,
    )
    col1, col2 = st.columns(2)

    col1.metric(
        label=f"CNPJ Ativos em {MESES_DIC[ult_mes]} de {ult_ano}",
        value=f"{cnpj_ativos_ult_mes:,.0f}".replace(",", "."),
        delta=f"{cnpj_ativos_yoy}%".replace(".", ","),
        help="Taxa de Variação percentual em relação ao mesmo mês do ano anterior",
        border=True,
    )
    col2.metric(
        label=f"MEI / Simples Ativos em {MESES_DIC[ult_mes]} de {ult_ano}",
        value=f"{mei_ativos_ult_mes:,.0f}".replace(",", "."),
        delta=f"{mei_ativos_yoy}%".replace(".", ","),
        help="Taxa de Variação percentual em relação ao mesmo mês do ano anterior",
        border=True,
    )


@st.cache_data
def preparar_dados_grafico_empresas_ativas(df, df_cnae):
    df_graf_total = pd.DataFrame()
    df_graf_setor = pd.DataFrame()
    df_tab_cnae = pd.DataFrame()

    df_graf_total = (
        df.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            columns="municipio",
            values="empresas_ativas",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )

    df_graf_setor = (
        df_cnae.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="date",
            columns="grupo_ibge",
            values="empresas_ativas",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
    )

    ult_ano = df_cnae["ano"].max()
    ult_mes = df_cnae[df_cnae["ano"] == ult_ano]["mes"].max()
    date_sort = pd.to_datetime(f"{ult_ano}-{ult_mes:02d}-01")

    df_tab_cnae = (
        df_cnae.assign(
            date=lambda x: pd.to_datetime(
                x["ano"].astype(str) + "-" + x["mes"].astype(str).str.zfill(2) + "-01"
            )
        )
        .pivot_table(
            index="grupo",
            columns="date",
            values="empresas_ativas",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_values(by=date_sort, ascending=False)
    )

    novos_nomes_colunas = [
        f"{MESES_DIC[data.month][:3]}/{str(data.year)[-2:]}"
        for data in df_tab_cnae.columns
    ]

    df_tab_cnae.columns = novos_nomes_colunas
    df_tab_cnae.index.name = "CNAE - Grupo"

    return df_graf_total, df_graf_setor, df_tab_cnae


def display_empresas_ativas_expander(df, df_cnae, titulo_expander, key_prefix):
    with st.expander(f"{titulo_expander}", expanded=False):
        df_graf_total, df_graf_cnae, df_tab_cnae = (
            preparar_dados_grafico_empresas_ativas(df=df, df_cnae=df_cnae)
        )

        anos_disponiveis = sorted(df["ano"].unique().tolist(), reverse=True)
        col1, col2 = st.columns(2)
        with col1:
            if not anos_disponiveis:
                st.warning("Nenhum dado disponível para os filtros selecionados.")
            else:
                ANO_SELECIONADO = st.selectbox(
                    "Selecione o ano para o gráfico:",
                    options=anos_disponiveis,
                    index=0,
                    key=f"selecionar_ano_{key_prefix}",
                )
        tab_total, tab_setor, tab_cnae = st.tabs(
            [f"{titulo_expander} por Município", "Setor", "CNAE"]
        )
        df_graf_total_anos = df_graf_total[df_graf_total.index.year == ANO_SELECIONADO]
        df_graf_total_anos.index = [
            f"{MESES_DIC[date.month][:3]}/{str(date.year)[2:]}"
            for date in df_graf_total_anos.index
        ]

        df_graf_cnae_anos = df_graf_cnae[df_graf_cnae.index.year == ANO_SELECIONADO]
        df_graf_cnae_anos.index = [
            f"{MESES_DIC[date.month][:3]}/{str(date.year)[2:]}"
            for date in df_graf_cnae_anos.index
        ]

        with tab_total:
            titulo_centralizado(
                f"Quantidade de {titulo_expander} em {ANO_SELECIONADO}", 5
            )
            fig_total = criar_grafico_barras(
                df=df_graf_total_anos,
                titulo="",
                label_y="Quantidade de Empresas Ativas",
                barmode="group",
                height=500,
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_map=CORES_MUNICIPIOS,
            )
            st.plotly_chart(fig_total, use_container_width=True)

        with tab_setor:
            titulo_centralizado(
                f"{titulo_expander} por Setor em {municipio_de_interesse} - {ANO_SELECIONADO}",
                5,
            )
            fig_setor = criar_grafico_barras(
                df=df_graf_cnae_anos,
                titulo="",
                label_y="Quantidade de Empresas Ativas",
                barmode="stack",
                height=500,
                data_label_format=",.0f",
                hover_label_format=",.0f",
                color_map=CORES_MUNICIPIOS,
            )
            st.plotly_chart(fig_setor, use_container_width=True)

        with tab_cnae:
            colunas_do_ano = [
                col
                for col in df_tab_cnae.columns
                if col.endswith(f"/{str(ANO_SELECIONADO)[-2:]}")
            ]
            df_tab_cnae_filtrada = df_tab_cnae[colunas_do_ano]

            titulo_centralizado(
                f"{titulo_expander} por CNAE em {municipio_de_interesse} - {ANO_SELECIONADO}",
                5,
            )

            tab_cnae = df_tab_cnae_filtrada.style.format(
                lambda x: f"{x:,.0f}".replace(",", ".")
            ).background_gradient(cmap="GnBu")
            st.dataframe(tab_cnae, width="stretch")


def show_page_empresas_ativas(
    df_cnpj, df_cnpj_cnae, df_mei, df_mei_cnae, municipio_de_interesse
):
    titulo_centralizado("Dashboard de Empresas Ativas", 1)
    display_cnpj_kpi_cards(
        df_cnpj=df_cnpj, df_mei=df_mei, municipio_de_interesse=municipio_de_interesse
    )
    titulo_centralizado("Clique nos menus abaixo para explorar os dados", 5)
    display_empresas_ativas_expander(
        df=df_cnpj,
        df_cnae=df_cnpj_cnae,
        titulo_expander="CNPJ Ativos",
        key_prefix="cnpj_ativos",
    )
    display_empresas_ativas_expander(
        df=df_mei,
        df_cnae=df_mei_cnae,
        titulo_expander="MEI / Simples Ativos",
        key_prefix="mei_ativos",
    )
