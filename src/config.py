municipio_de_interesse = "São Leopoldo"
municipios_de_interesse = [
    "Canoas",
    "Novo Hamburgo",
    "São Leopoldo",
    "Gravataí",
]
anos_de_interesse = tuple(range(2021, 2026))

anos_comex = tuple(range(min(anos_de_interesse) - 1, max(anos_de_interesse) + 1))

CORES_MUNICIPIOS = {
    "São Leopoldo": "#4C82F7",  # Azul Google
    "Canoas": "#FF6B6B",  # Coral Suave
    "Novo Hamburgo": "#1DD1A1",  # Verde Menta/Turquesa
    "Gravataí": "#A354FF",  # Roxo Vibrante
}

ordem_instrucao = [
    "Analfabeto",
    "Até 5ª Incompleto",
    "5ª Completo Fundamental",
    "6ª a 9ª Fundamental",
    "Fundamental Completo",
    "Médio Incompleto",
    "Médio Completo",
    "Superior Incompleto",
    "Superior Completo",
    "Pós-Graduação ou Mestrado",
    "Doutorado",
]

ordem_tamanho_estabelecimentos = [
    "De 1 a 4",
    "De 5 a 9",
    "De 10 a 19",
    "De 20 a 49",
    "De 50 a 99",
    "De 100 a 249",
    "De 250 a 499",
    "De 500 a 999",
    "1000 ou Mais",
]
