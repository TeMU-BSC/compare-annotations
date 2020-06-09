class IAA:

    @staticmethod
    def IAA_ANN(annotators_entities, distros_dict):
        ann_file = dict()
        ann_file_dic = dict()

        for dir, files in annotators_entities.items():
            for file, records in files.items():
                # source = os.path.join(annotators_dir, dir, self.set, file).replace(".ann", ".txt")
                if file.replace(".ann", ".txt") in distros_dict:

                    if ann_file.get(file) is None:
                        ann_records = {}
                        ann_records_dic = {}
                    else:
                        ann_records = ann_file[file].copy()
                        ann_records_dic = ann_file_dic[file].copy()

                    # records_list = []
                    for record in records:
                        records_list = [(record["label"], record["start"], record["end"], record["text"])]
                        records_dic = [{"label": record["label"], "start": record["start"], "end": record["end"],
                                        "text": record["text"]}]
                        if dir not in ann_records.keys():
                            ann_records[dir] = records_list
                            ann_records_dic[dir] = records_dic
                        else:

                            temp = ann_records.get(dir).copy()
                            temp += records_list
                            update = {dir: temp}
                            ann_records.update(update)

                            temp = ann_records_dic.get(dir).copy()
                            temp += records_dic
                            update = {dir: temp}
                            ann_records_dic.update(update)

                    ann_file[file] = ann_records
                    ann_file_dic[file] = ann_records_dic
        shared_ann_files = ann_file
        shared_ann_files_dic = ann_file_dic

        return shared_ann_files, shared_ann_files_dic