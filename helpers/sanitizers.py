import enum


class MaritalStatus(enum.Enum):
    CASADO_CASADA = 'Coniugato/a'
    DIVORCIADO_DIVORCIADA = 'Divorziato/a'
    VIUDO_VIUDA = 'Vedovo/a'
    SOLTERO_SOLTERA = 'Celibe/Nubile'
    SEPARADO_SEPARADA = 'Separato/a'
    UNION_CIVIL = 'Unito/a Civilmente'
    SEPARADO_UNION_CIVIL = 'Separato/a da Un. Civ.'
    DIVORCIADO_UNION_CIVIL = 'Divorziato/a da Un. Civ.'
    VIUDO_UNION_CIVIL = 'Vedovo/a da Un. Civ.'


class ParentalRelationship(enum.Enum):
    CONCUBINO = 'Convivente'
    CONYUGE = 'Coniuge'
    CONYUGE_DIVORCIADO = 'Coniuge divorziato'
    CONYUGE_SEPARADO = 'Coniuge separato'
    HERMANO_HERMANA = 'Fratello/Sorella'
    HIJO_OTRO_CONYUGE = 'Figlio di altro coniuge'
    HIJO_HIJA = 'Figlio/a'
    MENOR_EN_TENENCIA = 'Minore in affidamento'
    NIETO = 'Nipote'
    PADRE_MADRE = 'Genitore'
    SUEGRO_SUEGRA = 'Suocero/Suocera'
    YERNO_NUERA = 'Genero/Nuora'


def return_full_marital_status(marital_status):
    marital_status = marital_status.upper()
    if marital_status == 'CASADO' or marital_status == 'CASADA' or marital_status == 'CASADO/A':
        return MaritalStatus.CASADO_CASADA
    if marital_status == 'DIVORCIADO' or marital_status == 'DIVORCIADA' or marital_status == 'DIVORCIADO/A':
        return MaritalStatus.DIVORCIADO_DIVORCIADA
    if marital_status == 'VIUDO' or marital_status == 'VIUDA' or marital_status == 'VIUDO/A':
        return MaritalStatus.VIUDO_VIUDA
    if marital_status == 'SOLTERO' or marital_status == 'SOLTERA' or marital_status == 'SOLTERO/A':
        return MaritalStatus.SOLTERO_SOLTERA
    if marital_status == 'SEPARADO' or marital_status == 'SEPARADA' or marital_status == 'SEPARADO/A':
        return MaritalStatus.SEPARADO_SEPARADA
    if marital_status == 'UNION CIVIL':
        return MaritalStatus.UNION_CIVIL
    if marital_status == 'SEPARADO U/C' or marital_status == 'SEPARADA U/C' or marital_status == 'SEPARADO/A U/C':
        return MaritalStatus.SEPARADO_UNION_CIVIL
    if marital_status == 'DIVORCIADO U/C' or marital_status == 'DIVORCIADA U/C' or marital_status == 'DIVORCIADO/A U/C':
        return MaritalStatus.DIVORCIADO_UNION_CIVIL
    if marital_status == 'VIUDO U/C' or marital_status == 'VIUDA U/C' or marital_status == 'VIUDO/A U/C':
        return MaritalStatus.VIUDO_UNION_CIVIL
    raise Exception('Marital status not present in Prenotami availability list')


def return_full_parental_relationship(parental_relationship):
    relationship = parental_relationship.upper()
    if relationship == 'CONCUBINO':
        return ParentalRelationship.CONCUBINO
    if relationship == 'CONYUGE':
        return ParentalRelationship.CONYUGE
    if relationship == 'CONYUGE DIVORCIADO':
        return ParentalRelationship.CONYUGE_DIVORCIADO
    if relationship == 'CONYUGE SEPARADO':
        return ParentalRelationship.CONYUGE_SEPARADO
    if relationship == 'HERMANO' or relationship == 'HERMANA' or relationship == 'HERMANO/HERMANA':
        return ParentalRelationship.HERMANO_HERMANA
    if relationship == 'HIJO DE OTRO CONYUGE':
        return ParentalRelationship.HIJO_OTRO_CONYUGE
    if relationship == 'HIJO' or relationship == 'HIJA' or relationship == 'HIJO/A':
        return ParentalRelationship.HIJO_HIJA
    if relationship == 'MENOR EN TENENCIA':
        return ParentalRelationship.MENOR_EN_TENENCIA
    if relationship == 'NIETO':
        return ParentalRelationship.NIETO
    if relationship == 'PADRE' or relationship == 'MADRE' or relationship == 'PADRE/MADRE':
        return ParentalRelationship.PADRE_MADRE
    if relationship == 'SUEGRO' or relationship == 'SUEGRA' or relationship == 'SUEGRO/SUEGRA':
        return ParentalRelationship.SUEGRO_SUEGRA
    if relationship == 'YERNO' or relationship == 'NUERA' or relationship == 'YERNO/NUERA':
        return ParentalRelationship.YERNO_NUERA
    raise Exception('Parental relationship not present in Prenotami availability list')


def sanitize_appointment_reason(appointment_reason):
    valid_reasons = {'Negocios', 'Tratamientos médicos', 'Competencia deportiva', 'Trabajo independiente',
                     'Trabajo subordinado', 'Misión', 'Motivos religiosos', 'Investigación', 'Estudio', 'Tránsito',
                     'Transporte', 'Turismo', 'Turista - Visita familiares/amigos', 'Reingresso', 'Altro'}
    if appointment_reason not in valid_reasons:
        raise Exception('Invalid appointment reason')

    return appointment_reason
