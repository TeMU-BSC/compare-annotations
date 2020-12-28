import difflib
import os
import string
from unidecode import unidecode
import src.core.const.const as const
from src.core.entity import final_label


class Entities:

    removed_punc_counter = dict()
    removed_punc = dict()

    @staticmethod
    def update_punc(punc, annotator, who):
        if who == "annotators" and punc not in Entities.removed_punc:
            if annotator not in Entities.removed_punc.keys():
                Entities.removed_punc[annotator] = [punc]
            else:
                temp = Entities.removed_punc.get(annotator)
                if punc not in temp:
                    temp.append(punc)
                    Entities.removed_punc.update({annotator: temp})

    @staticmethod
    def span_fixer(text, start_span, end_span, label, who, annotator):
        original_text = text
        if not (label.startswith("NIHSS") or label.startswith("mRankin") or label.startswith("ASPECTS") or len(text) != 0):
            punctuation = string.punctuation.replace(".", "")

            before_rstrip = len(text)
            text = text.rstrip()
            after_rstrip = len(text)
            end_span -= before_rstrip - after_rstrip
            while text[len(text) - 1] in punctuation:
                Entities.update_punc(text[len(text) - 1], annotator, who)

                text = text[:-1]
                removed_space = len(text) - len(text.rstrip())
                text = text.rstrip()
                end_span -= 1 + removed_space
            before_lstrip = len(text)
            text = text.lstrip()
            after_lstrip = len(text)
            start_span += before_lstrip - after_lstrip
            while text[0] in string.punctuation:
                Entities.update_punc(text[0], annotator, who)

                text = text[1:]
                removed_space = len(text) - len(text.lstrip())
                text = text.lstrip()
                start_span += 1 + removed_space

        if who == "annotators" and original_text != text:
            if annotator not in Entities.removed_punc_counter.keys():
                Entities.removed_punc_counter[annotator] = 1
            else:
                temp = Entities.removed_punc_counter.get(annotator)
                Entities.removed_punc_counter.update({annotator: temp + 1})

        return text, start_span, end_span

    # @staticmethod
    # def get_ctakes_entities(list_annotators, ctakes_dir, bunch, t_number=False):
    #     ctk = {}
    #     bunch_prefix = bunch.split("_")[0]
    #     for dir in list_annotators:
    #         ctakes_entities = {}
    #         for ctakes_files in os.listdir(os.path.join(ctakes_dir, bunch_prefix, dir)):
    #             if ctakes_files.endswith(".ann"):
    #                 first_main_variables = []
    #                 with open(os.path.join(ctakes_dir, bunch_prefix, dir, ctakes_files), "r") as r:
    #                     entites = []
    #                     for line in r:
    #                         temp_line = line.strip().split("\t", 2)
    #                         if line.startswith("T"):
    #                             checking_text = temp_line[-1].replace("\n", "")
    #                             checking_start = int(temp_line[1].split()[1])
    #                             checking_end = int(temp_line[1].split()[2])
    #                             checking_label = temp_line[1].split()[0]
    #
    #                             # THIS FILTER HAS BEEN ADDED TO BRATMERGER
    #                             # if checking_label in const.REQUIRED_SECOND_VARIABLES_FIRST :
    #                             #     if checking_label.split("_SUG_")[-1] in first_main_variables:
    #                             #         continue
    #                             #         # first_main_variables.append(record["label"].split("_SUG_")[-1])
    #                             #     else:
    #                             #         first_main_variables.append(checking_label.split("_SUG_")[-1])
    #
    #                             if bunch.startswith("04") or bunch.startswith("03") or bunch.startswith(
    #                                     "02") or bunch.startswith("01"):
    #                                 checking_text, checking_start, checking_end = \
    #                                     Entities.span_fixer(checking_text, checking_start, checking_end, checking_label,
    #                                                     "ctakes", dir)
    #
    #                                 if bunch.startswith("03") and temp_line[-1].replace("\n", "") != checking_text:
    #                                     print("ERROR!!!!!!")
    #
    #                             entity = {}
    #                             if t_number:
    #                                 entity = {'row': temp_line[0], 'text': checking_text,
    #                                       'start': checking_start,
    #                                       'end': checking_end, 'label': checking_label}
    #                             else:
    #                                 entity = {'text': checking_text,
    #                                       'start': checking_start,
    #                                       'end': checking_end, 'label': checking_label}
    #
    #                             entites.append(entity)
    #                     ctakes_ents = sorted(entites, key=lambda entity: entity['start'])
    #                     ctakes_entities[ctakes_files] = ctakes_ents
    #
    #         ctk[dir] = ctakes_entities
    #     return ctk

    @staticmethod
    def get_ctakes_entities(list_annotators, ctakes_dir, bunch, t_number=False):
        bunch_prefix = bunch.split("_")[0]

        ann_variable = {}
        ann_variable_hash = {}
        ann_sections = {}

        for dir in list_annotators:
            annotators_variable = {}
            annotators_variable_hash = {}
            annotators_sections = {}

            ctakes_entities = {}
            for annotators_files in os.listdir(os.path.join(ctakes_dir, bunch_prefix, dir)):
                if annotators_files.endswith(".ann"):

                    if annotators_files.startswith("sonespases_968053009"):
                        checl = 0
                    first_main_variables = []
                    with open(os.path.join(ctakes_dir, bunch_prefix, dir, annotators_files), "r") as r:
                        entites = []
                        entity_tuple = ()
                        entities_row = dict()
                        hash_entities = dict()
                        sections = []
                        pre_header = ""
                        for line in r:
                            if line.startswith("T10"):
                                check = 0
                            temp_line = line.strip().split("\t", 2)
                            if line.startswith("T"):

                                checking_text = temp_line[-1].replace("\n", "")
                                checking_start = int(temp_line[1].split()[1])
                                checking_end = int(temp_line[1].split()[2])
                                checking_label = temp_line[1].split()[0]
                                if bunch.startswith("04") or bunch.startswith("03") or bunch.startswith(
                                        "02") or bunch.startswith("01"):
                                    # For bunch 1,2,3 we revised manual annotations for variables and sections that
                                    # ended with a punctuations except of dot (.) and started with a punctuations
                                    # we fixed the span and saved it in a correct file (03, 02)...
                                    # for having a correct evaluation our pipeline tools with the manual, we should
                                    # apply the same for output of pipeline
                                    checking_text, checking_start, checking_end = \
                                        Entities.span_fixer(checking_text, checking_start, checking_end, checking_label,
                                                            "ctakes", dir)

                                    if bunch.startswith("03") and temp_line[-1].replace("\n", "") != checking_text:
                                        print("ERROR!!!!!!")

                                # entity['row'] = temp_line[0]
                                # entity['text'] = checking_text
                                # entity['start'] = checking_start
                                # entity['end'] = checking_end
                                # entity['label'] = checking_label

                                if checking_label.startswith("SECCION_"):
                                    # if checking_label != pre_header:
                                    if t_number:
                                        section = {'row': temp_line[0], 'text': checking_text,
                                                   'start': checking_start,
                                                   'end': checking_end, 'label': checking_label}
                                    else:
                                        section = {'text': checking_text,
                                                   'start': checking_start,
                                                   'end': checking_end, 'label': checking_label}

                                    sections.append(section)
                                    # else:
                                    #     print("X")
                                    pre_header = checking_label
                                else:
                                    if t_number:
                                        entity = {'row': temp_line[0], 'text': checking_text,
                                                  'start': checking_start,
                                                  'end': checking_end, 'label': checking_label}
                                    else:
                                        entity = {'text': checking_text,
                                                  'start': checking_start,
                                                  'end': checking_end, 'label': checking_label}

                                        entity_tuple = (checking_text, checking_start, checking_end, checking_label)

                                    entites.append(entity)

                                    if not t_number:
                                        entities_row[temp_line[0]] = entity_tuple

                            elif line.startswith("#"):

                                if t_number:
                                    hash_entities[temp_line[0]] = temp_line[1] + "\t" + temp_line[2]
                                else:
                                    hash_entities[temp_line[1].split(" ")[-1]] = temp_line[2]

                        vars_ordered = sorted(entites, key=lambda entity: entity['start'])
                        secs_ordered = sorted(sections, key=lambda entity: entity['start'])

                        annotators_variable[annotators_files] = vars_ordered

                        final_hash_entities = dict()
                        for hash, notes in hash_entities.items():
                            if t_number:
                                final_hash_entities[hash] = notes
                            elif entities_row.get(hash) is not None:
                                final_hash_entities[entities_row[hash]] = notes
                        annotators_variable_hash[annotators_files] = final_hash_entities

                        annotators_sections[annotators_files] = secs_ordered

            ann_variable[dir] = annotators_variable
            ann_variable_hash[dir] = annotators_variable_hash
            ann_sections[dir] = annotators_sections

        return ann_variable, ann_variable_hash, ann_sections

    @staticmethod
    def get_annotators_entities(list_annotators, annotators_dir, bunch, freq=None, t_number=False):
        all_files = {}
        annotator = {}
        annotator_notes = {}
        all_files_list = []
        for dir in list_annotators:
            list_files = []
            annotators_entities = {}
            annotators_hash = {}
            annotators_deep_dir = os.path.join(annotators_dir, bunch, dir)
            for annotators_files in os.listdir(annotators_deep_dir):
                if annotators_files.endswith(".ann"):
                    all_files_list.append(annotators_files.replace(".ann", ".txt"))
                    list_files.append(annotators_files)
                    with open(os.path.join(annotators_deep_dir, annotators_files), "r") as r:
                        entities = []
                        hash_ent = []
                        all_hash = []
                        keephash = []
                        for full_line in r:
                            line = full_line.split("\t", 1)
                            try:
                                line = line[1]
                            except:
                                print(dir, annotators_files, full_line)
                                exit()

                            if full_line.startswith("T") and not (line.startswith("HORA")or line.startswith("FECHA")
                                    or line.startswith("_SUG_") or line.startswith("TIEMPO")):
                                entity = {}
                                temp_line = full_line.split("\t", 2)
                                checking_text = temp_line[-1].replace("\n", "")
                                checking_start = int(temp_line[1].split()[1])
                                checking_end = int(temp_line[1].split()[-1])
                                checking_label = temp_line[1].split()[0]
                                if bunch.startswith("04") or bunch.startswith("03") or bunch.startswith(
                                        "02") or bunch.startswith("01"):
                                    # For bunch 1,2,3 we revised manual annotations for varibalea and section that
                                    # ended with a punctuations except of dot (.) and started with a punctuations
                                    # we fixed the span and saved it in a correct file (03, 02)...
                                    checking_text, checking_start, checking_end = \
                                        Entities.span_fixer(checking_text, checking_start, checking_end, checking_label,
                                                        "annotators", dir)

                                if t_number:
                                    entity['row'] = temp_line[0]
                                keephash.append(temp_line[0])
                                entity['text'] = checking_text
                                entity['start'] = checking_start
                                entity['end'] = checking_end
                                entity['label'] = checking_label
                                entities.append(entity)
                            elif full_line.startswith("T"):
                                entity = {}
                                temp_line = full_line.split("\t", 2)
                                if t_number:
                                    entity['row'] = temp_line[0]
                                entity['text'] = temp_line[-1].replace("\n", "")
                                entity['start'] = int(temp_line[1].split()[1])
                                entity['end'] = int(temp_line[1].split()[2])
                                entity['label'] = temp_line[1].split()[0]
                                if freq is not None:
                                    freq.update_notacceptance_freq(entity['text'], entity['label'])
                            elif full_line.startswith("#"):
                                all_hash.append(full_line)
                        for hash in all_hash:
                            row = hash.strip().split("\t", 2)[1].split(" ")[1]
                            if row in keephash:
                                # w_revised.write(hash)
                                entity = {}
                                temp_line = hash.strip().split("\t", 2)
                                entity['T'] = temp_line[1].split(" ")[1]
                                entity['rest'] = "\t".join(temp_line[2:])
                                hash_ent.append(entity)

                        r.close()
                        annotators_hash[annotators_files] = hash_ent
                        entities_ordered = sorted(entities, key=lambda entity: entity['start'])
                        annotators_entities[annotators_files] = entities_ordered

            annotator_notes[dir] = annotators_hash
            annotator[dir] = annotators_entities
            all_files[dir] = list_files

        return all_files_list, annotator, annotator_notes

    @staticmethod
    def get_final_annotators_entities(list_annotators, annotators_dir, bunch, t_number=False):

        variable_dict = dict()
        variable_hash_dict = dict()
        section_dict = dict()
        all_files_list = []
        # entities_dir = os.path.join(input_dir, dir, bunch)
        # for annotators_files in os.listdir(entities_dir):
        for dir in list_annotators:
            annotators_variable = {}
            annotators_variable_hash = {}
            annotators_sections = {}
            if not os.path.isdir(os.path.join(annotators_dir, bunch, dir)):
                continue
            for annotators_files in os.listdir(os.path.join(annotators_dir, bunch, dir)):
                if annotators_files.endswith(".ann"):
                    if annotators_files not in all_files_list:
                        all_files_list.append(annotators_files.replace(".ann", ".txt"))
                    if dir in variable_dict.keys() and annotators_files in variable_dict.get(dir).keys():
                        print("Douplicated file", bunch, dir, annotators_files)
                    with open(os.path.join(annotators_dir, bunch, dir, annotators_files), "r") as r:
                        entites = []
                        entity_tuple = ()
                        entities_row = dict()
                        hash_entities = dict()
                        sections = []
                        pre_header = ""
                        for line in r:
                            temp_line = line.strip().split("\t", 2)

                            if line.startswith("T") and not \
                                    (temp_line[1].startswith("HORA") or
                                     temp_line[1].startswith("FECHA") or
                                     temp_line[1].startswith("_SUG_") or
                                     temp_line[1].startswith("TIEMPO")):

                                checking_text = temp_line[-1].replace("\n", "")
                                checking_start = int(temp_line[1].split()[1])
                                checking_end = int(temp_line[1].split()[2])
                                checking_label = temp_line[1].split()[0]
                                if bunch.startswith("04") or bunch.startswith("03") or bunch.startswith(
                                        "02") or bunch.startswith("01"):
                                    # For bunch 1,2,3 we revised manual annotations for variables and sections that
                                    # ended with a punctuations except of dot (.) and started with a punctuations
                                    # we fixed the span and saved it in a correct file (03, 02)...
                                    # for having a correct evaluation our pipeline tools with the manual, we should
                                    # apply the same for output of pipeline
                                    checking_text, checking_start, checking_end = \
                                        Entities.span_fixer(checking_text, checking_start, checking_end, checking_label,
                                                        "ctakes", dir)

                                    if bunch.startswith("03") and temp_line[-1].replace("\n", "") != checking_text:
                                        print("ERROR!!!!!!")

                                # entity['row'] = temp_line[0]
                                # entity['text'] = checking_text
                                # entity['start'] = checking_start
                                # entity['end'] = checking_end
                                # entity['label'] = checking_label

                                if (checking_label.startswith("SECCION_") or
                                        (dir == 'eugenia' and (checking_label.split("_SUG_")[-1] in const.EUGENIA or
                                                           checking_label in const.FECHA_HORA_TIEMO)) or
                                        (dir == 'victoria' and (
                                                checking_label.split("_SUG_")[-1] in const.VICTORIA)) or
                                        ((dir == 'carmen' or dir == 'isabel') and
                                         (checking_label.split("_SUG_")[-1] in const.CARMEN_ISABEL or
                                          checking_label in const.FECHA_HORA_TIEMO))):

                                    if checking_label.startswith("SECCION_"):
                                        if checking_label != pre_header:
                                            if t_number:
                                                section = {'row': temp_line[0], 'text': checking_text,
                                                           'start': checking_start,
                                                           'end': checking_end, 'label': checking_label}
                                            else:
                                                section = {'text': checking_text,
                                                           'start': checking_start,
                                                           'end': checking_end, 'label': checking_label}


                                            sections.append(section)
                                        # else:
                                        #     print("X")
                                        pre_header = checking_label



                                    else:
                                        if t_number:
                                            entity = {'row': temp_line[0], 'text': checking_text,
                                                  'start': checking_start,
                                                  'end': checking_end, 'label': checking_label}
                                        else:
                                            entity = {'text': checking_text,
                                                      'start': checking_start,
                                                      'end': checking_end, 'label': checking_label}

                                            entity_tuple = (checking_text,checking_start, checking_end, checking_label)


                                        entites.append(entity)

                                        if not t_number:
                                            entities_row[temp_line[0]] = entity_tuple

                            elif line.startswith("#"):

                                if t_number:
                                    hash_entities[temp_line[0]] = temp_line[1] + "\t" + temp_line[2]
                                else:
                                    hash_entities[temp_line[1].split(" ")[-1]] = temp_line[2]


                        vars_ordered = sorted(entites, key=lambda entity: entity['start'])
                        secs_ordered = sorted(sections, key=lambda entity: entity['start'])

                        annotators_variable[annotators_files] = vars_ordered


                        final_hash_entities = dict()
                        for hash, notes in hash_entities.items():
                            if t_number:
                                final_hash_entities[hash] = notes
                            elif entities_row.get(hash) is not None:
                                final_hash_entities[entities_row[hash]] = notes
                        annotators_variable_hash[annotators_files] = final_hash_entities

                        annotators_sections[annotators_files] = secs_ordered


            # variable_dict[dir] = annotators_variable
            variable_dict = Entities.update_dic(dir, variable_dict, annotators_variable)
            variable_hash_dict = Entities.update_dic(dir, variable_hash_dict, annotators_variable_hash)
            section_dict = Entities.update_dic(dir, section_dict, annotators_sections)

            # variable_hash_dict[dir] = annotators_variable_hash
            # section_dict[dir] = annotators_sections

        return all_files_list, variable_dict, variable_hash_dict, section_dict

    @staticmethod
    def fix_ctakes_entities(bunch, ctakes_dir, merged_variables_hash, section_entities, variable_type):
        for file, sections in section_entities.items():
            print(file)
            if file.startswith("sonespases_968053009"):
                checl = 0
            text_file = open(os.path.join(ctakes_dir, bunch, 'eugenia', file.replace("ann", "txt")))
            lines = text_file.read()
            lines_lower = unidecode(lines.lower())
            start_span_line = 0
            changed_varibales = []
            last_section = list(sections.keys())[-1]
            fecha_alta_section = ""
            hora_alta_section = ""
            for i, (section, records) in enumerate(sections.items()):
                fecha_de_ingreso_note = ''
                current_Section_start_span = 0 if i == 0 else records[0]['end']
                start_span_line = current_Section_start_span

                next_section_start_span = sections[list(sections.keys())[i+1]][0]['start'] \
                    if len(sections) > i+1 else len(lines)
                # new_record = records[:]
                related_lines = lines # [current_Section_start_span:next_section_start_span]

                if variable_type == "EUGENIA_FECHA_HORA":
                    records, hora_alta_section, fecha_alta_section = \
                        final_label.Eugenia_fecha_label(file, records, section, last_section,
                                                        changed_varibales, merged_variables_hash, related_lines,
                                                        start_span_line, hora_alta_section, fecha_alta_section,
                                                        fecha_de_ingreso_note)
                    check = 0
                elif variable_type == "TAC":
                    related_lines = lines[current_Section_start_span:next_section_start_span]
                    records = final_label.TAC(section, related_lines, current_Section_start_span, records)
                elif variable_type == "DIAGNOSTICOS" and section in const.REQUIRED_HEADERS:
                    related_lines = lines[current_Section_start_span:next_section_start_span]
                    records = final_label.Diagnosticos(section, related_lines, current_Section_start_span, records)

        return section_entities

    @staticmethod
    def update_dic(dir, dict, value):
        if dir not in dict.keys():
            dict[dir] = value
        else:
            dict[dir].update(value)
        return dict

    @staticmethod
    def label_suffix_prefix_fixer(label):
            if label.startswith("Fecha") or label.startswith("Hora"):
                return label
            else:
                return const.remove_suffix_prefix(label)

    @staticmethod
    def entities_suffix_prefix_fixer(records):
        fixed_records = []
        for record in records:
            entity = {}
            entity['text'] = record['text']
            entity['start'] = record['start']
            entity['end'] = record['end']
            if record['label'].startswith("Fecha") or record['label'].startswith("Hora"):
                entity['label'] = record['label']
            else:
                entity['label'] = const.remove_suffix_prefix(record['label'])

            fixed_records.append(entity)
        fixed_records_ordered = sorted(fixed_records, key=lambda entity: entity['start'])

        return fixed_records_ordered

    @staticmethod
    def filter_on_diagnotstic(file, annotators):

        filtered_annotators = dict()
        for dir, records in annotators.items():
            filtered_records = []
            correct_header = False
            correct_diag = False
            for record in records:
                if correct_header or record[0] in const.REQUIRED_HEADERS:
                    correct_header = True
                    if record[0] not in const.REQUIRED_HEADERS and record[0].startswith("SECCION_"):
                        correct_header = False
                        if record[0] in const.REQUIRED_MAIN_VARIABLES:
                            filtered_records.append(record)
                    if correct_header and record[0] in const.REQUIRED_MAIN_VARIABLES:
                        correct_diag = True

                    if correct_header and (
                            record[0] in const.REQUIRED_HEADERS or record[0] in const.REQUIRED_MAIN_VARIABLES or record[
                        0] in const.REQUIRED_SECOND_VARIABLES):
                        filtered_records.append(record)

            filtered_annotators[dir] = filtered_records
            if not correct_diag:
                print("In", file + ",", dir, "did not annotated:", "Ictus_isquemico", "Ataque_isquemico_transitorio",
                      "Hemorragia_cerebral", "in Diagnostic Secccion")
        return filtered_annotators

    @staticmethod
    def filter_on_diagnotstic_everywhere(annotators):

        filtered_annotators = dict()
        for dir, records in annotators.items():
            filtered_records = []
            for record in records:
                if record[0] in const.REQUIRED_HEADERS or record[0] in const.REQUIRED_MAIN_VARIABLES or \
                        record[0] in const.REQUIRED_SECOND_VARIABLES:
                    filtered_records.append(record)
            filtered_annotators[dir] = filtered_records
        return filtered_annotators

    @staticmethod
    def filter_section(annotators):

        filtered_annotators = dict()
        for dir, records in annotators.items():
            filtered_records = []
            for record in records:
                if not record[0].startswith("SECCION_"):
                    filtered_records.append(record)
            filtered_annotators[dir] = filtered_records
        return filtered_annotators


    @staticmethod
    def isEntityAdded(adds_ann, file, annotator, rec_list):

        records_added = adds_ann[annotator][file]
        for record in records_added:
            if (rec_list[0] == record['label'] and rec_list[1] == record['start']
                    and rec_list[2] == record['end'] and rec_list[3] == record['text']):
                return 1
        return 0

    @staticmethod
    def isEntityChanged(changes_ann, file, annotator, rec_list):
        records_changed = changes_ann[annotator][file]
        for record in records_changed:
            if (rec_list[0] == record['label'] and rec_list[1] == record['start']
                    and rec_list[2] == record['end'] and rec_list[3] == record['text']):
                return 1
        return 0


    @staticmethod

    def set_wrong_category(type, status, label):
        wrong_categories = dict()
        if label == 'SECCION_DIAGNOSTICO_PRINCIPAL':
            check = 0
        score = 2 if status == "Agreed" else 1
        if type not in wrong_categories.keys():
            status_record = {label: {status: score}}
            wrong_categories[type] = status_record
        else:
            status_record_temp = wrong_categories[type]
            if label not in status_record_temp.keys():
                status_record_temp[label] = {status: score}
            else:
                label_temp = status_record_temp.get(label)
                if status not in label_temp.keys():
                    label_temp[status] = score
                else:
                    temp_status = label_temp.get(status)
                    temp_status += score
                    label_temp.update({status: temp_status})
                status_record_temp.update({label: label_temp})
            wrong_categories.update({type: status_record_temp})

        return wrong_categories

    @staticmethod
    def find_max_similarity_cat(rec, not_direct_cat):

        word = unidecode(rec[3].lower())
        max_score = -1
        list_similarities = difflib.get_close_matches(word, not_direct_cat.keys(), 1, 0.85)
        if len(list_similarities) > 0:
            for code_dic in not_direct_cat[list_similarities[0]]:
                if code_dic["label"] == rec[0]:
                    score = difflib.SequenceMatcher(None, word, list_similarities[0]).ratio()
                    return list_similarities[0], code_dic["label"], code_dic["code"], score
            return None, None, None, None
        else:
            return None, None, None, None


    @staticmethod
    def note_normolized_finder(annotators_entities, file, annotator, rec, list_notes):
        records = annotators_entities[annotator][file]
        row = None
        normolized = None
        for record in records:
            if record["label"] == rec[0] and record["start"] == rec[1] and record["end"] == rec[2] and record["text"] == \
                    rec[3]:
                row = record['row']

        for notes in list_notes:
            if notes['T'] == row:
                normolized = notes['rest']

        return normolized