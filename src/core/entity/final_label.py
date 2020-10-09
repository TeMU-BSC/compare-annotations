from src.core.const import const


def Eugenia_fecha_label(file, records, section, last_section, changed_varibales, merged_variables_hash, related_lines,
                        start_span_line, hora_alta_section, fecha_alta_section, fecha_de_ingreso_note):
    if section == 'SECCION_DEFAULT' or section == 'SECCION_TIPO_DE_INGRESO' \
            or section == last_section or section == 'SECCION_EVOLUCION':
        if section == 'SECCION_EVOLUCION':
            const.Fecha_hora_de_alta = ['exitus']
        else:
            const.Fecha_hora_de_alta = ['alta', 'exitus']
        for j, record in enumerate(records):
            if record['label'] == "FECHA":
                tuple = (record['text'], record['start'], record['end'], record['label'])
                fecha_note = merged_variables_hash[file][tuple]
                # if record['lable'] == "HORA":
                #     start_span_line = start_span_line
                # else:
                #     start_span_line = record['start']

                start_span_ent = record['start']
                if section == 'SECCION_DEFAULT' and 'Fecha_de_ingreso' not in changed_varibales and any(
                        ext in related_lines[start_span_line:start_span_ent].lower() for ext in const.Fecha_de_ingreso):
                    record['label'] = 'Fecha_de_ingreso'
                    start_span_line = record['start']
                    changed_varibales.append(record['label'])
                    fecha_de_ingreso_note = fecha_note

                elif (
                        hora_alta_section == section or hora_alta_section == "") and 'Fecha_de_alta' not in changed_varibales and \
                        fecha_de_ingreso_note != fecha_note and \
                        any(ext in related_lines[start_span_line:start_span_ent].lower() for ext in const.Fecha_hora_de_alta):
                    record['label'] = 'Fecha_de_alta'
                    changed_varibales.append(record['label'])
                    fecha_alta_section = section

            elif record['label'] == "HORA":
                start_span_ent = record['start']
                if (
                        fecha_alta_section == "" or fecha_alta_section == section) and 'Hora_de_alta' not in changed_varibales and any(
                        ext in related_lines[start_span_line:start_span_ent].lower() for ext in const.Fecha_hora_de_alta):
                    record['label'] = 'Hora_de_alta'
                    changed_varibales.append(record['label'])
                    hora_alta_section = section
    return records, hora_alta_section, fecha_alta_section


def TAC(section, related_lines, current_section_start_span, records):
    line_iterator = iter(related_lines.split('\n'))
    tac_enable = False
    next_line = next(line_iterator)
    start = 0
    for j, record in enumerate(records):

        if record['label'] == "_SUG_TAC_craneal":
            if section == "SECCION_DEFAULT":
                record['label'] = "WRONG_TAC_craneal"
            else:
                record['label'] = "TAC_craneal"
                Fecha_enable = True
                Hora_enable = True
        elif not tac_enable:
            continue

        length = len(next_line)
        while next_line is not None and record['end'] > start + current_section_start_span + len(next_line):
            start += len(next_line) + 1
            next_line = next(line_iterator)
            tac_enable = False

        if next_line is not None and (tac_enable or
                                      (record['label'] == "TAC_craneal" and
                                       record['start'] >= start + current_section_start_span  and
                                      record['end'] <= start + current_section_start_span + len(next_line))):
            tac_enable = True
            if record['end'] <= start + current_section_start_span + len(next_line):
                if record['label'] == "FECHA" and Fecha_enable:
                    record['label'] = "Fecha_TAC"
                    Fecha_enable = False
                elif record['label'] == "HORA" and Hora_enable:
                    record['label'] = "Hora_TAC"
                    Hora_enable = False
                elif record['label'] != "TAC_craneal":
                    tac_enable = False

            else:
                tac_enable = False

    return records
        # if next_line is not None and not tac_enable:
        #     start += len(next_line) + 1
        #     next_line = next(line_iterator)




