# src/views/home.py

import streamlit as st
from src.utils import MESES_DIC, BIMESTRE_DIC, titulo_centralizado
from src.config import municipio_de_interesse

# ==============================================================================
# FUNÇÕES DA PÁGINA HOME
# ==============================================================================


def show_page_home(
    df_emprego,
    df_comex,
    df_seguranca,
    df_assistencia_cad,
    df_assistencia_bolsa,
    df_financas,
    df_empresas,
    df_educacao_matriculas,
    df_educacao_ideb,
):
    """
    Renderiza a página inicial do dashboard com instruções, informações e datas de atualização.
    """

    titulo_centralizado("📊 Dashboard de Indicadores Municipais", 1)
    st.markdown("---")
    titulo_centralizado("Bem-vindo(a) ao painel de visualização de dados!", 2)
    st.markdown(
        f"""
        ##### Este dashboard foi desenvolvido para apresentar diversos indicadores socioeconômicos de **{municipio_de_interesse}**, permitindo a comparação direta com municípios vizinhos e de perfil semelhante.
        """
    )
    st.markdown("---")
    st.subheader("🧭 Como Utilizar o Dashboard")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """

            #### 1. Filtro Global de Municípios

            No topo da barra lateral à esquerda, você pode selecionar um ou mais municípios. Sua escolha será aplicada a **todas as páginas** do dashboard.

            """
        )

    with col2:
        st.markdown(
            """

            #### 2. Menus de Análise (`Expanders`)

            Em cada página, os dados são organizados em seções recolhíveis. Clique em qualquer seção para expandir e ver as análises detalhadas, que podem estar divididas em abas ou gráficos.

            """
        )

    st.markdown(
        """

        #### 3. Alternar Visualizações (`Toggles`)

        Em algumas seções, você encontrará botões (toggles) que permitem alternar a visualização dos dados entre **"Números Absolutos"** e **"Taxas"**, oferecendo diferentes perspectivas sobre a mesma informação.

        """
    )

    st.markdown("---")
    st.subheader("📂 Sobre as Páginas e Atualizações")

    # --- Lógica para encontrar as datas mais recentes ---
    try:
        ult_ano_emprego = df_emprego["ano"].max()
        ult_mes_emprego = df_emprego[df_emprego["ano"] == ult_ano_emprego]["mes"].max()
        data_emprego = f"{MESES_DIC[ult_mes_emprego]} de {ult_ano_emprego}"
    except Exception:
        data_emprego = "Não disponível"

    try:
        ult_ano_comex = df_comex["ano"].max()
        ult_mes_comex = df_comex[df_comex["ano"] == ult_ano_comex]["mes"].max()
        data_comex = f"{MESES_DIC[ult_mes_comex]} de {ult_ano_comex}"
    except Exception:
        data_comex = "Não disponível"

    try:
        ult_ano_seg = df_seguranca["ano"].max()
        ult_mes_seg = df_seguranca[df_seguranca["ano"] == ult_ano_seg]["mes"].max()
        data_seguranca = f"{MESES_DIC[ult_mes_seg]} de {ult_ano_seg}"
    except Exception:
        data_seguranca = "Não disponível"

    try:
        ult_ano_cad = df_assistencia_cad["ano"].max()
        ult_mes_cad = df_assistencia_cad[df_assistencia_cad["ano"] == ult_ano_cad][
            "mes"
        ].max()
        data_cad = f"{MESES_DIC[ult_mes_cad]} de {ult_ano_cad}"

        ult_ano_bolsa = df_assistencia_bolsa["ano"].max()
        ult_mes_bolsa = df_assistencia_bolsa[
            df_assistencia_bolsa["ano"] == ult_ano_bolsa
        ]["mes"].max()
        data_bolsa = f"{MESES_DIC[ult_mes_bolsa]} de {ult_ano_bolsa}"
    except Exception:
        data_cad = "Não disponível"
        data_bolsa = "Não disponível"

    try:
        ult_ano_fin = df_financas["exercicio"].max()
        ult_bim_fin = df_financas[df_financas["exercicio"] == ult_ano_fin][
            "periodo"
        ].max()
        data_financas = f"{BIMESTRE_DIC[ult_bim_fin]} de {ult_ano_fin}"
    except Exception:
        data_financas = "Não disponível"

    try:
        ult_ano_empresas = df_empresas["ano"].max()
        ult_mes_empresas = df_empresas[df_empresas["ano"] == ult_ano_empresas][
            "mes"
        ].max()
        data_empresas = f"{MESES_DIC[ult_mes_empresas]} de {ult_ano_empresas}"
    except Exception:
        data_empresas = "Não disponível"
    try:
        data_matriculas = str(df_educacao_matriculas["ano"].max())
        data_ideb = str(df_educacao_ideb["ano"].max())
    except Exception:
        data_matriculas, data_ideb = "Não disponível", "Não disponível"

    # --- Exibição das descrições ---
    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown(
            f"""
            #### 💼 Emprego
            Analisa o mercado de trabalho formal através dos dados do **CAGED**. Explore o saldo de admissões e demissões e a análise por setor econômico.
            
            *Frequência: **Mensal** | Últimos dados: **{data_emprego}***
            """
        )
        st.markdown("---")
        st.markdown(
            f"""
            #### 🛡️ Segurança Pública
            Reúne os principais indicadores de criminalidade divulgados pela **SSP/RS**, com visualização em números absolutos e taxas por 100 mil habitantes.
            
            *Frequência: **Mensal** | Últimos dados: **{data_seguranca}***
            """
        )
        st.markdown("---")
        st.markdown(
            f"""
            #### ❤️ Assistência Social
            Apresenta informações sobre a população em vulnerabilidade social, com dados do **Cadastro Único (CadÚnico)** e do programa **Novo Bolsa Família**.
            
            *Frequência: **Mensal** | Últimos dados: **CadÚnico:** **{data_cad}** | **Novo Bolsa Família:** **{data_bolsa}***
            """
        )

    with col_b:
        st.markdown(
            f"""
            #### ✈️ Comércio Exterior
            Apresenta os dados de exportação com base nos dados do **Comexstat**. É possível analisar os valores totais, os principais produtos exportados e os países de destino.
            
            *Frequência: **Mensal** | Últimos dados: **{data_comex}***
            """
        )
        st.markdown("---")
        st.markdown(
            f"""
            #### 💰 Finanças Públicas
            Apresenta dados fiscais com base nos relatórios do **SICONFI**. Explore indicadores como Receitas Correntes e Total de Receitas.
            
            *Frequência: **Bimestral** | Últimos dados: **{data_financas}***
            """
        )
        st.markdown("---")
        st.markdown(
            f"""
            #### 🏢 Empresas Ativas
            Apresenta o número de CNPJs e MEIs ativos com base nos dados abertos da **Receita Federal**. Permite analisar a evolução e a concentração por setor econômico (CNAE).
            
            *Frequência de Atualização: **Mensal** | Últimos dados: **{data_empresas}***
            """
        )
        st.markdown("---")
        st.markdown(
            f"""
            #### 🎓 Educação
            Consolida indicadores educacionais do **Censo Escolar** e do **INEP (IDEB)**, incluindo matrículas, docentes, turmas, taxas de rendimento e notas de avaliação do SAEB.
            
            *Frequência: **Anual (Censo)** e **Bienal (IDEB)** | Últimos dados: **Censo:** **{data_matriculas}** | **IDEB:** **{data_ideb}***
            """
        )
