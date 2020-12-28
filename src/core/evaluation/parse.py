from src.core.const import const
from src.core.entity.entities import Entities
from src.core.util.utility import Util


class Parse:
    snomed_type_variable_varience_dic, snomed_type_varience_variable_dic = Util.get_type_variable_varience()
    original_snomed_type_variable_varience_dic, original_snomed_type_varience_variable_dic = Util.get_type_variable_varience_original()

    @staticmethod
    def manual_annotations(annotators_entities, hospital_names_dic):

        eval_dir_dic = dict()
        merged_file = dict()
        per_hospital = hospital_aquas = aquas_hospital = all_hospital = None
        for annotator, annotator_files in annotators_entities.items():
            for annotator_file, annotator_records in annotator_files.items():
                annotator_file = annotator_file.replace(".ann", ".txt")
                eval_dir_file = eval_dir_dic.get(annotator_file) if annotator_file in \
                                                                eval_dir_dic.keys() else {"ARCHETYPE": {}}

                hospital_name = hospital_names_dic.get(annotator_file) if annotator_file in \
                                                                          hospital_names_dic.keys() else None

                for record in annotator_records:
                    if record['label'].startswith("SECCION") and annotator != "victoria":
                        continue
                    else:
                        eval_dir_file = Parse.update_dic(annotator_file, record, eval_dir_file, eval_dir_dic)
                        eval_dir_dic.update({annotator_file: eval_dir_file})
                        if hospital_name is not None:
                            per_hospital = merged_file.get(hospital_name) if hospital_name in \
                                                                             merged_file.keys() else {"ARCHETYPE": {}}
                            per_hospital = Parse.update_dic(annotator_file, record, per_hospital, merged_file)
                            merged_file.update({hospital_name: per_hospital})
                        if hospital_name is None or hospital_name != "sonespases":
                            hospital_aquas = "aquas"
                            aquas_hospital = merged_file.get(hospital_aquas) if hospital_aquas in \
                                                                             merged_file.keys() else {"ARCHETYPE": {}}
                            aquas_hospital = Parse.update_dic(annotator_file, record, aquas_hospital, merged_file)
                            merged_file.update({hospital_aquas: aquas_hospital})
                        if True:
                            hospital_all = "all"
                            all_hospital = merged_file.get(hospital_all) if hospital_all in \
                                                                             merged_file.keys() else {"ARCHETYPE": {}}
                            all_hospital = Parse.update_dic(annotator_file, record, all_hospital, merged_file)
                            merged_file.update({hospital_all: all_hospital})
                # eval_dir_dic.update({annotator_file: eval_dir_file})
                # if hospital_name is not None:
                #     merged_file.update({hospital_name: per_hospital})
                # if hospital_name is None:
                #     merged_file.update({hospital_aquas: aquas_hospital})

        return eval_dir_dic, merged_file

    @staticmethod
    def update_dic(annotator_file, record, eval_dir_file, eval_dir_dic):
        cleaned_label = Entities.label_suffix_prefix_fixer(record['label'])

        specific_label = Util.find_type_variable_label(Parse.snomed_type_varience_variable_dic, cleaned_label, record['text'])

        if specific_label not in eval_dir_file["ARCHETYPE"].keys():
            eval_dir_file["ARCHETYPE"][specific_label] = {record['text']: 1}
        elif not specific_label.startswith("SECCION_") or annotator_file not in eval_dir_dic.keys():
            temp_dic = eval_dir_file["ARCHETYPE"][specific_label]
            if record['text'] not in temp_dic.keys():
                temp_dic[record['text']] = 1
            else:
                temp = temp_dic[record['text']]
                temp_dic.update({record['text']: temp + 1})
            eval_dir_file["ARCHETYPE"].update({specific_label: temp_dic})

        supertype = Util.archetype_finder(cleaned_label)
        if supertype is not None:
            if supertype not in eval_dir_file.keys():
                eval_dir_file[supertype] = {record['text']: 1}
            else:
                temp_dic = eval_dir_file[supertype]
                if record['text'] not in temp_dic.keys():
                    temp_dic[record['text']] = 1
                else:
                    temp = temp_dic[record['text']]
                    temp_dic.update({record['text']: temp + 1})
                eval_dir_file.update({supertype: temp_dic})
        return eval_dir_file




