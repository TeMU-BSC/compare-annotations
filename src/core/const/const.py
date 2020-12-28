CARMEN_ISABEL = ["Trombolisis_intravenosa", "Trombectomia_mecanica", "Trombolisis_intraarterial", "TAC_craneal",
                 "Test_de_disfagia",
                 "Fecha_trombolisis_rtPA", "Fecha_inicio_trombectomia", "Fecha_primera_serie_trombectomia",
                 "Fecha_recanalizacion", "Fecha_fin_trombectomia", "Fecha_inicio_trombolisis_intraarterial",
                 "Fecha_TAC",
                 "Hora_primer_bolus_trombolisis_rtPA", "Hora_inicio_trombectomia", "Hora_primera_serie_trombectomia",
                 "Hora_recanalizacion", "Hora_fin_trombectomia", "Hora_inicio_trombolisis_intraarterial", "Hora_TAC",
                 "Tiempo_puerta_puncion", "Tiempo_puerta_aguja"]

EUGENIA = ["Ictus_isquemico", "Ataque_isquemico_transitorio", "Hemorragia_cerebral",
           "Arteria_afectada", "Localizacion", "Lateralizacion", "Etiologia",
           "Fecha_de_ingreso", "Fecha_de_alta", "Hora_de_alta",
           "Fecha_llegada_hospital", "Hora_llegada_hospital",
           "Fecha_inicio_sintomas", "Hora_inicio_sintomas"]

VICTORIA = ["Tratamiento_anticoagulante", "Tratamiento_antiagregante",
            "Tratamiento_anticoagulante_hab", "Tratamiento_antiagregante_hab",
            "mRankin", "mRankin_previa", "mRankin_alta",
            "NIHSS", "NIHSS_previa", "NIHSS_alta", "ASPECTS",
            "Tratamiento_anticoagulante_alta", "Tratamiento_antiagregante_alta"]

ALL_TYPES = ["DIAGNOSTICOS_MAIN_VARIABLES", "DIAGNOSTICOS_ATTRIBUTES", "DIAGNOSTICOS", "PROCEDIMIENTOS", "TRATAMIENTOS", "ESCALAS"]
SUB_TYPES = ["Arteria_afectada", "Etiologia", "Lateralizacion", "Localizacion", "TAC_craneal"]
# --------------------EUGENIA----------------------

# Eugenia Diagsnotic

DIAGNOSTICOS = [
    'Ictus_isquemico',
    'Ataque_isquemico_transitorio',
    'Hemorragia_cerebral',
    'Arteria_afectada',
    'Localizacion',
    'Lateralizacion',
    'Etiologia'
]

# Eugenia Just 3 parameters, more in EUGENIA variable
EUGENIA_FECHA_HORA = ["Fecha_de_ingreso", "Fecha_de_alta", "Hora_de_alta"]

# EUGENIA_FECHA_HORA = ["Fecha_de_ingreso","Fecha_de_alta", "Hora_de_alta",
#                        "Fecha_llegada_hospital","Fecha_inicio_sintomas",
#                        "Hora_llegada_hospital", "Hora_inicio_sintomas"]

Fecha_de_ingreso = ['ingreso', 'ingres', 'inici', 'domicil', 'res.soc', 'admissio', 'aguts', "aten.primaria"]
Fecha_hora_de_alta = ['alta', 'exitus']

# --------------------EUGENIA----------------------

# -------------- Carmen and Isabel ------------------


# Carmen and Isabel Fecha and Hora
CARMEN_ISABEL_FECHA_HORA = ["Fecha_trombolisis_rtPA", "Hora_primer_bolus_trombolisis_rtPA",

                            "Fecha_fin_trombectomia", "Hora_fin_trombectomia",
                            "Fecha_primera_serie_trombectomia", "Hora_primera_serie_trombectomia",
                            "Fecha_inicio_trombectomia", "Hora_inicio_trombectomia",
                            "Fecha_inicio_trombolisis_intraarterial", "Hora_inicio_trombolisis_intraarterial",

                            "Fecha_TAC", "Hora_TAC",

                            "Fecha_recanalizacion", "Hora_recanalizacion",

                            "Tiempo_puerta_puncion","Tiempo_puerta_aguja"]

# Carmen and Isabel precedimientos
PROCEDIMIENTOS = [
        'Trombolisis_intravenosa',
        'Trombectomia_mecanica',
        'Trombolisis_intraarterial',
        'TAC_craneal',
        'Recanalizacion',
        'Puerta_aguja'
        'Test_de_disfagia',
]


# TAC and its Fecha anf Hora - related to Procedimientos category
TAC = ["Fecha_TAC", "Hora_TAC", 'TAC_craneal']


FECHA_HORA_DEPENDENCIES = {
                    "TAC_craneal": ["Fecha_TAC", "Hora_TAC"],
                    "Trombectomia_mecanica": ["Fecha_fin_trombectomia", "Fecha_inicio_trombectomia",
                                              "Fecha_primera_serie_trombectomia", "Hora_fin_trombectomia",
                                              "Hora_inicio_trombectomia", "Hora_primera_serie_trombectomia"],
                    "Trombolisis_intravenosa": ["Fecha_trombolisis_rtPA", "Hora_primer_bolus_trombolisis_rtPA"],
                    "Recanalizacion": ["Fecha_recanalizacion", "Fecha_recanalizacion"],
                    "Puerta_aguja": ["Tiempo_puerta_aguja"]}




# -------------- Carmen and Isabel ------------------


# --------------------VICTORIA-----------------------

# TRATAMIENTOS Category - VICTORIA
TRATAMIENTOS = [
        'Tratamiento_anticoagulante',
        'Tratamiento_antiagregante',
]

# ESCALAS Categories - VICTORIA
ESCALAS = [
        'mRankin',
        'NIHSS',
        'ASPECTS',
]
# --------------------VICTORIA-----------------------


SUFFIX = ['_previa', '_alta', '_hab']
PREFIX = ["_SUG_"]

ETILOGIA_LIST = ["a estudio", "aneurisma", "angiopatía amiloide", "ateromatosis", "aterosclerótico",
                         "Aterotrombótico", "Cardioembólico", "Cavernoma de circunvolución", "Criptogènic",
                         "criptogénico", "Disecció", "embòlic", "embólico", "ESUS", "Hipertensiva", "Indeterminado",
                         "indeterminada", "Indeterminado de causa doble",
                         "Indeterminado por estudio incompleto", "infrecuente", "Inhabitual",
                         "Lacunar", "malformación arteriovenosa", "mecanisme embòlic",
                         "secundaria a malformación vascular", "secundaria a tumor"]

# ---------------------------------------------------

REQUIRED_HEADERS = ["SECCION_DIAGNOSTICO_PRINCIPAL", "SECCION_DIAGNOSTICOS"]

REQUIRED_MAIN_VARIABLES = ["Ictus_isquemico", "Ataque_isquemico_transitorio", "Hemorragia_cerebral"]

REQUIRED_SECOND_VARIABLES_FIRST = ["Lateralizacion", "Etiologia"]

REQUIRED_SECOND_VARIABLES = ["Arteria_afectada", "Localizacion", "Lateralizacion", "Etiologia"]

FECHA_HORA_TIEMO = ["HORA", "FECHA", "TIEMPO"]

HOSPITAL_NAME= ["sonespases", "aquas", "sant_pau", "matua", "mar"]

def get_const(variable_type):


    if variable_type == 'DIAGNOSTICOS':
        return DIAGNOSTICOS
    elif variable_type == 'DIAGNOSTICOS_MAIN_VARIABLES':
        return REQUIRED_MAIN_VARIABLES
    elif variable_type == 'DIAGNOSTICOS_ATTRIBUTES':
        return REQUIRED_SECOND_VARIABLES
    elif variable_type == 'PROCEDIMIENTOS':
        return PROCEDIMIENTOS
    elif variable_type == 'TRATAMIENTOS':
        return TRATAMIENTOS
    elif variable_type == 'ESCALAS':
        return ESCALAS
    elif variable_type == 'EUGENIA_FECHA_HORA':
        return EUGENIA_FECHA_HORA
    elif variable_type == 'TAC':
        return TAC
    elif variable_type == 'VICTORIA':
        return VICTORIA


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