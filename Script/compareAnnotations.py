import argparse
import csv
import os
import shutil
from collections import OrderedDict
from shutil import copy
import unidecode
import xlsxwriter
import numpy as np
import unidecode

from Script.utility import reading_duplicated_files

fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
main_dir = os.path.join(parentDir, "Annotated")
Set = None
annotators_dir = ""
pre_processing_dir = ""
IAA_ANN_dir = ""
IAA_CSV_dir = ""
all_differences_csv_dir = ""
ctakes_dir = ""
headers_name_dic = dict()
headers_type_dic = dict()

acceptance_rate = dict()


def headers_dic(header):
    with open(header, "r") as h:
        for line in h:
            row_header = line.strip().split("\t")
            if not row_header[2] in headers_name_dic.keys():
                headers_name_dic[row_header[2]] = row_header[1]
            if not row_header[1] in headers_type_dic.keys():
                headers_type_dic[row_header[1]] = row_header[0]


def init(sset):
    global annotators_dir, pre_processing_dir, IAA_ANN_dir, IAA_CSV_dir, ctakes_dir, \
        all_differences_csv_dir

    annotators_dir = os.path.join(main_dir, "manual_annotations")
    pre_processing_dir = os.path.join(main_dir, "pre_processing")
    IAA_ANN_dir = os.path.join(main_dir, "IAA_ANN", sset)
    IAA_CSV_dir = os.path.join(main_dir, "IAA_CSV", sset)
    all_differences_csv_dir = os.path.join(main_dir, "analysis")
    ctakes_dir = os.path.join(main_dir, "pre_annotations")

    shutil.rmtree(IAA_ANN_dir, ignore_errors=True)
    os.makedirs(IAA_ANN_dir, exist_ok=True)
    os.makedirs(IAA_CSV_dir, exist_ok=True)


def annators():
    list_annotators = []
    for sub_dir in os.listdir(annotators_dir):
        if not sub_dir.startswith('.'):
            list_annotators.append(sub_dir)

    return list_annotators


def pre_processing(annotators, sset):
    all_files = {}
    annotator = {}
    annotator_notes = {}
    rm = {}
    for dir in annotators:
        list_files = []
        pre_pro = os.path.join(pre_processing_dir, dir, sset)

        # shutil.rmtree(pre_pro)
        os.makedirs(pre_pro, exist_ok=True)

        annotators_entities = {}
        annotators_hash = {}
        removes = {}
        annotators_deep_dir = os.path.join(annotators_dir, dir, sset)
        for annotators_files in os.listdir(annotators_deep_dir):
            if annotators_files.endswith(".ann"):
                list_files.append(annotators_files)
                with open(os.path.join(annotators_deep_dir, annotators_files), "r") as r:
                    entities = []
                    remove_ent = []
                    hash_ent = []
                    with open(os.path.join(pre_pro, annotators_files), "w") as w:
                        all_hash = []
                        keephash = []
                        for full_line in r:
                            line = full_line.split("\t", 1)[1]
                            if not (line.startswith("HORA") or full_line.startswith("#") or line.startswith("FECHA")
                                    or line.startswith("_SUG_") or line.startswith("TIEMPO")):
                                w.write(full_line)
                                entity = {}
                                temp_line = full_line.split("\t", 2)
                                entity['row'] = temp_line[0]
                                keephash.append(temp_line[0])
                                entity['text'] = temp_line[-1].replace("\n", "")
                                entity['start'] = int(temp_line[1].split()[1])
                                entity['end'] = int(temp_line[1].split()[2])
                                entity['label'] = temp_line[1].split()[0]
                                entities.append(entity)
                            elif not full_line.startswith("#"):
                                entity = {}
                                temp_line = full_line.split("\t", 2)
                                entity['row'] = temp_line[0]
                                entity['text'] = temp_line[-1].replace("\n", "")
                                entity['start'] = int(temp_line[1].split()[1])
                                entity['end'] = int(temp_line[1].split()[2])
                                entity['label'] = temp_line[1].split()[0]
                                remove_ent.append(entity)
                                update_notacceptance_freq(entity['text'], entity['label'])
                            elif full_line.startswith("#"):
                                all_hash.append(full_line)
                        for hash in all_hash:
                            row = hash.strip().split("\t", 2)[1].split(" ")[1]
                            if row in keephash:
                                w.write(hash)
                                entity = {}
                                temp_line = hash.split("\t", 2)
                                entity['T'] = temp_line[1].split(" ")[1]
                                entity['rest'] = "\t".join(temp_line[2:])
                                hash_ent.append(entity)
                        w.close()
                    r.close()
                    annotators_hash[annotators_files] = hash_ent
                    entities_ordered = sorted(entities, key=lambda entity: entity['start'])
                    annotators_entities[annotators_files] = entities_ordered
                    removes[annotators_files] = remove_ent

        annotator_notes[dir] = annotators_hash
        annotator[dir] = annotators_entities
        rm[dir] = removes
        all_files[dir] = list_files

    return all_files, annotator, annotator_notes, rm


def post_processing(annotators_entities, annotators_notes, adds, changes, removes, sett):
    file_dic = {}
    ann_file = {}

    distros_dict = reading_duplicated_files(sett)
    IAA_score = dict()

    for dir, files in annotators_entities.items():
        annotators = {}
        annotators[dir] = 'X'
        for file, records in files.items():
            source = os.path.join(annotators_dir, dir, sett, file).replace(".ann", ".txt")
            if file.replace(".ann", ".txt") in distros_dict:
                copy(source, IAA_ANN_dir)
                if file_dic.get(file) is None:
                    file_dic[file] = 1
                with open(os.path.join(IAA_ANN_dir, file), "a+") as w_ann:
                    for record in records:
                        w_ann.write("T" + str(file_dic.get(file)) + "\t" + record['label'] + " " + str(record['start'])
                                    + " " + str(record['end']) + "\t" + record['text'] + "\n")
                        _hash = False
                        for rec_note in annotators_notes.get(dir).get(file):
                            if rec_note['T'] == record['row']:
                                _hash = True
                                break
                        if _hash:
                            w_ann.write(
                                "#" + str(file_dic.get(file)) + "\tAnnotatorNotes T" + str(file_dic.get(file)) + "\t" +
                                rec_note['rest'].strip() + " Annotator: " + dir + "\n")
                        else:
                            w_ann.write(
                                "#" + str(file_dic.get(file)) + "\tAnnotatorNotes T" + str(file_dic.get(file)) + "\t" +
                                "Annotator: " + dir + "\n")

                        file_dic[file] += 1
                w_ann.close()

            if ann_file.get(file) is None:
                ann_records = {}
            else:
                ann_records = ann_file.get(file).copy()

            for record in records:
                temp_key = record["label"] + " " + str(record["start"]) + " " + str(record["end"]) \
                           + " " + record["text"]
                if temp_key not in ann_records.keys():
                    ann_records[temp_key] = annotators
                else:
                    temp = ann_records.get(temp_key).copy()
                    temp.update(annotators)
                    update = {temp_key: temp}
                    ann_records.update(update)

            if file.replace("ann", "txt") in distros_dict:
                Annotator_records = {}
                removed_list = removes.get(dir).get(file)
                for removed_record in removed_list:
                    temp_key = removed_record["label"].replace("_previa", "").replace("_alta", "") \
                                   .replace("_hab", "") + " " + str(removed_record["start"]) + " " \
                               + str(removed_record["end"]) + " " + removed_record["text"]
                    if temp_key not in Annotator_records.keys():
                        Annotator_records[temp_key] = {}
                IAA_score[file] = Annotator_records

            ann_file[file] = ann_records


    print('DONE')

    save_statistical_dir = os.path.join(all_differences_csv_dir, "statistical", Set)

    xlsx_mismatch = os.path.join(save_statistical_dir, "Set_" + Set + "_All_MisMatching_Records.xlsx")
    workbook_mismatch = xlsxwriter.Workbook(xlsx_mismatch)

    with open(os.path.join(save_statistical_dir, "Set_" + Set + "link_diff_files_in_Brat.txt"), "w") as w_mis:
        for file, records in ann_file.items():
            if file.replace("ann", "txt") in distros_dict:
                with open(os.path.join(IAA_CSV_dir, file + ".csv"), "w") as w_csv:
                    csv_writer = csv.writer(w_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    # csv_writer.writerow([" "] + list(annotators_entities.keys()))

                    list_annotators = []
                    for annotators in records.values():
                        for annt in annotators.keys():
                            if annt not in list_annotators:
                                list_annotators.append(annt)

                    list_annotators.sort()

                    csv_writer.writerow([" "] + list_annotators)
                    annotat_hyper = ""


                    w_mis.write('http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/'  +  list_annotators[0] + "/" +  sett.split("_")[0] +'/#/' + list_annotators[1] + "/" +  sett.split("_")[0] + "/" + file.replace(".ann", "") + "\n")

                    IAA_score[file].update(records)
                    for record, annotators in records.items():
                        list_ann = ["X" if ann in annotators.keys() else " " for ann in list_annotators]
                        csv_writer.writerow([record] + list_ann)
    # data_dir = os.path.join(parentDir, "Annotated/analysis/statistical", Set)
    xlsx_file = os.path.join(save_statistical_dir, "Set_" + Set + "_IAA_Score.xlsx")
    workbook = xlsxwriter.Workbook(xlsx_file)

    for file, records in IAA_score.items():
        IAA_matrix = np.zeros((2, 2))
        worksheet = workbook.add_worksheet(file)
        worksheet_mismatch = workbook_mismatch.add_worksheet(file)

        counter = 1
        counter_mistmatch = 1
        worksheet.set_column(0, 0, 100)
        worksheet_mismatch.set_column(0, 0, 100)

        list_annotators = []
        for annotators in records.values():
            for annt in annotators.keys():
                if annt not in list_annotators:
                    list_annotators.append(annt)

        list_annotators.sort()

        for i, annotators in enumerate(list_annotators):
            worksheet.write(0, i + 1, annotators)
            worksheet_mismatch.write(0, i + 1, annotators)

        for record, annotators in records.items():
            list_ann = [1 if ann in annotators.keys() else 0 for ann in list_annotators]
            if list_ann[0] == 1 and list_ann[1] == 1:
                IAA_matrix[0, 0] += 1
            elif list_ann[0] == 0 and list_ann[1] == 0:
                IAA_matrix[1, 1] += 1
            elif list_ann[0] == 1 and list_ann[1] == 0:
                IAA_matrix[0, 1] += 1

                worksheet_mismatch.write(counter_mistmatch, 0, record)
                worksheet_mismatch.write(counter_mistmatch, 1, list_ann[0])
                worksheet_mismatch.write(counter_mistmatch, 2, list_ann[1])
                counter_mistmatch += 1

            elif list_ann[0] == 0 and list_ann[1] == 1:
                IAA_matrix[1, 0] += 1
                worksheet_mismatch.write(counter_mistmatch, 0, record)
                worksheet_mismatch.write(counter_mistmatch, 1, list_ann[0])
                worksheet_mismatch.write(counter_mistmatch, 2, list_ann[1])
                counter_mistmatch += 1

            if not (list_ann[0] == 0 and list_ann[1] == 0):
                worksheet.write(counter, 0, record)
                worksheet.write(counter, 1, list_ann[0])
                worksheet.write(counter, 2, list_ann[1])

                counter += 1

        # worksheet.write(1, 4, "Cohen's Kappa Score:")
        # all = IAA_matrix[0][0] + IAA_matrix[0][1] + IAA_matrix[1][0]
        # Pa = (IAA_matrix[0][0]) / all
        # Pe_P = (((IAA_matrix[0][0] + IAA_matrix[0][1]) / all) * (((IAA_matrix[0][0] + IAA_matrix[1][0]) / all)))
        # Pe_N = (((IAA_matrix[1][0]) / all) * (((IAA_matrix[0][1]) / all)))
        # Pe = Pe_N + Pe_P
        # K = 1
        # if Pe != 1.0:
        #     K = (Pa - Pe) / (1 - Pe)
        #
        # worksheet.write(1, 5, K)
        # worksheet.set_column(4, 4, 20)
        #
        # worksheet.write(2, 4, "Cohen's Kappa Score with suggestions:")
        # all = IAA_matrix[0][0] + IAA_matrix[0][1] + IAA_matrix[1][0] + IAA_matrix[1][1]
        # Pa = (IAA_matrix[0][0] + IAA_matrix[1][1]) / all
        # Pe_P = (((IAA_matrix[0][0] + IAA_matrix[0][1]) / all) * (((IAA_matrix[0][0] + IAA_matrix[1][0]) / all)))
        # Pe_N = (((IAA_matrix[1][0] + IAA_matrix[1][1]) / all) * (((IAA_matrix[0][1] + IAA_matrix[1][1]) / all)))
        # Pe = Pe_N + Pe_P
        # K = (Pa - Pe) / (1 - Pe)
        #
        # worksheet.write(2, 5, K)


        worksheet.write(1, 4, "% All")
        K =  IAA_matrix[1][1] / (IAA_matrix[1][1] + IAA_matrix[0][1] + IAA_matrix[1][0])
        worksheet.write(1, 5, K)
        worksheet.set_column(4, 4, 20)

        worksheet.write(2, 4, "% Changed and added:")
        K =0

        worksheet.write(2, 5, K)
        # worksheet.set_column(6, 6, 20)

    workbook.close()
    workbook_mismatch.close()


def get_ctakes_entities(list_annotators, sset):
    ctk = {}
    sset_prefix = sset.split("_")[0]
    for dir in list_annotators:
        ctakes_entities = {}
        for ctakes_files in os.listdir(os.path.join(ctakes_dir, dir, sset_prefix)):
            if ctakes_files.endswith(".ann"):
                with open(os.path.join(ctakes_dir, dir, sset_prefix, ctakes_files), "r") as r:
                    entites = []
                    for line in r:
                        temp_line = line.strip().split("\t", 2)
                        if not line.startswith("#"):
                            entity = {'row': temp_line[0], 'text': temp_line[-1], 'start': int(temp_line[1].split()[1]),
                                      'end': int(temp_line[1].split()[2]), 'label': temp_line[1].split()[0]}
                            entites.append(entity)
                    ctakes_ents = sorted(entites, key=lambda entity: entity['start'])
                    ctakes_entities[ctakes_files] = ctakes_ents

        ctk[dir] = ctakes_entities
    return ctk


def normolized_text(text_original):
    normolized_whitespace = " ".join(text_original.split())
    unaccented_string = unidecode.unidecode(normolized_whitespace)

    return unaccented_string.lower()


def update_notacceptance_freq(text_original, lable_original):
    if lable_original.startswith("_SUG_"):
        label = lable_original.replace("_SUG_", "").replace("_previa", "").replace("_alta", "").replace("_hab", "")
        unaccented_string = normolized_text(text_original)
        if acceptance_rate.get(unaccented_string + "_" + label) is None:
            acceptance_rate[unaccented_string + "_" + label] = {"accepted": 0, "notaccepted": 1}
        else:
            temp_word = acceptance_rate.get(unaccented_string + "_" + label)
            temp_counter = temp_word.get("notaccepted")
            update = {"accepted": temp_word.get("accepted"), "notaccepted": temp_counter + 1}
            acceptance_rate.update({unaccented_string + "_" + label: update})


def update_acceptance_freq(text_original, lable_original):
    if not (lable_original.startswith("SECCION_") or lable_original.startswith("Hora_")
            or lable_original.startswith("Fecha_") or lable_original.startswith("Tiempo_")):

        label = lable_original.replace("_previa", "").replace("_alta", "").replace("_hab", "")
        unaccented_string = normolized_text(text_original)
        if acceptance_rate.get(unaccented_string + "_" + label) is None:
            acceptance_rate[unaccented_string + "_" + label] = {"accepted": 1, "notaccepted": 0}
        else:
            temp_word = acceptance_rate.get(unaccented_string + "_" + label)
            temp_counter = temp_word.get("accepted")
            update = {"accepted": temp_counter + 1, "notaccepted": temp_word.get("notaccepted")}
            acceptance_rate.update({unaccented_string + "_" + label: update})


def statistical_analysis(list_annotators, ctakes_entities, annotators_entities, sett):
    if int(sett.split("_")[0]) <= 2:
        header_file = os.path.join(parentDir, "../EHR-HeaderDetector/data/headers_original.txt")
    elif int(sett.split("_")[0]) == 3:
        header_file = os.path.join(parentDir, "../EHR-HeaderDetector/data/headers_28.11.2019.txt")
    else:
        header_file = os.path.join(parentDir, "../EHR-HeaderDetector/data/headers.txt")
    headers_dic(header_file)

    adds_ann = {}
    changes_ann = {}
    no_changes_ann = {}
    removes_ann = {}

    new_variables = {}
    # new_variables_who = {}
    # new_variables_where = {}
    for dir in list_annotators:

        adds = {}
        changes = {}
        no_changes = {}
        removes = {}

        annotators_entities_ant = annotators_entities.get(dir)
        ctakes_entities_ant = ctakes_entities.get(dir)

        for file in annotators_entities_ant.keys():
            ctakes_ents = ctakes_entities_ant.get(file)
            annotators_ents = annotators_entities_ant.get(file)

            ctakes_ents = sorted(ctakes_ents, key=lambda entity: entity['start'])
            annotators_ents = sorted(annotators_ents, key=lambda entity: entity['start'])

            add_ent = []
            change_ent = []
            no_change_ent = []
            remove_ent = []

            for cta_ent in ctakes_ents:
                # it detects if a anotation in pre-annotated file has the same start and end spans with manual annotation
                # and it pre-annotation is FECHA or HORA or TIEMPO or it starts with SECCION or
                # with the same suggection variable is not remobed, it might be changed or accepted.
                remove = True
                for ann_ent in annotators_ents:
                    if cta_ent['start'] == ann_ent['start'] and (cta_ent['label'] == "_SUG_" + ann_ent['label'] or
                                                                 cta_ent['label'].startswith("FECHA") or
                                                                 cta_ent['label'].startswith("HORA") or
                                                                 cta_ent['label'].startswith("TIEMPO") or
                                                                 cta_ent['label'].startswith("SECCION_")
                                                                 and cta_ent['end'] == ann_ent['end']):
                        remove = False
                        break
                if remove:
                    remove_ent.append(cta_ent)

            remove_ent = sorted(remove_ent, key=lambda entity: entity['start'])
            removes[file] = remove_ent

            for ann_ent in annotators_ents:
                add = True
                for cta_ent in ctakes_ents:
                    if cta_ent['start'] == ann_ent['start'] and cta_ent['end'] == ann_ent['end']:
                        # if start and end spans are same, then check the labels,
                        # if labels are same so it not changed, otherwise if it is not in removed ones it changed
                        if cta_ent['text'] == ann_ent['text']:
                            if cta_ent['label'] == ann_ent['label'] or cta_ent['label'] == "_SUG_" + \
                                    ann_ent['label'].replace("_previa", "").replace("_alta", "").replace("_hab", ""):
                                entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'],
                                          'text': cta_ent['text'], 'start': cta_ent['start'], 'end': cta_ent['end'],
                                          'label': cta_ent['label']}
                                no_change_ent.append(entity)
                                update_acceptance_freq(ann_ent['text'], ann_ent['label'])
                                add = False
                            else:
                                remove = True
                                for files in remove_ent:
                                    if files['start'] == cta_ent['start'] and files['end'] == cta_ent['end']:
                                        remove = False
                                        break
                                if remove:
                                    entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'],
                                              'text': ann_ent['text'], 'start': ann_ent['start'], 'end': ann_ent['end'],
                                              'label': ann_ent['label'], 'old_label': cta_ent['label']}
                                    change_ent.append(entity)
                                    update_acceptance_freq(ann_ent['text'], ann_ent['label'])
                                    add = False
                        else:
                            print("ERROR in " + file)
                            print("Annotators: " + ann_ent['text'])
                            print("cTAKES: " + cta_ent['text'])
                            add = False
                    elif ann_ent['start'] == cta_ent['start'] and (
                            cta_ent['label'] == "_SUG_" + ann_ent['label'] or cta_ent['label'].startswith(
                        'SECCION_')) and \
                            ann_ent['end'] != cta_ent['end']:
                        entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'], 'text': ann_ent['text'],
                                  'start': ann_ent['start'], 'end': ann_ent['end'], 'label': ann_ent['label'],
                                  'old_text': cta_ent['text'], 'old_end': cta_ent['end'], 'old_label': cta_ent['label']}
                        change_ent.append(entity)
                        update_acceptance_freq(ann_ent['text'], ann_ent['label'])
                        add = False
                if add:
                    add_ent.append(ann_ent)
                    # if ann_ent['text'] == "M3":
                    #     print(dir, file, ann_ent)
                    if not (ann_ent['label'].startswith('Hora_') or ann_ent['label'].startswith('Fecha_') or
                            ann_ent['label'].startswith('Tiempo_')):
                        if ann_ent['text'] not in new_variables.keys() and \
                                ann_ent['text'].upper() not in new_variables.keys():
                            if ann_ent['label'].startswith('SECCION_'):
                                if headers_name_dic.get(ann_ent["text"].upper()) is None:
                                    new_variables[ann_ent['text'].upper()] = [ann_ent['label']]
                                    # new_variables_who[ann_ent['text'].upper()] = [dir]
                                    # new_variables_where[ann_ent['text'].upper()] = [file]
                                else:
                                    print(dir + " " + file + " " + ' '.join(
                                        ['{0}: {1}'.format(k, v) for k, v in ann_ent.items()]))
                            else:
                                new_variables[ann_ent['text']] = ["_SUG_" + ann_ent['label'].replace("_previa", "")
                                    .replace("_alta", "").replace("_hab", "")]
                                # new_variables_who[ann_ent['text'].upper()] = [dir]
                                # new_variables_where[ann_ent['text'].upper()] = [file]
                        else:
                            temp_list = new_variables.get(ann_ent['text'])
                            if temp_list is None:
                                temp_list = new_variables.get(ann_ent['text'].upper())
                            if "_SUG_" + ann_ent['label'].replace("_previa", "").replace("_alta", "").\
                                    replace("_hab", "") not in temp_list and ann_ent['label'] not in temp_list:
                                if ann_ent['label'].startswith('SECCION_'):
                                    if headers_name_dic.get(ann_ent["text"].upper()) is None:
                                        temp_list.append(ann_ent['label'])
                                        update = {ann_ent['text'].upper(): temp_list}
                                        new_variables.update(update)
                                    else:
                                        print(dir + " " + file + " " + ' '.join(
                                            ['{0}: {1}'.format(k, v) for k, v in ann_ent.items()]))
                                else:
                                    temp_list.append("_SUG_" + ann_ent['label']
                                                     .replace("_previa", "").replace("_alta", "").replace("_hab", ""))
                                    update = {ann_ent['text']: temp_list}
                                    new_variables.update(update)


                                # update = {ann_ent['text']: temp_list}

            adds[file] = add_ent
            changes[file] = change_ent
            no_changes[file] = no_change_ent

        adds_ann[dir] = adds
        changes_ann[dir] = changes
        no_changes_ann[dir] = no_changes

        removes_ann[dir] = removes

    return adds_ann, changes_ann, no_changes_ann, removes_ann, new_variables


def save_analysis(Set, **kwargs):
    stat = {}
    for key, value in kwargs.items():
        for dir, files in value.items():
            count_key = stat.get(dir)
            if count_key is None:
                count_key = {}
            # os.makedirs(os.path.join(save_analysis_dir, dir, Set), exist_ok=True)
            count = 0
            count_hft = 0
            count_span = 0
            for file, records in files.items():
                analysis_dir = os.path.join(all_differences_csv_dir, dir, Set, file.split(".ann")[0])
                os.makedirs(analysis_dir, exist_ok=True)
                with open(os.path.join(analysis_dir, key + ".csv"), "w") as w_csv:
                    csv_writer = csv.writer(w_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    if records:
                        csv_writer.writerow(list(records[0].keys()))
                        count += len(records)
                        for i, record in enumerate(records):
                            if key == "changed" and (
                                    record['label'].startswith('Hora_') or record['label'].startswith('Fecha_') or
                                    record['label'].startswith('Tiempo_')):
                                count_hft += 1
                            elif key == "changed":
                                count_span += 1
                            csv_writer.writerow(list(record.values()))
                w_csv.close()
            count_key[key] = count
            if key == "changed":
                count_key[" *(changed_hft,"] = count_hft
                count_key["changed_span)* "] = count_span

            stat[dir] = count_key

    save_statistical_dir = os.path.join(all_differences_csv_dir, "statistical", Set)
    os.makedirs(save_statistical_dir, exist_ok=True)
    with open(os.path.join(save_statistical_dir, "Set_" + Set + "-Statistical_Analysis-Set.csv"), "w") as stat_csv:
        csv_writer = csv.writer(stat_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([" "] + list(list(stat.values())[0].keys()))
        for keys, values in stat.items():
            csv_writer.writerow([keys] + list(values.values()))
    stat_csv.close()

    return stat


def save_new_variables(new_variable, sset):
    statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", Set)
    os.makedirs(statical_analysis_dir, exist_ok=True)

    with open(os.path.join(statical_analysis_dir, "Set_" + sset + "-NEW_VARIABLES.csv"), "w") as var_csv, open(
            os.path.join(statical_analysis_dir, "Set_" + sset + "-NEW_SECCION.csv"), "w") as sec_csv:
        var_writer = csv.writer(var_csv, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        sec_writer = csv.writer(sec_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for keys, values in new_variable.items():
            temp_line = " ".join(keys.split())
            for value in values:
                if value.startswith("SECCION_"):
                    sec_writer.writerow([headers_type_dic.get(value)] + [value] + [temp_line.upper()])
                else:
                    var_writer.writerow([""] + [value] + [temp_line])
    var_csv.close()
    sec_csv.close()


def trim_name(name):
    unaccent_name = unidecode.unidecode(name)
    for i, ch in enumerate(reversed(unaccent_name)):
        if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
            if i == 0:
                return name
            else:
                return name[:-1 * i]


def checking_new_section(new_variable, annotators_entities, sset):
    nvariables = new_variable.keys()
    statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", Set)

    with open(os.path.join(statical_analysis_dir, "Set_" + sset + "-checking_new_section.csv"), "w") as check_csv:
        check_writer = csv.writer(check_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for dir, files in annotators_entities.items():
            for file, records in files.items():
                begin = 0
                with open(os.path.join(annotators_dir, dir, sset, file.replace(".ann", ".txt")), "r") as f_txt:
                    for line in f_txt:
                        line_size = len(line)
                        if line and ((line[0].isalpha() and line[0].isupper()) or not line[0].isalpha()) \
                                and not line.startswith("Nº") and not line.upper().startswith("SIN"):
                            for variable in nvariables:
                                if new_variable.get(variable)[0].startswith("SECCION_"):
                                    var = trim_name(variable).upper()
                                    upper_line = line.upper()
                                    if upper_line.startswith(var):
                                        check = True
                                        for ann_ent in records:
                                            if not (ann_ent['start'] == begin and ann_ent['label'].startswith(
                                                    "SECCION_") and ann_ent["text"].upper().startswith(var)):
                                                check = False
                                            else:
                                                check = True
                                                break
                                        if not check:
                                            check_writer.writerow(
                                                [dir] + [file] + [begin] + [variable.strip()] + [line.strip()])
                                            break
                        begin += line_size
                f_txt.close()
    check_csv.close()


def save_acceptance_rate(acceptance_rate, sset):
    ordered_acceptance_rate = OrderedDict(sorted(acceptance_rate.items(), key=lambda t: t[0]))

    statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", sset)
    os.makedirs(statical_analysis_dir, exist_ok=True)

    with open(os.path.join(statical_analysis_dir, "Set_" + sset + "-acceptance_freq_all.csv"), "w") as freq_all_csv, \
            open(os.path.join(statical_analysis_dir, "Set_" + sset + "-acceptance_freq_top_low.csv"),
                 "w") as freq_top_csv:
        freq_all_writer = csv.writer(freq_all_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        freq_top_writer = csv.writer(freq_top_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        removed_list = ["ASPECTS", "mRankin", "NIHSS"]

        for keys, values in ordered_acceptance_rate.items():
            text_lab = keys.split("_", 1)
            if text_lab[1] not in removed_list:
                freq_all_writer.writerow(text_lab + [values.get("accepted")] + [values.get("notaccepted")])

                acceptace_rate_score = values.get("accepted") / (values.get("accepted") + values.get("notaccepted"))
                if acceptace_rate_score < 0.50 and values.get("accepted") + values.get("notaccepted") >= 5:
                    freq_top_writer.writerow(text_lab + [values.get("accepted")] + [values.get("notaccepted")] + [
                        "%.2f" % acceptace_rate_score])

        freq_all_csv.close()
        freq_top_csv.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="comparing")

    parser.add_argument('--set', help='Which set is going to compare')

    args = parser.parse_args()
    Set = args.set

    init(Set)
    list_annotators = annators()
    all_files, annotators_entities, annotators_notes, removes = pre_processing(list_annotators, Set)
    ctakes_entities = get_ctakes_entities(list_annotators, Set)

    adds, changes, accepts, removes_2, new_variable = statistical_analysis(list_annotators, ctakes_entities,
                                                                           annotators_entities, Set)

    save_acceptance_rate(acceptance_rate, Set)

    save_analysis(Set, added=adds, changed=changes, accepted=accepts, removed=removes_2)

    save_new_variables(new_variable, Set)

    # checking_new_section(new_variable, annotators_entities, Set)

    post_processing(annotators_entities, annotators_notes, adds, changes, removes_2, Set)
