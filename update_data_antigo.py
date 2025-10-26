# %%
import pandas as pd
from sqlalchemy import create_engine, text
import json
from gspread_pandas import Spread
import os
from dotenv import load_dotenv


from src.queries import (
    QUERY_EMPREGO_MUNICIPIOS,
    QUERY_VINCULOS_MUNICIPIOS,
    QUERY_EMPREGO_CNAE,
    QUERY_VINCULOS_CNAE,
    QUERY_EMPREGO_GRAU_INSTRUCAO,
    QUERY_VINCULOS_GRAU_INSTRUCAO,
    QUERY_EMPREGO_FAIXA_ETARIA,
    QUERY_VINCULOS_FAIXA_ETARIA,
    QUERY_EMPREGO_RACA_COR,
    QUERY_VINCULOS_RACA_COR,
    QUERY_EMPREGO_SEXO,
    QUERY_VINCULOS_SEXO,
    QUERY_RENDA_SEXO,
    QUERY_RENDA_MUNICIPIOS,
    QUERY_RENDA_CNAE,
    QUERY_ESTABELECIMENTOS_MUNICIPIOS,
    QUERY_ESTABELECIMENTOS_CNAE,
    QUERY_ESTABELECIMENTOS_TAMANHO,
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
    QUERY_SAUDE_DESPESAS,
    QUERY_SAUDE_LEITOS,
    QUERY_SAUDE_MEDICOS,
    QUERY_SAUDE_VACINAS,
    QUERY_PIB_MUNICIPIOS,
    QUERY_POP_SEXO_IDADE,
    QUERY_POP_TOTAL_DENSIDADE,
    QUERY_FINANCAS,
    QUERY_INDICADORES_FINANCEIROS,
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


# ATUALIZACAO MENSAL


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
    QUERY_SAUDE_MENSAL,
    "dados_saude_mensal",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_FINANCAS,
    "dados_financas",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

# %%

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_INDICADORES_FINANCEIROS,
    "dados_indicadores_financeiros",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)


# %%
atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_POP_TOTAL_DENSIDADE,
    "dados_populacao_densidade",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_POP_SEXO_IDADE,
    "dados_populacao_sexo_idade",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_VINCULOS_MUNICIPIOS,
    "dados_vinculos_municipios",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)
# %%


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_VINCULOS_CNAE,
    "dados_vinculos_cnae",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_VINCULOS_GRAU_INSTRUCAO,
    "dados_vinculos_grau_instrucao",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_VINCULOS_FAIXA_ETARIA,
    "dados_vinculos_faixa_etaria",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_VINCULOS_RACA_COR,
    "dados_vinculos_raca_cor",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)


atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_VINCULOS_SEXO,
    "dados_vinculos_sexo",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_RENDA_SEXO,
    "dados_renda_sexo",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_RENDA_MUNICIPIOS,
    "dados_renda_municipios",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_RENDA_CNAE,
    "dados_renda_cnae",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)
# %%
atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_ESTABELECIMENTOS_MUNICIPIOS,
    "dados_estabelecimentos_municipios",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)
# %%
atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_ESTABELECIMENTOS_CNAE,
    "dados_estabelecimentos_cnae",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_ESTABELECIMENTOS_TAMANHO,
    "dados_estabelecimentos_tamanho",
    params={
        "municipio": municipio_de_interesse,
        "lista_anos": tuple(anos_de_interesse),
    },
)

# %%

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
    QUERY_SAUDE_VACINAS,
    "dados_saude_vacinas",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_SAUDE_DESPESAS,
    "dados_saude_despesas",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_SAUDE_LEITOS,
    "dados_saude_leitos",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)

atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_SAUDE_MEDICOS,
    "dados_saude_medicos",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
        "lista_anos": tuple(anos_de_interesse),
    },
)
# %%
atualizar_google_sheet(
    gspread_config,
    engine,
    QUERY_PIB_MUNICIPIOS,
    "dados_pib_municipios",
    params={
        "lista_municipios": tuple(municipios_de_interesse),
    },
)
