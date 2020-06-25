DIAGNOSTICOS = [
    'Ictus_isquemico',
    'Ataque_isquemico_transitorio',
    'Hemorragia_cerebral',
    'Arteria_afectada',
    'Localizacion',
    'Lateralizacion',
    'Etiologia'
]


PROCEDIMIENTOS = [
        'Trombolisis_intravenosa',
        'Trombectomia_mecanica',
        'Trombolisis_intraarterial',
        'TAC_craneal',
        'Test_de_disfagia',
        'Recanalizacion',
        'Puerta_aguja'
]

TRATAMIENTOS = [
        'Tratamiento_anticoagulante',
        'Tratamiento_antiagregante',
]



ESCALAS = [
        'mRankin',
        'NIHSS',
        'ASPECTS',
]


SUFFIX = ['_previa', '_alta', '_hab']
PREFIX = ["_SUG_"]

REQUIRED_HEADERS = ["SECCION_DIAGNOSTICO_PRINCIPAL", "SECCION_DIAGNOSTICOS"]

REQUIRED_MAIN_VARIABLES = ["Ictus_isquemico", "Ataque_isquemico_transitorio", "Hemorragia_cerebral"]

REQUIRED_SECOND_VARIABLES_FIRST = ["Lateralizacion", "Etiologia"]

REQUIRED_SECOND_VARIABLES = ["Arteria_afectada", "Localizacion", "Lateralizacion", "Etiologia"]

FECHA_HORA_DEPENDENCIES = {
                    "TAC_craneal": ["Fecha_TAC_inicial", "Hora_TAC_inicial"],
                    "Trombectomia_mecanica": ["Fecha_fin_trombectomia", "Fecha_inicio_trombectomia",
                                              "Fecha_primera_serie_trombectomia", "Hora_fin_trombectomia",
                                              "Hora_inicio_trombectomia", "Hora_primera_serie_trombectomia"],
                    "Trombolisis_intravenosa": ["Fecha_trombolisis_rtPA", "Hora_primer_bolus_trombolisis_rtPA"],
                    "Recanalizacion": ["Fecha_recanalizacion", "Fecha_recanalizacion"],
                    "Puerta_aguja": ["Tiempo_puerta_aguja"]}

def get_const(variable_type):

    if variable_type == 'DIAGNOSTICOS':
        return DIAGNOSTICOS
    elif variable_type == 'PROCEDIMIENTOS':
        return PROCEDIMIENTOS
    elif variable_type == 'TRATAMIENTOS':
        return TRATAMIENTOS
    elif variable_type == 'ESCALAS':
        return ESCALAS

def remove_suffix_prefix(label):
    for suffix in SUFFIX:
        label = label.replace(suffix, "")
    for prefix in PREFIX:
        label = label.replace(prefix, "")

    return label

def check_variable_type(records, variables_type):
    records_with_correct_variable_type = []

    for record in records:

        if record['label'] in get_const(variables_type):
            records_with_correct_variable_type.append(record)

    return records_with_correct_variable_type