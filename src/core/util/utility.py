import itertools
import os
import json
import string
from unidecode import unidecode
import src.core.const.const as const
from src.core.entity.entities import Entities
from pathlib import Path
import difflib


class Util:

    file_dir = Path(__file__).parent.parent.parent
    parentDir = os.path.dirname(file_dir)
    data_dir = os.path.join(parentDir, "data")

    main_dir = os.path.join(parentDir, "annotations")
    annotators_dir = os.path.join(main_dir, "manual_annotations")
    pre_processing_dir = os.path.join(main_dir, "pre_processing")
    ctakes_dir = os.path.join(main_dir, "pre_annotations")

    analysis_dir = os.path.join(parentDir, "analysis")
    all_differences_csv_dir = os.path.join(analysis_dir, "analysis_per_file")

    os.makedirs(pre_processing_dir, exist_ok=True)



    @staticmethod
    def similarity_diff(candidate_name, line):
        """
        :param line: input line
        :return:
            The most similarity defined section with the given line
        """

        list_similarities = difflib.get_close_matches(line, candidate_name.keys(), 1, 0.85)
        if len(list_similarities) > 0:
            return candidate_name.get(list_similarities[0]), True
        else:
            return "", False

    @staticmethod
    def get_annotated_corpora(dir_annotated_corpora):
        list_files = []
        for reports in os.listdir(dir_annotated_corpora):
            if reports.endswith(".txt") and not reports.startswith("sonespases"):
                list_files.append(reports)
        return list_files

    @staticmethod
    def similarity_words(candidate_name, line):
        """
        :param line: input line
        :return:
            The most similarity defined section with the given line
        """

        list_similarities = difflib.get_close_matches(line, candidate_name, 1, 0.70)
        if len(list_similarities) > 0:
            return list_similarities[0], True
        else:
            return "", False

    @staticmethod
    def reading_duplicated_files(bunch, data_dir):
        loaded_json = os.path.join(data_dir, "Duplicated_files.txt")

        with open(loaded_json, 'r') as f:
            distros_dict = json.load(f)
        if bunch.split("_")[0] not in distros_dict.keys():
            return []
        else:
            return distros_dict.get(bunch.split("_")[0])

    @staticmethod
    def get_IAA_dirs(bunch):
        IAA_CSV_dir = os.path.join(Util.analysis_dir, "IAA", "CSV", bunch)

        os.makedirs(IAA_CSV_dir, exist_ok=True)

        return IAA_CSV_dir

    @staticmethod
    def get_all_bunches(bunch):
        bunches = bunch.split("-")
        list_bunches = []
        suffix = bunches[0].split("_")[-1] if len(bunches[0].split("_")) > 1 else None
        for bnch in range(int(bunches[0].split("_")[0]), int(bunches[1].split("_")[0])+1):
            list_bunches.append(str(bnch) if bnch >=10 else "0" + str(bnch))

        return list_bunches, suffix

    @staticmethod
    def archetype_finder(label):
        if label.startswith("Fecha"):
            return "FECHA"
        elif label.startswith("Hora"):
            return "HORA"
        elif label.startswith("Tiempo"):
            return "TIEMPO"
        elif not label.startswith("SECCION_"):
            return label
        # for type in const.ALL_TYPES:
        #     type_list = const.get_const(type)
        #     if label in type_list:
        #         return type

    @staticmethod
    def get_file_hospital(all_files):
        hospital_dic = {}
        relacio_codis_dic = Util.get_marata_hospitals()
        for file in all_files:
            if file.startswith("sonespases_"):
                hospital_dic[file] = "sonespases"  # = Util.update_dic(hospital_dic, file, "sonespases")
            else:
                #hospital_dic[file] = "aquas"  #Util.update_dic(hospital_dic, file, "aquas")
                file_name = file.split(".")[0]
                if file_name in relacio_codis_dic.keys():
                    hospital_dic[file] =  relacio_codis_dic[file_name]  #= Util.update_dic(hospital_dic, file, relacio_codis_dic[file_name])

        return hospital_dic

    @staticmethod
    def get_marata_hospitals():
        relacio_codis = os.path.join(Util.data_dir, "excel_ID_stpau_mutua_mar.csv")
        relacio_codis_files = open(relacio_codis, "r+")
        relacio_codis_dic = dict()
        for f in relacio_codis_files:
            file_code = f.strip().split(",")
            relacio_codis_dic[file_code[0]] = file_code[1]
        return relacio_codis_dic

    @staticmethod
    def printPatternUtil(extended_var, string, buff, i, j, n):

        if i == n:
            #buff[j] = '&# 092;&# 048;'
            extended_var.append("".join(buff[:j]))
            return

        # Either put the character
        buff[j] = string[i]
        Util.printPatternUtil(extended_var, string, buff, i + 1,
                         j + 1, n)

        # Or put a space followed by next character
        buff[j] = ' '
        buff[j + 1] = string[i]

        Util.printPatternUtil(extended_var, string, buff, i + 1,
                         j + 2, n)

    # This function creates buf[] to
    # store individual output string
    # and uses printPatternUtil() to
    # print all permutations.
    @staticmethod
    def printPattern(string):
        extended_var = []
        splited_string = string.split(" ")
        n = len(splited_string)

        # Buffer to hold the string
        # containing spaces

        # 2n - 1 characters and 1 string terminator
        buff = [0] * (2 * n)

        # Copy the first character as it is,
        # since it will be always
        # at first position
        buff[0] = splited_string[0]

        Util.printPatternUtil(extended_var, splited_string, buff, 1, 1, n)
        return extended_var

    @staticmethod
    def extend_varience(varience):

        extended_var = Util.printPattern(varience)
        return extended_var

    @staticmethod
    def get_type_variable_varience_original():
        snomed = os.path.join(Util.data_dir, "SNOMNED_DIC.csv")
        snomed_dic = open(snomed, "r+")
        snomed_type_variable_varience_dic = dict()
        snomed_type_varience_variable_dic = dict()

        for f in snomed_dic:
            file_code = f.strip().split("|")
            file_code[1] = file_code[1].split("_SUG_")[-1]
            file_code[2] = unidecode(file_code[2]).lower()
            file_code[3] = unidecode(file_code[3]).lower() if len(file_code[3]) != 1 else unidecode(file_code[3])


            if file_code[1]not in snomed_type_variable_varience_dic.keys():
                snomed_type_variable_varience_dic[file_code[1]] = {file_code[2]: [file_code[3]]}
                snomed_type_varience_variable_dic[file_code[1]] = {file_code[3]: file_code[2]}
            else:
                type_variance = snomed_type_varience_variable_dic[file_code[1]]
                type_variance[file_code[3]] = file_code[2]
                snomed_type_varience_variable_dic.update({file_code[1]: type_variance})

                type_variable = snomed_type_variable_varience_dic[file_code[1]]
                if file_code[2] not in type_variable.keys():
                    type_variable[file_code[2]] = [file_code[3]]
                else:
                    variance = type_variable[file_code[2]]
                    variance.append(file_code[3])
                    type_variable.update({file_code[2]: variance})
                snomed_type_variable_varience_dic.update({file_code[1]:type_variable})

        header = os.path.join(Util.data_dir, "headers.txt")
        header_dic = open(header, "r+")

        for f in header_dic:
            f = "\t" +f.strip()
            file_code = f.split("\t")
            file_code[1] = file_code[2].split("_SUG_")[-1]
            file_code[2] = file_code[2].split("_SUG_")[-1]
            file_code[3] = unidecode(file_code[3]).lower()

            if file_code[1] not in snomed_type_variable_varience_dic.keys():
                snomed_type_variable_varience_dic[file_code[1]] = {file_code[2]: [file_code[3]]}
                snomed_type_varience_variable_dic[file_code[1]] = {file_code[3]: file_code[2]}
            else:
                type_variance = snomed_type_varience_variable_dic[file_code[1]]
                type_variance[file_code[3]] = file_code[2]
                snomed_type_varience_variable_dic.update({file_code[1]: type_variance})

                type_variable = snomed_type_variable_varience_dic[file_code[1]]
                if file_code[2] not in type_variable.keys():
                    type_variable[file_code[2]] = [file_code[3]]
                else:
                    variance = type_variable[file_code[2]]
                    variance.append(file_code[3])
                    type_variable.update({file_code[2]: variance})
                snomed_type_variable_varience_dic.update({file_code[1]: type_variable})

            #
            #
            # snomed_type_variable_varience_dic[file_code[1].split("_SUG_")[-1] + "#" + file_code[2]] = file_code[3]
            # if file_code[3] not in snomed_type_varience_variable_dic.keys():
            #     snomed_type_varience_variable_dic[file_code[3]] = [file_code[1].split("_SUG_")[-1] + "#" + file_code[2]]
            # else:
            #     temp = snomed_type_varience_variable_dic[file_code[3]]
            #     temp.append(file_code[1].split("_SUG_")[-1] + "#" + file_code[2])
            #     snomed_type_varience_variable_dic.update({file_code[3]:temp})
        return snomed_type_variable_varience_dic, snomed_type_varience_variable_dic

    @staticmethod
    def get_type_variable_varience():
        snomed = os.path.join(Util.data_dir, "SNOMNED_DIC.csv")
        snomed_dic = open(snomed, "r+")
        snomed_type_variable_varience_dic = dict()
        snomed_type_varience_variable_dic = dict()

        for f in snomed_dic:
            file_code = f.strip().split("|")
            file_code[1] = file_code[1].split("_SUG_")[-1]
            file_code[2] = unidecode(file_code[2]).lower()
            file_code[3] = unidecode(file_code[3]).lower()

            variance = Util.extend_varience(file_code[3])
            for var in variance:
                file_code[3] = var
                if file_code[1]not in snomed_type_variable_varience_dic.keys():
                    snomed_type_variable_varience_dic[file_code[1]] = {file_code[2]: [file_code[3]]}
                    snomed_type_varience_variable_dic[file_code[1]] = {file_code[3]: file_code[2]}
                else:
                    type_variance = snomed_type_varience_variable_dic[file_code[1]]
                    type_variance[file_code[3]] = file_code[2]
                    snomed_type_varience_variable_dic.update({file_code[1]: type_variance})

                    type_variable = snomed_type_variable_varience_dic[file_code[1]]
                    if file_code[2] not in type_variable.keys():
                        type_variable[file_code[2]] = [file_code[3]]
                    else:
                        variance = type_variable[file_code[2]]
                        variance.append(file_code[3])
                        type_variable.update({file_code[2]: variance})
                    snomed_type_variable_varience_dic.update({file_code[1]:type_variable})


            #
            #
            # snomed_type_variable_varience_dic[file_code[1].split("_SUG_")[-1] + "#" + file_code[2]] = file_code[3]
            # if file_code[3] not in snomed_type_varience_variable_dic.keys():
            #     snomed_type_varience_variable_dic[file_code[3]] = [file_code[1].split("_SUG_")[-1] + "#" + file_code[2]]
            # else:
            #     temp = snomed_type_varience_variable_dic[file_code[3]]
            #     temp.append(file_code[1].split("_SUG_")[-1] + "#" + file_code[2])
            #     snomed_type_varience_variable_dic.update({file_code[3]:temp})
        return snomed_type_variable_varience_dic, snomed_type_varience_variable_dic

    @staticmethod
    def get_hospital_file(all_files):
        hospital_dic = {}
        relacio_codis_dic = Util.get_marata_hospitals()
        for file in all_files:
            hospital_dic = Util.update_dic(hospital_dic, file, "all")
            if file.startswith("sonespases_"):
                hospital_dic = Util.update_dic(hospital_dic, file, "sonespases")
            else:
                hospital_dic = Util.update_dic(hospital_dic, file, "aquas")
                file_name = file.split(".")[0]
                if file_name in relacio_codis_dic.keys():
                    hospital_dic = Util.update_dic(hospital_dic, file, relacio_codis_dic[file_name])

        return hospital_dic

    @staticmethod
    def update_dic(hospital_dic, file, hospital):
        if hospital not in hospital_dic.keys():
            hospital_dic[hospital] = [file]
        else:
            temp = hospital_dic[hospital]
            temp.append(file)
            hospital_dic.update({hospital:temp})
        return hospital_dic

    @staticmethod
    def get_statistical_dir(bunch):
        statistical_dir = os.path.join(Util.analysis_dir, "statistical", bunch)
        os.makedirs(statistical_dir, exist_ok=True)
        return statistical_dir

    @staticmethod
    def get_ctakes_annotators_dirs(parent_dir):
        if parent_dir is not None:
            Util.main_dir = os.path.join(parent_dir, "annotations")
            Util.annotators_dir = os.path.join(Util.main_dir, "manual_annotations")
            Util.pre_processing_dir = os.path.join(Util.main_dir, "pre_processing")
            Util.ctakes_dir = os.path.join(Util.main_dir, "pre_annotations")

            Util.analysis_dir = os.path.join(parent_dir, "analysis")
            Util.all_differences_csv_dir = os.path.join(Util.analysis_dir, "analysis_per_file")

            os.makedirs(Util.pre_processing_dir, exist_ok=True)
        return Util.annotators_dir, Util.ctakes_dir

    @staticmethod
    def annators_name(bunch, annotators_dir):

        list_annotators = []
        annotators_path = os.path.join(annotators_dir, bunch)
        for sub_dir in os.listdir(annotators_path):
            if not sub_dir.startswith('.'):
                list_annotators.append(sub_dir)

        return list_annotators


    @staticmethod
    def get_shared_reports(bunch):
        data_dir = os.path.join(Util.parentDir, "data")
        return Util.reading_duplicated_files(bunch, data_dir)


    @staticmethod
    def get_header_variable_files(bunch):
        """ For comparing how annotators change annotated variables by ctakes for each bunch how change everything
        we should take into account
        the dictionary that cTAKES pipeline (pre_annotation and Header_detection) used.

        """
        variable_dir = "/Users/siamak/Downloads/SpaCTeS_light/ctakes-SpaCTeS-res/src/main/resources/org/apache/ctakes/examples/dictionary/lookup/fuzzy"
        header_dir = "../EHR-HeaderDetector/data/"

        variable_file = header_file = ""

        if int(bunch.split("_")[0]) <= 2:
            header_file = os.path.join(Util.parentDir, header_dir, "headers_original_bunch_1-2.txt")
            variable_file = os.path.join(variable_dir, "IctusnetDict_original_bunch_1-2.bsv")
        elif int(bunch.split("_")[0]) == 3:
            header_file = os.path.join(Util.parentDir, header_dir, "headers_13.11.2019_bunch_3.txt")
            # Because Variable Dictionary for Bunch 3 filled by mistake.
            header_file = os.path.join(Util.parentDir, header_dir, "headers_28.11.2019_bunch_4.txt")
            variable_file = os.path.join(variable_dir, "IctusnetDict_28.11.2019_bunch_4.bsv")
        elif int(bunch.split("_")[0]) == 4:
            header_file = os.path.join(Util.parentDir, header_dir, "headers_28.11.2019_bunch_4.txt")
            variable_file = os.path.join(variable_dir, "IctusnetDict_28.11.2019_bunch_4.bsv")
        elif int(bunch.split("_")[0]) == 5:
            header_file = os.path.join(Util.parentDir, header_dir, "headers_17.12.2019_bunch_5.txt")
            variable_file = os.path.join(variable_dir, "IctusnetDict_28.11.2019_bunch_5.bsv")
        elif int(bunch.split("_")[0]) == 6:
            header_file = os.path.join(Util.parentDir, header_dir, "headers_11.01.2020_bunch_6.txt")
            variable_file = os.path.join(variable_dir, "IctusnetDict_24.01.2020_bunch_6.bsv")
        elif int(bunch.split("_")[0]) == 7:
            header_file = os.path.join(Util.parentDir, header_dir,  "headers.txt")
            variable_file = os.path.join(variable_dir, "IctusnetDict.bsv")
        elif int(bunch.split("_")[0]) == 8:
            header_file = os.path.join(Util.parentDir, header_dir, "headers.txt")
            variable_file = os.path.join(variable_dir, "IctusnetDict.bsv")

        if not os.path.isfile(header_file):
            header_file = os.path.join(Util.parentDir, 'data', 'headers.txt')

        if not os.path.isfile(variable_file):
            variable_file = os.path.join(Util.parentDir, 'data', 'IctusnetDict.bsv')

        return header_file, variable_file


    @staticmethod
    def headers_dic(header_file):

        headers_name_dic = dict()
        headers_type_dic = dict()

        with open(header_file, "r") as h:
            for line in h:
                row_header = line.strip().split("\t")
                if not row_header[2] in headers_name_dic.keys():
                    headers_name_dic[row_header[2]] = row_header[1]
                if not row_header[1] in headers_type_dic.keys():
                    headers_type_dic[row_header[1]] = row_header[0]


        return headers_name_dic, headers_type_dic

    @staticmethod
    def variable_dic(variable_file):

        variables_name_dic = dict()

        with open(variable_file, "r") as h:
            for line in h:
                row_header = line.strip().split("|")
                unaccented_string = unidecode(row_header[2]).lower()
                if not unaccented_string in variables_name_dic.keys():
                    variables_name_dic[unaccented_string] = [row_header[1]]
                else:
                    temp = variables_name_dic[unaccented_string]
                    temp.append(row_header[1])
                    variables_name_dic.update({unaccented_string: temp})

        return variables_name_dic

    @staticmethod
    def remove_punc(str):
        punctuations = string.punctuation
        no_punct = ""
        for char in str:
            if char not in punctuations:
                no_punct = no_punct + char
            else:
                no_punct = no_punct + " "
        return no_punct

    @staticmethod
    def call_span_checker_accepted(begin, line, records):

        if records['text'][0] in string.punctuation or records['text'][len(records['text']) - 1] in string.punctuation:
            return False

        if records['label'].startswith('SECCION') and len(records['text']) <= 5:
            char_before = " "
            char_after = " "

            if begin < records['start']:
                char_before = line[records['start'] - 1 - begin]

            if begin + len(line) > records['end']:
                char_after = line[records['end'] - begin]

            unaccented_char_before = unidecode(char_before)
            unaccented_char_after = unidecode(char_after)

            if unaccented_char_before == "." or unaccented_char_after == ".":
                return False
            else:
                return True
        return True

    @staticmethod
    def call_span_checker(begin, line, records):

        if records['text'][0] in string.punctuation or records['text'][len(records['text']) - 1] in string.punctuation:
            return False

        char_before = " "
        char_after = " "
        if begin < records['start']:
            char_before = line[records['start'] - 1 - begin]

        if begin + len(line) > records['end']:
            char_after = line[records['end'] - begin]

        unaccented_char_before = unidecode(char_before)
        unaccented_char_after = unidecode(char_after)

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

    @staticmethod
    def checking_fecha_hora_dependencies(checker_list):
        mistakes = []
        for suspicious in checker_list:

            if suspicious in const.FECHA_HORA_DEPENDENCIES.keys():
                temp_susp = const.FECHA_HORA_DEPENDENCIES.get(suspicious)
                for temp in temp_susp:
                    if temp in checker_list:
                        break
                    else:
                        if suspicious not in mistakes:
                            mistakes.append(suspicious)
            else:
                full_suspicious_gen = (x for x in const.FECHA_HORA_DEPENDENCIES.values() for y in x if suspicious == y)
                full_suspicious = next(full_suspicious_gen)
                temp_susp = None
                for key, value in const.FECHA_HORA_DEPENDENCIES.items():
                    if value == full_suspicious:
                        temp_susp = key
                        break
                if temp_susp is not None and temp_susp not in checker_list:
                    mistakes.append(suspicious)
                elif temp_susp is None:
                    print(suspicious)
        return mistakes



    @staticmethod
    def load_categories():

        direct_cat = dict()
        not_direct_cat = dict()

        dir_cat_file = open(os.path.join(Util.data_dir, "direct_category.csv"), "r")
        not_dir_cat_file = open(os.path.join(Util.data_dir, "not_direct_category.csv"), "r")
        for line in dir_cat_file:
            row = line.strip().split("\t")
            word = unidecode(row[2].lower())
            if row[1] not in direct_cat.keys():
                direct_cat[row[1]] = {"variabel": [word], "code": row[0]}
            else:
                temp = direct_cat[row[1]]
                temp_variable = temp["variabel"]
                temp_variable.append(word)
                temp_new = {"variabel": temp_variable, "code": temp["code"]}
                direct_cat.update({row[1]: temp_new})

        for line in not_dir_cat_file:
            row = line.strip().split("\t")
            word = unidecode(row[2].lower())
            if word not in not_direct_cat.keys():
                not_direct_cat[word] = [{"code": row[3], "label": row[1]}]
            else:
                temp = not_direct_cat[word]
                temp.append({"code": row[3], "label": row[1]})
                not_direct_cat.update({word: temp})

        return direct_cat, not_direct_cat


    @staticmethod
    def find_type_variable_label(snomed_type_varience_variable_dic, cleaned_label, text):
        if text == "carotídeo":
            check = 0
        if cleaned_label in const.SUB_TYPES:
            snomed_varience_dic = snomed_type_varience_variable_dic[cleaned_label]
            correct_name, result = Util.similarity_words(snomed_varience_dic.keys(), unidecode(text).lower())
            if result and correct_name in snomed_varience_dic.keys():
                candidate_label = snomed_varience_dic[correct_name]
                return cleaned_label + "#" + candidate_label
                # for label in candidate_label:
                #     if cleaned_label == label.split("#")[0]:
                #         return label
            # return "UNKNOW"
        return cleaned_label


    @staticmethod
    def code_checker(direct_cat, not_direct_cat, record):
        if record[0] in direct_cat.keys():
            return record[0]
        else:
            word, label, code, sim = Entities.find_max_similarity_cat(record, not_direct_cat)
            if code is not None:
                return label + "_" + code
            else:
                return None

    @staticmethod
    def counter_category_diagnostic(direct_cat, not_direct_cat, annotators):
        count_variabe_diagnostic = dict()
        for dir, records in annotators.items():
            unique_variabes_diagnostic = []
            for record in records:
                if record[0] in const.REQUIRED_HEADERS or record[0] in const.REQUIRED_MAIN_VARIABLES or record[
                    0] in const.REQUIRED_SECOND_VARIABLES:
                    var_diag = Util.code_checker(direct_cat, not_direct_cat, record)
                    if var_diag not in unique_variabes_diagnostic and var_diag is not None:
                        unique_variabes_diagnostic.append(var_diag)
                    if var_diag is None:
                        checkpoint = True
            for cat in unique_variabes_diagnostic:
                if cat not in count_variabe_diagnostic.keys():
                    count_variabe_diagnostic[cat] = 1
                else:
                    temp = count_variabe_diagnostic[cat]
                    temp += 1
                    count_variabe_diagnostic.update({cat: temp})

        return count_variabe_diagnostic

    @staticmethod
    def counter_variable_diag(count_cat_diag, count_variabe_diagnostic):
        for cat_diag, count_diag in count_cat_diag.items():
            if cat_diag not in count_variabe_diagnostic.keys():
                count_variabe_diagnostic[cat_diag] = count_diag
            else:
                temp = count_variabe_diagnostic[cat_diag]
                temp += count_diag
                count_variabe_diagnostic.update({cat_diag: temp})
        return count_variabe_diagnostic

    @staticmethod
    def merge(a, b, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    Util.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
            else:
                a[key] = b[key]
        return a

    @staticmethod
    def trim_name(name):
        unaccent_name = unidecode(name)
        for i, ch in enumerate(reversed(unaccent_name)):
            if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
                if i == 0:
                    return name
                else:
                    return name[:-1 * i]