import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime

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


def exportar_query_para_csv(engine, query, file_path, params=None):
    """Executa uma query e salva o resultado em um arquivo CSV."""
    try:
        df = pd.read_sql_query(text(query), engine, params=params)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df.to_csv(file_path, index=False)
        print(f"-> Arquivo '{file_path}' foi atualizado com sucesso.")
    except Exception as e:
        print(f"ERRO ao exportar para '{file_path}': {e}")


# --- CONFIGURAÇÃO DA CONEXÃO ---
usuario = "rnbirck"
senha = "ceiunisinos"
host = "localhost"
banco = "cei"
engine = create_engine(f"postgresql+psycopg2://{usuario}:{senha}@{host}/{banco}")

print("Iniciando o script de atualização de dados...")

# --- EXECUÇÃO DAS EXPORTAÇÕES ---
exportar_query_para_csv(
    engine,
    QUERY_EMPREGO_MUNICIPIOS,
    "data/emprego/caged_municipios.csv",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

exportar_query_para_csv(
    engine,
    QUERY_EMPREGO_CNAE,
    "data/emprego/caged_cnae.csv",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

exportar_query_para_csv(
    engine,
    QUERY_EXP_ANUAL,
    "data/comex/comex_anual.csv",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_comex),
    },
)

exportar_query_para_csv(
    engine,
    QUERY_EXP_MENSAL,
    "data/comex/comex_mensal.csv",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_comex),
    },
)

exportar_query_para_csv(
    engine,
    QUERY_EXP_MUN_SELECIONADO,
    "data/comex/comex_municipio.csv",
    params={"municipio": municipio_de_interesse, "lista_anos": tuple(anos_comex)},
)

print("\nDados atualizados localmente com sucesso!")
