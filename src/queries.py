# Queries de Emprego
## Emprego por Municipio

QUERY_EMPREGO_MUNICIPIOS = """
SELECT 
    t1.ano,
    t1.mes,
    t2.municipio,
    SUM(t1.saldo_movimentacao) AS saldo_movimentacao
FROM caged_prefeituras t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t2.municipio
ORDER BY t1.ano, t1.mes;
"""

QUERY_EMPREGO_CNAE = """
SELECT 
    t1.ano,
    t1.mes,
    t2.municipio,
    t1.cnae_2_subclasse,
    t3.subclasse,
    t3.grupo,
    t3.grupo_ibge,
    SUM(t1.saldo_movimentacao) AS saldo_movimentacao
FROM caged_prefeituras t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
JOIN cnae t3 ON t1.cnae_2_subclasse = t3.cod_subclasse
WHERE t2.municipio = :municipio AND t1.ano IN :lista_anos
GROUP BY t1.ano, t1.mes, t2.municipio, t1.cnae_2_subclasse, t3.subclasse, t3.grupo, t3.grupo_ibge
ORDER BY t1.ano DESC, t1.mes DESC;
"""

QUERY_EXP_ANUAL = """
-- CTE 1: Agrega os dados por ano e municipio.
WITH tabDadosAnuais AS (
    SELECT
        t1.ano,
        t2.municipio,
        SUM(t1.valor) AS total_exp_anual
    FROM comexstat_mun t1
    JOIN municipio t2 ON t1.id_municipio = t2.id_municipio::BIGINT
    WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
    GROUP BY
        t1.ano,
        t2.municipio
),

-- CTE 2: Usa os dados anuais para buscar o valor do ano anterior (LAG).
tabComparativoAnual AS (
    SELECT
        ano,
        municipio,
        total_exp_anual,
        LAG(total_exp_anual, 1, 0) OVER (PARTITION BY municipio ORDER BY ano) AS exp_ano_anterior
    FROM tabDadosAnuais
)

SELECT
    ano,
    municipio,
    total_exp_anual,
    exp_ano_anterior,
    ROUND(
        ((total_exp_anual / NULLIF(exp_ano_anterior, 0)) - 1) * 100,
        2
    ) AS perc_var_ano_anterior
FROM tabComparativoAnual
ORDER BY
    ano DESC,
    total_exp_anual DESC
"""

QUERY_EXP_MENSAL = """
-- CTE 1: Agrega os dados por mes e municipio.
WITH tabDadosMensais AS
    (SELECT t1.ano,
            t1.mes,
            t2.municipio,
            SUM(t1.valor) AS total_exp_mensal
     FROM comexstat_mun t1
     JOIN municipio t2 ON t1.id_municipio = t2.id_municipio::BIGINT
     WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
     GROUP BY t1.ano,
              t1.mes,
              t2.municipio), 
              
-- CTE 2: Calcula o valor do acumulado no ano no mês.
tabAcumulado AS
    (SELECT ano,
            mes,
            municipio,
            total_exp_mensal,
            SUM(total_exp_mensal) OVER (PARTITION BY municipio, ano
                                        ORDER BY mes) AS total_exp_acumulado
     FROM tabDadosMensais), 

-- CTE 3: Calcula o valor no ano anterior
tabComparativoAnoAnterior AS
    (SELECT ano,
            mes,
            municipio,
            total_exp_mensal,
            total_exp_acumulado,
            LAG(total_exp_mensal, 1, 0) OVER (PARTITION BY municipio, mes
                                              ORDER BY ano) AS exp_mes_ano_anterior,
            LAG(total_exp_acumulado, 1, 0) OVER (PARTITION BY municipio, mes
                                                 ORDER BY ano) AS exp_acum_ano_anterior
     FROM tabAcumulado) 
     
-- Tabela final com os cálculos de variação percentual
SELECT ano,
       mes,
       municipio,
       total_exp_mensal,
       exp_mes_ano_anterior,
       ROUND(((total_exp_mensal / NULLIF(exp_mes_ano_anterior, 0)) - 1) * 100, 2) AS perc_var_mes_ano_anterior,
       total_exp_acumulado,
       exp_acum_ano_anterior,
       ROUND(((total_exp_acumulado / NULLIF(exp_acum_ano_anterior, 0)) - 1) * 100, 2) AS perc_var_acum_ano_anterior
FROM tabComparativoAnoAnterior
"""

QUERY_EXP_MUN_SELECIONADO = """
WITH tabMensal AS
    (SELECT t1.ano,
            t1.mes,
            t2.municipio,
            t1.cod_sh4,
            t3.pais,
            SUM(t1.valor) AS valor_exp_mensal
     FROM comexstat_mun t1
     JOIN municipio t2 ON t1.id_municipio = t2.id_municipio::BIGINT
     JOIN countries t3 ON t1.cod_pais = t3.cod_pais
     WHERE t2.municipio = :municipio AND t1.ano IN :lista_anos
     GROUP BY t1.ano,
              t1.mes,
              t2.municipio,
              t1.cod_sh4,
              t3.pais),
     
     tabAcumulado AS
    (SELECT ano,
            mes,
            municipio,
            pais,
            cod_sh4,
            valor_exp_mensal,
            SUM(valor_exp_mensal) OVER (PARTITION BY ano, municipio, pais, cod_sh4
                                        ORDER BY mes) AS valor_acumulado_ano
     FROM tabMensal),
     
     tabFinal AS
    (SELECT ano,
            mes,
            municipio,
            pais,
            cod_sh4,
            valor_exp_mensal,
            valor_acumulado_ano,
            NULLIF(LAG(valor_exp_mensal, 1, 0) OVER (PARTITION BY municipio, pais, mes, cod_sh4
                                                     ORDER BY ano), 0) AS valor_exp_mensal_ano_anterior,
            NULLIF(LAG(valor_acumulado_ano, 1, 0) OVER (PARTITION BY municipio, pais, mes, cod_sh4
                                                        ORDER BY ano), 0) AS valor_acumulado_ano_anterior
     FROM tabAcumulado)

SELECT ano,
       mes,
       municipio,
       pais,
       CONCAT(tabFinal.cod_sh4, ' - ', t2.desc_sh4) AS produto,
       valor_exp_mensal,
       valor_exp_mensal_ano_anterior,
       valor_acumulado_ano,
       valor_acumulado_ano_anterior
FROM tabFinal
JOIN sh4 t2 on tabFinal.cod_sh4 = t2.cod_sh4
ORDER BY ano DESC,
         pais,
         mes DESC;
"""


QUERY_SEGURANCA = """
SELECT 
    ano,
    mes,
    municipio,
    homicidio_doloso,
    total_vitimas_homicidio_doloso,
    latrocinio,
    furtos,
    abigeato,
    furto_veiculo,
    roubos,
    roubo_veiculo,
    estelionato,
    delitos_armas_municoes,
    entorpecentes_posse,
    entorpecentes_trafico,
    vitimas_latrocinio,
    vitimas_lesao_corp_seg_morte,
    feminicidio_consumado,
    feminicidio_tentado,
    ameaca,
    estupro,
    lesao_corporal
FROM
    seguranca
WHERE
    municipio IN :lista_municipios AND ano IN :lista_anos
"""

QUERY_SEGURANCA_TAXA = """
WITH pop_feminina AS (
    SELECT
        ano,
        municipio,
        pop_estimada AS pop_feminina
    FROM populacao_sexo
    WHERE sexo = 'Feminino'
)
SELECT
    t1.ano,
    t1.mes,
    t1.municipio,
    ROUND(((t1.homicidio_doloso * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_homicidio_doloso,
    ROUND(((t1.total_vitimas_homicidio_doloso * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_vitimas_homicidio_doloso,
    ROUND(((t1.latrocinio * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_latrocinio,
    ROUND(((t1.furtos * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_furtos,
    ROUND(((t1.abigeato * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_abigeato,
    ROUND(((t1.furto_veiculo * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_furto_veiculo,
    ROUND(((t1.roubos * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_roubos,
    ROUND(((t1.roubo_veiculo * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_roubo_veiculo,
    ROUND(((t1.estelionato * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_estelionato,
    ROUND(((t1.delitos_armas_municoes * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_delitos_armas_municoes,
    ROUND(((t1.entorpecentes_posse * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_entorpecentes_posse,
    ROUND(((t1.entorpecentes_trafico * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_entorpecentes_trafico,
    ROUND(((t1.vitimas_latrocinio * 10000.0) / NULLIF(t2.pop_estimada, 0))::NUMERIC, 3) AS taxa_vitimas_latrocinio,
    
    ROUND(((t1.feminicidio_consumado * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_feminicidio_consumado,
    ROUND(((t1.feminicidio_tentado * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_feminicidio_tentado,
    ROUND(((t1.ameaca * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_ameaca,
    ROUND(((t1.estupro * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_estupro,
    ROUND(((t1.lesao_corporal * 10000.0) / NULLIF(t3.pop_feminina, 0))::NUMERIC, 3) AS taxa_lesao_corporal
FROM seguranca t1
JOIN populacao t2 ON t1.ano = t2.ano AND t1.municipio = t2.municipio
JOIN pop_feminina t3 ON t1.ano = t3.ano AND t1.municipio = t3.municipio
WHERE t1.municipio IN :lista_municipios AND t1.ano IN :lista_anos
"""
