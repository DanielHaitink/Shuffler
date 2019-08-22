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

class Fold:
    FOLD_NAME = "fold_"
    TEST_NAME = "test"
    TRAIN_NAME = "train"
    LABEL_FILE = "Labels.txt"

    def __init__(self, origin_dir: str, out_dir: str, train_part: float, fold_number: int, shuffle: bool = True):
        self._origin_dir = origin_dir
        self._out_dir = os.path.join(out_dir, self.FOLD_NAME + str(fold_number))
        self._train_part = train_part
        self._shuffle = shuffle

        assert train_part < 1

        if not os.path.isdir(self._out_dir):
            os.makedirs(self._out_dir)

        self._read_labels()
        self._create_new_labels(self._out_dir)
        self._create_fold()

    def _read_labels(self):
        labels = []

        with open(os.path.join(self._origin_dir, self.LABEL_FILE), "r") as file:
            for line in file:
                labels.append(line.strip())

        self._origin_labels = labels

        if self._shuffle:
            self._new_labels = random.sample(labels, len(labels))
        else:
            self._new_labels = labels

    def _create_new_labels(self, write_dir: str, start: int = 0, end: int = 0):
        if end is 0:
            end = len(self._new_labels)

        with open(os.path.join(write_dir, self.LABEL_FILE), 'w+') as file:
            for index in range(start, end):
                file.write(self._new_labels[index] + '\n')

    def _create_fold(self):
        label_length = len(self._new_labels)
        train_length = math.floor(label_length * self._train_part)
        train_path = os.path.join(self._out_dir, self.TRAIN_NAME)
        test_path = os.path.join(self._out_dir, self.TEST_NAME)

        # Move the train and test files
        self._move_files(0, train_length, train_path)
        self._create_new_labels(train_path, 0, train_length)
        self._move_files(train_length, label_length, test_path)
        self._create_new_labels(test_path, train_length, label_length)

    def _move_files(self, start: int, end: int, destination: str):
        progress = ProgressBar(end - start, fmt=ProgressBar.FULL)

        for index in range(start, end):
            # Get the new label and the index of the label in the original directory
            new_label = self._new_labels[index]
            old_label_index = self._origin_labels.index(new_label)

            # Create the origin directory for the label and the destination directory
            src_dir = os.path.join(self._origin_dir, str(old_label_index))
            dest_dir = os.path.join(destination, str(index))

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

class Folder:
    def __init__(self, origin_dir: str, out_dir: str, folds: int, train_part: float = 0.8):
        for fold in range(0, folds):
            print("Creating fold " + str(fold))
            Fold(origin_dir, out_dir, train_part, fold, False if fold == 0 else True)

if __name__ == '__main__':
    if len(sys.argv) > 4:
        Folder(sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]))
    elif len(sys.argv) > 3:
        Folder(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    else:
        exit("Should have at least 3 arguments! Origin dir, output dir and number of folds.\n"
             "You can give a third argument: the training part of the data. This should be a number between 0 and 1. By default this is set to 0.8 (80%). This is optional.")
