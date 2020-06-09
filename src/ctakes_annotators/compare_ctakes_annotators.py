import argparse

from src.core.util.utility import Util
from src.core.entity.entities import Entities
from src.core.evaluation.comparison import Comparison
from src.core.file_writer.writer import WritterXlsx


class EvaluationPreAnnotations:

    def __init__(self):
        self.v = "0.1"
        self.list_annotators = []
        self.all_files = None
        self.annotators_entities = None
        self.annotators_notes = None
        self.ctakes_entities = None




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="comparing")
    parser.add_argument('--bunch', help='Which bunch is going to src')
    parser.add_argument('--variable_type', choices=["DIAGNOSTICOS", "PROCEDIMIENTOS", "TRATAMIENTOS", "ESCALAS"],
                        help='Which variable type needs to src')

    args = parser.parse_args()


    bunch = args.bunch
    variable_type = args.variable_type


    if bunch is None or variable_type is None:
        print("Please set the bunch by --bunch or variable type by --variable_type \n "
              "For example: --bunch 08_2020.06.22 --variable_type DIAGNOSTICOS")
        exit()

    evalu = EvaluationPreAnnotations()

    annotators_dir, ctakes_dir = Util.get_ctakes_annotators_dirs()

    evalu.list_annotators = Util.annators_name(bunch, annotators_dir)
    statistical_dir = Util.get_statistical_dir(bunch)

    evalu.all_files, evalu.annotators_entities, evalu.annotators_notes = \
        Entities.get_annotators_entities(evalu.list_annotators, annotators_dir, bunch, freq=None, t_number=False)

    evalu.ctakes_entities = Entities.get_ctakes_entities(evalu.list_annotators, ctakes_dir, bunch, t_number=False)

    result_evaluation = Comparison.ctakes_annotators_per_type(
        evalu.ctakes_entities, evalu.annotators_entities, variable_type)

    WritterXlsx.ctakes_annotatots(result_evaluation, statistical_dir, bunch, variable_type)


    print("Done")
