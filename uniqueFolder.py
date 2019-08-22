from __future__ import print_function

import math
import os
import random
import re
import shutil
import sys


class ProgressBar(object):
    # ProgressBar is created by Romuald Brunet.
    DEFAULT = 'Progress: %(bar)s %(percent)3d%%'
    FULL = '%(bar)s %(current)d/%(total)d (%(percent)3d%%) %(remaining)d to go'

    def __init__(self, total, width=40, fmt=DEFAULT, symbol='=',
                 output=sys.stderr):
        assert len(symbol) == 1

        self.total = total
        self.width = width
        self.symbol = symbol
        self.output = output
        self.fmt = re.sub(r'(?P<name>%\(.+?\))d',
                          r'\g<name>%dd' % len(str(total)), fmt)

        self.current = 0

    def __call__(self):
        percent = self.current / float(self.total)
        size = int(self.width * percent)
        remaining = self.total - self.current
        bar = '[' + self.symbol * size + ' ' * (self.width - size) + ']'

        args = {
            'total': self.total,
            'bar': bar,
            'current': self.current,
            'percent': percent * 100,
            'remaining': remaining
        }
        print('\r' + self.fmt % args, file=self.output, end='')

    def done(self):
        self.current = self.total
        self()
        print('', file=self.output)

    def halt(self):
        self()
        print('', file=self.output)

class UniqueFold:
    FOLD_NAME = "fold_"
    TEST_NAME = "test"
    TRAIN_NAME = "train"
    LABEL_FILE = "Labels.txt"

    def __init__(self, origin_dir: str, out_dir: str, labels: list, test_set: list, fold_number: int):
        self._origin_dir = origin_dir
        self._out_dir = os.path.join(out_dir, self.FOLD_NAME + str(fold_number))
        self._origin_labels = labels
        self._test_labels = test_set
        self._train_labels = self._remove_instances(labels, test_set)
        self._train_labels = random.sample(self._train_labels, len(self._train_labels))

        if not os.path.isdir(self._out_dir):
            os.makedirs(self._out_dir)

        self._create_new_labels(self._train_labels + self._test_labels, self._out_dir)
        self._create_fold()

    def _remove_instances(self, baseList: list, instanceList: list):
        newList = baseList.copy()

        for item in instanceList:
            if item in newList:
                newList.remove(item)

        return newList

    def _create_new_labels(self, labels: list, write_dir: str, start: int = 0, end: int = 0):
        if end is 0:
            end = len(labels)

        with open(os.path.join(write_dir, self.LABEL_FILE), 'w+') as file:
            for index in range(start, end):
                file.write(labels[index] + '\n')

    def _create_fold(self):
        train_path = os.path.join(self._out_dir, self.TRAIN_NAME)
        test_path = os.path.join(self._out_dir, self.TEST_NAME)

        # Move the train and test files
        self._move_files(self._train_labels, train_path)
        self._create_new_labels(self._train_labels, train_path)
        self._move_files(self._test_labels, test_path, len(self._train_labels))
        self._create_new_labels(self._test_labels, test_path)

    def _move_files(self, move_labels: list, destination: str, map_name_addition = 0):
        progress = ProgressBar(len(move_labels), fmt=ProgressBar.FULL)

        for index in range(0, len(move_labels)):
            # Get the new label and the index of the label in the original directory
            new_label = move_labels[index]
            old_label_index = self._origin_labels.index(new_label)

            # Create the origin directory for the label and the destination directory
            src_dir = os.path.join(self._origin_dir, str(old_label_index))
            dest_dir = os.path.join(destination, str(index + map_name_addition))

            # Copy the directory
            try:
                shutil.copytree(src_dir, dest_dir)
            except:
                exit("Could not copy folder %s to %s.\nCheck if the output directory is completely empty!" % (
                    src_dir, dest_dir))
                progress.halt()

            # Update progress bar
            progress.current += 1
            progress()

        progress.done()

class UniqueFolder:
    LABEL_FILE = "Labels.txt"

    _labels = []

    def __init__(self, origin_dir: str, out_dir: str, folds: int, train_part: float = 0.8):
        self._origin_dir = origin_dir

        max_folds = math.floor(1 /  (1 - train_part))

        if max_folds > folds:
            print("Number of folds with a completely unique test set cannot be higher than %d, "
                  "number of folds is set to this maximum. If you wish to change the number of folds, "
                  "please change the train/test ratio" % (max_folds))
            folds = max_folds

        self._read_labels()
        test_labels = self._create_test_sets(1 - train_part)

        for fold in range(0, folds):
            print("Creating fold " + str(fold))
            UniqueFold(origin_dir, out_dir, self._labels, test_labels[fold], fold)

    def _create_test_sets(self, test_part):
        new_labels = random.sample(self._labels, len(self._labels))
        test_labels = []

        number_of_test = math.floor(len(new_labels) * test_part)

        for fold in range(0, math.floor(1 / test_part)):
            test_labels.append(new_labels[fold * number_of_test : (fold + 1) * number_of_test])

        return test_labels

    def _read_labels(self):
        labels = []

        with open(os.path.join(self._origin_dir, self.LABEL_FILE), "r") as file:
            for line in file:
                labels.append(line.strip())

        self._labels = labels


if __name__ == '__main__':
    if len(sys.argv) > 4:
        UniqueFolder(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
    elif len(sys.argv) > 3:
        UniqueFolder(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    else:
        exit("Should have at least 3 arguments! Origin dir, output dir and number of folds.\n"
             "You can give a third argument: the training part of the data. This should be a number between 0 and 1. By default this is set to 0.8 (80%). This is optional.")
