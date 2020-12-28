import argparse

from src.core.const import const
from src.core.util.utility import Util
from src.core.entity.entities import Entities
from src.core.evaluation.parse import Parse
from src.core.file_writer.writer import WriterXlsx


class ParseManualAnnotations:

    def __init__(self):
        self.v = "0.2"
        self.list_annotators = []
        self.all_files = set()
        self.annotators_entities = dict()
        self.annotators_notes = dict()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="parsing")
    parser.add_argument('--bunch', help='First and last bunches are going to evaluate')
    parser.add_argument('--annotations', help='Root of Annotations (manual_annotations and pre_annotations)'
                                              ' & Analysis results')

    args = parser.parse_args()

    bunches = args.bunch

    if bunches is None:
        print("Please set the bunch by --bunch \n "
              "For example: --bunch 08_2020.06.22-12_2020.06.22 \n"
              "All bunches should have same suffix")
        exit()

    evalu = ParseManualAnnotations()

    annotators_dir, ctakes_dir = Util.get_ctakes_annotators_dirs(args.annotations)

    list_bunches, suffix_bunches = Util.get_all_bunches(bunches)

    for bunch in list_bunches:
        bunch = bunch + ("_" + suffix_bunches) if suffix_bunches is not None else bunch

        evalu.list_annotators = Util.annators_name(bunch, annotators_dir)

        statistical_dir = Util.get_statistical_dir(bunch)

        all_files, annotators_entities, annotators_notes = \
            Entities.get_annotators_entities(evalu.list_annotators, annotators_dir, bunch, freq=None, t_number=False)

        evalu.annotators_entities = Util.merge(evalu.annotators_entities, annotators_entities)
        evalu.all_files = evalu.all_files.union(set(all_files))

    hospital_names = Util.get_file_hospital(evalu.all_files)
    result_parse, merged_hospital = Parse.manual_annotations(evalu.annotators_entities, hospital_names)

    statistical_dir = Util.get_statistical_dir(bunches)

    hospital_names = Util.get_hospital_file(evalu.all_files)
    for hospital_name, hospital_files in hospital_names.items():
        WriterXlsx.per_hospital(merged_hospital, statistical_dir, bunches, hospital_name, hospital_files, Parse.original_snomed_type_varience_variable_dic)

    print("Done")
