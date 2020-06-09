import argparse
from src.core.entity.entities import Entities
from src.core.evaluation.iaa import IAA
from src.core.file_writer.writer import WriterCSV, WritterXlsx
from src.core.util.utility import Util
from src.core.evaluation.frequency import FreqCalculator
from src.core.evaluation.comparison import Comparison


class Eval(object):

    # def __init__(self):
    #
    #     self.headers_name_dic = dict()
    #     self.headers_type_dic = dict()
    #
    #     self.variables_name_dic = dict()
    #
    #     self.list_annotators = []
    #
    #     self.set = None
    #
    #     self.acceptance_rate = dict()
    #
    #     self.adds_ann = None
    #     self.changes_ann = None
    #     self.no_changes_ann = None
    #     self.removes_ann = None
    #     self.new_variables = None
    #
    #     self.all_files_list = []
    #
    #     self.annotators_entities = None
    #     self.annotators_notes = None
    #     self.ctakes_entities = None
    #
    #     self.shared_ann_files = None
    #
    #     # self.data_dir = os.path.join(self.parentDir, "data")
    #     self.distros_dict = []
    #     self.removed_punc_counter = dict()
    #     self.removed_punc = dict()



    def IAA(self, adds_ann, changes_ann, annotators_entities, distros_dict, IAA_CSV_dir, save_statistical_dir, annotators_notes, bunch, bunch_2):

        # But for Bunch 5, because there are some doubt about the output of the annotators, we are going to shift bunch 3
        # (Give files related to first annotators to the second one and ...) and re-annotation all of them to have a better IAA.
        # For dublicated files in bunch 3, we are deleting them in bunch 5 and replace them with 8 new files and dublicated in annotatos' direcotry. (We should keep the list of dublicated file).
        # Because Bunch 3 we will use headers from bunch 4 + (DIAG. + PROC.).

        # We should correct bunch 3 with the correct variables in header dictionary 5 For having correct IAA

        # Header List in bunch 2 and 1 has been changed. for IAA bunch 2 and 6 we should fix section of bunch 2 with the correct one.

        shared_ann_files, shared_ann_files_dic = IAA.IAA_ANN(annotators_entities, distros_dict)
        WriterCSV.IAA_CSV_BRRAT(annotators_dir, shared_ann_files, IAA_CSV_dir, save_statistical_dir, bunch, bunch_2)
        WriterCSV.IAA_Score_mismatched(adds_ann, changes_ann, save_statistical_dir, shared_ann_files, annotators_entities, annotators_notes, bunch)

        return shared_ann_files_dic


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="comparing")
    parser.add_argument('--bunch', help='Which set is going to src')
    parser.add_argument('--bunch_2', help='Which sets is going to src')
    args = parser.parse_args()
    bunch = args.bunch
    bunch_2 = args.bunch_2

    if bunch is None:
        print("Please set the bunch by --bunch arg \n For example: --bunch 08_2020.06.22")
        exit()

    evalu = Eval()

    annotators_dir, ctakes_dir = Util.get_ctakes_annotators_dirs()
    IAA_CSV_dir = Util.get_IAA_dirs(bunch)
    statistical_dir = Util.get_statistical_dir(bunch)

    evalu.distros_dict = Util.get_shared_reports(bunch)

    evalu.list_annotators = Util.annators_name(bunch, annotators_dir)

    freq = FreqCalculator()

    evalu.all_files_list, evalu.annotators_entities, evalu.annotators_notes = \
        Entities.get_annotators_entities(evalu.list_annotators, annotators_dir, bunch, freq=freq, t_number=True)

    WriterCSV.pre_process(evalu.annotators_entities, Util.pre_processing_dir, bunch)

    evalu.ctakes_entities = Entities.get_ctakes_entities(evalu.list_annotators, ctakes_dir, bunch, True)

    header_file, varibale_file = Util.get_header_variable_files(bunch)

    headers_name_dic, headers_type_dic = Util.headers_dic(header_file)
    variables_name_dic = Util.variable_dic(varibale_file)

    evalu.adds_ann, evalu.changes_ann, evalu.no_changes_ann, evalu.removes_ann, evalu.new_variables = \
        Comparison.changed_annotations_by_annotators\
        (evalu.ctakes_entities, evalu.annotators_entities, headers_name_dic, bunch, freq=freq)

    WriterCSV.freq_acceptance_rate(statistical_dir, bunch, freq)

    stat = WriterCSV.changed_annotations_per_file(
        evalu.adds_ann, evalu.changes_ann, evalu.no_changes_ann,
        evalu.removes_ann, bunch, Util.all_differences_csv_dir)
    WriterCSV.overal_statistical(statistical_dir, bunch, stat)


    WriterCSV.new_variables_sections(statistical_dir, headers_name_dic, headers_type_dic,
                               variables_name_dic, evalu.new_variables, bunch)

    WriterCSV.checking_variables_depended_on_text(evalu.annotators_entities, evalu.adds_ann, evalu.changes_ann,
                                                  evalu.no_changes_ann, evalu.new_variables, annotators_dir,
                                                  statistical_dir, bunch)

    WriterCSV.nihss_aspect_rankin(evalu.annotators_entities, statistical_dir, bunch)

    if bunch_2 is not None:
        check = 0
        evalu2 = Eval()

        evalu2.distros_dict = Util.get_shared_reports(bunch)

        evalu2.list_annotators = Util.annators_name(bunch, annotators_dir)

        evalu2.all_files_list, evalu2.annotators_entities, evalu2.annotators_notes = \
            Entities.get_annotators_entities(evalu2.list_annotators, annotators_dir, bunch, freq=freq, t_number=True)

        evalu2.ctakes_entities = Entities.get_ctakes_entities(evalu2.list_annotators, ctakes_dir, bunch, True)

        evalu2.adds_ann, evalu2.changes_ann, evalu2.no_changes_ann, evalu2.removes_ann, evalu2.new_variables = \
            Comparison.changed_annotations_by_annotators(
                evalu2.ctakes_entities, evalu2.annotators_entities, headers_name_dic, bunch, freq=freq)

        Util.merge(evalu.annotators_entities, evalu2.annotators_entities)
        Util.merge(evalu.adds_ann, evalu2.adds_ann)
        Util.merge(evalu.changes_ann, evalu2.changes_ann)

        distros_dict = list(set(evalu2.all_files_list).intersection(evalu.all_files_list))
        evalu.distros_dict = distros_dict

        new_bunch = bunch + "-with-" + bunch_2
        IAA_CSV_dir = Util.get_IAA_dirs(new_bunch)
        statistical_dir = Util.get_statistical_dir(new_bunch)

    shared_ann_files_dic = evalu.IAA(evalu.adds_ann, evalu.changes_ann, evalu.annotators_entities, evalu.distros_dict,
                                     IAA_CSV_dir, statistical_dir, evalu.annotators_notes, bunch, bunch_2)

    WritterXlsx.suspecions_labels(shared_ann_files_dic, statistical_dir, annotators_dir, bunch)

    print("---Done---")
