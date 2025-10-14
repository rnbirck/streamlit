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

QUERY_EMPREGO_GRAU_INSTRUCAO = """
SELECT t1.ano,
       t1.mes,
       t3.municipio,
       t2.grau_instrucao_desc AS grau_instrucao,
       SUM(t1.saldo_movimentacao) as saldo_movimentacao
FROM caged_prefeituras t1
JOIN grau_instrucao t2 ON t1.grau_instrucao = t2.cod_grau_instrucao
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio = :municipio AND t1.ano IN :lista_anos
GROUP BY t1.ano,
         t1.mes,
         t3.municipio,
         t2.grau_instrucao_desc
"""

QUERY_EMPREGO_FAIXA_ETARIA = """
SELECT t1.ano,
       t1.mes,
       t3.municipio,
       t2.faixa_etaria_desc AS faixa_etaria,
       SUM(t1.saldo_movimentacao) as saldo_movimentacao
FROM caged_prefeituras t1
JOIN faixa_etaria t2 ON t1.faixa_etaria = t2.cod_faixa_etaria
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio = :municipio AND t1.ano IN :lista_anos
GROUP BY t1.ano,
         t1.mes,
         t3.municipio,
         t2.faixa_etaria_desc;
"""

QUERY_EMPREGO_RACA_COR = """
SELECT t1.ano,
       t1.mes,
       t3.municipio,
       t2.raca_cor_desc AS raca_cor,
       SUM(t1.saldo_movimentacao) as saldo_movimentacao
FROM caged_prefeituras t1
JOIN raca_cor t2 ON t1.raca_cor = t2.cod_raca_cor
JOIN municipio t3 ON t1.id_municipio = t3.id_municipio
WHERE t3.municipio = :municipio AND t1.ano IN :lista_anos
GROUP BY t1.ano,
         t1.mes,
         t3.municipio,
         t2.raca_cor_desc;
"""

QUERY_EMPREGO_SEXO = """
SELECT t1.ano,
       t1.mes,
       t2.municipio,
       t1.sexo AS cod_sexo, 
       SUM(t1.saldo_movimentacao) as saldo_movimentacao,
CASE
    WHEN t1.sexo = '1' THEN 'Masculino'
    WHEN t1.sexo = '2' THEN 'Feminino'
    ELSE 'Indefinido'
END AS sexo
FROM caged_prefeituras t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio = :municipio AND t1.ano IN :lista_anos
GROUP BY t1.ano,
         t1.mes,
         t2.municipio,
         sexo
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

QUERY_CAD = """
SELECT 
    t2.municipio,
    CAST(t1.ano AS INT) AS ano, 
    CAST(t1.mes AS INT) AS mes,
    t1.qtd_fam_pob,
    t1.qtd_fam_baixa_renda,
    t1.qtd_fam_acima_meio_sm,
    t1.total_familias,
    t1.qtd_fam_ate_meio_sm,
    t1.total_pessoas
FROM
    cadastro_unico t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE
    t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
"""

QUERY_BOLSA_FAMILIA = """
SELECT t2.municipio,
       t1.ano,
       t1.mes,
       t1.valor_total_beneficio,
       t1.qtd_beneficiados,
       (t1.valor_total_beneficio / t1.qtd_beneficiados) AS beneficio_medio
FROM novo_bolsa_familia AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
WHERE
    t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
"""

QUERY_CNPJ_TOTAL = """
SELECT t2.municipio,
       t1.ano,
       t1.mes,
       SUM(t1.empresas_ativas) AS empresas_ativas
FROM cnpj AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
WHERE
    t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY
    t2.municipio,
    t1.ano,
    t1.mes
"""

QUERY_CNPJ_CNAE = """
with cnae_unico AS
    (SELECT LPAD(cod_grupo::VARCHAR, 3, '0') AS cod_grupo,
            MIN(grupo) AS grupo,
            MIN(grupo_ibge) AS grupo_ibge
     FROM cnae
     GROUP BY cod_grupo)
SELECT t2.municipio,
       t1.ano,
       t1.mes,
       t3.grupo,
       t3.grupo_ibge,
       SUM(t1.empresas_ativas) as empresas_ativas
FROM cnpj AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
JOIN cnae_unico t3 ON t1.cod_grupo = LPAD(t3.cod_grupo::VARCHAR, 3, '0')
WHERE t2.municipio = :municipio AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY t2.municipio,
         t1.ano,
         t1.mes,
         t3.grupo,
         t3.grupo_ibge
"""

QUERY_MEI_TOTAL = """
SELECT t2.municipio,
       t1.ano,
       t1.mes,
       SUM(t1.empresas_ativas) AS empresas_ativas
FROM mei AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
WHERE
    t2.municipio IN :lista_municipios AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY
    t2.municipio,
    t1.ano,
    t1.mes
"""

QUERY_MEI_CNAE = """
with cnae_unico AS
    (SELECT LPAD(cod_grupo::VARCHAR, 3, '0') AS cod_grupo,
            MIN(grupo) AS grupo,
            MIN(grupo_ibge) AS grupo_ibge
     FROM cnae
     GROUP BY cod_grupo)
SELECT t2.municipio,
       t1.ano,
       t1.mes,
       t3.grupo,
       t3.grupo_ibge,
       SUM(t1.empresas_ativas) as empresas_ativas
FROM mei AS t1
JOIN municipio AS t2 on t1.id_municipio = t2.id_municipio
JOIN cnae_unico t3 ON t1.cod_grupo = LPAD(t3.cod_grupo::VARCHAR, 3, '0')
WHERE t2.municipio = :municipio AND CAST(t1.ano AS INT) IN :lista_anos
GROUP BY t2.municipio,
         t1.ano,
         t1.mes,
         t3.grupo,
         t3.grupo_ibge
"""

QUERY_EDUCACAO_MATRICULAS = """
SELECT t1.ano,
       t2.municipio,
       t1.dependencia,
       t1.mat_infantil_creche,
       t1.mat_basico,
       t1.mat_infantil,
       t1.mat_fundamental,
       t1.mat_medio,
       t1.mat_profissional,
       t1.mat_eja,
       t1.docentes_basico,
       t1.docentes_infantil,
       t1.docentes_fundamental,
       t1.docentes_medio,
       t1.docentes_profissional,
       t1.docentes_eja,
       t1.turmas_basico,
       t1.turmas_infantil,
       t1.turmas_fundamental,
       t1.turmas_medio,
       t1.turmas_profissional,
       t1.turmas_eja,
       t1.qntd_escolas,
       t1.taxa_matricula_creche
FROM educacao_matriculas t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
"""

QUERY_EDUCACAO_RENDIMENTO = """
SELECT 
    t1.ano,
    t2.municipio,
    t1.dependencia,
    t1.taxa_abandono_fundamental,
    t1.taxa_abandono_fundamental_anos_finais,
    t1.taxa_abandono_fundamental_anos_iniciais,
    t1.taxa_aprovacao_fundamental,
    t1.taxa_aprovacao_fundamental_anos_finais,
    t1.taxa_aprovacao_fundamental_anos_iniciais,
    t1.taxa_distorcao_fundamental,
    t1.taxa_distorcao_fundamental_anos_finais,
    t1.taxa_distorcao_fundamental_anos_iniciais,
    t1.taxa_reprovacao_fundamental,
    t1.taxa_reprovacao_fundamental_anos_finais,
    t1.taxa_reprovacao_fundamental_anos_iniciais
FROM educacao_rendimento t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
"""
QUERY_EDUCACAO_RENDIMENTO = """
SELECT 
    t1.ano,
    t2.municipio,
    t1.dependencia,
    t1.taxa_abandono_fundamental,
    t1.taxa_abandono_fundamental_anos_finais,
    t1.taxa_abandono_fundamental_anos_iniciais,
    t1.taxa_aprovacao_fundamental,
    t1.taxa_aprovacao_fundamental_anos_finais,
    t1.taxa_aprovacao_fundamental_anos_iniciais,
    t1.taxa_distorcao_fundamental,
    t1.taxa_distorcao_fundamental_anos_finais,
    t1.taxa_distorcao_fundamental_anos_iniciais,
    t1.taxa_reprovacao_fundamental,
    t1.taxa_reprovacao_fundamental_anos_finais,
    t1.taxa_reprovacao_fundamental_anos_iniciais
FROM educacao_rendimento t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios AND t1.ano IN :lista_anos
"""
QUERY_EDUCACAO_IDEB_MUNICIPIOS = """
SELECT
    t1.ano,
    t2.municipio,
    t1.rede AS dependencia,
    t1.valor,
    t1.indicador,
    t1.categoria
FROM educacao_ideb_municipio t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios
"""
QUERY_EDUCACAO_IDEB_ESCOLAS = """
SELECT
    t1.ano,
    t2.municipio,
    t1.escola,
    t1.rede AS dependencia,
    t1.valor,
    t1.indicador,
    t1.categoria
FROM educacao_ideb_escolas t1
JOIN municipio t2 ON t1.id_municipio = t2.id_municipio
WHERE t2.municipio IN :lista_municipios
"""

QUERY_SAUDE_MENSAL = """
SELECT ano,
       mes,
       municipio,
       internacoes_icsab,
       internacoes_totais,
       prop_icsab * 100 AS prop_icsab,
       nascimentos,
       prop_nasc_adolesc,
       obitos,
       taxa_obitos_infantis,
       coef_neonatal,
       nasc_baixo_peso,
       prop_nasc_baixo_peso,
       consultas_pre_natal,
       prop_consultas_pre_natal,
       obitos_causa_definida,
       obitos_totais,
       prop_obitos_causas_definidas * 100 AS prop_obitos_causas_definidas,
       obitos_causa_nao_definida,
       notificacoes_acidentes_trab,
       populacao,
       "nascimentos/1000_hab",
       taxa_acidentes_trab
FROM saude
WHERE municipio IN :lista_municipios AND ano IN :lista_anos
"""
