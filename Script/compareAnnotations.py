import argparse
import csv
import os
import shutil
import string
from collections import OrderedDict
from shutil import copy
import unidecode
import xlsxwriter
import numpy as np
import unidecode

from Script.utility import reading_duplicated_files


class Evaluation(object):
    def __init__(self):
        # set = None
        # annotators_dir = ""
        # pre_processing_dir = ""
        # IAA_ANN_dir = ""
        # IAA_CSV_dir = ""
        # all_differences_csv_dir = ""
        # ctakes_dir = ""

        file_dir = os.path.dirname(os.path.abspath(__file__))
        self.parentDir = os.path.dirname(file_dir)

        self.headers_name_dic = dict()
        self.headers_type_dic = dict()

        self.variables_name_dic = dict()

        self.list_annotators = []

        self.set = None

        self.acceptance_rate = dict()

        self.adds_ann = None
        self.changes_ann = None
        self.no_changes_ann = None
        self.removes_ann = None
        self.new_variables = None

        self.all_files = None
        self.all_files_list = []

        self.annotators_entities = None
        self.annotators_notes = None
        self.ctakes_entities = None

        self.shared_ann_files = None

        self.wrong_categories = dict()

        # self.data_dir = os.path.join(self.parentDir, "data")
        self.distros_dict = []
        self.removed_punc_counter = dict()
        self.removed_punc = dict()

    def headers_dic(self, header):
        with open(header, "r") as h:
            for line in h:
                row_header = line.strip().split("\t")
                if not row_header[2] in self.headers_name_dic.keys():
                    self.headers_name_dic[row_header[2]] = row_header[1]
                if not row_header[1] in self.headers_type_dic.keys():
                    self.headers_type_dic[row_header[1]] = row_header[0]

    def variable_dic(self, header):
        with open(header, "r") as h:
            for line in h:
                row_header = line.strip().split("|")
                unaccented_string = unidecode.unidecode(row_header[2]).lower()
                if not unaccented_string in self.variables_name_dic.keys():
                    self.variables_name_dic[unaccented_string] = [row_header[1]]
                else:
                    temp = self.variables_name_dic[unaccented_string]
                    temp.append(row_header[1])
                    self.variables_name_dic.update({unaccented_string: temp})

    def init_paths(self, sset):
        self.set = sset
        global annotators_dir, pre_processing_dir, IAA_ANN_dir, IAA_CSV_dir, ctakes_dir, \
            all_differences_csv_dir, save_statistical_dir
        main_dir = os.path.join(self.parentDir, "Annotated")
        annotators_dir = os.path.join(main_dir, "manual_annotations")
        pre_processing_dir = os.path.join(main_dir, "pre_processing")
        IAA_ANN_dir = os.path.join(main_dir, "IAA_ANN", self.set)
        IAA_CSV_dir = os.path.join(main_dir, "IAA_CSV", self.set)
        all_differences_csv_dir = os.path.join(main_dir, "analysis")
        ctakes_dir = os.path.join(main_dir, "pre_annotations")
        save_statistical_dir = os.path.join(all_differences_csv_dir, "statistical", self.set)

        data_dir = os.path.join(self.parentDir, "data")
        self.distros_dict = reading_duplicated_files(self.set, data_dir)

        shutil.rmtree(IAA_ANN_dir, ignore_errors=True)
        os.makedirs(IAA_ANN_dir, exist_ok=True)
        os.makedirs(IAA_CSV_dir, exist_ok=True)

    def annators_name(self):

        list_annotators = []
        for sub_dir in os.listdir(annotators_dir):
            if not sub_dir.startswith('.'):
                list_annotators.append(sub_dir)

        self.list_annotators = list_annotators


    def update_punc(self, punc, annotator, who):
        if who is "annotators" and punc not in self.removed_punc:
            if annotator not in self.removed_punc.keys():
                self.removed_punc[annotator] = [punc]
            else:
                temp = self.removed_punc.get(annotator)
                if punc not in temp:
                    temp.append(punc)
                    self.removed_punc.update({annotator: temp})


    def span_fixer(self, text, start_span, end_span, label, who, annotator):
        original_text = text
        if not (label.startswith("NIHSS") or label.startswith("mRankin") or label.startswith("ASPECTS")):
            punctuation = string.punctuation.replace(".", "")

            before_rstrip = len(text)
            text = text.rstrip()
            after_rstrip = len(text)
            end_span -= before_rstrip - after_rstrip
            while text[len(text) - 1] in punctuation:
                self.update_punc(text[len(text) - 1], annotator, who)

                text = text[:-1]
                removed_space = len(text) - len(text.rstrip())
                text = text.rstrip()
                end_span -= 1 + removed_space
            before_lstrip = len(text)
            text = text.lstrip()
            after_lstrip = len(text)
            start_span += before_lstrip - after_lstrip
            while text[0] in string.punctuation:
                self.update_punc(text[0], annotator, who)

                text = text[1:]
                removed_space = len(text) - len(text.lstrip())
                text = text.lstrip()
                start_span += 1 + removed_space
            # punctuation = string.punctuation.replace(".","")
            # if text[len(text)-1] in punctuation:
            #     text = text[:-1]
            #     removed_spase = len(text) - len(text.rstrip())
            #     text = text.rstrip()
            #     end_span = end_span-1-removed_spase
            # if text[0] in string.punctuation:
            #     text = text[1:]
            #     removed_spase = len(text) - len(text.lstrip())
            #     text = text.lstrip()
            #     start_span = start_span+1+removed_spase

        if who is "annotators" and original_text != text:
            if annotator not in self.removed_punc_counter.keys():
                self.removed_punc_counter[annotator] = 1
            else:
                temp = self.removed_punc_counter.get(annotator)
                self.removed_punc_counter.update({annotator: temp+1})

            # self.removed_punc_counter += 1
        return text, start_span, end_span

    def get_annotators_entities(self):
        all_files = {}
        annotator = {}
        annotator_notes = {}
        rm = {}
        for dir in self.list_annotators:
            list_files = []
            pre_pro = os.path.join(pre_processing_dir, dir, self.set)

            pre_pro_revised = os.path.join(pre_processing_dir, dir, self.set.split("_", 1)[0])
            os.makedirs(pre_pro_revised, exist_ok=True)

            os.makedirs(pre_pro, exist_ok=True)

            annotators_entities = {}
            annotators_hash = {}
            removes = {}
            annotators_deep_dir = os.path.join(annotators_dir, dir, self.set)
            for annotators_files in os.listdir(annotators_deep_dir):
                if annotators_files.endswith(".ann"):
                    self.all_files_list.append(annotators_files)
                    list_files.append(annotators_files)
                    with open(os.path.join(annotators_deep_dir, annotators_files), "r") as r:
                        entities = []
                        remove_ent = []
                        hash_ent = []
                        with open(os.path.join(pre_pro, annotators_files), "w") as w, \
                                open(os.path.join(pre_pro_revised, annotators_files), "w") as w_revised:
                            all_hash = []
                            keephash = []
                            for full_line in r:
                                try:
                                    line = full_line.split("\t", 1)[1]
                                except:
                                    print(dir, annotators_files, line)
                                if not (full_line.startswith("#")):
                                    temp_line = full_line.split("\t", 2)
                                    checking_text = temp_line[-1].replace("\n", "")
                                    checking_start = int(temp_line[1].split()[1])
                                    checking_end = int(temp_line[1].split()[2])
                                    checking_label = temp_line[1].split()[0]
                                    if self.set.startswith("04") or self.set.startswith("03") or self.set.startswith(
                                            "02") or self.set.startswith("01"):
                                        # For bunch 1,2,3 we revised manual annotations for varibalea and section that
                                        # ended with a punctuations except of dot (.) and started with a punctuations
                                        # we fixed the span and saved it in a correct file (03, 02)...
                                        checking_text, checking_start, checking_end = \
                                            self.span_fixer(checking_text, checking_start, checking_end, checking_label, "annotators", dir)
                                    w_revised.write(
                                        temp_line[0] + "\t" + checking_label + " " + str(checking_start) + " " +
                                        str(checking_end) + "\t" + checking_text + "\n")
                                else:
                                    w_revised.write(full_line)

                                if not (line.startswith("HORA") or full_line.startswith("#") or line.startswith("FECHA")
                                        or line.startswith("_SUG_") or line.startswith("TIEMPO")):
                                    w.write(full_line)
                                    entity = {}
                                    temp_line = full_line.split("\t", 2)
                                    checking_text = temp_line[-1].replace("\n", "")
                                    checking_start = int(temp_line[1].split()[1])
                                    checking_end = int(temp_line[1].split()[2])
                                    checking_label = temp_line[1].split()[0]
                                    if self.set.startswith("04") or self.set.startswith("03") or self.set.startswith(
                                            "02") or self.set.startswith("01"):
                                        # For bunch 1,2,3 we revised manual annotations for varibalea and section that
                                        # ended with a punctuations except of dot (.) and started with a punctuations
                                        # we fixed the span and saved it in a correct file (03, 02)...
                                        checking_text, checking_start, checking_end = \
                                            self.span_fixer(checking_text, checking_start, checking_end, checking_label, "annotators", dir)
                                    # w_revised.write(temp_line[0] + "\t" + checking_label + " " + str(checking_start) + " " +
                                    #                 str(checking_end) + "\t" + checking_text + "\n")
                                    entity['row'] = temp_line[0]
                                    keephash.append(temp_line[0])
                                    entity['text'] = checking_text
                                    entity['start'] = checking_start
                                    entity['end'] = checking_end
                                    entity['label'] = checking_label
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
                                    self.update_notacceptance_freq(entity['text'], entity['label'])
                                elif full_line.startswith("#"):
                                    all_hash.append(full_line)
                            for hash in all_hash:
                                row = hash.strip().split("\t", 2)[1].split(" ")[1]
                                if row in keephash:
                                    w.write(hash)
                                    # w_revised.write(hash)
                                    entity = {}
                                    temp_line = hash.split("\t", 2)
                                    entity['T'] = temp_line[1].split(" ")[1]
                                    entity['rest'] = "\t".join(temp_line[2:])
                                    hash_ent.append(entity)
                            w.close()
                            w_revised.close()
                        r.close()
                        annotators_hash[annotators_files] = hash_ent
                        entities_ordered = sorted(entities, key=lambda entity: entity['start'])
                        annotators_entities[annotators_files] = entities_ordered
                        removes[annotators_files] = remove_ent

            annotator_notes[dir] = annotators_hash
            annotator[dir] = annotators_entities
            rm[dir] = removes
            all_files[dir] = list_files

        # return all_files, annotator, annotator_notes, rm
        self.all_files = all_files
        self.annotators_entities = annotator
        self.annotators_notes = annotator_notes

    def IAA_ANN(self):
        file_dic = {}
        ann_file = {}



        for dir, files in self.annotators_entities.items():
            for file, records in files.items():
                # source = os.path.join(annotators_dir, dir, self.set, file).replace(".ann", ".txt")
                if file.replace(".ann", ".txt") in self.distros_dict:
                    # copy(source, IAA_ANN_dir)
                    # if file_dic.get(file) is None:
                    #     file_dic[file] = 1
                    # with open(os.path.join(IAA_ANN_dir, file), "a+") as w_ann:
                    #     for record in records:
                    #         w_ann.write(
                    #             "T" + str(file_dic.get(file)) + "\t" + record['label'] + " " + str(record['start'])
                    #             + " " + str(record['end']) + "\t" + record['text'] + "\n")
                    #         _hash = False
                    #         for rec_note in self.annotators_notes.get(dir).get(file):
                    #             if rec_note['T'] == record['row']:
                    #                 _hash = True
                    #                 break
                    #         if _hash:
                    #             w_ann.write(
                    #                 "#" + str(file_dic.get(file)) + "\tAnnotatorNotes T" + str(
                    #                     file_dic.get(file)) + "\t" +
                    #                 rec_note['rest'].strip() + " Annotator: " + dir + "\n")
                    #         else:
                    #             w_ann.write(
                    #                 "#" + str(file_dic.get(file)) + "\tAnnotatorNotes T" + str(
                    #                     file_dic.get(file)) + "\t" +
                    #                 "Annotator: " + dir + "\n")
                    #
                    #         file_dic[file] += 1
                    # w_ann.close()

                    if ann_file.get(file) is None:
                        ann_records = {}
                    else:
                        ann_records = ann_file.get(file).copy()

                    # records_list = []
                    for record in records:
                        records_list = [(record["label"], record["start"], record["end"], record["text"])]
                        if dir not in ann_records.keys():
                            ann_records[dir] = records_list
                        else:
                            temp = ann_records.get(dir).copy()
                            temp += records_list
                            update = {dir: temp}
                            ann_records.update(update)

                    ann_file[file] = ann_records
        self.shared_ann_files = ann_file

    def IAA_CSV_BRRAT(self):
        w_mis = open(os.path.join(save_statistical_dir, "Set_" + self.set + "_link_diff_files_in_Brat.txt"), "w")
        for file, annotators in self.shared_ann_files.items():
            w_csv = open(os.path.join(IAA_CSV_dir, file + ".csv"), "w")
            csv_writer = csv.writer(w_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # csv_writer.writerow([" "] + list(annotators_entities.keys()))

            list_annotators = list(annotators.keys())

            # for annotators in records.values():
            #     for annt in annotators.keys():
            #         if annt not in list_annotators:
            #             list_annotators.append(annt)

            list_annotators.sort()

            csv_writer.writerow([" "] + list_annotators)
            annotat_hyper = ""

            if len(list_annotators) == 2:
                w_mis.write('http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/' + list_annotators[0] + "/" +
                            self.set.split("_")[0] + '/#/' + list_annotators[1] + "/" + self.set.split("_")[
                                0] + "/" + file.replace(".ann", "") + "\n")

                # IAA_score[file].update(records)

                #
                # list_ann = ["X" if ann in annotators.keys() else " " for ann in list_annotators]

                # ORDER?!!!!

                intersection = set(annotators[list_annotators[0]]).intersection(
                    set(annotators[list_annotators[1]]))
                first_more = set(annotators[list_annotators[0]]) - set(annotators[list_annotators[1]])
                second_more = set(annotators[list_annotators[1]]) - set(annotators[list_annotators[0]])

                for rec in intersection:
                    csv_writer.writerow([rec] + ["X", "X"])
                for rec in first_more:
                    csv_writer.writerow([rec] + ["X", ""])
                for rec in second_more:
                    csv_writer.writerow([rec] + ["", "X"])


    def set_wrong_category(self, type, status, label):
        if label == 'SECCION_DIAGNOSTICO_PRINCIPAL':
            checl = 0
        score = 2 if status == "Agreed" else 1
        if type not in self.wrong_categories.keys():
            status_record = {label: {status: score}}
            self.wrong_categories[type] = status_record
        else:
            status_record_temp = self.wrong_categories[type]
            if label not in status_record_temp.keys():
                status_record_temp[label]= {status: score}
            else:
                label_temp = status_record_temp.get(label)
                if status not in label_temp.keys():
                    label_temp[status] = score
                else:
                    temp_status = label_temp.get(status)
                    temp_status += score
                    label_temp.update({status: temp_status})
                status_record_temp.update({label:label_temp})
            self.wrong_categories.update({type: status_record_temp})







    def IAA_Score_mismatched(self):

        xlsx_details = os.path.join(save_statistical_dir, "Set_" + self.set + "_Details_of_IAA_Score_In_one_File.xlsx")
        workbook_details = xlsxwriter.Workbook(xlsx_details)


        xlsx_mismatch = os.path.join(save_statistical_dir, "Set_" + self.set + "_All_MisMatching_Records.xlsx")
        workbook_mismatch = xlsxwriter.Workbook(xlsx_mismatch)

        xlsx_file = os.path.join(save_statistical_dir, "Set_" + self.set + "_IAA_Score.xlsx")
        workbook = xlsxwriter.Workbook(xlsx_file)

        worksheet_details = workbook_details.add_worksheet("General_IAA_Score")

        IAA_matrix_general_all = np.zeros((2, 2))
        IAA_matrix_general_changed = np.zeros((2, 2))
        for file, annotators in self.shared_ann_files.items():
            IAA_matrix_all = np.zeros((2, 2))
            IAA_matrix_changed = np.zeros((2, 2))

            worksheet = workbook.add_worksheet(file)
            worksheet_mismatch = workbook_mismatch.add_worksheet(file)

            counter = 1
            counter_mistmatch = 1
            worksheet.set_column(0, 0, 40)
            worksheet_mismatch.set_column(0, 0, 40)
            worksheet.set_column(3, 3, 30)
            worksheet_mismatch.set_column(3, 3, 30)

            worksheet.set_column(6, 7, 10)

            worksheet.freeze_panes(1, 0)
            worksheet_mismatch.freeze_panes(1, 0)

            list_annotators = list(annotators.keys())
            list_annotators.sort()

            for i, annot in enumerate(list_annotators):
                worksheet.write(0, i + 4, annot)
                worksheet_mismatch.write(0, i + 4, annot)


            worksheet.write(0, 0, "Label")
            worksheet_mismatch.write(0, 0, "Label")

            worksheet.write(0, 1, "Start")
            worksheet_mismatch.write(0, 1, "Start")

            worksheet.write(0, 2, "End")
            worksheet_mismatch.write(0, 2, "End")

            worksheet.write(0, 3, "Text")
            worksheet_mismatch.write(0, 3, "Text")

            worksheet.write(0, 6, "Changed")
            worksheet.write(0, 7, "Added")

            if len(list_annotators) == 2:

                intersection = set(annotators[list_annotators[0]]).intersection(
                    set(annotators[list_annotators[1]]))
                first_more = set(annotators[list_annotators[0]]) - set(annotators[list_annotators[1]])
                second_more = set(annotators[list_annotators[1]]) - set(annotators[list_annotators[0]])

                for rec in intersection:

                    rec_list = list(rec)
                    # temp_str = rec_list[0] + " " + str(rec_list[1]) + " " + str(rec_list[2]) + "\t" + rec_list[3]



                    list_ann = [1, 1]
                    IAA_matrix_all[0, 0] += 1

                    is_added = self.isEntityAdded(file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 0] += is_added

                    is_changed = self.isEntityChanged(file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 0] += is_changed

                    type = "CH_A" if is_changed + is_added > 0 else "AC"
                    status = "Agreed"
                    label = rec_list[0]
                    self.set_wrong_category(type, status, label)

                    worksheet.write(counter, 0, rec_list[0])
                    worksheet.write(counter, 1, rec_list[1])
                    worksheet.write(counter, 2, rec_list[2])
                    worksheet.write(counter, 3, rec_list[3])
                    worksheet.write(counter, 4, list_ann[0])
                    worksheet.write(counter, 5, list_ann[1])

                    worksheet.write(counter, 6, is_changed)
                    worksheet.write(counter, 7, is_added)

                    counter += 1

                for rec in first_more:
                    rec_list = list(rec)
                    # temp_str = rec_list[0] + " " + str(rec_list[1]) + " " + str(rec_list[2]) + "\t" + rec_list[3]

                    list_ann = [1, 0]
                    IAA_matrix_all[0, 1] += 1

                    is_added = self.isEntityAdded(file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 1] += is_added

                    is_changed = self.isEntityChanged(file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 1] += is_changed

                    type = "CH_A" if is_changed + is_added > 0 else "AC"
                    status = "Not_Agreed"
                    label = rec_list[0]
                    self.set_wrong_category(type, status, label)

                    worksheet.write(counter, 0, rec_list[0])
                    worksheet.write(counter, 1, rec_list[1])
                    worksheet.write(counter, 2, rec_list[2])
                    worksheet.write(counter, 3, rec_list[3])
                    worksheet.write(counter, 4, list_ann[0])
                    worksheet.write(counter, 5, list_ann[1])
                    worksheet.write(counter, 6, is_changed)
                    worksheet.write(counter, 7, is_added)
                    counter += 1

                    worksheet_mismatch.write(counter_mistmatch, 0, rec_list[0])
                    worksheet_mismatch.write(counter_mistmatch, 1, rec_list[1])
                    worksheet_mismatch.write(counter_mistmatch, 2, rec_list[2])
                    worksheet_mismatch.write(counter_mistmatch, 3, rec_list[3])
                    worksheet_mismatch.write(counter_mistmatch, 4, list_ann[0])
                    worksheet_mismatch.write(counter_mistmatch, 5, list_ann[1])
                    counter_mistmatch += 1

                for rec in second_more:
                    rec_list = list(rec)
                    # temp_str = rec_list[0] + " " + str(rec_list[1]) + " " + str(rec_list[2]) + "\t" + rec_list[3]

                    list_ann = [0, 1]
                    IAA_matrix_all[1, 0] += 1

                    is_added = self.isEntityAdded(file, list_annotators[1], rec_list)
                    IAA_matrix_changed[1, 0] += is_added

                    is_changed = self.isEntityChanged(file, list_annotators[1], rec_list)
                    IAA_matrix_changed[1, 0] += is_changed

                    type = "CH_A" if is_changed + is_added > 0 else "AC"
                    status = "Not_Agreed"
                    label = rec_list[0]
                    self.set_wrong_category(type, status, label)

                    worksheet.write(counter, 0, rec_list[0])
                    worksheet.write(counter, 1, rec_list[1])
                    worksheet.write(counter, 2, rec_list[2])
                    worksheet.write(counter, 3, rec_list[3])
                    worksheet.write(counter, 4, list_ann[0])
                    worksheet.write(counter, 5, list_ann[1])
                    worksheet.write(counter, 6, is_changed)
                    worksheet.write(counter, 7, is_added)
                    counter += 1

                    worksheet_mismatch.write(counter_mistmatch, 0, rec_list[0])
                    worksheet_mismatch.write(counter_mistmatch, 1, rec_list[1])
                    worksheet_mismatch.write(counter_mistmatch, 2, rec_list[2])
                    worksheet_mismatch.write(counter_mistmatch, 3, rec_list[3])
                    worksheet_mismatch.write(counter_mistmatch, 4, list_ann[0])
                    worksheet_mismatch.write(counter_mistmatch, 5, list_ann[1])
                    counter_mistmatch += 1

            IAA_matrix_general_all += IAA_matrix_all
            IAA_matrix_general_changed += IAA_matrix_changed

            worksheet.write(0, 8, "% All")
            K = IAA_matrix_all[0][0] / (IAA_matrix_all[0][0] + IAA_matrix_all[0][1] + IAA_matrix_all[1][0])
            worksheet.write(0, 9, K)

            worksheet.set_column(10, 10, 20)

            worksheet.write(0, 10, "% Changed and added:")
            denominator = (IAA_matrix_changed[0][0] + IAA_matrix_changed[0][1] + IAA_matrix_changed[1][0])

            if denominator == 0:
                K = "No Changed and No Added"
            else:
                K = IAA_matrix_changed[0][0] / denominator

            worksheet.write(0, 11, K)
            # worksheet.set_column(6, 6, 20)

        worksheet_details.write(0, 0, "% All")
        K = IAA_matrix_general_all[0][0] / (IAA_matrix_general_all[0][0] + IAA_matrix_general_all[0][1] + IAA_matrix_general_all[1][0])
        worksheet_details.write(0, 1, K)

        worksheet_details.set_column(2, 2, 20)

        worksheet_details.write(0, 2, "% Changed and added:")
        denominator = (IAA_matrix_general_changed[0][0] + IAA_matrix_general_changed[0][1] + IAA_matrix_general_changed[1][0])

        if denominator == 0:
            K = "No Changed and No Added"
        else:
            K = IAA_matrix_general_changed[0][0] / denominator

        worksheet_details.write(0, 3, K)
        worksheet_details = workbook_details.add_worksheet("Wrong_Variables_Details")

        count = 1
        status_agreed = "Agreed"
        status_not_agreed = "Not_Agreed"
        worksheet_details.write(0, 0, "Status of Annotation")
        worksheet_details.write(0, 1, "Label")
        worksheet_details.write(0, 2, "For how many files it happened:")
        worksheet_details.write(0, 3, "For how many files annotators are agree:")
        worksheet_details.write(0, 4, "For how many files annotators are not agree")
        worksheet_details.write(0, 5, "Rate of agreement")
        worksheet_details.set_column(0, 0, 15)
        worksheet_details.set_column(1, 1, 40)
        worksheet_details.set_column(2, 5, 20)
        # worksheet_details.set_column(1, 4, 40)
        for i, (type, labels) in enumerate(self.wrong_categories.items()):
            type_details = "Accepted" if type == "AC" else "Changed_or_Added"
            worksheet_details.write(count + i, 0, type_details)
            count += 1
            for (label, status) in labels.items():
                num_status_agreed = status[status_agreed] if status.get(status_agreed) != None else 0
                num_status_not_agreed = status[status_not_agreed] if status.get(status_not_agreed) != None else 0
                worksheet_details.write(count , 1, label)
                worksheet_details.write(count, 2, num_status_agreed + num_status_not_agreed)
                worksheet_details.write(count, 3, num_status_agreed)
                worksheet_details.write(count, 4, num_status_not_agreed)
                score = None if num_status_agreed + num_status_not_agreed == 0 else (num_status_agreed / (num_status_agreed + num_status_not_agreed))
                worksheet_details.write(count, 5, score)
                count += 1



        workbook.close()
        workbook_mismatch.close()
        workbook_details.close()

    def IAA(self):

        # But for Bunch 5, because there are some doubt about the output of the annotators, we are going to shift bunch 3
        # (Give files related to first annotators to the second one and ...) and re-annotation all of them to have a better IAA.
        # For dublicated files in bunch 3, we are deleting them in bunch 5 and replace them with 8 new files and dublicated in annotatos' direcotry. (We should keep the list of dublicated file).
        # Because Bunch 3 we will use headers from bunch 4 + (DIAG. + PROC.).

        # We should correct bunch 3 with the correct variables in header dictionary 5 For having correct IAA

        # Header List in bunch 2 and 1 has been changed. for IAA bunch 2 and 6 we should fix section of bunch 2 with the correct one.

        self.IAA_ANN()

        self.IAA_CSV_BRRAT()

        self.IAA_Score_mismatched()

        # data_dir = os.path.join(parentDir, "Annotated/analysis/statistical", Set)

    def isEntityAdded(self, file, annotator, rec_list):
        records_added = self.adds_ann[annotator][file]
        for record in records_added:
            if (rec_list[0] == record['label'] and rec_list[1] == record['start']
                    and rec_list[2] == record['end'] and rec_list[3] == record['text']):
                return 1
        return 0

    def isEntityChanged(self, file, annotator, rec_list):
        records_changed = self.changes_ann[annotator][file]
        for record in records_changed:
            if (rec_list[0] == record['label'] and rec_list[1] == record['start']
                    and rec_list[2] == record['end'] and rec_list[3] == record['text']):
                return 1
        return 0

    def get_ctakes_entities(self):
        ctk = {}
        sset_prefix = self.set.split("_")[0]
        for dir in self.list_annotators:
            ctakes_entities = {}
            for ctakes_files in os.listdir(os.path.join(ctakes_dir, dir, sset_prefix)):
                if ctakes_files.endswith(".ann"):
                    with open(os.path.join(ctakes_dir, dir, sset_prefix, ctakes_files), "r") as r:
                        entites = []
                        for line in r:
                            temp_line = line.strip().split("\t", 2)
                            if not line.startswith("#"):

                                checking_text = temp_line[-1].replace("\n", "")
                                checking_start = int(temp_line[1].split()[1])
                                checking_end = int(temp_line[1].split()[2])
                                checking_label = temp_line[1].split()[0]
                                if self.set.startswith("04") or self.set.startswith("03") or self.set.startswith(
                                        "02") or self.set.startswith("01"):
                                    # For bunch 1,2,3 we revised manual annotations for variables and sections that
                                    # ended with a punctuations except of dot (.) and started with a punctuations
                                    # we fixed the span and saved it in a correct file (03, 02)...
                                    # for having a correct evaluation our pipeline tools with the manual, we should
                                    # apply the same for output of pipeline
                                    checking_text, checking_start, checking_end = \
                                        self.span_fixer(checking_text, checking_start, checking_end, checking_label, "ctakes", dir)

                                    if self.set.startswith("03") and temp_line[-1].replace("\n", "") != checking_text:
                                        print("ERROR!!!!!!")

                                # entity['row'] = temp_line[0]
                                # entity['text'] = checking_text
                                # entity['start'] = checking_start
                                # entity['end'] = checking_end
                                # entity['label'] = checking_label

                                entity = {'row': temp_line[0], 'text': checking_text,
                                          'start': checking_start,
                                          'end': checking_end, 'label': checking_label}
                                entites.append(entity)
                        ctakes_ents = sorted(entites, key=lambda entity: entity['start'])
                        ctakes_entities[ctakes_files] = ctakes_ents

            ctk[dir] = ctakes_entities
        self.ctakes_entities = ctk

    def normolized_text(self, text_original):
        normolized_whitespace = " ".join(text_original.split())
        unaccented_string = unidecode.unidecode(normolized_whitespace)

        return unaccented_string.lower()

    def update_notacceptance_freq(self, text_original, lable_original):
        if lable_original.startswith("_SUG_"):
            label = lable_original.replace("_SUG_", "").replace("_previa", "").replace("_alta", "").replace("_hab", "")
            unaccented_string = self.normolized_text(text_original)
            if self.acceptance_rate.get(unaccented_string + "_" + label) is None:
                self.acceptance_rate[unaccented_string + "_" + label] = {"accepted": 0, "notaccepted": 1}
            else:
                temp_word = self.acceptance_rate.get(unaccented_string + "_" + label)
                temp_counter = temp_word.get("notaccepted")
                update = {"accepted": temp_word.get("accepted"), "notaccepted": temp_counter + 1}
                self.acceptance_rate.update({unaccented_string + "_" + label: update})

    def update_acceptance_freq(self, text_original, lable_original):
        if not (lable_original.startswith("SECCION_") or lable_original.startswith("Hora_")
                or lable_original.startswith("Fecha_") or lable_original.startswith("Tiempo_")):

            label = lable_original.replace("_previa", "").replace("_alta", "").replace("_hab", "")
            unaccented_string = self.normolized_text(text_original)
            if self.acceptance_rate.get(unaccented_string + "_" + label) is None:
                self.acceptance_rate[unaccented_string + "_" + label] = {"accepted": 1, "notaccepted": 0}
            else:
                temp_word = self.acceptance_rate.get(unaccented_string + "_" + label)
                temp_counter = temp_word.get("accepted")
                update = {"accepted": temp_counter + 1, "notaccepted": temp_word.get("notaccepted")}
                self.acceptance_rate.update({unaccented_string + "_" + label: update})

    def statistical_analysis(self):
        variable_dir = "/home/siabar/eclipse-workspace/ctakes/ctakes-SpaCTeS-res/src/main/resources/org/apache/ctakes/examples/dictionary/lookup/fuzzy"

        if int(self.set.split("_")[0]) <= 2:
            header_file = os.path.join(self.parentDir, "../EHR-HeaderDetector/data/headers_original_bunch_1-2.txt")
            varibale_file = os.path.join(variable_dir, "IctusnetDict_original_bunch_1-2.bsv")

            header_file = os.path.join(self.parentDir, "../EHR-HeaderDetector/data/headers_28.11.2019_bunch_4.txt")
            varibale_file = os.path.join(variable_dir, "IctusnetDict_28.11.2019_bunch_4.bsv")
        elif int(self.set.split("_")[0]) == 3:
            header_file = os.path.join(self.parentDir, "../EHR-HeaderDetector/data/headers_13.11.2019_bunch_3.txt")
            # Because Variable Dictionary for Bunch 3 filled by mistake.
            header_file = os.path.join(self.parentDir, "../EHR-HeaderDetector/data/headers_28.11.2019_bunch_4.txt")
            varibale_file = os.path.join(variable_dir, "IctusnetDict_28.11.2019_bunch_4.bsv")
        elif int(self.set.split("_")[0]) == 4:
            header_file = os.path.join(self.parentDir, "../EHR-HeaderDetector/data/headers_28.11.2019_bunch_4.txt")
            varibale_file = os.path.join(variable_dir, "IctusnetDict_28.11.2019_bunch_4.bsv")

        self.headers_dic(header_file)
        self.variable_dic(varibale_file)

        adds_ann = {}
        changes_ann = {}
        no_changes_ann = {}
        removes_ann = {}

        new_variables = {}
        new_variables_where = {}
        for dir in self.list_annotators:
            print("New added Sections by annotators, that we have already them in our dictionary:")

            adds = {}
            changes = {}
            no_changes = {}
            removes = {}

            annotators_entities_ant = self.annotators_entities.get(dir)
            ctakes_entities_ant = self.ctakes_entities.get(dir)

            for file in annotators_entities_ant.keys():

                if file.startswith("sonespases_973918779"):
                    check = 0

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
                                if cta_ent['label'] == ann_ent['label'] or \
                                        cta_ent['label'].replace("_previa", "").replace("_alta", "").replace("_hab", "") \
                                        == "_SUG_" + \
                                        ann_ent['label'].replace("_previa", "").replace("_alta", "").replace("_hab",
                                                                                                             ""):
                                    entity = {'Annotated': ann_ent['row'], 'cTAKES': cta_ent['row'],
                                              'text': cta_ent['text'], 'start': cta_ent['start'], 'end': cta_ent['end'],
                                              'label': cta_ent['label']}
                                    no_change_ent.append(entity)
                                    self.update_acceptance_freq(ann_ent['text'], ann_ent['label'])
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
                                        self.update_acceptance_freq(ann_ent['text'], ann_ent['label'])
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
                            self.update_acceptance_freq(ann_ent['text'], ann_ent['label'])
                            add = False
                            break
                    if add:
                        add_ent.append(ann_ent)

                        suffix = ""
                        if not file.startswith("son"):
                            suffix = ".utf8"

                        dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + dir + "/" + \
                                   self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + dir[
                                       0].upper() + "_" + file + "\")"
                        if not (ann_ent['label'].startswith('Hora_') or ann_ent['label'].startswith('Fecha_') or
                                ann_ent['label'].startswith('Tiempo_')):
                            if ann_ent['label'] + "|" + ann_ent['text'] not in new_variables.keys() and \
                                    ann_ent['label'].upper() + "|" + \
                                    ann_ent['text'].upper() not in new_variables.keys():
                                if ann_ent['label'].startswith('SECCION_'):
                                    if self.headers_name_dic.get(ann_ent["text"].upper()) is None:
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
                                    if self.headers_name_dic.get(ann_ent["text"].upper()) is None:
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

        self.adds_ann = adds_ann
        self.changes_ann = changes_ann
        self.no_changes_ann = no_changes_ann
        self.removes_ann = removes_ann
        self.new_variables = new_variables
        print("Finish new added Sections that we have already in our dictionary")

    def save_analysis(self):
        stat = {}
        all_changes = {"added": self.adds_ann, "changed": self.changes_ann, "accepted": self.no_changes_ann,
                       "removed": self.removes_ann}
        for key, value in all_changes.items():
            for dir, files in value.items():
                count_key = stat.get(dir)
                if count_key is None:
                    count_key = {}
                # os.makedirs(os.path.join(save_analysis_dir, dir, Set), exist_ok=True)
                count = 0
                count_hft = 0
                count_span = 0
                for file, records in files.items():
                    analysis_dir = os.path.join(all_differences_csv_dir, dir, self.set, file.split(".ann")[0])
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

        save_statistical_dir = os.path.join(all_differences_csv_dir, "statistical", self.set)
        os.makedirs(save_statistical_dir, exist_ok=True)
        with open(os.path.join(save_statistical_dir, "Set_" + self.set + "-Statistical_Analysis-Set.csv"),
                  "w") as stat_csv:
            csv_writer = csv.writer(stat_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow([" "] + list(list(stat.values())[0].keys()) + ["Number of fixed varibales and sections (spans)", "Removed punctuations"])
            for keys, values in stat.items():
                puc_counter = 0 if self.removed_punc_counter.get(keys) == None else self.removed_punc_counter.get(keys)
                puc = 0 if self.removed_punc.get(keys) == None else self.removed_punc.get(keys)
                csv_writer.writerow([keys] + list(values.values()) + [puc_counter] + [puc])

            # csv_writer.writerow("----")
            # csv_writer.writerow(["Removed punctuations"] + self.removed_punc)
            # csv_writer.writerow(["Number varibales that fixed span happend", self.removed_punc_counter])
        stat_csv.close()

        return stat

    def save_new_variables_sections(self):
        print("Adding new added Variables by annotators that we already have in our dictionary")
        statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", self.set)
        os.makedirs(statical_analysis_dir, exist_ok=True)

        with open(os.path.join(statical_analysis_dir, "Set_" + self.set + "-NEW_VARIABLES.csv"), "w") as var_csv, \
                open(os.path.join(statical_analysis_dir, "Set_" + self.set + "-NEW_SECCION.csv"), "w") as sec_csv:
            var_writer = csv.writer(var_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            sec_writer = csv.writer(sec_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            sec_writer.writerow([])
            var_writer.writerow([" ", "Lable", "Text", "File With Link to BRAT"])

            removed_list = ["_SUG_mRankin", "_SUG_NIHSS", "_SUG_ASPECTS"]

            for keys, values in sorted(self.new_variables.items()):
                label_text = keys.split("|", 1)
                temp_line = " ".join(label_text[1].split())
                if label_text[0].startswith("SECCION_"):
                    if not (temp_line.upper() in self.headers_name_dic.keys()
                            and self.headers_name_dic[temp_line.upper()] == label_text[0]):
                        sec_writer.writerow(
                            [self.headers_type_dic.get(label_text[0])] + [label_text[0]] + [temp_line.upper()] + values)
                else:
                    unaccent_name = unidecode.unidecode(temp_line).lower()
                    if not (unaccent_name in self.variables_name_dic.keys()
                            and label_text[0] in self.variables_name_dic[unaccent_name]) \
                            and label_text[0] not in removed_list:
                        var_writer.writerow([""] + [label_text[0]] + [temp_line] + values)
                    elif (unaccent_name in self.variables_name_dic.keys()
                          and label_text[0] in self.variables_name_dic[unaccent_name]) \
                            and label_text[0] not in removed_list:
                        print(temp_line, label_text[0], self.variables_name_dic.get(unaccent_name))

        var_csv.close()
        sec_csv.close()
        print("Finish new added Variables that we have already in our dictionary")

    def trim_name(self, name):
        unaccent_name = unidecode.unidecode(name)
        for i, ch in enumerate(reversed(unaccent_name)):
            if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
                if i == 0:
                    return name
                else:
                    return name[:-1 * i]

    def call_span_checker_accepted(self, begin, line, records):

        if records['text'][0] in string.punctuation or records['text'][len(records['text']) - 1] in string.punctuation:
            return False

        if records['label'].startswith('SECCION') and len(records['text']) <= 5:
            char_before = " "
            char_after = " "

            if begin < records['start']:
                char_before = line[records['start'] - 1 - begin]

            if begin + len(line) > records['end']:
                char_after = line[records['end'] - begin]

            unaccented_char_before = unidecode.unidecode(char_before)
            unaccented_char_after = unidecode.unidecode(char_after)

            if unaccented_char_before is "." or unaccented_char_after is ".":
                return False
            else:
                return True
        return True

    def call_span_checker(self, begin, line, records):

        if records['text'][0] in string.punctuation or records['text'][len(records['text']) - 1] in string.punctuation:
            return False

        char_before = " "
        char_after = " "
        if begin < records['start']:
            char_before = line[records['start'] - 1 - begin]

        if begin + len(line) > records['end']:
            char_after = line[records['end'] - begin]

        unaccented_char_before = unidecode.unidecode(char_before)
        unaccented_char_after = unidecode.unidecode(char_after)

        if ((records['text'] == 'ACM' and unaccented_char_after == "I") or
                (records['text'] == 'I' and unaccented_char_before == "M") or
                (records['text'] == 'ACM' and unaccented_char_after == "e") or
                (records['text'] == 'e' and unaccented_char_before == "M") or
                (records['text'] == 'ACM' and unaccented_char_after == "D") or
                (records['text'] == 'D' and unaccented_char_before == "M") or
                (records['text'] == 'ACA' and unaccented_char_after == "I") or
                (records['text'] == 'I' and unaccented_char_before == "A") or

                (records['text'] == 'ACI' and unaccented_char_after == "D") or
                (records['text'] == 'D' and unaccented_char_before == "I") or

                (records['text'] == 'ACP' and unaccented_char_after == "I") or
                (records['text'] == 'I' and unaccented_char_before == "P") or

                (records['text'] == 'ACM' and unaccented_char_after == "s") or
                (records['text'] == 's' and unaccented_char_before == "M") or

                (records['text'] == 'AIT' and unaccented_char_after == "s") or
                (records['text'] == 's' and unaccented_char_before == "T")):
            return True

        return not (unaccented_char_before.isalpha() or unaccented_char_after.isalpha())

    def remove_punc(self, str):
        punctuations = string.punctuation
        no_punct = ""
        for char in str:
            if char not in punctuations:
                no_punct = no_punct + char
            else:
                no_punct = no_punct + " "
        return no_punct

    def checking_new_section_added(self):
        nvariables = self.new_variables.keys()
        statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", self.set)

        check_csv = open(os.path.join(statical_analysis_dir, "Set_" + self.set + "-Suspicious_new_section.csv"), "w")
        check_writer = csv.writer(check_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        check_span_csv = open(os.path.join(statical_analysis_dir, "Set_" + self.set + "-Suspicious_strange_spans.csv"),
                              "w")
        check_span_writer = csv.writer(check_span_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        check_etilogia_csv = open(
            os.path.join(statical_analysis_dir, "Set_" + self.set + "-checking_etilogia_variables.csv"), "w")
        check_etilogia_writer = csv.writer(check_etilogia_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        check_fre_etilogia_csv = open(
            os.path.join(statical_analysis_dir, "Set_" + self.set + "-checking_freq_etilogia_variables.csv"), "w")
        check_fre_etilogia_writer = csv.writer(check_fre_etilogia_csv, delimiter='\t', quotechar='"',
                                               quoting=csv.QUOTE_MINIMAL)

        etilogia_list = ["a estudio", "aneurisma", "angiopatía amiloide", "ateromatosis", "aterosclerótico",
                         "Aterotrombótico", "Cardioembólico", "Cavernoma de circunvolución", "Criptogènic",
                         "criptogénico", "Disecció", "embòlic", "embólico", "ESUS", "Hipertensiva", "Indeterminado",
                         "indeterminada", "Indeterminado de causa doble",
                         "Indeterminado por estudio incompleto", "infrecuente", "Inhabitual",
                         "Lacunar", "malformación arteriovenosa", "mecanisme embòlic",
                         "secundaria a malformación vascular", "secundaria a tumor"]

        etilogia_dict = dict()
        for dir, files in self.annotators_entities.items():
            for file, records in files.items():
                records_not_order = self.adds_ann[dir][file] + self.changes_ann[dir][file] + self.no_changes_ann[dir][
                    file]
                records = sorted(records_not_order, key=lambda entity: entity['start'])

                if file.startswith("sonespases_973918779"):
                    check = 0

                records_seek = 0
                begin = 0
                f_txt = open(os.path.join(annotators_dir, dir, self.set, file.replace(".ann", ".txt")), "r")
                for line in f_txt:

                    if line.startswith("NIHSS 0. [3]"):
                        check = 1
                    line_size = len(line)

                    # Check if Etiligia word and the acceptable variables happens together in one line:
                    unaccented_line = unidecode.unidecode(self.remove_punc(line)).lower().split()
                    if "etiologia" in unaccented_line:
                        for etilogial in etilogia_list:
                            unaccented_etilogial = unidecode.unidecode(etilogial).lower()
                            if unaccented_etilogial in unaccented_line:
                                check_etilogia_writer.writerow([dir, file, etilogial, begin, line.strip()])

                    for etilogial in etilogia_list:
                        unaccented_etilogial = unidecode.unidecode(etilogial).lower()

                        if unaccented_etilogial in unaccented_line and "etiologia" in unaccented_line:
                            if unaccented_etilogial not in etilogia_dict.keys():
                                etilogia_dict[unaccented_etilogial] = {"with": 1, "notwith": 0}
                            else:
                                temp = etilogia_dict[unaccented_etilogial]
                                temp.update({"with": temp["with"] + 1, "notwith": temp["notwith"]})
                                etilogia_dict.update({unaccented_etilogial: temp})
                        elif unaccented_etilogial in unaccented_line and "etiologia" not in unaccented_line:
                            if unaccented_etilogial not in etilogia_dict.keys():
                                etilogia_dict[unaccented_etilogial] = {"with": 0, "notwith": 1}
                            else:
                                temp = etilogia_dict[unaccented_etilogial]
                                temp.update({"with": temp["with"], "notwith": temp["notwith"] + 1})
                                etilogia_dict.update({unaccented_etilogial: temp})
                    # Finish checking

                    while records_seek < len(records) and records[records_seek]['start'] >= begin and \
                            records[records_seek]['end'] <= begin + line_size:
                        if records[records_seek] in self.no_changes_ann[dir][file]:
                            is_correct = self.call_span_checker_accepted(begin, line, records[records_seek])
                            if not is_correct and not (records[records_seek]['label'].startswith("Fecha_") or
                                                       records[records_seek]['label'].startswith("Hora_") or
                                                       records[records_seek]['label'].startswith("Tiempo_")):
                                dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + dir + "/" + \
                                           self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + dir[
                                               0].upper() + "_" + file + "\")"
                                check_span_writer.writerow([dir_file] + [records[records_seek]['label'],
                                                                         records[records_seek]['start'],
                                                                         records[records_seek]['end']
                                    , records[records_seek]['text']] + ["Accepted"])
                        else:
                            is_correct = self.call_span_checker(begin, line, records[records_seek])
                            if not is_correct and not (records[records_seek]['label'].startswith("Fecha_") or
                                                       records[records_seek]['label'].startswith("Hora_") or
                                                       records[records_seek]['label'].startswith("Tiempo_")):
                                dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + dir + "/" + \
                                           self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + dir[
                                               0].upper() + "_" + file + "\")"
                                check_span_writer.writerow([dir_file] + [records[records_seek]['label'],
                                                                         records[records_seek]['start'],
                                                                         records[records_seek]['end']
                                    , records[records_seek]['text']])

                        records_seek += 1
                    # elif records[records_seek]['start'] < begin or records[records_seek]['end'] > begin + line_size:
                    #     print("STRANGE", dir, file, records[records_seek]['text'])

                    # if line and ((line[0].isalpha() and line[0].isupper()) or not line[0].isalpha()) \
                    #         and not line.startswith("Nº") and not line.upper().startswith("SIN"):
                    #     for variable in nvariables:
                    #         if self.new_variables.get(variable)[0].startswith("SECCION_"):
                    #             var = self.trim_name(variable).upper()
                    #             upper_line = line.upper()
                    #             if upper_line.startswith(var):
                    #                 check = True
                    #                 for ann_ent in records:
                    #                     if not (ann_ent['start'] == begin and ann_ent['label'].startswith(
                    #                             "SECCION_") and ann_ent["text"].upper().startswith(var)):
                    #                         check = False
                    #                     else:
                    #                         check = True
                    #                         break
                    #                 if not check:
                    #                     check_writer.writerow(
                    #                         [dir] + [file] + [begin] + [variable.strip()] + [line.strip()])
                    #                     break
                    begin += line_size
                f_txt.close()

        for keys, value in etilogia_dict.items():
            check_fre_etilogia_writer.writerow([keys, value])

        check_csv.close()
        check_span_csv.close()
        check_etilogia_csv.close()
        check_fre_etilogia_csv.close()

    def save_acceptance_rate(self):
        ordered_acceptance_rate = OrderedDict(sorted(self.acceptance_rate.items(), key=lambda t: t[0]))

        statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", self.set)
        os.makedirs(statical_analysis_dir, exist_ok=True)

        freq_all_csv = open(os.path.join(statical_analysis_dir, "Set_" + self.set + "-acceptance_freq_all.csv"), "w")

        freq_top_csv = open(os.path.join(statical_analysis_dir, "Set_" + self.set + "-acceptance_freq_top_low.csv"),
                            "w")

        freq_all_writer = csv.writer(freq_all_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        freq_top_writer = csv.writer(freq_top_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        removed_list = ["ASPECTS", "mRankin", "NIHSS"]
        freq_all_writer.writerow(["", "", "Accepted", "Not Accepted"])
        freq_top_writer.writerow(["", "", "Accepted", "Not Accepted", "Rate Acceptance"])
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

    def NIHH_ASPECT_RANKIN_Finder(self):

        pattern_list = ["mRankin", "NIHSS", "ASPECTS"]

        statical_analysis_dir = os.path.join(all_differences_csv_dir, "statistical", self.set)

        check_csv = open(os.path.join(statical_analysis_dir, "Set_" + self.set + "-All_NIHSS_ASPECT_NISS.csv"), "w")
        check_writer = csv.writer(check_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        need_pattern = dict()

        for dir in self.list_annotators:
            for file, records in self.annotators_entities.get(dir).items():

                for record in records:
                    if record['label'].replace("_previa", "").replace("_alta", "").replace("_hab",
                                                                                           "") in pattern_list and \
                            record['text'] not in need_pattern.keys():
                        need_pattern[record['text']] = record

        for keys, values in need_pattern.items():
            check_writer.writerow(
                [values['label'].replace("_previa", "").replace("_alta", "").replace("_hab", ""), keys])

    def merge(self, a, b, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    # works


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="comparing")
    parser.add_argument('--set', help='Which set is going to compare')
    parser.add_argument('--set_2', help='Which sets is going to compare')
    args = parser.parse_args()

    evalu = Evaluation()

    evalu.init_paths(args.set)

    evalu.annators_name()

    evalu.get_annotators_entities()  # Also save in pre_process folder
    evalu.get_ctakes_entities()
    #
    evalu.statistical_analysis()
    #
    evalu.save_acceptance_rate()
    evalu.save_analysis()
    evalu.save_new_variables_sections()

    evalu.checking_new_section_added()

    evalu.NIHH_ASPECT_RANKIN_Finder()

    if args.set_2 != None:
        checl = 0
        evalu2 = Evaluation()

        evalu2.init_paths(args.set_2)

        evalu2.annators_name()

        evalu2.get_annotators_entities()  # Also save in pre_process folder
        evalu2.get_ctakes_entities()

        evalu.merge(evalu.annotators_entities, evalu2.annotators_entities)

        evalu.distros_dict = list(set(evalu2.all_files_list).intersection(evalu.all_files_list))

    evalu.IAA()

    print("---Done---")
