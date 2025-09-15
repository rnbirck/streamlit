import pandas as pd
from sqlalchemy import create_engine, text
import json
from gspread_pandas import Spread
from datetime import datetime
import os
from dotenv import load_dotenv

from queries import (
    QUERY_EMPREGO_MUNICIPIOS,
    QUERY_EMPREGO_CNAE,
    QUERY_EXP_ANUAL,
    QUERY_EXP_MENSAL,
    QUERY_EXP_MUN_SELECIONADO,
)

from app import (
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

print(f"\nProcesso concluído em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!")
