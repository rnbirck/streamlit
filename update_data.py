# %%
import pandas as pd
from sqlalchemy import create_engine, text
import json
from gspread_pandas import Spread
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


from src.queries import (
    QUERY_EMPREGO_MUNICIPIOS,
    QUERY_EMPREGO_CNAE,
    QUERY_EMPREGO_GRAU_INSTRUCAO,
    QUERY_EMPREGO_FAIXA_ETARIA,
    QUERY_EMPREGO_RACA_COR,
    QUERY_EMPREGO_SEXO,
    QUERY_EXP_ANUAL,
    QUERY_EXP_MENSAL,
    QUERY_EXP_MUN_SELECIONADO,
    QUERY_SEGURANCA,
    QUERY_SEGURANCA_TAXA,
    QUERY_CAD,
    QUERY_BOLSA_FAMILIA,
    QUERY_CNPJ_TOTAL,
    QUERY_CNPJ_CNAE,
    QUERY_MEI_TOTAL,
    QUERY_MEI_CNAE,
    QUERY_EDUCACAO_MATRICULAS,
    QUERY_EDUCACAO_RENDIMENTO,
    QUERY_EDUCACAO_IDEB_MUNICIPIOS,
    QUERY_EDUCACAO_IDEB_ESCOLAS,
    QUERY_SAUDE_MENSAL,
)

from src.config import (
    municipio_de_interesse,
    municipios_de_interesse,
    anos_de_interesse,
    anos_comex,
)

load_dotenv()

usuario = os.getenv("DB_USUARIO")
senha = os.getenv("DB_SENHA")
host = os.getenv("DB_HOST")
banco = os.getenv("DB_BANCO")

# --- CONFIGURAÇÃO DA CONEXÃO LOCAL ---
engine = create_engine(f"postgresql+psycopg2://{usuario}:{senha}@{host}/{banco}")


def atualizar_google_sheet(gspread_config, engine, query, sheet_name, params=None):
    """Executa uma query e envia o resultado para uma Google Sheet específica."""
    print(f"Processando: '{sheet_name}'...")
    try:
        df = pd.read_sql_query(text(query), engine, params=params)

        spread = Spread(sheet_name, config=gspread_config)

        spread.df_to_sheet(df, index=False, headers=True, start="A1", replace=True)
        print(f"-> Planilha '{sheet_name}' foi atualizada com sucesso.")
    except Exception as e:
        print(f"ERRO ao atualizar a planilha '{sheet_name}': {e}")


print("Iniciando o script de atualização de dados...")

try:
    with open("credentials.json", "r") as f:
        gspread_config = json.load(f)
    print("Arquivo de credenciais 'credentials.json' carregado com sucesso.")
except FileNotFoundError:
    print("ERRO: Arquivo 'credentials.json' não encontrado.")
    exit()
except Exception as e:
    print(f"Erro ao ler o arquivo de credenciais: {e}")
    exit()

print("\nIniciando o script de atualização de dados para o Google Sheets...")


def atualizar_gsheet_com_df(gspread_config, df, sheet_name):
    """Envia um DataFrame já existente para uma Google Sheet específica."""
    print(f"Processando DataFrame para: '{sheet_name}'...")
    try:
        spread = Spread(sheet_name, config=gspread_config)
        spread.df_to_sheet(df, index=False, headers=True, start="A1", replace=True)
        print(f"-> Planilha '{sheet_name}' foi atualizada com sucesso.")
    except Exception as e:
        print(f"ERRO ao atualizar a planilha '{sheet_name}': {e}")


# %%
atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EMPREGO_MUNICIPIOS,
    "dados_emprego_municipios",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EMPREGO_CNAE,
    "dados_emprego_cnae",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EMPREGO_GRAU_INSTRUCAO,
    "dados_emprego_grau_instrucao",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EMPREGO_FAIXA_ETARIA,
    "dados_emprego_faixa_etaria",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EMPREGO_RACA_COR,
    "dados_emprego_raca_cor",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EMPREGO_SEXO,
    "dados_emprego_sexo",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EXP_ANUAL,
    "dados_comex_anual",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_comex),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EXP_MENSAL,
    "dados_comex_mensal",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_comex),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EXP_MUN_SELECIONADO,
    "dados_comex_municipio",
    params={"municipio": municipio_de_interesse, "lista_anos": tuple(anos_comex)},
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_SEGURANCA,
    "dados_seguranca",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_SEGURANCA_TAXA,
    "dados_seguranca_taxa",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_CAD,
    "dados_cadastro_unico",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)
atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_BOLSA_FAMILIA,
    "dados_bolsa_familia",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_CNPJ_TOTAL,
    "dados_cnpj_total",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_CNPJ_CNAE,
    "dados_cnpj_cnae",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_MEI_TOTAL,
    "dados_mei_total",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_MEI_CNAE,
    "dados_mei_cnae",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EDUCACAO_MATRICULAS,
    "dados_educacao_matriculas",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EDUCACAO_RENDIMENTO,
    "dados_educacao_rendimento",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EDUCACAO_IDEB_MUNICIPIOS,
    "dados_educacao_ideb_municipios",
    params={"lista_municipios": tuple(municipios_de_interesse)},
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_EDUCACAO_IDEB_ESCOLAS,
    "dados_educacao_ideb_escolas",
    params={"lista_municipios": tuple(municipios_de_interesse)},
)
# %%
atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_SAUDE_MENSAL,
    "dados_saude_mensal",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

# %%
# --- FUNÇÃO PARA COLETAR DADOS DO SICONFI ---

id_municipios = pd.read_sql(
    text(
        "SELECT id_municipio, municipio FROM municipio WHERE municipio IN :lista_municipios"
    ),
    engine,
    params={"lista_municipios": tuple(municipios_de_interesse)},
)

print("\nColetando dados do SICONFI...")


def coletar_rreo(
    co_esfera,
    co_tipo_demonstrativo,
    anos,
    periodos,
    trad_mun,
    max_workers=20,
):
    """
    Coleta dados do RREO de forma flexível para diferentes periodicidades.

    Parâmetros:
    - co_tipo_demonstrativo: str (ex: 'RREO' ou 'RREO Simplificado')
    - periodicidade: str ('Q' ou 'S')
    - anos: list[int] (ex: [2021, 2022, 2023])
    - trad_mun: DataFrame com id_municipio e municipio
    - max_workers: int (número de threads para paralelismo)

    Retorna:
    - DataFrame consolidado com os dados
    """

    colunasInteresse = ["No Bimestre (b)", "Até o Bimestre (c)"]
    codContasInteresse = [
        "Impostos",
        "ReceitasCorrentes",
        "TransferenciasCorrentes",
        "TotalReceitas",
    ]
    # Gerar lista de tarefas
    tasks = [
        (row["id_municipio"], ano, periodo)
        for _, row in trad_mun.iterrows()
        for ano in anos
        for periodo in periodos
    ]

    # Função interna para buscar dados
    def fetch_data(task):
        id_ente, ano, periodo = task
        url = (
            f"https://apidatalake.tesouro.gov.br/ords/siconfi/tt//rreo?"
            f"an_exercicio={ano}&"
            f"nr_periodo={periodo}&co_tipo_demonstrativo={co_tipo_demonstrativo}&"
            f"co_esfera={co_esfera}&id_ente={id_ente}"
        )

        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    df = pd.DataFrame(data["items"])
                    df["id_ente"] = id_ente
                    return df
            else:
                print(f"Erro {response.status_code} em {id_ente}-{ano}-{periodo}")
        except Exception as e:
            print(f"Falha em {id_ente}-{ano}-{periodo}: {str(e)}")

        return pd.DataFrame()

    # Executar requisições
    df_list = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_data, task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            df = future.result()
            if not df.empty:
                df_list.append(df)

    # Consolidar e mergear com municípios
    if df_list:
        df_final = pd.concat(df_list, ignore_index=True)
        df_final = df_final.merge(
            trad_mun[["id_municipio", "municipio"]],
            left_on="id_ente",
            right_on="id_municipio",
            how="left",
        )
        df_final = df_final[
            (df_final["cod_conta"].isin(codContasInteresse))
            & (df_final["coluna"].isin(colunasInteresse))
        ]
        colunas_para_retornar = [
            "municipio",
            "exercicio",
            "periodo",
            "coluna",
            "cod_conta",
            "conta",
            "valor",
        ]
        return df_final[colunas_para_retornar]
    else:
        return pd.DataFrame()


df_rreo = coletar_rreo(
    co_esfera="M",
    co_tipo_demonstrativo="RREO",
    anos=anos_de_interesse,
    periodos=range(1, 7),  # Períodos de 1 a 6 (bimestral)
    trad_mun=id_municipios,
    max_workers=20,
)
atualizar_gsheet_com_df(gspread_config, df_rreo, "dados_siconfi_rreo")

print(f"\nProcesso concluído em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!")

# %%
