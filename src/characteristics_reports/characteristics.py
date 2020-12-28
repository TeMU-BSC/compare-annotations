#! /usr/bin/python3

import argparse
import pyfreeling
import sys, os

import xlsxwriter

from src.core.util.utility import Util

## Check whether we know where to find FreeLing data files
if "FREELINGDIR" not in os.environ:
    if sys.platform == "win32" or sys.platform == "win64":
        os.environ["FREELINGDIR"] = "C:\\Program Files"
    else:
        os.environ["FREELINGDIR"] = "/usr/local"
    print("FREELINGDIR environment variable not defined, trying ", os.environ["FREELINGDIR"], file=sys.stderr)

if not os.path.exists(os.environ["FREELINGDIR"] + "/share/freeling"):
    print("Folder", os.environ["FREELINGDIR"] + "/share/freeling",
          "not found.\nPlease set FREELINGDIR environment variable to FreeLing installation directory",
          file=sys.stderr)
    sys.exit(1)

# Location of FreeLing configuration files.
DATA = os.environ["FREELINGDIR"] + "/share/freeling/"

# Init locales
pyfreeling.util_init_locale("default")

# create language detector. Used just to show it. Results are printed
# but ignored (after, it is assumed language is LANG)
la = pyfreeling.lang_ident(DATA + "common/lang_ident/ident-few.dat")

# create options set for maco analyzer. Default values are Ok, except for data files.
LANG = "es"
op = pyfreeling.maco_options(LANG)
op.set_data_files("",
                  DATA + "common/punct.dat",
                  DATA + LANG + "/dicc.src",
                  DATA + LANG + "/afixos.dat",
                  "",
                  DATA + LANG + "/locucions.dat",
                  DATA + LANG + "/np.dat",
                  DATA + LANG + "/quantities.dat",
                  DATA + LANG + "/probabilitats.dat")

# create analyzers
tk = pyfreeling.tokenizer(DATA + LANG + "/tokenizer.dat")
sp = pyfreeling.splitter(DATA + LANG + "/splitter.dat")
sid = sp.open_session()
mf = pyfreeling.maco(op)

# activate mmorpho odules to be used in next call
mf.set_active_options(False, True, True, True,  # select which among created
                      True, True, True, True,  # submodules are to be used.
                      False, False, True, True)  # default: all created submodules are used

# create tagger, sense anotator, and parsers
tg = pyfreeling.hmm_tagger(DATA + LANG + "/tagger.dat", True, 2)
sen = pyfreeling.senses(DATA + LANG + "/senses.dat")
parser = pyfreeling.chart_parser(DATA + LANG + "/chunker/grammar-chunk.dat")
dep = pyfreeling.dep_txala(DATA + LANG + "/dep_txala/dependences.dat", parser.get_start_symbol())


def distribution(hospital_files_names):
    dist_hospitals = {}
    for name, files in hospital_file_names.items():
        if name != 'all':
            dist_hospitals[name] = len(files)

    return dist_hospitals


def file_size(hospitals_files_name, dir_annotated_corpora):
    file_size_hospitals = {}
    for name, files in hospitals_files_name.items():
        d_size = {"Number of Tokens":0, "Number of Uniq tokens":0, "Number of Sentences": 0}
        d_size_min = {"Number of Tokens": sys.maxsize, "Number of Uniq tokens": sys.maxsize, "Number of Sentences": sys.maxsize}
        details_file_size_hosp = {"Minimum" : d_size_min.copy(), "Average": d_size.copy(), "Maximum":d_size.copy(), "Total":d_size.copy()}
        if name != 'all':
            for file in files:
                num_token, num_uniq_token, num_sent = parse_file(file, dir_annotated_corpora)
                details_file_size_hosp = update_file_size_hosp(num_token, num_uniq_token, num_sent, details_file_size_hosp)
            file_size_hospitals[name] = details_file_size_hosp
    return file_size_hospitals

def parse_file(file, dir_annotated_corpora):
    num_token = 0
    num_uniq_token = 0
    num_sent = 0
    token = []
    sent = []
    file_path = os.path.join(dir_annotated_corpora, file)
    file_read = open(file_path, "r")
    for f in file_read:
        token_f, sent_f = freeling_tokenizer(f)
        token += token_f
        sent += sent_f
    return len(token), len(set(token)), len(sent)

def update_file_size_hosp(n_token, n_uniq_token, n_sent, details_file_size_hosp):
    for keys in details_file_size_hosp.keys():
        if keys == "Minimum":
            for key, value in details_file_size_hosp[keys].items():
                if key == "Number of Tokens":
                    details_file_size_hosp[keys][key] = n_token if n_token < value else value
                elif key == "Number of Uniq tokens":
                    details_file_size_hosp[keys][key] = n_uniq_token if n_uniq_token < value else value
                elif key == "Number of Sentences":
                    details_file_size_hosp[keys][key] = n_sent if n_sent < value else value
        elif keys == "Maximum":
            for key, value in details_file_size_hosp[keys].items():
                if key == "Number of Tokens":
                    details_file_size_hosp[keys][key] = n_token if n_token > value else value
                elif key == "Number of Uniq tokens":
                    details_file_size_hosp[keys][key] = n_uniq_token if n_uniq_token > value else value
                elif key == "Number of Sentences":
                    details_file_size_hosp[keys][key] = n_sent if n_sent > value else value
        elif keys == "Average":
            for key, value in details_file_size_hosp[keys].items():
                details_file_size_hosp[keys][key] = value +1

        elif keys == "Total":
            for key, value in details_file_size_hosp[keys].items():
                if key == "Number of Tokens":
                    details_file_size_hosp[keys][key] = n_token + value
                elif key == "Number of Uniq tokens":
                    details_file_size_hosp[keys][key] = n_uniq_token + value
                elif key == "Number of Sentences":
                    details_file_size_hosp[keys][key] = n_sent + value



    return details_file_size_hosp





def freeling_tokenizer(lin):
    tokens = []
    sentence = []
    while (lin):

        l = tk.tokenize(lin)
        ls = sp.split(sid, l, True)

        ls = mf.analyze(ls)
        ls = tg.analyze(ls)
        ls = sen.analyze(ls)
        # ls = parser.analyze(ls)
        # ls = dep.analyze(ls)

        ## output results

        for s in ls:
            ws = s.get_words()
            sentence.append(s)
            for w in ws:
                tokens.append(w.get_form())

    # return lin.split(), lin.split(".")
    return tokens, sentence


def save_excel(output, hospital_name, info):
    statistical_information_per_hospital_xlsx = os.path.join(output, 'Set__charactersistics_report_per_hospital_' + hospital_name + '.xlsx')
    workbook_stat = xlsxwriter.Workbook(statistical_information_per_hospital_xlsx)
    worksheet_stat = workbook_stat.add_worksheet(hospital_name)
    for row, (key, value) in enumerate(info.items()):
        for col, (tok, inf) in enumerate(value.items()):
            worksheet_stat.write(row + 1, 0, key)
            worksheet_stat.write(0, col + 1, tok)
            if key == "Average":
                worksheet_stat.write(row + 1, col + 1, info['Total'][tok]/inf)
                worksheet_stat.write(7, 0, "Number Files")
                worksheet_stat.write(7, 1, inf)
            else:
                worksheet_stat.write(row + 1, col + 1, inf)
    workbook_stat.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="characteristic")
    parser.add_argument('--annotated_corpora', help='Root of Reports')
    parser.add_argument('--output', help='Path output files')

    args = parser.parse_args()
    dir_annotated_corpora = os.path.join(args.annotated_corpora)
    dir_output = os.path.join(args.output)
    list_files = Util.get_annotated_corpora(dir_annotated_corpora)

    hospital_file_names = Util.get_hospital_file(list_files)

    file_size_hospitals = file_size(hospital_file_names, dir_annotated_corpora)

    for hospital_name, info in file_size_hospitals.items():
        save_excel(dir_output, hospital_name, info)


    # clean up
    sp.close_session(sid)


