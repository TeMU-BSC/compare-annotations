import argparse
import csv
import os
import xlsxwriter
from collections import OrderedDict
from src.annotators import compare_annotations
from src.core.util import reading_duplicated_files

fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
data_dir = os.path.join(parentDir, "data")

section_list = []
variables_list = []
fecha_hora_tiempo_list = []

hos_file = dict()
file_hos = dict()

annotators_dic = dict()





def reading_hopitals_files():
    # loaded = os.path.join(data_dir, "Codigos_Hospitales-" + Set + ".csv")
    loaded = os.path.join(data_dir, "relacio_codis_textmining_BSC.csv")
    with open(loaded) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line in csv_reader:
            file_hos[line[0]] = line[1]
            if hos_file.get(line[1]) is None:
                hos_file[line[1]] = [line[0]]
            else:
                temp_list = hos_file.get(line[1])
                temp_list.append(line[0])
                hos_file.update({line[1]: temp_list})
        csv_file.close()


def prepare_comparative(annotations, duplicated_list):
    comparative_dic = dict()
    for annotator, files in annotations.items():
        for file, entities in files.items():
            file_without_suffix = file.split(".")[0]
            file_text = file.replace(".ann", ".txt")
            if file_hos.get(file_without_suffix) is not None:
                codigos = file_hos.get(file_without_suffix)
            else:
                codigos = "Son_Espases"
            file_final = file_without_suffix + "_" + annotator[0]
            annotators_dic[annotator[0]] = annotator
            # if file_text in duplicated_list:
            #     file_final = file_without_suffix + "_" + annotator[0]
            # else:
            #     file_final = file_without_suffix

            com_file = {}
            com_entities = {}
            for entity in entities:
                if entity['label'].startswith("SECCION"):
                    if entity['label'] not in section_list:
                        section_list.append(entity['label'])
                elif entity['label'].startswith("Fecha_") or entity['label'].startswith("Hora_") or entity['label'].startswith("Tiempo_"):
                    if entity['label'] not in fecha_hora_tiempo_list:
                        fecha_hora_tiempo_list.append(entity['label'])
                else:
                    if entity['label'] not in variables_list:
                        variables_list.append(entity['label'])
                if com_entities.get(entity['label']) is None:
                    com_entities[entity['label']] = 1
                else:
                    temp_counter = com_entities.get(entity['label']) + 1
                    com_entities.update({entity['label']: temp_counter})

            if comparative_dic.get(codigos) is None:
                com_file[file_final] = com_entities
                comparative_dic[codigos] = com_file
            else:
                com_file = comparative_dic.get(codigos)
                com_file[file_final] = com_entities
                comparative_dic.update({codigos: com_file})
            # if comparative_dic.get(codigos) is None:
            #     com_file = {}
            #     com_entities = {}
            #     for entity in entities:
            #
            #         if com_entities.get(entity['label']) is None:
            #             com_entities[entity['label']] = 1
            #         else:
            #             temp_counter = com_entities.get(entity['label']) + 1
            #             com_entities.update({entity['label']: temp_counter})
            #     com_file[file_final] = com_entities
            #     comparative_dic[codigos] = com_file
            # else:
            #     com_file = comparative_dic.get(codigos)
            #     com_entities = {}
            #     for entity in entities:
            #         if com_entities.get(entity['label']) is None:
            #             com_entities[entity['label']] = 1
            #         else:
            #             temp_counter = com_entities.get(entity['label']) + 1
            #             com_entities.update({entity['label']: temp_counter})
            #     com_file[file_final] = com_entities
            #     comparative_dic.update({codigos: com_file})
    return comparative_dic

def save_comparative_marato(comparative_dic, Set):
    data_dir = os.path.join(parentDir, "Annotated/analysis/statistical", Set)
    xlsx_file = os.path.join(data_dir, "Set_" + Set+ "_Comparativa_Hospitals.xlsx")
    xlsx_absent_file = os.path.join(data_dir, "Set_" + Set+ "_Absent_seccion_hospitals.xlsx")


    workbook = xlsxwriter.Workbook(xlsx_file)
    workbook_absent = xlsxwriter.Workbook(xlsx_absent_file)
    worksheet_absent = workbook_absent.add_worksheet("Sheet")
    for i, (codigos, files) in enumerate(comparative_dic.items()):
        worksheet = workbook.add_worksheet(codigos)
        worksheet.set_column(0, 0, 36)
        worksheet.freeze_panes(1, 0)
        last_col = 0
        sorted_files= OrderedDict(sorted(files.items()))
        sum_r = [0] * (len(section_list) + len(variables_list) + len(fecha_hora_tiempo_list) + 2)
        skip_rows = []

        section_list.sort()
        variables_list.sort()
        fecha_hora_tiempo_list.sort()

        number_files = len(sorted_files)
        sum_headers = 0
        last_col_headers = 0
        for col, (file, entities) in enumerate(sorted_files.items()):

            cell_format = workbook.add_format({'bold': False})
            suffix = ""
            if not file.startswith("son"):
                suffix =  ".utf8"
            # worksheet.write_url(0, col+1, 'http://temu.bsc.es/ICTUSnet/index.xhtml#/' + annotators_dic.get(file[-1]) +
            #                     '/' + Set.split("_",1)[0] + '/' + file[0:-2] + suffix , string=file.upper())
            worksheet.write(0, col+1, file.upper(), cell_format)
            counter = 1
            sum_c = 0
            for variable in section_list:
                worksheet.write(counter, 0, variable.replace("SECCION_",""), cell_format)
                if entities.get(variable) is not None:
                    worksheet.write(counter, col + 1, entities.get(variable))
                    sum_c += entities.get(variable)
                    sum_r[counter-1] += entities.get(variable)
                else:
                    worksheet.write(counter, col + 1, "")
                counter += 1


            skip_rows.append(counter-1)
            counter += 1

            for variable in variables_list:
                worksheet.write(counter, 0, variable, cell_format)
                if entities.get(variable) is not None:
                    worksheet.write(counter, col + 1, entities.get(variable))
                    sum_c += entities.get(variable)
                    sum_r[counter-1] += entities.get(variable)
                else:
                    worksheet.write(counter, col + 1, "")
                counter += 1
            skip_rows.append(counter-1)

            counter += 1
            for variable in fecha_hora_tiempo_list:
                worksheet.write(counter, 0, variable, cell_format)
                if entities.get(variable) is not None:
                    worksheet.write(counter, col + 1, entities.get(variable))
                    sum_c += entities.get(variable)
                    sum_r[counter-1] += entities.get(variable)
                else:
                    worksheet.write(counter, col + 1, "")
                counter += 1

            worksheet.write(counter+2, col+1, sum_c)



            last_col = col
            last_col_headers = counter

            sum_headers += sum_c
        worksheet.write( last_col_headers, 0, sum_headers/number_files)

        zero_rows = []
        for counter in range(len(sum_r)):
            if counter not in skip_rows:
                if sum_r[counter] == 0:
                    zero_rows.append(section_list[counter].replace("SECCION_", ""))
                worksheet.write(counter+1, last_col + 3, sum_r[counter])

        print(len(section_list))
        worksheet_absent.write(i, 0, codigos)
        worksheet_absent.write(i, 1, len(zero_rows))
        for col, rows in enumerate(zero_rows):
            worksheet_absent.write(i, col+2, rows)

        worksheet.set_column(1, last_col+1, 11.5)
    workbook.close()
    workbook_absent.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="comparing")

    parser.add_argument('--set', help='Which set is going to src')

    args = parser.parse_args()
    duplicated_list = reading_duplicated_files(args.set, data_dir)
    reading_hopitals_files()

    evalu = compare_annotations.Comparison()
    evalu.init_paths(args.set)
    evalu.annators_name()

    evalu.get_annotators_entities()
    comparative_dic = prepare_comparative(evalu.annotators_entities, duplicated_list)

    save_comparative_marato(comparative_dic, args.set)

    print("---DONE---")
