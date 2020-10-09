from collections import OrderedDict

from src.core.util.utility import Util


class Merge:

    @staticmethod
    def merge_variables_sections(variables, sections):

        removed_varibale = 0
        section_variable = dict()

        # for files in variables.keys():
        file_section_variavle = {}
        for file, section_ann in sections.items():
            if file == "sonespases_920854601.ann":
                print("check")

            section_dic = OrderedDict()

            # section_ann = records

            variable_ann = variables.get(file)

            section_id = 0

            section_id = 0
            if section_ann is not None and variable_ann is not None:
                for variable_id, variable in enumerate(variable_ann):
                    variable['T'] = "T" + str(variable_id + 1)
                    current_section = section_ann[section_id]

                    # if current_section['label'] == 'SECCION_EVOLUCION':
                    #     print("D")
                    #
                    # if variable['start'] == 13210:
                    #     print("D")

                    if section_id == 0 and variable['start'] <= current_section['start']:
                        if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                            'label'] == "_SUG_Etiologia") and
                                variable['start'] >= current_section['start'] and variable['end'] <= current_section[
                                    'end']):
                            if "SECCION_DEFAULT" not in section_dic.keys():
                                section_dic['SECCION_DEFAULT'] = [variable]
                            else:
                                temp = section_dic['SECCION_DEFAULT']
                                temp.append(variable)
                                section_dic.update({'SECCION_DEFAULT': temp})
                        else:
                            # print(annotator, file, variable)
                            removed_varibale += 1
                    elif section_id == len(section_ann) - 1 and variable['start'] >= current_section['start']:
                        if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                            'label'] == "_SUG_Etiologia") and
                                variable['start'] >= current_section['start'] and variable['end'] <= current_section[
                                    'end']):
                            if current_section['label'] not in section_dic.keys():
                                section_dic[current_section['label']] = [
                                    {"T": "Details", "label": current_section['label'],
                                     "start": current_section['start'], "end": current_section['end'],
                                     "text": current_section['text']},
                                    variable]
                            else:
                                temp = section_dic.get(current_section['label'])
                                temp.append(variable)
                                section_dic.update({current_section['label']: temp})
                        else:
                            # print(annotator, file, variable)
                            removed_varibale += 1
                    elif current_section['start'] <= variable['start'] < section_ann[section_id + 1]['start']:
                        if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                            'label'] == "_SUG_Etiologia") and
                                variable['start'] >= current_section['start'] and variable['end'] <= current_section[
                                    'end']):
                            if current_section['label'] not in section_dic.keys():
                                section_dic[current_section['label']] = [
                                    {"T": "Details", "label": current_section['label'],
                                     "start": current_section['start'], "end": current_section['end'],
                                     "text": current_section['text']},
                                    variable]
                            else:
                                temp = section_dic[current_section['label']]
                                temp.append(variable)
                                section_dic.update({current_section['label']: temp})
                        else:
                            # print(annotator, file, variable)
                            removed_varibale += 1
                        if variable_id < (len(variable_ann) - 1):
                            if section_ann[section_id]['label'] not in section_dic.keys():
                                section_dic[section_ann[section_id]['label']] = [
                                    {"T": "Details", "start": section_ann[section_id]['start'],
                                     "end": section_ann[section_id]['end'], "label": section_ann[section_id]['label'],
                                     "text": section_ann[section_id]['text']}]
                            while section_id < (len(section_ann) - 1) and variable_ann[variable_id + 1]['start'] >= \
                                    section_ann[section_id + 1]['start']:
                                if section_ann[section_id + 1]['label'] not in section_dic.keys():
                                    section_dic[section_ann[section_id + 1]['label']] = [
                                        {"T": "Details", "start": section_ann[section_id + 1]['start'],
                                         "end": section_ann[section_id + 1]['end'],
                                         "label": section_ann[section_id + 1]['label'],
                                         "text": section_ann[section_id + 1]['text']}]
                                else:
                                    missed = True
                                    for sec_detail in section_dic.get(section_ann[section_id + 1]['label']):
                                        if sec_detail['T'].startswith("Details") and sec_detail['start'] == \
                                                section_ann[section_id + 1]['start']:
                                            missed = False
                                    if missed:
                                        temp = section_dic[section_ann[section_id + 1]['label']]
                                        temp.append({"T": "Details", "start": section_ann[section_id + 1]['start'],
                                                     "end": section_ann[section_id + 1]['end'],
                                                     "label": section_ann[section_id + 1]['label'],
                                                     "text": section_ann[section_id + 1]['text']})
                                        section_dic.update({section_ann[section_id + 1]['label']: temp})
                                section_id += 1
                        # else:
                        #     print("CHECK")
                    else:
                        if variable_id < (len(variable_ann) - 1):
                            while section_id < (len(section_ann) - 1) and variable_ann[variable_id]['start'] >= \
                                    section_ann[section_id + 1]['start']:
                                if section_ann[section_id]['label'] not in section_dic.keys():
                                    section_dic[section_ann[section_id]['label']] = [
                                        {"T": "Details", "start": section_ann[section_id]['start'],
                                         "end": section_ann[section_id]['end'],
                                         "label": section_ann[section_id]['label'],
                                         "text": section_ann[section_id]['text']}]
                                else:
                                    missed = True
                                    for sec_detail in section_dic.get(section_ann[section_id]['label']):
                                        if sec_detail['T'].startswith("Details") and sec_detail['start'] == \
                                                section_ann[section_id]['start']:
                                            missed = False
                                    if missed:
                                        temp = section_dic[section_ann[section_id]['label']]
                                        temp.append({"T": "Details", "start": section_ann[section_id]['start'],
                                                     "end": section_ann[section_id]['end'],
                                                     "label": section_ann[section_id]['label'],
                                                     "text": section_ann[section_id]['text']})
                                        section_dic.update({section_ann[section_id]['label']: temp})
                                section_id += 1
                            if not ((variable['label'] == "_SUG_Lateralizacion" or variable[
                                'label'] == "_SUG_Etiologia") and
                                    variable['start'] >= section_ann[section_id]['start'] and variable['end'] <=
                                    section_ann[section_id]['end']):
                                if section_ann[section_id]['label'] not in section_dic.keys():
                                    section_dic[section_ann[section_id]['label']] = [
                                        {"T": "Details", "start": section_ann[section_id]['start'],
                                         "end": section_ann[section_id]['end'],
                                         "label": section_ann[section_id]['label'],
                                         "text": section_ann[section_id]['text']}, variable]
                                else:
                                    temp = section_dic[section_ann[section_id]['label']]
                                    temp.append(variable)
                                    section_dic.update({section_ann[section_id]['label']: temp})
                        # else:
                        #     print("CHECK")

                for current_section in section_ann:
                    if current_section['label'] not in section_dic.keys():
                        section_dic[current_section['label']] = [
                            {"T": "Details", "start": current_section['start'], "end": current_section['end'],
                             "label": current_section['label'], "text": current_section['text']}]
                    else:
                        missed = True
                        for sec_detail in section_dic.get(current_section['label']):
                            if sec_detail['T'].startswith("Details") and sec_detail['start'] \
                                    == current_section['start']:
                                missed = False
                        if missed:
                            temp = section_dic[current_section['label']]
                            temp.append({"T": "Details", "start": current_section['start'],
                                         "end": current_section['end'],
                                         "label": current_section['label'],
                                         "text": current_section['text']})
                            section_dic.update({current_section['label']: temp})
            elif section_ann is None and variable_ann is not None:
                for variable_id, variable in enumerate(variable_ann):
                    if "SECCION_DEFAULT" not in section_dic.keys():
                        section_dic['SECCION_DEFAULT'] = [variable]
                    else:
                        temp = section_dic['SECCION_DEFAULT']
                        temp.append(variable)
                        section_dic.update({'SECCION_DEFAULT': temp})
            elif variable_ann is None and section_ann is not None:
                for current_section in section_ann:
                    if current_section['label'] not in section_dic.keys():
                        section_dic[current_section['label']] = [
                            {"T": "Details", "start": current_section['start'], "end": current_section['end'],
                             "label": current_section['label'], "text": current_section['text']}]
                    else:
                        missed = True
                        for sec_detail in section_dic.get(current_section['label']):
                            if sec_detail['T'].startswith("Details") and sec_detail['start'] \
                                    == current_section['start']:
                                missed = False
                        if missed:
                            temp = section_dic[current_section['label']]
                            temp.append({"T": "Details", "start": current_section['start'],
                                         "end": current_section['end'],
                                         "label": current_section['label'],
                                         "text": current_section['text']})
                            section_dic.update({current_section['label']: temp})
            else:
                continue


            file_section_variavle[file] = section_dic

        print(removed_varibale,
              "Number of variables that have been removed for _SUG_Lateralizacion and _SUG_Etiologia\n")

        return file_section_variavle


    @staticmethod
    def merge_entities(entities):
        merged_ents = dict()
        owner_file = dict()
        for annotator, annotation_files in entities.items():
            for annotator_file, records in annotation_files.items():
                # if annotator_file == "sonespases_920854601.ann":
                #     print("checl")
                if annotator_file not in owner_file.keys():
                    owner_file[annotator_file] = annotator

                merged_records = merged_ents.get(annotator_file)
                if merged_records is None:
                    merged_records = []
                for record in records:
                    if record not in merged_records:
                        merged_records.append(record)
                        merged_ents.update({annotator_file: merged_records})
                    else:
                        pass
        return merged_ents, owner_file

    @staticmethod
    def merge_hash(entities_hash):
        merged_ents = dict()
        for annotator, annotation_files in entities_hash.items():
            for annotator_file, records in annotation_files.items():
                merged_records = merged_ents.get(annotator_file)
                if merged_records is None:
                    merged_records = dict()
                for record, value in records.items():
                    if record not in merged_records.keys():
                        merged_records[record] = value
                        merged_ents.update({annotator_file: merged_records})
                    else:
                        if record[3].startswith("Fecha") and "-" in value and "-" not in merged_records[record]:
                            merged_records[record] = value
                            merged_ents.update({annotator_file: merged_records})
                        elif not record[3].startswith("Fecha") and len(value) > len(merged_records[record]):
                            merged_records[record] = value
                            merged_ents.update({annotator_file: merged_records})
                        # if value != merged_records[record]:
                        #     print(annotator, annotator_file, value, merged_records[record])

        return merged_ents

    @staticmethod
    def merge_normal_variable_section(variable, section):
        entities = dict()
        for dir, files in variable.items():
            enttites_dir = dict()
            for file, records in files.items():
                enttites_dir[file] = records + section[dir][file]
            entities[dir] = enttites_dir

        return entities

    @staticmethod
    def unmerged(section_variables):
        entities = dict()
        for file, sections in section_variables.items():
            entity_file = []
            # t = 0
            for section, records in sections.items():
                for record in records:
                    entity = {}
                    entity['text'] = record['text']
                    entity['start'] = record['start']
                    entity['end'] = record['end']
                    entity['label'] = record['label']
                    # entity['row'] = "T" + str(t)
                    entity_file.append(entity)
                    # t += 1
            entities[file] = entity_file
        return entities

