municipio_de_interesse = "São Leopoldo"
municipios_de_interesse = [
    "Canoas",
    "Novo Hamburgo",
    "São Leopoldo",
    "Gravataí",
]
anos_de_interesse = list(range(2021, 2026))

anos_comex = list(range(min(anos_de_interesse) - 1, max(anos_de_interesse) + 1))

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
