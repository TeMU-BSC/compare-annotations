import argparse
import csv
import os
import shutil
from collections import OrderedDict

fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
main_dir = os.path.join(parentDir, "Annotated")
Set = None
annotators_dir = ""
pre_processing_dir = ""
post_processing_ann_dir = ""
post_processing_csv_dir = ""
all_differences_csv_dir = ""
ctakes_dir = ""


def init(Set):
    global annotators_dir, pre_processing_dir, post_processing_ann_dir, post_processing_csv_dir, ctakes_dir, \
        all_differences_csv_dir

    annotators_dir = os.path.join(main_dir, "manual_annotations")
    pre_processing_dir = os.path.join(main_dir, "pre_processing")
    post_processing_ann_dir = os.path.join(main_dir, "IAA_ANN", Set)
    post_processing_csv_dir = os.path.join(main_dir, "IAA_CSV", Set)
    all_differences_csv_dir = os.path.join(main_dir, "analysis")
    ctakes_dir = os.path.join(main_dir, "pre_annotations")


    shutil.rmtree(post_processing_ann_dir, ignore_errors=True)
    os.makedirs(post_processing_ann_dir, exist_ok=True)
    os.makedirs(post_processing_csv_dir, exist_ok=True)



def annators():
    list_annotators = []
    for sub_dir in os.listdir(annotators_dir):
        if not sub_dir.startswith('.'):
            list_annotators.append(sub_dir)

    return list_annotators


def pre_processing(annotators, Set):
    all_files = {}
    annotator = {}
    annotator_notes = {}
    rm = {}
    for dir in annotators:
        list_files = []
        pre_pro = os.path.join(pre_processing_dir, dir, Set)

        # shutil.rmtree(pre_pro)
        os.makedirs(pre_pro, exist_ok=True)

        annotators_entities = {}
        annotators_hash = {}
        removes = {}
        annotators_deep_dir = os.path.join(annotators_dir, dir, Set)
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
                                temp_line = full_line.strip().split("\t")
                                entity['row'] = temp_line[0]
                                keephash.append(temp_line[0])
                                entity['text'] = temp_line[-1]
                                entity['start'] = int(temp_line[1].split()[1])
                                entity['end'] = int(temp_line[1].split()[2])
                                entity['label'] = temp_line[1].split()[0]
                                entities.append(entity)
                            elif not full_line.startswith("#"):
                                entity = {}
                                temp_line = full_line.strip().split("\t")
                                entity['row'] = temp_line[0]
                                entity['text'] = temp_line[-1]
                                entity['start'] = int(temp_line[1].split()[1])
                                entity['end'] = int(temp_line[1].split()[2])
                                entity['label'] = temp_line[1].split()[0]
                                remove_ent.append(entity)
                            elif full_line.startswith("#"):
                                all_hash.append(full_line)
                        for hash in all_hash:
                            row = hash.strip().split("\t")[1].split(" ")[1]
                            if row in keephash:
                                w.write(hash)
                                entity = {}
                                temp_line = hash.split("\t")
                                entity['T'] = temp_line[1].split(" ")[1]
                                entity['rest'] = "\t".join(temp_line[2:])
                                hash_ent.append(entity)
                        w.close()
                    r.close()

                    annotators_hash[annotators_files] = hash_ent
                    annotators_entities[annotators_files] = entities
                    removes[annotators_files] = remove_ent

        annotator_notes[dir] = annotators_hash
        annotator[dir] = annotators_entities
        rm[dir] = removes
        all_files[dir] = list_files

    return all_files, annotator, annotator_notes, rm


def post_processing(annotators_entities, annotators_notes):
    file_dic = {}
    ann_file = {}
    for dir, files in annotators_entities.items():
        annotators = {}
        annotators[dir] = 'X'
        for file, records in files.items():
            if file_dic.get(file) is None:
                file_dic[file] = 1
            with open(os.path.join(post_processing_ann_dir, file), "a+") as w_ann:
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
                temp_key = record["label"] + " " + str(record["start"]) + " " + str(record["end"]) + " " + record[
                    "text"]
                if temp_key not in ann_records.keys():
                    ann_records[temp_key] = annotators
                else:
                    temp = ann_records.get(temp_key).copy()
                    temp.update(annotators)
                    update = {temp_key: temp}
                    ann_records.update(update)

            ann_file[file] = ann_records

    print('DONE')

    save_statistical_dir = os.path.join(all_differences_csv_dir, "statistical", Set)

    with open(os.path.join(save_statistical_dir, "All_MisMatching_Records.csv"), "w") as w_mis:
        csv_mis_writer = csv.writer(w_mis, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_mis_writer.writerow([" ", " "] + list(annotators_entities.keys()))
        for file, records in ann_file.items():
            with open(os.path.join(post_processing_csv_dir, file + ".csv"), "w") as w_csv:
                csv_writer = csv.writer(w_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                # csv_writer.writerow([" "] + list(annotators_entities.keys()))
                list_annotators = set()
                for annotators in records.values():
                    list_annotators.update(set(annotators.keys()))
                csv_writer.writerow([" "] + list(list_annotators))

                for record, annotators in records.items():
                    list_ann = ["X" if ann in annotators.keys() else " " for ann in list_annotators]
                    csv_writer.writerow([record] + list_ann)
                    if " " in list_ann:
                        list_ann_mis = ["1" if ann in annotators.keys() else "0" for ann in annotators_entities.keys()]
                        csv_mis_writer.writerow([file, record] + list_ann_mis)


def get_ctakes_entities(list_annotators, Set):
    ctk = {}
    for dir in list_annotators:
        ctakes_entities = {}
        for ctakes_files in os.listdir(os.path.join(ctakes_dir, dir, Set)):
            if ctakes_files.endswith(".ann"):
                with open(os.path.join(ctakes_dir, dir, Set, ctakes_files), "r") as r:
                    entites = []
                    for line in r:
                        temp_line = line.strip().split("\t")
                        if not line.startswith("#"):
                            entity = {}
                            entity['row'] = temp_line[0]
                            entity['text'] = temp_line[-1]
                            entity['start'] = int(temp_line[1].split()[1])
                            entity['end'] = int(temp_line[1].split()[2])
                            entity['label'] = temp_line[1].split()[0]
                            entites.append(entity)
                    ctakes_entities[ctakes_files] = entites

        ctk[dir] = ctakes_entities
    return ctk


def statistical_analysis(list_annotators, ctakes_entities, annotators_entities):
    adds_ann = {}
    changes_ann = {}
    no_changes_ann = {}
    removes_ann = {}

    new_variables = {}
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
                            if cta_ent['label'] == ann_ent['label'] or cta_ent['label'] == "_SUG_" + ann_ent['label']:
                                entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'],
                                          'text': cta_ent['text'], 'start': cta_ent['start'], 'end': cta_ent['end'],
                                          'label': cta_ent['label']}
                                no_change_ent.append(entity)
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
                                    add = False
                        else:
                            print("ERROR in " + file)
                            print("Annotators: " + ann_ent['text'])
                            print("cTAKES: " + cta_ent['text'])
                            add = False
                    elif ann_ent['start'] == cta_ent['start'] and (cta_ent['label'] == "_SUG_" + ann_ent['label'] or cta_ent['label'].startswith('SECCION_')) and \
                            ann_ent['end'] != cta_ent['end']:
                        entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'], 'text': ann_ent['text'],
                                  'start': ann_ent['start'], 'end': ann_ent['end'], 'label': ann_ent['label'],
                                  'old_text': cta_ent['text'], 'old_end': cta_ent['end'], 'old_label': cta_ent['label']}
                        change_ent.append(entity)
                        add = False
                if add:
                    add_ent.append(ann_ent)
                    if ann_ent['text'] == "M3":
                        print(dir, file, ann_ent)
                    if not (ann_ent['label'].startswith('Hora_') or ann_ent['label'].startswith('Fecha') or
                            ann_ent['label'].startswith('Tiempo_') or ann_ent['label'].startswith('SECCION_')):
                        if ann_ent['text'] not in new_variables.keys():

                            new_variables[ann_ent['text']] = ["_SUG_" + ann_ent['label']]
                        else:
                            temp_list = new_variables.get(ann_ent['text'])
                            if "_SUG_" + ann_ent['label'] not in temp_list:
                                temp_list.append("_SUG_" + ann_ent['label'])
                                update = {ann_ent['text']: temp_list}
                                new_variables.update(update)
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
                                    record['label'].startswith('Hora_') or record['label'].startswith('Fecha') or
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


def save_new_variables(new_variable, Set):
    statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", Set)
    os.makedirs(statical_analysis_dir, exist_ok=True)

    with open(os.path.join(statical_analysis_dir, "Set_" + Set + "-New_Variables.csv"), "w") as var_csv:
        csv_writer = csv.writer(var_csv, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for keys, values in new_variable.items():
            csv_writer.writerow([" "] + values + [keys.upper()])
    var_csv.close()


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
                                                                           annotators_entities)
    save_analysis(Set, added=adds, changed=changes, accepted=accepts, removed=removes_2)

    save_new_variables(new_variable, Set)

    post_processing(annotators_entities, annotators_notes)
