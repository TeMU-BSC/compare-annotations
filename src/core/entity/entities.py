import difflib
import os
import string
from unidecode import unidecode
import core.const.const as const


class Entities:

    removed_punc_counter = dict()
    removed_punc = dict()

    @staticmethod
    def update_punc(punc, annotator, who):
        if who is "annotators" and punc not in Entities.removed_punc:
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

        if who is "annotators" and original_text != text:
            if annotator not in Entities.removed_punc_counter.keys():
                Entities.removed_punc_counter[annotator] = 1
            else:
                temp = Entities.removed_punc_counter.get(annotator)
                Entities.removed_punc_counter.update({annotator: temp + 1})

        return text, start_span, end_span

    @staticmethod
    def get_ctakes_entities(list_annotators, ctakes_dir, bunch, t_number=False):
        ctk = {}
        bunch_prefix = bunch.split("_")[0]
        for dir in list_annotators:
            ctakes_entities = {}
            for ctakes_files in os.listdir(os.path.join(ctakes_dir, bunch_prefix, dir)):
                if ctakes_files.endswith(".ann"):
                    first_main_variables = []
                    with open(os.path.join(ctakes_dir, bunch_prefix, dir, ctakes_files), "r") as r:
                        entites = []
                        for line in r:
                            temp_line = line.strip().split("\t", 2)
                            if line.startswith("T"):
                                checking_text = temp_line[-1].replace("\n", "")
                                checking_start = int(temp_line[1].split()[1])
                                checking_end = int(temp_line[1].split()[2])
                                checking_label = temp_line[1].split()[0]

                                # THIS FILTER HAS BEEN ADDED TO BRATMERGER
                                # if checking_label in const.REQUIRED_SECOND_VARIABLES_FIRST :
                                #     if checking_label.split("_SUG_")[-1] in first_main_variables:
                                #         continue
                                #         # first_main_variables.append(record["label"].split("_SUG_")[-1])
                                #     else:
                                #         first_main_variables.append(checking_label.split("_SUG_")[-1])

                                if bunch.startswith("04") or bunch.startswith("03") or bunch.startswith(
                                        "02") or bunch.startswith("01"):
                                    checking_text, checking_start, checking_end = \
                                        Entities.span_fixer(checking_text, checking_start, checking_end, checking_label,
                                                        "ctakes", dir)

                                    if bunch.startswith("03") and temp_line[-1].replace("\n", "") != checking_text:
                                        print("ERROR!!!!!!")

                                entity = {}
                                if t_number:
                                    entity = {'row': temp_line[0], 'text': checking_text,
                                          'start': checking_start,
                                          'end': checking_end, 'label': checking_label}
                                else:
                                    entity = {'text': checking_text,
                                          'start': checking_start,
                                          'end': checking_end, 'label': checking_label}

                                entites.append(entity)
                        ctakes_ents = sorted(entites, key=lambda entity: entity['start'])
                        ctakes_entities[ctakes_files] = ctakes_ents

            ctk[dir] = ctakes_entities
        return ctk

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
    def entities_suffix_prefix_fixer(records):
        fixed_records = []

        for record in records:

            entity = {}
            entity['text'] = record['text']
            entity['start'] = record['start']
            entity['end'] = record['end']
            entity['label'] = const.remove_suffix_prefix(record['label'])

            fixed_records.append((entity))
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
                if record[0] in const.REQUIRED_HEADERS or record[0] in const.REQUIRED_MAIN_VARIABLES or record[
                    0] in const.REQUIRED_SECOND_VARIABLES:
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