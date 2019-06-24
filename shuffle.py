import random
import os
import shutil
import sys


class Shuffler:
    LABEL_FILE = "Labels.txt"

    _original_labels = []
    _new_labels = []
    _shuffled_dir = ""
    _file_dir = ""

    def __init__(self, file_dir: str, shuffled_dir: str):
        self._file_dir = file_dir
        self._shuffled_dir = shuffled_dir

        self._read_labels()
        self._create_new_labels()
        self.move_files()

    def _read_labels(self):
        labels = []

        with open(os.path.join(self._file_dir, self.LABEL_FILE), "r") as file:
            for line in file:
                labels.append(line.strip())

        self._original_labels = labels
        self._new_labels = random.sample(labels, len(labels))

    def create_dict(self):
        label_dict = {}

        for new_label, originalLabel in zip(self._new_labels, self._original_labels):
            label_dict[originalLabel] = new_label

        return label_dict

    def _create_new_labels(self):
        with open(os.path.join(self._shuffled_dir, self.LABEL_FILE), 'w+') as file:
            for label in self._new_labels:
                file.write(label + "\n")

    def move_files(self):
        dir_name = 0

        for label in self._original_labels:
            print("move " + str(dir_name) + "to " + str(self._new_labels.index(label)))
            shutil.move(os.path.join(self._file_dir, str(dir_name)),
                        os.path.join(self._shuffled_dir, str(self._new_labels.index(label))))
            dir_name += 1


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        Shuffler(sys.argv[1], sys.argv[2])
    else:
        exit("Should have 2 arguments! Origin dir and output dir")
