def return_full_marital_status(marital_status):
    marital_status = marital_status.upper()
    if marital_status == 'CASADO' or marital_status == 'CASADA' or marital_status == 'CASADO/A':
        return 'Casado/a'
    if marital_status == 'DIVORCIADO' or marital_status == 'DIVORCIADA' or marital_status == 'DIVORCIADO/A':
        return 'Divorciado/a'
    if marital_status == 'VIUDO' or marital_status == 'VIUDA' or marital_status == 'VIUDO/A':
        return 'Viudo/a'
    if marital_status == 'SOLTERO' or marital_status == 'SOLTERA' or marital_status == 'SOLTERO/A':
        return 'Soltero/a'
    if marital_status == 'SEPARADO' or marital_status == 'SEPARADA' or marital_status == 'SEPARADO/A':
        return 'Separado/a'
    if marital_status == 'UNION CIVIL':
        return 'Unido/a civilmente'
    if marital_status == 'SEPARADO U/C' or marital_status == 'SEPARADA U/C' or marital_status == 'SEPARADO/A U/C':
        return 'Separado/a de Un. Civ.'
    if marital_status == 'DIVORCIADO U/C' or marital_status == 'DIVORCIADA U/C' or marital_status == 'DIVORCIADO/A U/C':
        return 'Divorciado/a de Un. Civ.'
    if marital_status == 'VIUDO U/C' or marital_status == 'VIUDA U/C' or marital_status == 'VIUDO/A U/C':
        return 'Viudo/a de Un. Civ.'
    raise Exception('Marital status not present in Prenotami availability list')


def return_full_parental_relationship(parental_relationship):
    if parental_relationship == 'Concubino':
        return 'Concubino'
    if parental_relationship == 'Conyuge':
        return 'Conyuge'
    if parental_relationship == 'Conyuge divorciado':
        return 'Conyuge divorciado'
    if parental_relationship == 'Conyuge separado':
        return 'Conyuge separado'
    if parental_relationship == 'Hermano' or parental_relationship == 'Hermana' or parental_relationship == 'Hermano/Hermana':
        return 'Hermano/Hermana'
    if parental_relationship == 'Hijo de otro conyuge':
        return 'Hijo de otro conyuge'
    if parental_relationship == 'Hijo' or parental_relationship == 'Hija' or parental_relationship == 'Hijo/a':
        return 'Hijo/a'
    if parental_relationship == 'Menor en tenencia':
        return 'Menor en tenencia'
    if parental_relationship == 'Nieto':
        return 'Nieto'
    if parental_relationship == 'Padre' or parental_relationship == 'Madre' or parental_relationship == 'Padre/Madre':
        return 'Padre/Madre'
    if parental_relationship == 'Suegro' or parental_relationship == 'Suegra' or parental_relationship == 'Suegro/Suegra':
        return 'Suegro/Suegra'
    if parental_relationship == 'Yerno' or parental_relationship == 'Nuera' or parental_relationship == 'Yerno/Nuera':
        return 'Yerno/Nuera'
    raise Exception('Parental relationship not present in Prenotami availability list')


def sanitize_appointment_reason(appointment_reason):
    valid_reasons = {'Negocios', 'Tratamientos médicos', 'Competencia deportiva', 'Trabajo independiente',
                     'Trabajo subordinado', 'Misión', 'Motivos religiosos', 'Investigación', 'Estudio', 'Tránsito',
                     'Transporte', 'Turismo', 'Turista - Visita familiares/amigos', 'Reingresso', 'Altro'}
    if appointment_reason not in valid_reasons:
        raise Exception('Invalid appointment reason')

    return appointment_reason
