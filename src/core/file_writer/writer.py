import csv
from collections import OrderedDict
import xlsxwriter
import os
from unidecode import unidecode
import itertools
from src.core.entity.entities import Entities
from src.core.util.utility import Util
import src.core.const.const as const
import numpy as np

class WritterXlsx:

    @staticmethod
    def ctakes_annotatots(result_evaluation, statistical_dir, bunch, variabel_tyep):

        evalute_ctakes_annotators_xlsx = os.path.join(statistical_dir , 'Set_' + bunch +
                                                      '_evaluation_ctakes_annotators_' + variabel_tyep + '.xlsx')

        workbook = xlsxwriter.Workbook(evalute_ctakes_annotators_xlsx)

        for annotator, annotator_files in result_evaluation.items():
            worksheet = workbook.add_worksheet(annotator)
            row = 0

            intersection = 0
            ctakes_more = 0
            annotator_more = 0

            worksheet.write(row, 0, 'File')
            worksheet.write(row, 1, 'Label')
            worksheet.write(row, 2, 'Start')
            worksheet.write(row, 3, 'End')
            worksheet.write(row, 4, 'TEXT')
            worksheet.write(row, 6, 'Annotator')
            worksheet.write(row, 7, 'cTAKES')
            worksheet.write(row, 8, 'IAA')
            row += 1

            for annotator_file, results in annotator_files.items():
                worksheet.write(row, 0, annotator_file)

                for records in results['intersection']:
                    worksheet.write(row, 1, records['label'])
                    worksheet.write(row, 2, records['start'])
                    worksheet.write(row, 3, records['end'])
                    worksheet.write(row, 4, records['text'])
                    worksheet.write(row, 6, '1')
                    worksheet.write(row, 7, '1')

                    row += 1
                    intersection += 1

                for records in results['ctakes_more']:
                    worksheet.write(row, 1, records['label'])
                    worksheet.write(row, 2, records['start'])
                    worksheet.write(row, 3, records['end'])
                    worksheet.write(row, 4, records['text'])
                    worksheet.write(row, 6, '0')
                    worksheet.write(row, 7, '1')

                    row += 1
                    ctakes_more += 1

                for records in results['annotator_more']:
                    worksheet.write(row, 1, records['label'])
                    worksheet.write(row, 2, records['start'])
                    worksheet.write(row, 3, records['end'])
                    worksheet.write(row, 4, records['text'])
                    worksheet.write(row, 6, '1')
                    worksheet.write(row, 7, '0')

                    row += 1
                    annotator_more +=1

            denominator = (intersection + ctakes_more + annotator_more)

            if denominator == 0:
                worksheet.write(row, 8, 'ZERO')
            else:
                worksheet.write(1, 8, intersection / denominator)

        workbook.close()


    @staticmethod
    def suspecions_labels(shared_ann_files_dic, save_statistical_dir, annotators_dir, bunch):
        xlsx_suspections_label = os.path.join(save_statistical_dir,
                                              "Set_" + bunch + "_Details_of_suspections_labels.xlsx")
        workbook_suspections_label = xlsxwriter.Workbook(xlsx_suspections_label)
        sheets = {}
        sheets_counter = {}
        suspections_label = ["Localizacion", "Lateralizacion", "Arteria_afectada", "Fecha_TAC_inicial",
                             "Fecha_llegada_hospital"]
        row_keeper_label = np.zeros((1, len(suspections_label)))

        for file, annotators in shared_ann_files_dic.items():
            list_annotators = list(annotators.keys())
            list_annotators.sort()

            if file.startswith("432062870.utf8"):
                check = 0

            if len(list_annotators) == 2:

                listA = annotators[list_annotators[0]]
                listB = annotators[list_annotators[1]]

                intersection = [i for i in listA for j in listB if
                                i['start'] == j['start'] and
                                i['end'] == j['end'] and
                                i['label'] == j['label'] and
                                i['text'] == j['text']]



                second_more = list(itertools.filterfalse(lambda x: x in listA, listB))
                first_more = list(itertools.filterfalse(lambda x: x in listB, listA))

                # annotators = self.shared_ann_files.get(files)
                # i  = set(annotators[list_annotators[0]]).intersection(
                #     set(annotators[list_annotators[1]]))
                # first_more = set(annotators[list_annotators[0]]) - set(annotators[list_annotators[1]])
                # second_more = set(annotators[list_annotators[1]]) - set(annotators[list_annotators[0]])

                records = sorted(intersection, key=lambda entity: entity['start'])

                records_seek = 0
                begin = 0
                file_ = os.path.join(annotators_dir, bunch.split("-with-")[0], list_annotators[0],
                                     file.replace(".ann", ".txt"))
                if os.path.isfile(file_):
                    f_txt = open(file_, "r")
                else:
                    file_ = os.path.join(annotators_dir, bunch.split("-with-")[1], list_annotators[0],
                                         file.replace(".ann", ".txt"))
                    f_txt = open(file_, "r")

                for line in f_txt:
                    line_size = len(line)
                    if begin >= 3000:
                        checl = 9

                    while records_seek < len(records) and records[records_seek]['start'] >= begin and \
                            records[records_seek]['end'] <= begin + line_size:
                        if records[records_seek]['label'] in suspections_label:
                            # is_correct = self.call_span_checker_accepted(begin, line, records[records_seek])
                            if records[records_seek]['label'] not in sheets.keys():
                                sheets[records[records_seek]['label']] = workbook_suspections_label.add_worksheet(
                                    records[records_seek]['label'])
                                sheets_counter[records[records_seek]['label']] = 1
                            ws = sheets[records[records_seek]['label']]

                            ws.set_column(0, 0, 27)
                            ws.set_column(1, 3, 12)
                            ws.set_column(4, 4, 17)
                            ws.set_column(5, 5, 200)

                            ws.write(0, 0, "File")
                            ws.write(0, 1, "Annotator 1")
                            ws.write(0, 2, "Annotator 2")
                            ws.write(0, 3, "Label")
                            ws.write(0, 4, "Text")
                            ws.write(0, 5, "Line")

                            counter = sheets_counter[records[records_seek]['label']]

                            ws.write_url(counter, 0,
                                         'http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/.' + bunch.split("_")[0] + "/" +
                                         list_annotators[0] + '/#/.' + bunch.split("_")[0] + "/." +
                                         list_annotators[1]
                                         + "/" + file.replace(".ann", ""), string=file)
                            # ws.write(counter, 0, file)
                            # ws.write_url(counter, 1,
                            #              'http://temu.bsc.es/ICTUSnet/index.xhtml#/' + list_annotators[0] +
                            #              '/' + self.set.split("_")[0] + '/' + file.replace(".ann", ""),
                            #              string=list_annotators[0].upper())
                            # ws.write_url(counter, 2,
                            #              'http://temu.bsc.es/ICTUSnet/index.xhtml#/' + list_annotators[1] +
                            #              '/' + self.set.split("_")[0] + '/' + file.replace(".ann", ""),
                            #              string=list_annotators[1].upper())

                            ws.write(counter, 1, list_annotators[0])
                            ws.write(counter, 2, list_annotators[1])
                            # ws.write(counter, 1, dir_file_1)
                            # ws.write(counter, 2, dir_file_2)
                            cell_format = workbook_suspections_label.add_format({'bold': True, 'font_color': 'green'})
                            ws.write(counter, 3, "Agreed", cell_format)
                            ws.write(counter, 4, records[records_seek]['text'])
                            ws.write(counter, 5, line.strip())
                            sheets_counter.update({records[records_seek]['label']: counter + 1})
                        # else:
                        #     records_seek +=1
                        # if not is_correct and not (records[records_seek]['label'].startswith("Fecha_") or
                        #                            records[records_seek]['label'].startswith("Hora_") or
                        #                            records[records_seek]['label'].startswith("Tiempo_")):
                        # dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + dir + "/" + \
                        #            self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + dir[
                        #                0].upper() + "_" + file + "\")"

                        records_seek += 1
                    begin += line_size
                f_txt.close()

                # ---------------------------------

                records = sorted(first_more, key=lambda entity: entity['start'])
                second_more_ordered = sorted(second_more, key=lambda entity: entity['start'])

                records_seek = 0
                begin = 0
                # f_txt = open(os.path.join(annotators_dir, list_annotators[0], self.set.split("-with-")[0], file.replace(".ann", ".txt")),
                #              "r")

                file_ = os.path.join(annotators_dir, bunch.split("-with-")[0], list_annotators[0] ,
                                     file.replace(".ann", ".txt"))
                if os.path.isfile(file_):
                    f_txt = open(file_, "r")
                else:
                    file_ = os.path.join(annotators_dir, bunch.split("-with-")[1], list_annotators[0],
                                         file.replace(".ann", ".txt"))
                    f_txt = open(file_, "r")

                for line in f_txt:
                    line_size = len(line)
                    if begin >= 3000:
                        check = 9

                    while records_seek < len(records) and records[records_seek]['start'] >= begin and \
                            records[records_seek]['end'] <= begin + line_size:
                        if records[records_seek]['label'] in suspections_label:
                            # is_correct = self.call_span_checker_accepted(begin, line, records[records_seek])
                            if records[records_seek]['label'] not in sheets.keys():
                                sheets[records[records_seek]['label']] = workbook_suspections_label.add_worksheet(
                                    records[records_seek]['label'])
                                sheets_counter[records[records_seek]['label']] = 0
                            ws = sheets[records[records_seek]['label']]

                            # dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + list_annotators[0] + "/" + \
                            #            self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + list_annotators[
                            #                0].upper() + "_" + file + "\")"

                            ws.set_column(0, 0, 27)
                            ws.set_column(1, 3, 12)
                            ws.set_column(4, 4, 17)
                            ws.set_column(5, 5, 200)
                            counter = sheets_counter[records[records_seek]['label']]
                            # ws.write(counter, 0, file)
                            ws.write_url(counter, 0,
                                         'http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/.' + bunch.split("_")[0]+ "/" +
                                         list_annotators[0] + '/#/.' + bunch.split("_")[0] + "/" +
                                         list_annotators[1]
                                         + "/" + file.replace(".ann", ""), string=file)
                            ws.write(counter, 1, list_annotators[0])
                            # ws.write_url(counter, 1,
                            #                 'http://temu.bsc.es/ICTUSnet/index.xhtml#/' + list_annotators[0] +
                            #                 '/' + self.set.split("_")[0] + '/' + file.replace(".ann", "") , string=list_annotators[0].upper())
                            ws.write(counter, 2, "Not by " + list_annotators[1])
                            cell_format = workbook_suspections_label.add_format({'bold': True, 'font_color': 'red'})
                            ws.write(counter, 3, "Not_Agreed", cell_format)
                            ws.write(counter, 4, records[records_seek]['text'])
                            ws.write(counter, 5, line.strip())
                            sheets_counter.update({records[records_seek]['label']: counter + 1})
                        # else:
                        #     records_seek +=1
                        # if not is_correct and not (records[records_seek]['label'].startswith("Fecha_") or
                        #                            records[records_seek]['label'].startswith("Hora_") or
                        #                            records[records_seek]['label'].startswith("Tiempo_")):
                        # dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + dir + "/" + \
                        #            self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + dir[
                        #                0].upper() + "_" + file + "\")"

                        records_seek += 1
                    begin += line_size
                f_txt.close()
                # ---------------------------------

                # ---------------------------------

                records = sorted(second_more, key=lambda entity: entity['start'])

                records_seek = 0
                begin = 0
                # f_txt = open(os.path.join(annotators_dir, list_annotators[1], self.set.split("-with-")[1], file.replace(".ann", ".txt")),
                #              "r")
                #
                file_ = os.path.join(annotators_dir,  bunch.split("-with-")[0], list_annotators[1],
                                     file.replace(".ann", ".txt"))
                if os.path.isfile(file_):
                    f_txt = open(file_, "r")
                else:
                    file_ = os.path.join(annotators_dir,  bunch.split("-with-")[1], list_annotators[1],
                                         file.replace(".ann", ".txt"))
                    f_txt = open(file_, "r")

                for line in f_txt:
                    line_size = len(line)
                    if begin >= 3000:
                        checl = 9

                    while records_seek < len(records) and records[records_seek]['start'] >= begin and \
                            records[records_seek]['end'] <= begin + line_size:
                        if records[records_seek]['label'] in suspections_label:
                            # is_correct = self.call_span_checker_accepted(begin, line, records[records_seek])
                            if records[records_seek]['label'] not in sheets.keys():
                                sheets[records[records_seek]['label']] = workbook_suspections_label.add_worksheet(
                                    records[records_seek]['label'])
                                sheets_counter[records[records_seek]['label']] = 0
                            ws = sheets[records[records_seek]['label']]

                            # dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + list_annotators[1] + "/" + \
                            #            self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + list_annotators[
                            #                1].upper() + "_" + file + "\")"

                            ws.set_column(0, 0, 27)
                            ws.set_column(1, 3, 12)
                            ws.set_column(4, 4, 17)
                            ws.set_column(5, 5, 200)
                            counter = sheets_counter[records[records_seek]['label']]
                            ws.write_url(counter, 0,
                                         'http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/.' + bunch.split("_")[0] + "/" +
                                         list_annotators[0] + '/#/.' + bunch.split("_")[0] + "/" +
                                         list_annotators[1]
                                         + "/" + file.replace(".ann", ""), string=file)
                            # ws.write(counter, 0, file)
                            ws.write(counter, 1, "Not by " + list_annotators[0])
                            # ws.write_url(counter, 1,
                            #                 'http://temu.bsc.es/ICTUSnet/index.xhtml#/' + list_annotators[1] +
                            #                 '/' + self.set.split("_")[0] + '/' + file.replace(".ann", "") , string=list_annotators[1].upper())
                            ws.write(counter, 2, list_annotators[1])
                            cell_format = workbook_suspections_label.add_format({'bold': True, 'font_color': 'red'})
                            ws.write(counter, 3, "Not_Agreed", cell_format)
                            ws.write(counter, 4, records[records_seek]['text'])
                            ws.write(counter, 5, line.strip())
                            sheets_counter.update({records[records_seek]['label']: counter + 1})
                        # else:
                        #     records_seek +=1
                        # if not is_correct and not (records[records_seek]['label'].startswith("Fecha_") or
                        #                            records[records_seek]['label'].startswith("Hora_") or
                        #                            records[records_seek]['label'].startswith("Tiempo_")):
                        # dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + dir + "/" + \
                        #            self.set.split("_")[0] + "/" + file.replace(".ann", "") + "\";\"" + dir[
                        #                0].upper() + "_" + file + "\")"

                        records_seek += 1
                    begin += line_size
                f_txt.close()
                # ---------------------------------
        workbook_suspections_label.close()

        # for i, annot in enumerate(list_annotators):
        #     worksheet.write(0, i + 4, annot)
        #     worksheet_mismatch.write(0, i + 4, annot)

class WriterCSV:

    @staticmethod
    def pre_process(entities, pre_processing_dir, bunch):

        for annotator, files in entities.items():
            pre_pro = os.path.join(pre_processing_dir, bunch, annotator)
            os.makedirs(pre_pro, exist_ok=True)

            for file, records in files.items():
                w = open(os.path.join(pre_pro, file), "w")
                for record in records:
                    w.write('{}  {} {} {}    {}\n'.format(
                        record["row"], record["label"], record["start"], record["end"], record["label"]))

    @staticmethod
    def freq_acceptance_rate(statical_analysis_dir, bunch, freq):
        ordered_acceptance_rate = OrderedDict(sorted(freq.acceptance_rate.items(), key=lambda t: t[0]))


        freq_all_csv = open(os.path.join(statical_analysis_dir, "Set_" + bunch + "_acceptance_freq_all.csv"), "w")

        freq_top_csv = open(os.path.join(statical_analysis_dir, "Set_" + bunch + "_acceptance_freq_top_low.csv"),
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


    @staticmethod
    def changed_annotations_per_file(adds_ann, changes_ann, no_changes_ann, removes_ann, bunch, all_differences_csv_dir):
        stat = dict()
        all_changes = {"added": adds_ann, "changed": changes_ann, "accepted": no_changes_ann,
                       "removed": removes_ann}
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
                    analysis_dir = os.path.join(all_differences_csv_dir, bunch, dir, file.split(".ann")[0])
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
        return stat

    @staticmethod
    def overal_statistical(save_statistical_dir, bunch, stat):

        removed_punc_counter = dict()
        removed_punc = dict()

        stat_csv = open(os.path.join(save_statistical_dir, "Set_" + bunch + "_Statistical_Analysis-Set.csv"), "w")

        csv_writer = csv.writer(stat_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(
            [" "] + list(list(stat.values())[0].keys()) + ["Number of fixed varibales and sections (spans)",
                                                           "Removed punctuations"])
        for keys, values in stat.items():
            puc_counter = 0 if removed_punc_counter.get(keys) is None else removed_punc_counter.get(keys)
            puc = 0 if removed_punc.get(keys) is None else removed_punc.get(keys)
            csv_writer.writerow([keys] + list(values.values()) + [puc_counter] + [puc])

            # csv_writer.writerow("----")
            # csv_writer.writerow(["Removed punctuations"] + self.removed_punc)
            # csv_writer.writerow(["Number varibales that fixed span happend", self.removed_punc_counter])
        stat_csv.close()


    @staticmethod
    def new_variables_sections(statical_analysis_dir, headers_name_dic, headers_type_dic,
                               variables_name_dic, new_variables, bunch):
        print("Adding new added Variables by annotators that we already have in our dictionary")

        with open(os.path.join(statical_analysis_dir, "Set_" + bunch + "_NEW_VARIABLES.csv"), "w") as var_csv, \
                open(os.path.join(statical_analysis_dir, "Set_" + bunch + "_NEW_SECCION.csv"), "w") as sec_csv:
            var_writer = csv.writer(var_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            sec_writer = csv.writer(sec_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            sec_writer.writerow([])
            var_writer.writerow([" ", "Label", "Text", "File With Link to BRAT"])

            # removed_list = ["_SUG_mRankin", "_SUG_NIHSS", "_SUG_ASPECTS"]
            removed_list = []

            for keys, values in sorted(new_variables.items()):
                label_text = keys.split("|", 1)
                temp_line = " ".join(label_text[1].split())
                if temp_line == "Enoxaparina":
                    check = 0
                if label_text[0].startswith("SECCION_"):
                    if not (temp_line.upper() in headers_name_dic.keys()
                            and headers_name_dic[temp_line.upper()] == label_text[0]):
                        sec_writer.writerow(
                            [headers_type_dic.get(label_text[0])] + [label_text[0]] + [temp_line.upper()] + values)
                else:
                    unaccent_name = unidecode(temp_line).lower()
                    if not (unaccent_name in variables_name_dic.keys()
                            and label_text[0] in variables_name_dic[unaccent_name]) \
                            and label_text[0] not in removed_list:
                        var_writer.writerow([""] + [label_text[0]] + [temp_line] + values)
                    elif (unaccent_name in variables_name_dic.keys()
                          and label_text[0] in variables_name_dic[unaccent_name]) \
                            and label_text[0] not in removed_list:
                        print(temp_line, label_text[0], variables_name_dic.get(unaccent_name))

        var_csv.close()
        sec_csv.close()
        print("Finish new added Variables that we have already in our dictionary")



    @staticmethod
    def checking_variables_depended_on_text(annotators_entities, adds_ann, changes_ann, no_changes_ann,
                                            new_variables, annotators_dir, statical_analysis_dir, bunch):
        nvariables = new_variables.keys()

        # check_csv = open(os.path.join(statical_analysis_dir, "Set_" + self.set + "_Suspicious_new_section.csv"), "w")
        # check_writer = csv.writer(check_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        check_span_csv = open(os.path.join(statical_analysis_dir, "Set_" + bunch + "_Suspicious_strange_spans.csv"),
                              "w")
        check_span_writer = csv.writer(check_span_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        check_etilogia_csv = open(
            os.path.join(statical_analysis_dir, "Set_" + bunch + "_checking_etilogia_variables.csv"), "w")
        check_etilogia_writer = csv.writer(check_etilogia_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)


        check_fecha_hora_dependency_csv = open(
            os.path.join(statical_analysis_dir, "Set_" + bunch + "_checking_fecha_hora_dependency.csv"), "w")
        check_fecha_hora_dependency_writer = csv.writer(check_fecha_hora_dependency_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        check_fre_etilogia_csv = open(
            os.path.join(statical_analysis_dir, "Set_" + bunch + "_checking_freq_etilogia_variables.csv"), "w")
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


        for dir, files in annotators_entities.items():
            for file, records in files.items():

                if file not in adds_ann[dir].keys():
                    continue

                records_not_order = adds_ann[dir][file] + changes_ann[dir][file] + no_changes_ann[dir][
                    file]
                records = sorted(records_not_order, key=lambda entity: entity['start'])

                records_seek = 0
                begin = 0
                f_txt = open(os.path.join(annotators_dir, bunch, dir, file.replace(".ann", ".txt")), "r")
                for line in f_txt:

                    checker_list = []
                    line_size = len(line)

                    # Check if Etiologia word and the acceptable variables happens together in one line:
                    unaccented_line = unidecode(Util.remove_punc(line)).lower().split()
                    if "etiologia" in unaccented_line:
                        for etilogial in etilogia_list:
                            unaccented_etilogial = unidecode(etilogial).lower()
                            if unaccented_etilogial in unaccented_line:
                                check_etilogia_writer.writerow([dir, file, etilogial, begin, line.strip()])

                    for etilogial in etilogia_list:
                        unaccented_etilogial = unidecode(etilogial).lower()

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
                    # Finish checking Etiologia

                    while records_seek < len(records) and records[records_seek]['start'] >= begin and \
                            records[records_seek]['end'] <= begin + line_size:
                        if records[records_seek] in no_changes_ann[dir][file]:
                            is_correct = Util.call_span_checker_accepted(begin, line, records[records_seek])
                            if not is_correct and not (records[records_seek]['label'].startswith("Fecha_") or
                                                       records[records_seek]['label'].startswith("Hora_") or
                                                       records[records_seek]['label'].startswith("Tiempo_")):
                                dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + bunch.split("_")[0] + "/" + \
                                           dir + "/" + file.replace(".ann", "") + "\";\"" + dir[
                                               0].upper() + "_" + file + "\")"
                                check_span_writer.writerow([dir_file] + [records[records_seek]['label'],
                                                                         records[records_seek]['start'],
                                                                         records[records_seek]['end']
                                    , records[records_seek]['text']] + ["Accepted"])
                        else:
                            is_correct = Util.call_span_checker(begin, line, records[records_seek])
                            if not is_correct and not (records[records_seek]['label'].startswith("Fecha_") or
                                                       records[records_seek]['label'].startswith("Hora_") or
                                                       records[records_seek]['label'].startswith("Tiempo_")):
                                dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + bunch.split("_")[0]  + "/" + \
                                           dir+ "/" + file.replace(".ann", "") + "\";\"" + dir[
                                               0].upper() + "_" + file + "\")"
                                check_span_writer.writerow([dir_file] + [records[records_seek]['label'],
                                                                         records[records_seek]['start'],
                                                                         records[records_seek]['end']
                                    , records[records_seek]['text']])


                        if records[records_seek]['label'] in const.FECHA_HORA_DEPENDENCIES.keys() or \
                                any(records[records_seek]['label'] == y
                                    for x in const.FECHA_HORA_DEPENDENCIES.values() for y in x):
                            checker_list.append(records[records_seek]['label'])



                        records_seek += 1

                    mistake = Util.checking_fecha_hora_dependencies(checker_list)
                    for mis in mistake:
                        dir_file = "=HYPERLINK(\"http://temu.bsc.es/ICTUSnet/index.xhtml#/" + bunch.split("_")[0]  + "/" + \
                                   dir+ "/" + file.replace(".ann", "") + "\";\"" + dir[
                                       0].upper() + "_" + file + "\")"
                        check_fecha_hora_dependency_writer.writerow([dir_file] + [mis] + [line.strip()])
                    begin += line_size
                f_txt.close()

        for keys, value in etilogia_dict.items():
            check_fre_etilogia_writer.writerow([keys, value])

        # check_csv.close()
        check_span_csv.close()
        check_etilogia_csv.close()
        check_fre_etilogia_csv.close()
        check_fecha_hora_dependency_csv.close()

    @staticmethod
    def nihss_aspect_rankin(annotators_entities, statical_analysis_dir, bunch):

        pattern_list = ["mRankin", "NIHSS", "ASPECTS"]

        check_csv = open(os.path.join(statical_analysis_dir, "Set_" + bunch + "_All_NIHSS_ASPECT_NISS.csv"), "w")
        check_writer = csv.writer(check_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        need_pattern = dict()

        for dir in annotators_entities.keys():
            for file, records in annotators_entities.get(dir).items():

                for record in records:
                    if record['label'].replace("_previa", "").replace("_alta", "").replace("_hab",
                                                                                           "") in pattern_list and \
                            record['text'] not in need_pattern.keys():
                        need_pattern[record['text']] = record

        for keys, values in need_pattern.items():
            check_writer.writerow(
                [values['label'].replace("_previa", "").replace("_alta", "").replace("_hab", ""), keys])

    @staticmethod
    def IAA_CSV_BRRAT(annotators_dir, shared_ann_files, IAA_CSV_dir, save_statistical_dir, bunch, bunch_2):
        w_mis = open(os.path.join(save_statistical_dir, "Set_" + bunch + "_link_diff_files_in_Brat.txt"), "w")
        for file, annotators in shared_ann_files.items():
            w_csv = open(os.path.join(IAA_CSV_dir, file + ".csv"), "w")
            csv_writer = csv.writer(w_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            list_annotators = list(annotators.keys())
            list_annotators.sort()

            csv_writer.writerow([" "] + list_annotators)
            if len(list_annotators) == 2:
                if bunch_2 is None:
                    w_mis.write('http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/' + list_annotators[0] + "/" +
                                bunch.split("_")[0] + '/#/' + list_annotators[1] + "/" + bunch.split("_")[0]
                                + "/" + file.replace(".ann", "") + "\n")
                else:
                    if os.path.isfile(os.path.join(annotators_dir, bunch.split("-")[0], list_annotators[0], file)):
                        w_mis.write('http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/' +  list_annotators[0] + "/" +
                                    bunch.split("_")[0] + '/#/' + list_annotators[1] + "/" + bunch_2.split("_")[0]
                                    + "/" + file.replace(".ann", "") + "\n")
                    else:
                        w_mis.write('http://temu.bsc.es/ICTUSnet/diff.xhtml?diff=/' + list_annotators[0] + "/" +
                                    bunch_2.split("_")[0]  + '/#/' + list_annotators[1] + "/" + bunch.split("_")[0]
                                    + "/" + file.replace(".ann", "") + "\n")

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


    @staticmethod
    def IAA_Score_mismatched(adds_ann, changes_ann, save_statistical_dir, shared_ann_files,
                             annotators_entities, annotators_notes, bunch):
        direct_cat, not_direct_cat = Util.load_categories()

        filter_seccion = True
        filter_seccion_diag = False

        wrong_categories = dict()

        if filter_seccion_diag:
            xlsx_file_details_codemapper = os.path.join(save_statistical_dir,
                                                        "Set_" + bunch + "_Details_of_IAA_Score_CodeMapper_Diag_without_Seccion.xlsx")
            xlsx_details = os.path.join(save_statistical_dir,
                                        "Set_" + bunch + "_Details_of_IAA_Score_In_one_File_Diag_without_Seccion.xlsx")
            xlsx_mismatch = os.path.join(save_statistical_dir,
                                         "Set_" + bunch + "_All_MisMatching_Records_Diag_without_Seccion.xlsx")
            xlsx_file = os.path.join(save_statistical_dir, "Set_" + bunch + "_IAA_Score_Diag_without_Seccion.xlsx")
            xlsx_file_CodeMapper = os.path.join(save_statistical_dir,
                                                "Set_" + bunch + "_IAA_Score_CodeMapper_Diag_without_Seccion.xlsx")
        elif filter_seccion:
            xlsx_file_details_codemapper = os.path.join(save_statistical_dir,
                                                        "Set_" + bunch + "_Details_of_IAA_Score_CodeMapper_All_Annotations_Without_Seccion.xlsx")
            xlsx_details = os.path.join(save_statistical_dir,
                                        "Set_" + bunch + "_Details_of_IAA_Score_In_one_File_All_Annotations_Without_Seccion.xlsx")
            xlsx_mismatch = os.path.join(save_statistical_dir,
                                         "Set_" + bunch + "_All_MisMatching_Records_All_Annotations_Without_Seccion.xlsx")
            xlsx_file = os.path.join(save_statistical_dir,
                                     "Set_" + bunch + "_IAA_Score.xlsx_All_Annotations_Without_Seccion.xlsx")
            xlsx_file_CodeMapper = os.path.join(save_statistical_dir,
                                                "Set_" + bunch + "_IAA_Score_CodeMapper_All_Annotations_Without_Seccion.xlsx")
        else:
            xlsx_file_details_codemapper = os.path.join(save_statistical_dir,
                                                        "Set_" + bunch + "_Details_of_IAA_Score_CodeMapper.xlsx")
            xlsx_details = os.path.join(save_statistical_dir,
                                        "Set_" + bunch + "_Details_of_IAA_Score_In_one_File.xlsx")
            xlsx_mismatch = os.path.join(save_statistical_dir, "Set_" + bunch + "_All_MisMatching_Records.xlsx")
            xlsx_file = os.path.join(save_statistical_dir, "Set_" + bunch + "_IAA_Score.xlsx")
            xlsx_file_CodeMapper = os.path.join(save_statistical_dir, "Set_" + bunch + "_IAA_Score_CodeMapper.xlsx")

        workbook_details_codemapper = xlsxwriter.Workbook(xlsx_file_details_codemapper)
        workbook_details = xlsxwriter.Workbook(xlsx_details)
        worksheet_details = workbook_details.add_worksheet("General_IAA_Score")

        workbook_mismatch = xlsxwriter.Workbook(xlsx_mismatch)
        workbook = xlsxwriter.Workbook(xlsx_file)
        workbook_CodeMapper = xlsxwriter.Workbook(xlsx_file_CodeMapper)
        just_row = 1
        worksheet_details_codemapper = workbook_details_codemapper.add_worksheet(bunch)
        worksheet_details_codemapper.write(0, 0, 'File')
        worksheet_details_codemapper.write(0, 1, "CodeMapper")
        # worksheet_details_codemapper.write(0, 2, "Changed_Added")
        worksheet_details_codemapper.write(0, 2, "Original")
        worksheet_details_codemapper.write(0, 3, "Diff")
        worksheet_details_codemapper.set_column(0, 3, 30)

        # removed_variable = ["Localizacion", "Etiologia"]
        IAA_matrix_general_all = np.zeros((2, 2))
        IAA_matrix_general_changed = np.zeros((2, 2))
        count_variabe_diagnostic_diag = dict()
        count_variabe_diagnostic = dict()
        compare_annotator_IAA = dict()
        compare_annotator_IAA_codeMapper = dict()
        for file, annotators in shared_ann_files.items():
            # calculate number of new categories in Diagnostic Seccion
            # count_variabe_diagnostic = Util.counter_variable_diag(Util.counter_category_diagnostic(direct_cat, not_direct_cat, annotators), count_variabe_diagnostic)
            # annotators = self.filter_on_diagnotstic(file, annotators)
            if filter_seccion_diag:
                annotators = Entities.filter_on_diagnotstic(file, annotators)
                annotators = Entities.filter_section(annotators)
            elif filter_seccion:
                annotators = Entities.filter_section(annotators)

            # annotators = self.filter_on_diagnotstic_everywhere(annotators)
            # count_variabe_diagnostic_diag = self.counter_variable_diag(Util.counter_category_diagnostic(direct_cat, not_direct_cat, annotators), count_variabe_diagnostic_diag)

            IAA_matrix_all = np.zeros((2, 2))

            # IAA_matrix_all_filtered = np.zeros((2, 2))
            # IAA_matrix_all_CodeMapper_filtered = np.zeros((2, 2))
            IAA_matrix_all_CodeMapper = np.zeros((2, 2))
            IAA_matrix_changed = np.zeros((2, 2))

            worksheet = workbook.add_worksheet(file)
            worksheet_CodeMapper = workbook_CodeMapper.add_worksheet(file)
            worksheet_mismatch = workbook_mismatch.add_worksheet(file)

            counter = 1
            counter_mistmatch = 1
            counter_CodeMapper = 1

            worksheet.set_column(0, 0, 40)
            worksheet_mismatch.set_column(0, 0, 40)
            worksheet.set_column(3, 3, 30)
            worksheet_mismatch.set_column(3, 3, 30)
            worksheet.set_column(6, 7, 10)
            worksheet.freeze_panes(1, 0)

            # worksheet_CodeMapper.set_column(0, 0, 40)
            # worksheet_CodeMapper.set_column(3, 3, 30)
            # worksheet_CodeMapper.set_column(6, 7, 10)
            worksheet_CodeMapper.freeze_panes(1, 0)
            worksheet_mismatch.freeze_panes(1, 0)

            list_annotators = list(annotators.keys())
            list_annotators.sort()

            for i, annot in enumerate(list_annotators):
                worksheet.write(0, i + 4, annot)
                worksheet_mismatch.write(0, i + 4, annot)
                worksheet_CodeMapper.write(0, i + 10, annot)

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

            worksheet_CodeMapper.write(0, 0, "Label")
            worksheet_CodeMapper.write(0, 1, "Code")
            worksheet_CodeMapper.write(0, 2, "Start")
            worksheet_CodeMapper.write(0, 3, "End")
            worksheet_CodeMapper.write(0, 4, "Text")
            worksheet_CodeMapper.write(0, 5, "Label")
            worksheet_CodeMapper.write(0, 6, "Code")
            worksheet_CodeMapper.write(0, 7, "Start")
            worksheet_CodeMapper.write(0, 8, "End")
            worksheet_CodeMapper.write(0, 9, "Text")

            if len(list_annotators) == 2:

                intersection = set(annotators[list_annotators[0]]).intersection(
                    set(annotators[list_annotators[1]]))
                first_more = set(annotators[list_annotators[0]]) - set(annotators[list_annotators[1]])
                second_more = set(annotators[list_annotators[1]]) - set(annotators[list_annotators[0]])

                first_more_CodeMapper = first_more.copy()
                second_more_CodeMapper = second_more.copy()

                for rec in intersection:
                    rec_list = list(rec)
                    # temp_str = rec_list[0] + " " + str(rec_list[1]) + " " + str(rec_list[2]) + "\t" + rec_list[3]

                    list_ann = [1, 1]

                    IAA_matrix_all[0, 0] += 1
                    IAA_matrix_all_CodeMapper[0, 0] += 1

                    is_added = Entities.isEntityAdded(adds_ann, file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 0] += is_added

                    is_changed = Entities.isEntityChanged(changes_ann, file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 0] += is_changed

                    type = "CH_A" if is_changed + is_added > 0 else "AC"
                    status = "Agreed"
                    label = rec_list[0]
                    wrong_categories = Entities.set_wrong_category(type, status, label)

                    worksheet.write(counter, 0, rec_list[0])
                    worksheet.write(counter, 1, rec_list[1])
                    worksheet.write(counter, 2, rec_list[2])
                    worksheet.write(counter, 3, rec_list[3])
                    worksheet.write(counter, 4, list_ann[0])
                    worksheet.write(counter, 5, list_ann[1])

                    worksheet.write(counter, 6, is_changed)
                    worksheet.write(counter, 7, is_added)

                    worksheet_CodeMapper.write(counter_CodeMapper, 0, rec_list[0])

                    if rec_list[0] in direct_cat.keys():
                        code = direct_cat[rec_list[0]]["code"]
                    else:
                        _, _, code, _ = Entities.find_max_similarity_cat(rec_list, not_direct_cat)

                    worksheet_CodeMapper.write(counter_CodeMapper, 1, code)

                    worksheet_CodeMapper.write(counter_CodeMapper, 2, rec_list[1])
                    worksheet_CodeMapper.write(counter_CodeMapper, 3, rec_list[2])
                    worksheet_CodeMapper.write(counter_CodeMapper, 4, rec_list[3])

                    worksheet_CodeMapper.write(counter_CodeMapper, 10, list_ann[0])
                    worksheet_CodeMapper.write(counter_CodeMapper, 11, list_ann[1])

                    counter += 1
                    counter_CodeMapper += 1

                for rec_f in first_more:
                    max_score = -1
                    rec2 = None
                    code2 = None
                    if rec_f[0] in direct_cat.keys():
                        code1 = direct_cat[rec_f[0]]["code"]
                        for rec_s in second_more_CodeMapper:
                            if rec_s[0] in direct_cat.keys():
                                if rec_s[0] == rec_f[0]:
                                    code2 = direct_cat[rec_s[0]]["code"]
                                    rec2 = rec_s
                                    max_score = 1
                                    break
                    else:
                        word1, label1, code1, sim1 = Entities.find_max_similarity_cat(rec_f, not_direct_cat)
                        if word1 is not None:
                            for rec_s in second_more_CodeMapper:
                                word2, label2, code2, sim2 = Entities.find_max_similarity_cat(rec_s, not_direct_cat)
                                if label1 == label2 and code1 == code2 and sim2 > max_score:
                                    rec2 = rec_s
                                    max_score = sim2

                    if rec2 is not None:
                        fht = True
                        normolized_note_1 = None
                        normolized_note_2 = None
                        if rec2[0].startswith('Fecha_') or rec2[0].startswith('Hora_') or rec2[0].startswith('Tiempo_'):
                            list_notes = annotators_notes[list_annotators[0]][file]
                            normolized_note_1 = Entities.note_normolized_finder(annotators_entities, file, list_annotators[0], rec_f, list_notes)

                            list_notes = annotators_notes[list_annotators[1]][file]
                            normolized_note_2 = Entities.note_normolized_finder(annotators_entities, file, list_annotators[1], rec2, list_notes)
                            fht = False

                        if fht or (normolized_note_1 == normolized_note_2 or rec_f[3] == rec2[3]):
                            IAA_matrix_all_CodeMapper[0, 0] += 1

                            worksheet_CodeMapper.write(counter_CodeMapper, 0, rec_f[0])
                            worksheet_CodeMapper.write(counter_CodeMapper, 1, code1)
                            worksheet_CodeMapper.write(counter_CodeMapper, 2, rec_f[1])
                            worksheet_CodeMapper.write(counter_CodeMapper, 3, rec_f[2])
                            worksheet_CodeMapper.write(counter_CodeMapper, 4, rec_f[3])

                            worksheet_CodeMapper.write(counter_CodeMapper, 5, rec2[0])
                            worksheet_CodeMapper.write(counter_CodeMapper, 6, code2)
                            worksheet_CodeMapper.write(counter_CodeMapper, 7, rec2[1])
                            worksheet_CodeMapper.write(counter_CodeMapper, 8, rec2[2])
                            worksheet_CodeMapper.write(counter_CodeMapper, 9, rec2[3])

                            worksheet_CodeMapper.write(counter_CodeMapper, 10, 1)
                            worksheet_CodeMapper.write(counter_CodeMapper, 11, 1)

                            first_more_CodeMapper.remove(rec_f)
                            second_more_CodeMapper.remove(rec2)

                            counter_CodeMapper += 1

                for rec in first_more_CodeMapper:
                    rec_list = list(rec)
                    # temp_str = rec_list[0] + " " + str(rec_list[1]) + " " + str(rec_list[2]) + "\t" + rec_list[3]

                    list_ann = [1, 0]
                    IAA_matrix_all_CodeMapper[0, 1] += 1

                    worksheet_CodeMapper.write(counter_CodeMapper, 0, rec_list[0])
                    if rec_list[0] in direct_cat.keys():
                        code1 = direct_cat[rec_list[0]]["code"]
                    else:
                        _, _, code1, _ = Entities.find_max_similarity_cat(rec_list, not_direct_cat)

                    worksheet_CodeMapper.write(counter_CodeMapper, 1, code1)
                    worksheet_CodeMapper.write(counter_CodeMapper, 2, rec_list[1])
                    worksheet_CodeMapper.write(counter_CodeMapper, 3, rec_list[2])
                    worksheet_CodeMapper.write(counter_CodeMapper, 4, rec_list[3])
                    worksheet_CodeMapper.write(counter_CodeMapper, 10, list_ann[0])
                    worksheet_CodeMapper.write(counter_CodeMapper, 11, list_ann[1])

                    counter_CodeMapper += 1

                for rec in second_more_CodeMapper:
                    rec_list = list(rec)
                    # temp_str = rec_list[0] + " " + str(rec_list[1]) + " " + str(rec_list[2]) + "\t" + rec_list[3]

                    list_ann = [0, 1]
                    IAA_matrix_all_CodeMapper[1, 0] += 1

                    worksheet_CodeMapper.write(counter_CodeMapper, 5, rec_list[0])

                    if rec_list[0] in direct_cat.keys():
                        code2 = direct_cat[rec_list[0]]["code"]
                    else:
                        _, _, code2, _ = Entities.find_max_similarity_cat(rec_list, not_direct_cat)

                    worksheet_CodeMapper.write(counter_CodeMapper, 6, code2)
                    worksheet_CodeMapper.write(counter_CodeMapper, 7, rec_list[1])
                    worksheet_CodeMapper.write(counter_CodeMapper, 8, rec_list[2])
                    worksheet_CodeMapper.write(counter_CodeMapper, 9, rec_list[3])
                    worksheet_CodeMapper.write(counter_CodeMapper, 10, list_ann[0])
                    worksheet_CodeMapper.write(counter_CodeMapper, 11, list_ann[1])
                    counter_CodeMapper += 1

                for rec in first_more:
                    rec_list = list(rec)
                    # temp_str = rec_list[0] + " " + str(rec_list[1]) + " " + str(rec_list[2]) + "\t" + rec_list[3]

                    list_ann = [1, 0]
                    IAA_matrix_all[0, 1] += 1

                    is_added = Entities.isEntityAdded(adds_ann, file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 1] += is_added

                    is_changed = Entities.isEntityChanged(changes_ann, file, list_annotators[0], rec_list)
                    IAA_matrix_changed[0, 1] += is_changed

                    type = "CH_A" if is_changed + is_added > 0 else "AC"
                    status = "Not_Agreed"
                    label = rec_list[0]
                    wrong_categories = Entities.set_wrong_category(type, status, label)

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

                    is_added = Entities.isEntityAdded(adds_ann, file, list_annotators[1], rec_list)
                    IAA_matrix_changed[1, 0] += is_added

                    is_changed = Entities.isEntityChanged(changes_ann, file, list_annotators[1], rec_list)
                    IAA_matrix_changed[1, 0] += is_changed

                    type = "CH_A" if is_changed + is_added > 0 else "AC"
                    status = "Not_Agreed"
                    label = rec_list[0]
                    wrong_categories = Entities.set_wrong_category(type, status, label)

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

            worksheet_details_codemapper.write(just_row, 0, file)
            IAA_matrix_general_all += IAA_matrix_all
            IAA_matrix_general_changed += IAA_matrix_changed

            worksheet.write(0, 8, "% All")
            # K = IAA_matrix_all[0][0]
            denominator = (IAA_matrix_all[0][0] + IAA_matrix_all[0][1] + IAA_matrix_all[1][0])

            if denominator == 0:
                K = "Zero"
            else:
                K = IAA_matrix_all[0][0] / denominator

            K_original = K
            worksheet.write(0, 9, K)

            annotators_str = list_annotators[0] + "-" + list_annotators[1]
            if K != "Zero":
                if annotators_str not in compare_annotator_IAA.keys():
                    compare_annotator_IAA[annotators_str] = (K, 1)
                else:
                    temp, temp_count = compare_annotator_IAA.get(annotators_str)
                    compare_annotator_IAA.update({annotators_str: (temp + K, temp_count + 1)})

            # denominator = IAA_matrix_all_filtered[0][0] + IAA_matrix_all_filtered[0][1] + IAA_matrix_all_filtered[1][0]
            #
            # if denominator == 0:
            #     K  = "Zero"
            # else:
            #     K = IAA_matrix_all_filtered[0][0] / denominator
            # K_original = K

            worksheet_CodeMapper.write(0, 12, "% All")

            # K = IAA_matrix_all_CodeMapper[0][0]
            denominator = (IAA_matrix_all_CodeMapper[0][0] + IAA_matrix_all_CodeMapper[0][1] +
                           IAA_matrix_all_CodeMapper[1][0])

            if denominator == 0:
                K = "Zero"
            else:
                K = IAA_matrix_all_CodeMapper[0][0] / denominator

            K_CodeMapper = K

            if K != "Zero":
                if annotators_str not in compare_annotator_IAA_codeMapper.keys():
                    compare_annotator_IAA_codeMapper[annotators_str] = (K, 1)
                else:
                    temp, temp_count = compare_annotator_IAA_codeMapper.get(annotators_str)
                    compare_annotator_IAA_codeMapper.update({annotators_str: (temp + K, temp_count + 1)})
            worksheet_CodeMapper.write(0, 13, K)
            worksheet_details_codemapper.write(just_row, 1, K)

            # denominator = IAA_matrix_all_CodeMapper_filtered[0][0] + IAA_matrix_all_CodeMapper_filtered[0][1] + IAA_matrix_all_CodeMapper_filtered[1][0]
            # if denominator == 0:
            #     K  = "Zero"
            # else:
            #     K = IAA_matrix_all_CodeMapper_filtered[0][0] / denominator
            #
            # K_CodeMapper = K
            # worksheet_details_codemapper.write(just_row, 1, K)

            worksheet.set_column(10, 10, 20)

            worksheet.write(0, 10, "% Changed and added:")
            denominator = (IAA_matrix_changed[0][0] + IAA_matrix_changed[0][1] + IAA_matrix_changed[1][0])

            if denominator == 0:
                K = "No Changed and No Added"
            else:
                K = IAA_matrix_changed[0][0] / denominator

            worksheet.write(0, 11, K)
            # worksheet_details_codemapper.write(just_row, 2, K)

            worksheet_details_codemapper.write(just_row, 2, K_original)

            if K_CodeMapper is "Zero" or K_original is "Zero":
                worksheet_details_codemapper.write(just_row, 3, "Zero")
            else:
                worksheet_details_codemapper.write(just_row, 3, K_CodeMapper - K_original)

            just_row += 1

            # worksheet.set_column(6, 6, 20)

        worksheet_details.write(0, 0, "% All")
        K = IAA_matrix_general_all[0][0]
        denominator = (IAA_matrix_general_all[0][0] + IAA_matrix_general_all[0][1] + IAA_matrix_general_all[1][0])

        if denominator == 0:
            K = "No Changed and No Added"
        else:
            K = IAA_matrix_general_all[0][0] / denominator

        worksheet_details.write(0, 1, K)

        worksheet_details.set_column(2, 2, 20)

        worksheet_details.write(0, 2, "% Changed and added:")
        denominator = (
                IAA_matrix_general_changed[0][0] + IAA_matrix_general_changed[0][1] + IAA_matrix_general_changed[1][
            0])

        if denominator == 0:
            K = "No Changed and No Added"
        else:
            K = IAA_matrix_general_changed[0][0] / denominator

        worksheet_details.write(0, 3, K)

        for i, (annot, (value, value_count)) in enumerate(compare_annotator_IAA.items()):
            worksheet_details.write(i + 1, 0, annot)
            worksheet_details.write(i + 1, 1, value / value_count)
            worksheet_details.write(i + 1, 2, value_count)

        worksheet_details = workbook_details.add_worksheet("Wrong_Variables_Details")

        worksheet_details_codemapper = workbook_details_codemapper.add_worksheet("General_IAA_CodeMapper")
        for i, (annot, (value, value_count)) in enumerate(compare_annotator_IAA_codeMapper.items()):
            worksheet_details_codemapper.write(i + 1, 0, annot)
            worksheet_details_codemapper.write(i + 1, 1, value / value_count)
            worksheet_details_codemapper.write(i + 1, 2, value_count)

        count = 1
        status_agreed = "Agreed"
        status_not_agreed = "Not_Agreed"
        worksheet_details.write(0, 0, "Status of Annotation")
        worksheet_details.write(0, 1, "Label")
        worksheet_details.write(0, 2, "How many times it happened:")
        worksheet_details.write(0, 3, "How many times annotators are agree:")
        worksheet_details.write(0, 4, "How many times annotators are not agree")
        worksheet_details.write(0, 5, "Rate of agreement")
        worksheet_details.set_column(0, 0, 15)
        worksheet_details.set_column(1, 1, 40)
        worksheet_details.set_column(2, 5, 20)
        # worksheet_details.set_column(1, 4, 40)
        for i, (type, labels) in enumerate(wrong_categories.items()):
            type_details = "Accepted" if type == "AC" else "Changed_or_Added"
            worksheet_details.write(count + i, 0, type_details)
            count += 1
            for (label, status) in labels.items():
                num_status_agreed = status[status_agreed] if status.get(status_agreed) != None else 0
                num_status_not_agreed = status[status_not_agreed] if status.get(status_not_agreed) != None else 0
                worksheet_details.write(count, 1, label)
                worksheet_details.write(count, 2, num_status_agreed + num_status_not_agreed)
                worksheet_details.write(count, 3, num_status_agreed)
                worksheet_details.write(count, 4, num_status_not_agreed)
                score = None if num_status_agreed + num_status_not_agreed == 0 else (
                        num_status_agreed / (num_status_agreed + num_status_not_agreed))
                worksheet_details.write(count, 5, score)
                count += 1

        worksheet_details = workbook_details.add_worksheet("All_Wrong_Variables_Details")

        count = 1
        status_agreed = "Agreed"
        status_not_agreed = "Not_Agreed"
        worksheet_details.write(0, 0, "Status of Annotation")
        worksheet_details.write(0, 1, "Label")
        worksheet_details.write(0, 2, "How many times it happened:")
        worksheet_details.write(0, 3, "How many times annotators are agree:")
        worksheet_details.write(0, 4, "How many times annotators are not agree")
        worksheet_details.write(0, 5, "Rate of agreement")
        worksheet_details.set_column(0, 0, 15)
        worksheet_details.set_column(1, 1, 40)
        worksheet_details.set_column(2, 5, 20)
        # worksheet_details.set_column(1, 4, 40)
        all_details = dict()
        for i, (type, labels) in enumerate(wrong_categories.items()):
            type_details = "All"
            # worksheet_details.write(count + i, 0, type_details)
            count += 1
            for (label, status) in labels.items():
                if label not in all_details.keys():
                    all_details[label] = status
                else:
                    temp = all_details[label]
                    if temp.get(status_agreed) is None:
                        temp[status_agreed] = status[status_agreed] if status.get(status_agreed) is not None else 0
                    else:
                        temp[status_agreed] += status[status_agreed] if status.get(status_agreed) is not None else 0

                    if temp.get(status_not_agreed) is None:
                        temp[status_not_agreed] = status[status_not_agreed] if status.get(
                            status_not_agreed) is not None else 0
                    else:
                        temp[status_not_agreed] += status[status_not_agreed] if status.get(
                            status_not_agreed) is not None else 0
                    all_details.update({label: temp})

        for (label, status) in all_details.items():
            num_status_agreed = status[status_agreed] if status.get(status_agreed) is not None else 0
            num_status_not_agreed = status[status_not_agreed] if status.get(status_not_agreed) is not None else 0
            worksheet_details.write(count, 1, label)
            worksheet_details.write(count, 2, num_status_agreed + num_status_not_agreed)
            worksheet_details.write(count, 3, num_status_agreed)
            worksheet_details.write(count, 4, num_status_not_agreed)
            score = None if num_status_agreed + num_status_not_agreed == 0 else (
                    num_status_agreed / (num_status_agreed + num_status_not_agreed))
            worksheet_details.write(count, 5, score)
            count += 1

        worksheet_details = workbook_details.add_worksheet("Details_of_diagnostirc")

        worksheet_details.write(0, 0, "Labels_code_old")
        worksheet_details.write(0, 1, "count_old")  # In each files we count just each variables once
        worksheet_details.set_column(0, 0, 30)

        worksheet_details.write(0, 3, "Labels_code_CodeMapper")
        worksheet_details.write(0, 4, "count__CodeMapper")  # In each files we count just each variables once
        worksheet_details.set_column(3, 3, 30)

        rdered_count_variabe_diagnostic = OrderedDict(sorted(count_variabe_diagnostic.items(), key=lambda t: t[0]))
        rdered_count_variabe_diagnostic_diag = OrderedDict(
            sorted(count_variabe_diagnostic_diag.items(), key=lambda t: t[0]))
        for i, (cat, counter_diag) in enumerate(rdered_count_variabe_diagnostic.items()):
            worksheet_details.write(i + 1, 0, cat)
            worksheet_details.write(i + 1, 1, counter_diag)

        for i, (cat, counter_diag) in enumerate(rdered_count_variabe_diagnostic_diag.items()):
            worksheet_details.write(i + 1, 3, cat)
            worksheet_details.write(i + 1, 4, counter_diag)

        workbook.close()
        workbook_details_codemapper.close()
        workbook_mismatch.close()
        workbook_details.close()
        workbook_CodeMapper.close()