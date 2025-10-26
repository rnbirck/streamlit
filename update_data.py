# %%
import os
import time
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from supabase import create_client, Client
import numpy as np
from src.config import (
    anos_de_interesse,
    anos_comex,
)

# --- CARREGAR VARIÁVEIS DE AMBIENTE DO ARQUIVO .env ---
load_dotenv()

# CONFIGURAÇÃO DA CONEXÃO LOCAL ---
DB_USUARIO = os.getenv("DB_USUARIO")
DB_SENHA = os.getenv("DB_SENHA")
DB_HOST = os.getenv("DB_HOST")
DB_BANCO = os.getenv("DB_BANCO")

try:
    local_engine = create_engine(
        f"postgresql+psycopg2://{DB_USUARIO}:{DB_SENHA}@{DB_HOST}/{DB_BANCO}"
    )
    print("✅ Conexão com o banco de dados local estabelecida com sucesso.")
except Exception as e:
    print(f"❌ Erro ao conectar ao banco de dados local: {e}")
    exit()

# --- 2. CONFIGURAÇÃO DA CONEXÃO SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print(
        "❌ Erro: Variáveis SUPABASE_URL ou SUPABASE_KEY não encontradas no arquivo .env."
    )
    exit()

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conexão com o Supabase estabelecida com sucesso.")
except Exception as e:
    print(f"❌ Erro ao conectar ao Supabase: {e}")
    exit()

# ===================================================================
# --- 3. DEFINIÇÃO DOS FILTROS ---
# ===================================================================

MUNICIPIOS_PRINCIPAIS = ("São Leopoldo", "Esteio", "Nova Santa Rita", "Montenegro")
MUNICIPIOS_AUXILIARES = (
    "Canoas",
    "Gravataí",
    "Novo Hamburgo",
    "Cachoeirinha",
    "Guaíba",
    "Sapucaia do Sul",
    "Portão",
    "São Sebastião do Caí",
    "Taquari",
)
TODOS_OS_MUNICIPIOS = MUNICIPIOS_PRINCIPAIS + MUNICIPIOS_AUXILIARES

# ===================================================================
#  QUERIES
# ===================================================================

# Queries que usam :lista_municipios (TODOS_OS_MUNICIPIOS)
QUERY_EMPREGO_MUNICIPIOS = """
SELECT 
    t1.ano, t1.mes, t2.municipio, SUM(t1.saldo_movimentacao) AS saldo_movimentacao
FROM caged_prefeituras t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t2.municipio
ORDER BY t1.ano, t1.mes;
"""
QUERY_VINCULOS_MUNICIPIOS = """
SELECT 
    t1.ano, t2.municipio, SUM(t1.vinculos_ativos) AS vinculos_ativos
FROM rais_vinculos t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t2.municipio;
"""
QUERY_RENDA_MUNICIPIOS = """
with agregado_renda AS (
    SELECT t1.ano, t2.municipio,
           SUM(t1.massa_salarial_dezembro) AS massa_salarial_remuneracao_media_dezembro,
           SUM(t1.massa_salarial_dezembro_sm) AS massa_salarial_remuneracao_media_dezembro_sm
    FROM rais_renda t1
    JOIN municipio t2 on t1.id_municipio = t2.id_municipio
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t2.municipio
), agregado_vinculos AS (
    SELECT t1.ano, t2.municipio, SUM(t1.vinculos_ativos) AS vinculos_ativos
    FROM rais_vinculos t1
    JOIN municipio t2 on t1.id_municipio = t2.id_municipio
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t2.municipio
)
SELECT t1.ano, t1.municipio,
       t1.massa_salarial_remuneracao_media_dezembro / NULLIF(t2.vinculos_ativos, 0) AS remuneracao_media_dezembro,
       t1.massa_salarial_remuneracao_media_dezembro_sm / NULLIF(t2.vinculos_ativos, 0) AS valor_remuneracao_media_dezembro_sm
FROM agregado_renda t1
JOIN agregado_vinculos t2 ON t1.ano = t2.ano AND t1.municipio = t2.municipio;
"""
QUERY_ESTABELECIMENTOS_MUNICIPIOS = """
SELECT 
    t1.ano, t2.municipio, SUM(t1.qntd_estabelecimentos) AS qntd_estabelecimentos
FROM rais_estabelecimentos t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t2.municipio;
"""
QUERY_EXP_ANUAL = """
WITH tabDadosAnuais AS (
    SELECT t1.ano, t2.municipio, SUM(t1.valor) AS total_exp_anual
    FROM comexstat_mun t1
    JOIN municipio t2 ON t1.id_municipio = t2.id_municipio::BIGINT
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t2.municipio
),
tabComparativoAnual AS (
    SELECT ano, municipio, total_exp_anual,
           LAG(total_exp_anual, 1, 0) OVER (PARTITION BY municipio ORDER BY ano) AS exp_ano_anterior
    FROM tabDadosAnuais
)
SELECT ano, municipio, total_exp_anual, exp_ano_anterior,
    ROUND(CAST(((total_exp_anual::numeric / NULLIF(exp_ano_anterior, 0)) - 1) * 100 AS numeric), 2) AS perc_var_ano_anterior
FROM tabComparativoAnual
ORDER BY ano DESC, total_exp_anual DESC;
"""
QUERY_EXP_MENSAL = """
WITH tabDadosMensais AS (
    SELECT t1.ano, t1.mes, t2.municipio, SUM(t1.valor) AS total_exp_mensal
    FROM comexstat_mun t1
    JOIN municipio t2 ON t1.id_municipio = t2.id_municipio::BIGINT
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t1.mes, t2.municipio
), 
tabAcumulado AS (
    SELECT ano, mes, municipio, total_exp_mensal,
           SUM(total_exp_mensal) OVER (PARTITION BY municipio, ano ORDER BY mes) AS total_exp_acumulado
    FROM tabDadosMensais
), 
tabComparativoAnoAnterior AS (
    SELECT ano, mes, municipio, total_exp_mensal, total_exp_acumulado,
           LAG(total_exp_mensal, 1, 0) OVER (PARTITION BY municipio, mes ORDER BY ano) AS exp_mes_ano_anterior,
           LAG(total_exp_acumulado, 1, 0) OVER (PARTITION BY municipio, mes ORDER BY ano) AS exp_acum_ano_anterior
    FROM tabAcumulado
) 
SELECT ano, mes, municipio, total_exp_mensal, exp_mes_ano_anterior,
       ROUND(CAST(((total_exp_mensal::numeric / NULLIF(exp_mes_ano_anterior, 0)) - 1) * 100 AS numeric), 2) AS perc_var_mes_ano_anterior,
       total_exp_acumulado, exp_acum_ano_anterior,
       ROUND(CAST(((total_exp_acumulado::numeric / NULLIF(exp_acum_ano_anterior, 0)) - 1) * 100 AS numeric), 2) AS perc_var_acum_ano_anterior
FROM tabComparativoAnoAnterior;
"""
QUERY_SEGURANCA = """
SELECT 
    ano, mes, municipio, homicidio_doloso, furtos, furto_veiculo, roubos, roubo_veiculo,
    estelionato, delitos_armas_municoes, entorpecentes_posse, entorpecentes_trafico,
    feminicidio_consumado, feminicidio_tentado, ameaca, estupro, lesao_corporal
FROM seguranca
WHERE municipio IN :lista_municipios AND ano IN :lista_anos;
"""
QUERY_SEGURANCA_TAXA = """
WITH pop_feminina AS (
    SELECT ano, municipio, pop_estimada AS pop_feminina
    FROM populacao_sexo
    WHERE sexo = 'Feminino'
)
SELECT
    t1.ano, t1.mes, t1.municipio,
    ROUND(((t1.homicidio_doloso * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_homicidio_doloso,
    ROUND(((t1.furtos * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_furtos,
    ROUND(((t1.furto_veiculo * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_furto_veiculo,
    ROUND(((t1.roubos * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_roubos,
    ROUND(((t1.roubo_veiculo * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_roubo_veiculo,
    ROUND(((t1.estelionato * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_estelionato,
    ROUND(((t1.delitos_armas_municoes * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_delitos_armas_municoes,
    ROUND(((t1.entorpecentes_posse * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_entorpecentes_posse,
    ROUND(((t1.entorpecentes_trafico * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_entorpecentes_trafico,    
    ROUND(((t1.feminicidio_consumado * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_feminicidio_consumado,
    ROUND(((t1.feminicidio_tentado * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_feminicidio_tentado,
    ROUND(((t1.ameaca * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_ameaca,
    ROUND(((t1.estupro * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_estupro,
    ROUND(((t1.lesao_corporal * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_lesao_corporal
FROM seguranca t1
JOIN populacao t2 ON t1.ano = t2.ano AND t1.municipio = t2.municipio
JOIN pop_feminina t3 ON t1.ano = t3.ano AND t1.municipio = t3.municipio
WHERE t1.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_CAD = """
SELECT 
    t2.municipio, CAST(t1.ano AS INT) AS ano, CAST(t1.mes AS INT) AS mes,
    t1.qtd_fam_pob, t1.qtd_fam_baixa_renda, t1.qtd_fam_acima_meio_sm,
    t1.total_familias, t1.qtd_fam_ate_meio_sm, t1.total_pessoas
FROM cadastro_unico t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos;
"""
QUERY_BOLSA_FAMILIA = """
SELECT t2.municipio, t1.ano, t1.mes, t1.valor_total_beneficio, t1.qtd_beneficiados,
       (t1.valor_total_beneficio::numeric / NULLIF(t1.qtd_beneficiados, 0)) AS beneficio_medio
FROM novo_bolsa_familia AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos;
"""
QUERY_CNPJ_TOTAL = """
SELECT t2.municipio, t1.ano, t1.mes, SUM(t1.empresas_ativas) AS empresas_ativas
FROM cnpj AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY t2.municipio, t1.ano, t1.mes;
"""
QUERY_MEI_TOTAL = """
SELECT t2.municipio, t1.ano, t1.mes, SUM(t1.empresas_ativas) AS empresas_ativas
FROM mei AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY t2.municipio, t1.ano, t1.mes;
"""
QUERY_EDUCACAO_MATRICULAS = """
SELECT t1.ano, t2.municipio, t1.dependencia, t1.mat_infantil_creche, t1.mat_basico,
       t1.mat_infantil, t1.mat_fundamental, t1.mat_medio, t1.mat_profissional, t1.mat_eja,
       t1.docentes_basico, t1.docentes_infantil, t1.docentes_fundamental, t1.docentes_medio,
       t1.docentes_profissional, t1.docentes_eja, t1.turmas_basico, t1.turmas_infantil,
       t1.turmas_fundamental, t1.turmas_medio, t1.turmas_profissional, t1.turmas_eja,
       t1.qntd_escolas, t1.taxa_matricula_creche
FROM educacao_matriculas t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_EDUCACAO_RENDIMENTO = """
SELECT 
    t1.ano, t2.municipio, t1.dependencia, t1.taxa_abandono_fundamental,
    t1.taxa_abandono_fundamental_anos_finais, t1.taxa_abandono_fundamental_anos_iniciais,
    t1.taxa_aprovacao_fundamental, t1.taxa_aprovacao_fundamental_anos_finais,
    t1.taxa_aprovacao_fundamental_anos_iniciais, t1.taxa_distorcao_fundamental,
    t1.taxa_distorcao_fundamental_anos_finais, t1.taxa_distorcao_fundamental_anos_iniciais,
    t1.taxa_reprovacao_fundamental, t1.taxa_reprovacao_fundamental_anos_finais,
    t1.taxa_reprovacao_fundamental_anos_iniciais
FROM educacao_rendimento t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_EDUCACAO_IDEB_MUNICIPIOS = """
SELECT t1.ano, t2.municipio, t1.rede AS dependencia, t1.valor, t1.indicador, t1.categoria
FROM educacao_ideb_municipio t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios;
"""
QUERY_EDUCACAO_IDEB_ESCOLAS = """
SELECT t1.ano, t2.municipio, t1.escola, t1.rede AS dependencia, t1.valor, t1.indicador, t1.categoria
FROM educacao_ideb_escolas t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios;
"""
QUERY_SAUDE_MENSAL = """
SELECT ano, mes, municipio, internacoes_icsab, internacoes_totais, prop_icsab * 100 AS prop_icsab,
       nascimentos, prop_nasc_adolesc, obitos, taxa_obitos_infantis, coef_neonatal,
       nasc_baixo_peso, prop_nasc_baixo_peso, consultas_pre_natal, prop_consultas_pre_natal,
       obitos_causa_definida, obitos_totais, prop_obitos_causas_definidas * 100 AS prop_obitos_causas_definidas,
       obitos_causa_nao_definida, notificacoes_acidentes_trab, populacao, "nascimentos/1000_hab",
       taxa_acidentes_trab
FROM saude
WHERE municipio IN :lista_municipios AND ano IN :lista_anos;
"""
QUERY_SAUDE_DESPESAS = """
SELECT t1.ano, t2.municipio, t1.despesa_saude_deflacionada / 1000000 AS despesa_saude_deflacionada,
       t1.despesa_per_capita_deflacionada, t1.percental_gastos_saude
FROM saude_despesas t1
JOIN municipio t2 on t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_SAUDE_LEITOS = """
SELECT t1.ano, t2.municipio, t1.qtd_leitos_sus,
       t1.qtd_leitos_sus * 1.0 / NULLIF((t3.pop_estimada / 1000), 0) AS qtd_leitos_sus_mil_hab
FROM saude_leitos t1
JOIN municipio t2 on t1.id_municipio = t2.id_municipio
JOIN populacao t3 on t1.id_municipio = t3.id_municipio AND t1.ano = t3.ano
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_SAUDE_MEDICOS = """
SELECT t1.ano, t2.municipio, t1.qtd_medicos_sus,
       t1.qtd_medicos_sus * 1.0 / NULLIF((t3.pop_estimada / 1000), 0) AS qtd_medicos_sus_mil_hab
FROM saude_medicos t1
JOIN municipio t2 on t1.id_municipio = t2.id_municipio
JOIN populacao t3 on t1.id_municipio = t3.id_municipio AND t1.ano = t3.ano
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_SAUDE_VACINAS = """
SELECT t1.ano, t2.municipio, t1.cobertura_penta, t1.cobertura_meningococo,
       t1.cobertura_poliomielite, t1.cobertura_triplice_viral_d1, t1.doses_total
FROM saude_vacinas t1
JOIN municipio t2 on t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_PIB_MUNICIPIOS = """
WITH DadosBase AS (
    SELECT 
        t1.ano, t2.municipio, t1.id_municipio, t1.pib_mil,
        t1.valor_adicionado_bruto_adm_mil, t1.valor_adicionado_bruto_agropecuaria_mil,
        t1.valor_adicionado_bruto_industria_mil, t1.valor_adicionado_bruto_servicos_mil,
        t1.valor_adicionado_bruto_total_mil, t1.pop_estimada, t1.pib_per_capita,
        t1.percentual_pib_rs, t1.posicao_pib_geral, t1.posicao_pib_agropecuaria,
        t1.posicao_pib_industria, t1.posicao_pib_servico, t1.posicao_pib_adm_publica,
        t1.posicao_pib_per_capita, t1.posicao_percentual_pib_rs,
        LAG(t1.pib_mil, 1) OVER (PARTITION BY t1.id_municipio ORDER BY t1.ano) AS pib_mil_anterior,
        LAG(t1.valor_adicionado_bruto_adm_mil, 1) OVER (PARTITION BY t1.id_municipio ORDER BY t1.ano) AS adm_mil_anterior,
        LAG(t1.valor_adicionado_bruto_agropecuaria_mil, 1) OVER (PARTITION BY t1.id_municipio ORDER BY t1.ano) AS agro_mil_anterior,
        LAG(t1.valor_adicionado_bruto_industria_mil, 1) OVER (PARTITION BY t1.id_municipio ORDER BY t1.ano) AS industria_mil_anterior,
        LAG(t1.valor_adicionado_bruto_servicos_mil, 1) OVER (PARTITION BY t1.id_municipio ORDER BY t1.ano) AS servicos_mil_anterior,
        LAG(t1.valor_adicionado_bruto_total_mil, 1) OVER (PARTITION BY t1.id_municipio ORDER BY t1.ano) AS total_mil_anterior,
        LAG(t1.pib_per_capita, 1) OVER (PARTITION BY t1.id_municipio ORDER BY t1.ano) AS pib_per_capita_anterior
    FROM pib_mun_rs t1
    JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
    WHERE t2.municipio IN :lista_municipios
)
SELECT 
    ano, municipio, (pib_mil / 1000.0) AS pib_milhoes,
    ((pib_mil - pib_mil_anterior) * 1.0 / NULLIF(pib_mil_anterior, 0)) * 100 AS tx_cresc_pib_mil,
    valor_adicionado_bruto_adm_mil / 1000.0 AS valor_adicionado_bruto_adm_milhoes,
    ((valor_adicionado_bruto_adm_mil - adm_mil_anterior) * 1.0 / NULLIF(adm_mil_anterior, 0)) * 100 AS tx_cresc_adm_mil,
    valor_adicionado_bruto_agropecuaria_mil / 1000.0 AS valor_adicionado_bruto_agropecuaria_milhoes,
    ((valor_adicionado_bruto_agropecuaria_mil - agro_mil_anterior) * 1.0 / NULLIF(agro_mil_anterior, 0)) * 100 AS tx_cresc_agro_mil,
    valor_adicionado_bruto_industria_mil / 1000.0 AS valor_adicionado_bruto_industria_milhoes,
    ((valor_adicionado_bruto_industria_mil - industria_mil_anterior) * 1.0 / NULLIF(industria_mil_anterior, 0)) * 100 AS tx_cresc_industria_mil,
    valor_adicionado_bruto_servicos_mil / 1000.0 AS valor_adicionado_bruto_servicos_milhoes,
    ((valor_adicionado_bruto_servicos_mil - servicos_mil_anterior) * 1.0 / NULLIF(servicos_mil_anterior, 0)) * 100 AS tx_cresc_servicos_mil,
    valor_adicionado_bruto_total_mil / 1000.0 AS valor_adicionado_bruto_total_milhoes,
    ((valor_adicionado_bruto_total_mil - total_mil_anterior) * 1.0 / NULLIF(total_mil_anterior, 0)) * 100 AS tx_cresc_total_mil,
    pib_per_capita,
    ((pib_per_capita - pib_per_capita_anterior) * 1.0 / NULLIF(pib_per_capita_anterior, 0)) * 100 AS tx_cresc_pib_per_capita,
    percentual_pib_rs, posicao_pib_geral, posicao_pib_agropecuaria, posicao_pib_industria,
    posicao_pib_servico, posicao_pib_adm_publica, posicao_pib_per_capita, posicao_percentual_pib_rs
FROM DadosBase
ORDER BY municipio, ano;
"""
QUERY_POP_TOTAL_DENSIDADE = """
SELECT 
       ano, municipio, pop_estimada, area, densidade_demografica
FROM populacao
WHERE municipio IN :lista_municipios AND ano IN :lista_anos;
"""
QUERY_POP_SEXO_IDADE = """
SELECT 
       ano, municipio, pop_estimada, sexo, faixa_etaria
FROM populacao_rs
WHERE municipio IN :lista_municipios AND ano IN :lista_anos;
"""
QUERY_INDICADORES_FINANCEIROS = """
SELECT t1.ano, t2.municipio, t1.exec_orc_corrente, t1.autonomia_fiscal,
       t1.endividamento, t1.despesas_pessoal, t1.investimento,
       t1.disponibilidade_caixa, t1.geracao_de_caixa, t1.restos_a_pagar
FROM indicadores_financeiros t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""
QUERY_FINANCAS = """
SELECT 
    t1.ano, t2.municipio, t1.bimestre, t1.coluna, t1.cod_conta, t1.conta, t1.valor
FROM financas t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos;
"""

# Queries que usam :lista_municipios (MUNICIPIOS_PRINCIPAIS)
QUERY_EMPREGO_CNAE = """
SELECT 
    t1.ano, t1.mes, t2.municipio, t1.cnae_2_subclasse, t3.subclasse, t3.grupo, t3.grupo_ibge,
    SUM(t1.saldo_movimentacao) AS saldo_movimentacao
FROM caged_prefeituras t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
JOIN cnae t3 ON t1.cnae_2_subclasse = t3.cod_subclasse
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t2.municipio, t1.cnae_2_subclasse, t3.subclasse, t3.grupo, t3.grupo_ibge
ORDER BY t1.ano DESC, t1.mes DESC;
"""
QUERY_VINCULOS_CNAE = """
SELECT 
    t1.ano, t2.municipio, t1.cnae_2_subclasse, t3.subclasse, t3.grupo, t3.grupo_ibge,
    SUM(t1.vinculos_ativos) AS vinculos_ativos
FROM rais_vinculos_cnae t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
JOIN cnae t3 ON t1.cnae_2_subclasse = t3.cod_subclasse
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t2.municipio, t1.cnae_2_subclasse, t3.subclasse, t3.grupo, t3.grupo_ibge;
"""
QUERY_EMPREGO_GRAU_INSTRUCAO = """
SELECT t1.ano, t1.mes, t3.municipio, t2.grau_instrucao_desc AS grau_instrucao,
       SUM(t1.saldo_movimentacao) as saldo_movimentacao
FROM caged_prefeituras t1
JOIN grau_instrucao t2 ON t1.grau_instrucao = t2.cod_grau_instrucao
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t3.municipio, t2.grau_instrucao_desc;
"""
QUERY_VINCULOS_GRAU_INSTRUCAO = """
SELECT t1.ano, t3.municipio, t2.grau_instrucao_desc AS grau_instrucao,
       SUM(t1.vinculos_ativos) as vinculos_ativos
FROM rais_vinculos t1
JOIN grau_instrucao t2 ON t1.grau_instrucao = t2.cod_grau_instrucao
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t3.municipio, t2.grau_instrucao_desc;
"""
QUERY_EMPREGO_FAIXA_ETARIA = """
SELECT t1.ano, t1.mes, t3.municipio, t2.faixa_etaria_desc AS faixa_etaria,
       SUM(t1.saldo_movimentacao) as saldo_movimentacao
FROM caged_prefeituras t1
JOIN faixa_etaria t2 ON t1.faixa_etaria = t2.cod_faixa_etaria
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t3.municipio, t2.faixa_etaria_desc;
"""
QUERY_VINCULOS_FAIXA_ETARIA = """
SELECT t1.ano, t3.municipio, t2.faixa_etaria_desc AS faixa_etaria,
       SUM(t1.vinculos_ativos) as vinculos_ativos
FROM rais_vinculos t1
JOIN faixa_etaria t2 ON t1.faixa_etaria = t2.cod_faixa_etaria
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t3.municipio, t2.faixa_etaria_desc;
"""
QUERY_EMPREGO_RACA_COR = """
SELECT t1.ano, t1.mes, t3.municipio, t2.raca_cor_desc AS raca_cor,
       SUM(t1.saldo_movimentacao) as saldo_movimentacao
FROM caged_prefeituras t1
JOIN raca_cor t2 ON t1.raca_cor = t2.cod_raca_cor
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t3.municipio, t2.raca_cor_desc;
"""
QUERY_VINCULOS_RACA_COR = """
SELECT t1.ano, t3.municipio, t2.raca_cor_desc AS raca_cor,
       SUM(t1.vinculos_ativos) as vinculos_ativos
FROM rais_vinculos t1
JOIN raca_cor t2 ON t1.raca_cor = t2.cod_raca_cor
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t3.municipio, t2.raca_cor_desc;
"""
QUERY_EMPREGO_SEXO = """
SELECT t1.ano, t1.mes, t2.municipio, t1.sexo AS cod_sexo, 
       SUM(t1.saldo_movimentacao) as saldo_movimentacao,
       CASE WHEN t1.sexo = '1' THEN 'Masculino' WHEN t1.sexo = '2' THEN 'Feminino' ELSE 'Indefinido' END AS sexo
FROM caged_prefeituras t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t2.municipio, t1.sexo, sexo;
"""
QUERY_VINCULOS_SEXO = """
SELECT t1.ano, t2.municipio, t1.sexo AS cod_sexo, 
       SUM(t1.vinculos_ativos) as vinculos_ativos,
       CASE WHEN t1.sexo = '1' THEN 'Masculino' WHEN t1.sexo = '2' THEN 'Feminino' ELSE 'Indefinido' END AS sexo
FROM rais_vinculos t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t2.municipio, t1.sexo, sexo;
"""
QUERY_RENDA_SEXO = """
with agregado_renda AS (
    SELECT t1.ano, t2.municipio, t1.sexo,
           SUM(t1.massa_salarial_dezembro) AS massa_salarial_remuneracao_media_dezembro,
           SUM(t1.massa_salarial_dezembro_sm) AS massa_salarial_remuneracao_media_dezembro_sm
    FROM rais_renda t1
    JOIN municipio t2 on t1.id_municipio = t2.id_municipio
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t2.municipio, t1.sexo
), agregado_vinculos AS (
    SELECT t1.ano, t2.municipio, t1.sexo, SUM(t1.vinculos_ativos) AS vinculos_ativos
    FROM rais_vinculos t1
    JOIN municipio t2 on t1.id_municipio = t2.id_municipio
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t2.municipio, t1.sexo
)
SELECT t1.ano, t1.municipio, t1.sexo AS cod_sexo,
       t1.massa_salarial_remuneracao_media_dezembro / NULLIF(t2.vinculos_ativos, 0) AS remuneracao_media_dezembro,
       t1.massa_salarial_remuneracao_media_dezembro_sm / NULLIF(t2.vinculos_ativos, 0) AS valor_remuneracao_media_dezembro_sm,
       CASE WHEN t1.sexo = '1' THEN 'Masculino' WHEN t1.sexo = '2' THEN 'Feminino' ELSE 'Indefinido' END AS sexo
FROM agregado_renda t1
JOIN agregado_vinculos t2 ON t1.ano = t2.ano AND t1.municipio = t2.municipio AND t1.sexo = t2.sexo;
"""
QUERY_RENDA_CNAE = """
with agregado_renda AS (
    SELECT t1.ano, t2.municipio, t3.subclasse, t3.grupo, t3.grupo_ibge,
           SUM(t1.massa_salarial_dezembro) AS massa_salarial_remuneracao_media_dezembro,
           SUM(t1.massa_salarial_dezembro_sm) AS massa_salarial_remuneracao_media_dezembro_sm
    FROM rais_renda t1
    JOIN municipio t2 on t1.id_municipio = t2.id_municipio
    JOIN cnae t3 on t1.cnae_2_subclasse = t3.cod_subclasse
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t2.municipio, t3.subclasse, t3.grupo, t3.grupo_ibge
), agregado_vinculos AS (
    SELECT t1.ano, t2.municipio, t3.subclasse, t3.grupo, t3.grupo_ibge,
           SUM(t1.vinculos_ativos) AS vinculos_ativos
    FROM rais_vinculos_cnae t1
    JOIN municipio t2 on t1.id_municipio = t2.id_municipio
    JOIN cnae t3 on t1.cnae_2_subclasse = t3.cod_subclasse
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t2.municipio, t3.subclasse, t3.grupo, t3.grupo_ibge
)
SELECT t1.ano, t1.municipio, t1.subclasse, t1.grupo, t1.grupo_ibge, t2.vinculos_ativos,
       t1.massa_salarial_remuneracao_media_dezembro / NULLIF(t2.vinculos_ativos, 0) AS remuneracao_media_dezembro,
       t1.massa_salarial_remuneracao_media_dezembro_sm / NULLIF(t2.vinculos_ativos, 0) AS valor_remuneracao_media_dezembro_sm
FROM agregado_renda t1
JOIN agregado_vinculos t2 ON t1.ano = t2.ano AND t1.municipio = t2.municipio AND t1.grupo = t2.grupo AND t1.subclasse = t2.subclasse AND t1.grupo_ibge = t2.grupo_ibge;
"""
QUERY_ESTABELECIMENTOS_CNAE = """
SELECT 
    t1.ano, t2.municipio, t1.cnae_2_subclasse, t3.subclasse, t3.grupo, t3.grupo_ibge,
    SUM(t1.qntd_estabelecimentos) AS qntd_estabelecimentos
FROM rais_estabelecimentos t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
JOIN cnae t3 ON t1.cnae_2_subclasse = t3.cod_subclasse
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t2.municipio, t1.cnae_2_subclasse, t3.subclasse, t3.grupo, t3.grupo_ibge;
"""
QUERY_ESTABELECIMENTOS_TAMANHO = """
SELECT 
    t1.ano, t2.municipio, t3.tamanho_estab_desc AS tamanho_estabelecimento,
    SUM(t1.qntd_estabelecimentos) as qntd_estabelecimentos
FROM rais_estabelecimentos t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
JOIN tamanho_estabelecimento t3 ON t1.tamanho_estabelecimento = t3.cod_tamanho_estab
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t2.municipio, t3.tamanho_estab_desc;
"""
QUERY_EXP_MUN_SELECIONADO = """
WITH tabMensal AS (
    SELECT t1.ano, t1.mes, t2.municipio, t1.cod_sh4, t3.pais, SUM(t1.valor) AS valor_exp_mensal
    FROM comexstat_mun t1
    JOIN municipio t2 ON t1.id_municipio = t2.id_municipio::BIGINT
    JOIN countries t3 ON t1.cod_pais = t3.cod_pais
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY t1.ano, t1.mes, t2.municipio, t1.cod_sh4, t3.pais
),
tabAcumulado AS (
    SELECT ano, mes, municipio, pais, cod_sh4, valor_exp_mensal,
           SUM(valor_exp_mensal) OVER (PARTITION BY ano, municipio, pais, cod_sh4 ORDER BY mes) AS valor_acumulado_ano
    FROM tabMensal
),
tabFinal AS (
    SELECT ano, mes, municipio, pais, cod_sh4, valor_exp_mensal, valor_acumulado_ano,
           NULLIF(LAG(valor_exp_mensal, 1, 0) OVER (PARTITION BY municipio, pais, mes, cod_sh4 ORDER BY ano), 0) AS valor_exp_mensal_ano_anterior,
           NULLIF(LAG(valor_acumulado_ano, 1, 0) OVER (PARTITION BY municipio, pais, mes, cod_sh4 ORDER BY ano), 0) AS valor_acumulado_ano_anterior
    FROM tabAcumulado
)
SELECT tf.ano, tf.mes, tf.municipio, tf.pais, CONCAT(tf.cod_sh4, ' - ', t2.desc_sh4) AS produto,
       tf.valor_exp_mensal, tf.valor_exp_mensal_ano_anterior, tf.valor_acumulado_ano, tf.valor_acumulado_ano_anterior
FROM tabFinal tf
JOIN sh4 t2 on tf.cod_sh4 = t2.cod_sh4
ORDER BY ano DESC, pais, mes DESC;
"""
QUERY_CNPJ_CNAE = """
with cnae_unico AS (
    SELECT LPAD(cod_grupo::VARCHAR, 3, '0') AS cod_grupo,
           MIN(grupo) AS grupo,
           MIN(grupo_ibge) AS grupo_ibge
    FROM cnae
    GROUP BY cod_grupo
)
SELECT t2.municipio, t1.ano, t1.mes, t3.grupo, t3.grupo_ibge,
       SUM(t1.empresas_ativas) as empresas_ativas
FROM cnpj AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
JOIN cnae_unico t3 ON t1.cod_grupo = LPAD(t3.cod_grupo::VARCHAR, 3, '0')
WHERE t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY t2.municipio, t1.ano, t1.mes, t3.grupo, t3.grupo_ibge;
"""
QUERY_MEI_CNAE = """
with cnae_unico AS (
    SELECT LPAD(cod_grupo::VARCHAR, 3, '0') AS cod_grupo,
           MIN(grupo) AS grupo,
           MIN(grupo_ibge) AS grupo_ibge
    FROM cnae
    GROUP BY cod_grupo
)
SELECT t2.municipio, t1.ano, t1.mes, t3.grupo, t3.grupo_ibge,
       SUM(t1.empresas_ativas) as empresas_ativas
FROM mei AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
JOIN cnae_unico t3 ON t1.cod_grupo = LPAD(t3.cod_grupo::VARCHAR, 3, '0')
WHERE t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY t2.municipio, t1.ano, t1.mes, t3.grupo, t3.grupo_ibge;
"""


# ===================================================================
# FUNÇÃO DE PROCESSAMENTO E UPLOAD
# ===================================================================


def process_and_upload(
    query_string,
    target_table_name,
    engine,
    supabase_client,
    params=None,
    batch_size=500,
):
    """
    Executa uma query parametrizada no banco local, corrige os tipos
    de dados e insere em lotes numa tabela do Supabase.
    """
    print(f"\n--- Processando tabela: {target_table_name} ---")

    try:
        start_time = time.time()

        # Executar a query e carregar para o DataFrame
        print(
            f"1/4: Buscando dados do banco local (Parâmetros: {params is not None})..."
        )
        df = pd.read_sql_query(text(query_string), engine, params=params)

        if df.empty:
            print("(!) Aviso: A query não retornou dados. Tabela pulada.")
            return

        print(f"-> Encontrados {len(df)} registros.")

        # Corrigir os tipos de dados
        print("2/4: Corrigindo tipos de dados no DataFrame...")
        for col in df.columns:
            if pd.api.types.is_float_dtype(df[col]):
                if (df[col].dropna() % 1 == 0).all():
                    print(
                        f"   - Convertendo coluna float '{col}' para inteiro anulável (Int64)."
                    )
                    df[col] = df[col].astype("Int64")

        df.replace([np.inf, -np.inf], None, inplace=True)
        df = df.astype(object).where(pd.notna(df), None)

        # Apagar dados existentes na tabela de destino
        print(f"3/4: Limpando a tabela de destino '{target_table_name}' no Supabase...")
        # Deleta todos os dados existentes para garantir uma carga limpa
        supabase_client.table(target_table_name).delete().gt("ano", 0).execute()

        # Inserir dados em lotes
        print(f"4/4: Inserindo dados em lotes de {batch_size} registros...")
        total_batches = (len(df) // batch_size) + (1 if len(df) % batch_size > 0 else 0)

        for i, start in enumerate(range(0, len(df), batch_size)):
            end = start + batch_size
            batch_df = df.iloc[start:end]
            data_to_insert = batch_df.to_dict(orient="records")

            response = (
                supabase_client.table(target_table_name)
                .insert(data_to_insert)
                .execute()
            )

            if hasattr(response, "error") and response.error:
                print(f"   -> ERRO no lote {i + 1}/{total_batches}: {response.error}")
            else:
                print(f"   -> Lote {i + 1}/{total_batches} inserido com sucesso.")

        end_time = time.time()
        print(
            f"✅ Tabela '{target_table_name}' concluída com sucesso em {end_time - start_time:.2f} segundos."
        )

    except Exception as e:
        print(f"❌ ERRO GERAL ao processar a tabela '{target_table_name}': {e}")
        with open("log_erros.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"Erro na tabela {target_table_name}: {e}\n")


# ===================================================================
# --- 6. ORQUESTRADOR PRINCIPAL ---
# ===================================================================


def main():
    """
    Orquestra a execução de todas as tarefas de carga de dados
    com os parâmetros corretos.
    """

    # Parâmetros para queries de "lista" (Todos os Municípios)
    params_lista_todos = {
        "lista_municipios": TODOS_OS_MUNICIPIOS,
        "lista_anos": anos_de_interesse,
    }
    params_lista_comex = {
        "lista_municipios": TODOS_OS_MUNICIPIOS,
        "lista_anos": anos_comex,
    }
    params_lista_ideb = {"lista_municipios": TODOS_OS_MUNICIPIOS}
    params_lista_pib = {"lista_municipios": TODOS_OS_MUNICIPIOS}

    # Parâmetros para queries "específicas" (Municípios Principais)
    params_principais = {
        "lista_municipios": MUNICIPIOS_PRINCIPAIS,
        "lista_anos": anos_de_interesse,
    }
    params_principais_comex = {
        "lista_municipios": MUNICIPIOS_PRINCIPAIS,
        "lista_anos": anos_comex,
    }

    # Definição das tarefas
    tasks = [
        # --- Queries de Lista (Todos os Municípios) ---
        (QUERY_EMPREGO_MUNICIPIOS, "dados_emprego_municipios", params_lista_todos),
        (QUERY_VINCULOS_MUNICIPIOS, "dados_vinculos_municipios", params_lista_todos),
        (QUERY_RENDA_MUNICIPIOS, "dados_renda_municipios", params_lista_todos),
        (
            QUERY_ESTABELECIMENTOS_MUNICIPIOS,
            "dados_estabelecimentos_municipios",
            params_lista_todos,
        ),
        (QUERY_EXP_ANUAL, "dados_comex_anual", params_lista_comex),
        (QUERY_EXP_MENSAL, "dados_comex_mensal", params_lista_comex),
        (QUERY_SEGURANCA, "dados_seguranca", params_lista_todos),
        (QUERY_SEGURANCA_TAXA, "dados_seguranca_taxa", params_lista_todos),
        (QUERY_CAD, "dados_cadastro_unico", params_lista_todos),
        (QUERY_BOLSA_FAMILIA, "dados_bolsa_familia", params_lista_todos),
        (QUERY_CNPJ_TOTAL, "dados_cnpj_total", params_lista_todos),
        (QUERY_MEI_TOTAL, "dados_mei_total", params_lista_todos),
        (QUERY_EDUCACAO_MATRICULAS, "dados_educacao_matriculas", params_lista_todos),
        (QUERY_EDUCACAO_RENDIMENTO, "dados_educacao_rendimento", params_lista_todos),
        (
            QUERY_EDUCACAO_IDEB_MUNICIPIOS,
            "dados_educacao_ideb_municipios",
            params_lista_ideb,
        ),
        (QUERY_EDUCACAO_IDEB_ESCOLAS, "dados_educacao_ideb_escolas", params_lista_ideb),
        (QUERY_SAUDE_MENSAL, "dados_saude_mensal", params_lista_todos),
        (QUERY_SAUDE_DESPESAS, "dados_saude_despesas", params_lista_todos),
        (QUERY_SAUDE_LEITOS, "dados_saude_leitos", params_lista_todos),
        (QUERY_SAUDE_MEDICOS, "dados_saude_medicos", params_lista_todos),
        (QUERY_SAUDE_VACINAS, "dados_saude_vacinas", params_lista_todos),
        (QUERY_PIB_MUNICIPIOS, "dados_pib_municipios", params_lista_pib),
        (QUERY_POP_TOTAL_DENSIDADE, "dados_populacao_densidade", params_lista_todos),
        (QUERY_POP_SEXO_IDADE, "dados_populacao_sexo_idade", params_lista_todos),
        (
            QUERY_INDICADORES_FINANCEIROS,
            "dados_indicadores_financeiros",
            params_lista_todos,
        ),
        (QUERY_FINANCAS, "dados_financas", params_lista_todos),
        # --- Queries Específicas (Municípios Principais) ---
        (QUERY_EMPREGO_CNAE, "dados_emprego_cnae", params_principais),
        (QUERY_VINCULOS_CNAE, "dados_vinculos_cnae", params_principais),
        (
            QUERY_EMPREGO_GRAU_INSTRUCAO,
            "dados_emprego_grau_instrucao",
            params_principais,
        ),
        (
            QUERY_VINCULOS_GRAU_INSTRUCAO,
            "dados_vinculos_grau_instrucao",
            params_principais,
        ),
        (QUERY_EMPREGO_FAIXA_ETARIA, "dados_emprego_faixa_etaria", params_principais),
        (QUERY_VINCULOS_FAIXA_ETARIA, "dados_vinculos_faixa_etaria", params_principais),
        (QUERY_EMPREGO_RACA_COR, "dados_emprego_raca_cor", params_principais),
        (QUERY_VINCULOS_RACA_COR, "dados_vinculos_raca_cor", params_principais),
        (QUERY_EMPREGO_SEXO, "dados_emprego_sexo", params_principais),
        (QUERY_VINCULOS_SEXO, "dados_vinculos_sexo", params_principais),
        (QUERY_RENDA_SEXO, "dados_renda_sexo", params_principais),
        (QUERY_RENDA_CNAE, "dados_renda_cnae", params_principais),
        (QUERY_ESTABELECIMENTOS_CNAE, "dados_estabelecimentos_cnae", params_principais),
        (
            QUERY_ESTABELECIMENTOS_TAMANHO,
            "dados_estabelecimentos_tamanho",
            params_principais,
        ),
        (QUERY_EXP_MUN_SELECIONADO, "dados_comex_municipio", params_principais_comex),
        (QUERY_CNPJ_CNAE, "dados_cnpj_cnae", params_principais),
        (QUERY_MEI_CNAE, "dados_mei_cnae", params_principais),
    ]

    print("Iniciando script de carga de dados FILTRADOS para o Supabase.")

    total_tasks = len(tasks)
    for i, (query, table_name, params) in enumerate(tasks):
        print(
            f"\n==================== TAREFA {i + 1} de {total_tasks} ===================="
        )
        process_and_upload(query, table_name, local_engine, supabase, params=params)

    print("\nTodas as tarefas filtradas foram concluídas!")


if __name__ == "__main__":
    main()
# %%
