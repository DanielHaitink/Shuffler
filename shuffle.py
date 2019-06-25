from __future__ import print_function
import math
import random
import os
import shutil
import sys
import re


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


class Shuffler:
    LABEL_FILE = "Labels.txt"
    FOLD_NAME = "fold_"

    _folds = 1
    _original_labels = []
    _new_labels = []
    _shuffled_dir = ""
    _file_dir = ""

    def __init__(self, file_dir: str, shuffled_dir: str, folds: int = 5):
        self._file_dir = file_dir
        self._shuffled_dir = shuffled_dir
        self._folds = folds

        print("Shuffling files from %s to %s, in %i folds." % (file_dir, shuffled_dir, folds))

        self._read_labels()
        self._create_new_labels()
        self._move_files()

    def _create_fold_name(self, number: int):
        return self.FOLD_NAME + str(number)

    def _read_labels(self):
        labels = []

        with open(os.path.join(self._file_dir, self.LABEL_FILE), "r") as file:
            for line in file:
                labels.append(line.strip())

        self._original_labels = labels
        self._new_labels = random.sample(labels, len(labels))

    def _create_new_labels(self):
        with open(os.path.join(self._shuffled_dir, self.LABEL_FILE), 'w+') as file:
            for label in self._new_labels:
                file.write(label + "\n")

    def _move_files(self):
        start = 0
        files_per_fold = math.ceil(len(self._original_labels) / self._folds)

        if not os.path.exists(self._file_dir):
            print("Destination directory does not exist, creating directory...")
            os.makedirs(self._file_dir)

        print("Copying files to destination dir")

        progress = ProgressBar(len(self._original_labels), fmt=ProgressBar.FULL)

        for fold in range(0, self._folds):
            for file_number in range(start, start + files_per_fold):
                if (file_number >= len(self._original_labels)):
                    return

                new_label = self._new_labels[file_number]
                old_label_index = self._original_labels.index(new_label)

                src = os.path.join(self._file_dir, str(old_label_index))
                dest = os.path.join(self._shuffled_dir, self._create_fold_name(fold), str(file_number))

                try:
                    shutil.copytree(src, dest)
                except:
                    progress.halt()
                    exit("Could not copy folder %s to %s.\nCheck if the output directory is completely empty!" % (src, dest))

                progress.current += 1
                progress()

            start = start + files_per_fold

        progress.done()


if __name__ == '__main__':
    if len(sys.argv) > 3:
        Shuffler(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) > 2:
        Shuffler(sys.argv[1], sys.argv[2])
    else:
        exit("Should have at least 2 arguments! Origin dir and output dir.\n"
             "You can give a third argument: the number of folds. This is optional")
