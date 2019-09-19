from __future__ import print_function
import argparse
import contextlib
import gc
import os
import re
import six
import sys
import time


class BaseTask(object):
    def __init__(self, name, n_in_files=1):
        self.name = name
        self._n_in_files = n_in_files

    def size(self):
        """Return human readable task size."""
        raise NotImplementedError

    def complexity(self):
        """Return expected task time complexity."""
        raise NotImplementedError

    def write_task_to_file(self, f):
        """Write task to file."""
        raise NotImplementedError

    def read_answer_from_file(self, f):
        """Read answer from file."""
        raise NotImplementedError

    def check_answer(self, answer):
        """Check answer for correctness."""
        raise NotImplementedError

    def check_input(self):
        """Check task data for validity."""
        return True

    def performance(self, duration):
        """Return human readable performance data."""
        size = self.size()
        complexity = self.complexity()
        return 'T({}) / {:.3f} = {:.3g}'.format(
            size,
            duration,
            complexity / duration
        )

    def write_task(self):
        """Write task for computation."""

        if self._n_in_files == 1:
            filenames = ['tmp/in']
        else:
            filenames = [
                'tmp/in{}'.format(i + 1) for i in range(self._n_in_files)
            ]
        files = [None] * len(filenames)

        def open_files(i):
            if i < len(files):
                with open(filenames[i], 'w') as f:
                    files[i] = f
                    open_files(i + 1)
            else:
                self.write_task_to_file(*files)

        open_files(0)

    @classmethod
    def compute_answer(cls):
        """Compute answer for task."""
        if os.system('./run') != 0:
            cls.fail('computation failure')

    def read_answer(self):
        """Read computed answer."""
        with open('tmp/out', 'r') as f:
            return self.read_answer_from_file(f)

    @staticmethod
    def elapsed_time(f):
        start = time.time()
        result = f()
        finish = time.time()
        return result, finish - start

    @staticmethod
    def fail(what):
        raise Exception(what)

    @classmethod
    def fail_if(cls, f, what):
        if f:
            cls.fail(what)

    @classmethod
    def fail_if_neq(cls, a, b, what):
        if a != b:
            cls.fail('{}: {} != {}'.format(what, a, b))


class Runner(object):
    def __init__(self, task_class):
        self._task_class = task_class
        self._tasks = []

    def run(self, arg1, *args):
        if isinstance(arg1, six.string_types):
            assert len(args) == 1
            name = arg1
            task_data = args[0]
            self._append(name, lambda: task_data, ())
        elif isinstance(arg1, (tuple, list)):
            name, f = arg1
            self._append(name, f, args)
        else:
            f = arg1
            self._append(f.__name__, f, args)

    def main(self, args_=None):
        parser = argparse.ArgumentParser(description='Run tests')
        parser.add_argument(
            '-l',
            '--list',
            action='store_true', help='list tests'
        )
        parser.add_argument(
            'pattern',
            metavar='REGEXP',
            nargs='?',
            default='.*',
            type=str,
            help='regexp to select tests'
        )
        args = parser.parse_args(args_)

        if args.list:
            for n, _ in self._select_tasks(args.pattern):
                print(n)
            sys.exit(0)

        for n, f in self._select_tasks(args.pattern):
            self._run_task(n, f)
        sys.exit(0)

    def _append(self, name, f, args):
        ff = f
        if len(args) > 0:
            name = '_'.join([name] + list(map(str, args)))

            def ff():
                return f(*args)
        self._tasks.append((name, ff))

    def _select_tasks(self, pattern):
        for n, f in self._tasks:
            if re.search(pattern, n):
                yield n, f

    def _run_task(self, name, f):
        """Run task, check answer and report result."""

        task = self._task_class(name, f())

        print(task.name, end=' ')
        sys.stdout.flush()

        if not task.check_input():
            print('skip invalid task')
        else:
            task.write_task()

            task = None
            gc.collect()

            # start testing program
            _, elapsed = self._task_class.elapsed_time(
                self._task_class.compute_answer
            )

            task = self._task_class(name, f())

            print(task.performance(elapsed), end=' ')
            sys.stdout.flush()

            answer = task.read_answer()

            task.check_answer(answer)

        task = None
        gc.collect()


@contextlib.contextmanager
def runner(task_class, args=None):
    runner = Runner(task_class)
    yield runner.run
    runner.main(args)
