import itertools
from core.const.const import check_variable_type
from core.entity.entities import Entities


class Comparison:

    @staticmethod
    def ctakes_annotators_per_type(ctakes_entities, annotators_entities, variable_type):

        eval_dir_dic = dict()
        for annotator, annotator_files in annotators_entities.items():
            eval_file_dic = dict()
            for annotator_file, annotator_records_original in annotator_files.items():
                if ctakes_entities[annotator][annotator_file] is not None:
                    ctake_records_original = ctakes_entities[annotator][annotator_file]

                    annotator_records_witout_suffix = Entities.entities_suffix_prefix_fixer(annotator_records_original)

                    annotator_records = check_variable_type(annotator_records_witout_suffix, variable_type)
                    if len(annotator_records) != 0:
                        ctakes_records_witout_suffix = Entities.entities_suffix_prefix_fixer(ctake_records_original)
                        ctake_records = check_variable_type(ctakes_records_witout_suffix, variable_type)


                        intersection = [i for i in ctake_records for j in annotator_records if
                                        i['start'] == j['start'] and
                                        i['end'] == j['end'] and
                                        i['label'] == j['label'] and
                                        i['text'] == j['text']]

                        ctakes_more = list(itertools.filterfalse(lambda x: x in annotator_records, ctake_records))
                        annotator_more = list(itertools.filterfalse(lambda x: x in ctake_records, annotator_records))

                        eval_file_dic[annotator_file] = {"intersection": intersection,
                                                         "ctakes_more": ctakes_more,
                                                         "annotator_more" : annotator_more
                                                         }
            if len(eval_file_dic) != 0:
                eval_dir_dic[annotator] = eval_file_dic


        return eval_dir_dic

    @staticmethod
    def changed_annotations_by_annotators(ctakes_entities, annotators_entities, headers_name_dic, bunch, freq=None):
        adds_ann = {}
        changes_ann = {}
        no_changes_ann = {}
        removes_ann = {}

        new_variables = {}
        new_variables_where = {}
        for dir in annotators_entities.keys():
            print("New added Sections by annotators, that we have already them in our dictionary:")

            adds = {}
            changes = {}
            no_changes = {}
            removes = {}

            annotators_entities_ant = annotators_entities.get(dir)
            ctakes_entities_ant = ctakes_entities.get(dir)

            for file in annotators_entities_ant.keys():


                ctakes_ents = ctakes_entities_ant.get(file)
                annotators_ents = annotators_entities_ant.get(file)

                if ctakes_ents is None:
                    continue

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
                    if ann_ent["text"] == "NIHSS 2":
                        check = 0
                    add = True
                    for cta_ent in ctakes_ents:
                        if cta_ent['start'] == ann_ent['start'] and cta_ent['end'] == ann_ent['end']:
                            # if start and end spans are same, then check the labels,
                            # if labels are same so it not changed, otherwise if it is not in removed ones it changed
                            if cta_ent['text'] == ann_ent['text']:
                                if cta_ent['label'] == ann_ent['label'] or \
                                        cta_ent['label'].replace("_previa", "").replace("_alta", "").replace("_hab", "") \
                                        == "_SUG_" + \
                                        ann_ent['label'].replace("_previa", "").replace("_alta", "").replace("_hab",
                                                                                                             ""):
                                    entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'],
                                              'text': cta_ent['text'], 'start': cta_ent['start'], 'end': cta_ent['end'],
                                              'label': cta_ent['label']}
                                    no_change_ent.append(entity)
                                    freq.update_acceptance_freq(ann_ent['text'], ann_ent['label'])
                                    add = False
                                    break
                                else:
                                    remove = False
                                    for files in remove_ent:
                                        if files['start'] == cta_ent['start'] and files['end'] == cta_ent['end']:
                                            remove = True
                                            break
                                    if not remove:
                                        entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'],
                                                  'text': ann_ent['text'], 'start': ann_ent['start'],
                                                  'end': ann_ent['end'],
                                                  'label': ann_ent['label'], 'old_label': cta_ent['label']}
                                        change_ent.append(entity)
                                        freq.update_acceptance_freq(ann_ent['text'], ann_ent['label'])
                                        add = False
                                        break
                            else:
                                print("ERROR in " + file)
                                print("Annotators: " + ann_ent['text'])
                                print("cTAKES: " + cta_ent['text'])
                                add = False
                        elif ann_ent['start'] == cta_ent['start'] and \
                                (cta_ent['label'].replace("_previa", "").replace("_alta", "").replace("_hab", "") ==
                                 "_SUG_" +
                                 ann_ent['label'].replace("_previa", "").replace("_alta", "").replace("_hab", "") or
                                 cta_ent['label'].startswith('SECCION_')) and ann_ent['end'] != cta_ent['end']:
                            entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'], 'text': ann_ent['text'],
                                      'start': ann_ent['start'], 'end': ann_ent['end'], 'label': ann_ent['label'],
                                      'old_text': cta_ent['text'], 'old_end': cta_ent['end'],
                                      'old_label': cta_ent['label']}
                            change_ent.append(entity)
                            freq.update_acceptance_freq(ann_ent['text'], ann_ent['label'])
                            add = False
                            break
                    if add:
                        add_ent.append(ann_ent)

                        suffix = ""
                        if not file.startswith("son"):
                            suffix = ".utf8"

                        dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" +  bunch.split("_")[0] + "/" + \
                                  dir  + "/" + file.replace(".ann", "") + "\";\"" + dir[
                                       0].upper() + "_" + file + "\")"
                        if not (ann_ent['label'].startswith('Hora_') or ann_ent['label'].startswith('Fecha_') or
                                ann_ent['label'].startswith('Tiempo_')):
                            if ann_ent['label'] + "|" + ann_ent['text'] not in new_variables.keys() and \
                                    ann_ent['label'].upper() + "|" + \
                                    ann_ent['text'].upper() not in new_variables.keys():
                                if ann_ent['label'].startswith('SECCION_'):
                                    if headers_name_dic.get(ann_ent["text"].upper()) is None:
                                        new_variables[ann_ent['label'].upper() + "|" + ann_ent['text'].upper()] = \
                                            [dir_file]
                                    else:
                                        print(dir + " " + file + " " + ' '.join(
                                            ['{0}: {1}'.format(k, v) for k, v in ann_ent.items()]))
                                else:
                                    new_variables["_SUG_" + ann_ent['label'].
                                        replace("_previa", "").replace("_alta", "").replace("_hab", "") + "|" + ann_ent[
                                                      'text']] = \
                                        [dir_file]
                            else:
                                temp_list = new_variables.get(
                                    "_SUG_" + ann_ent['label'].replace("_previa", "")
                                    .replace("_alta", "").replace("_hab", "") + "|" + ann_ent['text'])
                                if temp_list is None:
                                    temp_list = new_variables.get(
                                        ann_ent['label'].upper() + "|" + ann_ent['text'].upper())

                                if ann_ent['label'].startswith('SECCION_'):
                                    if headers_name_dic.get(ann_ent["text"].upper()) is None:
                                        temp_list.append(dir_file)
                                        update = {ann_ent['label'].upper() + "|" + ann_ent['text'].upper(): temp_list}
                                        new_variables.update(update)

                                    else:
                                        print(dir + " " + file + " " + ' '.join(
                                            ['{0}: {1}'.format(k, v) for k, v in ann_ent.items()]))
                                else:
                                    temp_list.append(dir_file)
                                    update = {"_SUG_" + ann_ent['label']
                                        .replace("_previa", "").replace("_alta", "").replace("_hab", "") + "|" +
                                              ann_ent['text']: temp_list}
                                    new_variables.update(update)

                adds[file] = add_ent
                changes[file] = change_ent
                no_changes[file] = no_change_ent

            adds_ann[dir] = adds
            changes_ann[dir] = changes
            no_changes_ann[dir] = no_changes

            removes_ann[dir] = removes

        print("Finish new added Sections that we have already in our dictionary")
        return adds_ann, changes_ann, no_changes_ann,  removes_ann, new_variables


