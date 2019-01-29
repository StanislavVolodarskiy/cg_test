from __future__ import print_function
import mock
import pytest
from six.moves import range

import cg_test


class Task1(cg_test.BaseTask):
    def __init__(self, name, task):
        super(Task1, self).__init__(name)

    def size(self):
        return 15

    def complexity(self):
        return 60

    def write_task_to_file(self, f):
        f.write('task_data')

    def read_answer_from_file(self, f):
        return f.read()

    def check_answer(self, answer):
        assert answer == 'answer_data'
        print('')


class Task2(Task1):
    def __init__(self, name, task):
        super(Task2, self).__init__(name, task)
        assert isinstance(task, bool)
        self._task = task

    def check_input(self):
        return self._task


class TestBaseTask(object):
    def test_init(self):
        t = cg_test.BaseTask('task_name')
        assert t.name == 'task_name'

    def test_size(self):
        t = cg_test.BaseTask('')
        with pytest.raises(NotImplementedError):
            t.size()

    def test_complexity(self):
        t = cg_test.BaseTask('')
        with pytest.raises(NotImplementedError):
            t.complexity()

    def test_write_task_to_file(self):
        t = cg_test.BaseTask('')
        with pytest.raises(NotImplementedError):
            t.write_task_to_file(None)

    def test_read_answer_from_file(self):
        t = cg_test.BaseTask('')
        with pytest.raises(NotImplementedError):
            t.read_answer_from_file(None)

    def test_check_answer(self):
        t = cg_test.BaseTask('')
        with pytest.raises(NotImplementedError):
            t.check_answer(None)

    def test_performance(self):
        t = Task1('task_name', None)
        assert t.performance(7.5) == 'T(15) / 7.500 = 8'

    def test_write_task(self):
        t = Task1('task_name', None)
        with mock.patch('six.moves.builtins.open', mock.mock_open()) as open_:
            t.write_task()
            open_.assert_called_with('tmp/in', 'w')
            open_().write.assert_called_once_with('task_data')

    def test_compute_answer(self):
        with mock.patch('os.system', mock.Mock()) as os_system:
            os_system.return_value = 0
            cg_test.BaseTask.compute_answer()
            os_system.assert_called_with('./run')

        with mock.patch('os.system', mock.Mock()) as os_system:
            os_system.return_value = 1
            with pytest.raises(Exception) as e:
                cg_test.BaseTask.compute_answer()
            assert e.value.args == ('computation failure', )
            os_system.assert_called_with('./run')

    def test_read_answer(self):
        t = Task1('task_name', None)
        m = mock.mock_open(read_data='answer_data')
        with mock.patch('six.moves.builtins.open', m) as open_:
            assert t.read_answer() == 'answer_data'
            open_.assert_called_with('tmp/out', 'r')
            open_().read.assert_called_once_with()

    def test_elapsed_time(self):
        m = mock.Mock(side_effect=[32, 48])
        with mock.patch('time.time', m) as time_time:
            assert cg_test.BaseTask.elapsed_time(lambda: 'result') == \
                ('result', 16)
            assert time_time.call_args_list == [mock.call()] * 2

    def test_fail(self):
        with pytest.raises(Exception) as e:
            cg_test.BaseTask.fail('failure')
        assert e.value.args == ('failure', )

    def test_fail_if(self):
        cg_test.BaseTask.fail_if(False, 'failure')
        with pytest.raises(Exception) as e:
            cg_test.BaseTask.fail_if(True, 'failure')
        assert e.value.args == ('failure', )

    def test_fail_if_neq(self):
        cg_test.BaseTask.fail_if_neq(3, 3, 'failure')
        with pytest.raises(Exception) as e:
            cg_test.BaseTask.fail_if_neq(3, 4, 'failure')
        assert e.value.args == ('failure: 3 != 4', )


class TestRunner(object):
    def test_init(self):
        o = object()
        r = cg_test.Runner(o)
        assert r._task_class == o
        assert r._tasks == []

    def test_run(self):
        r = cg_test.Runner(None)
        r.run('task_name', ['task', 'data'])

        def task_func(arg1, arg2, arg3):
            return ['data', 'of', 'task', arg1, arg2, arg3]

        r.run(task_func, 'value1', 'value2', 'value3')

        r.run(
            ('task_func_name', lambda *a: ('data', 'of', 'task') + a),
            'value1',
            'value2',
            'value3'
        )

        task1, task2, task3 = r._tasks

        name, f = task1
        assert name == 'task_name'
        assert f() == ['task', 'data']

        name, f = task2
        assert name == 'task_func_value1_value2_value3'
        assert f() == ['data', 'of', 'task', 'value1', 'value2', 'value3']

        name, f = task3
        assert name == 'task_func_name_value1_value2_value3'
        assert f() == ('data', 'of', 'task', 'value1', 'value2', 'value3')

    def test_main_help(self, capsys):
        r = cg_test.Runner(None)
        with pytest.raises(SystemExit):
            r.main(['--help'])
        captured = capsys.readouterr()
        assert captured.out.startswith('usage: pytest')

    def test_main_list(self, capsys):
        r = cg_test.Runner(None)
        r.run('task_name', None)

        def task_func(arg1, arg2, arg3):
            return []

        r.run(task_func, 'value1', 'value2', 'value3')
        with pytest.raises(SystemExit):
            r.main(['--list'])
        captured = capsys.readouterr()
        assert captured.out == 'task_name\ntask_func_value1_value2_value3\n'

    def test_main_run(self, capsys):
        r = cg_test.Runner(Task1)
        r.run('task_name', None)

        def task_func(arg1, arg2, arg3):
            return []

        r.run(task_func, 'value1', 'value2', 'value3')

        open_ = mock.mock_open(read_data='answer_data')
        time_time = mock.Mock(side_effect=range(0, 100, 2))

        with mock.patch('six.moves.builtins.open', open_):
            with mock.patch('os.system', mock.Mock()) as os_system:
                with mock.patch('time.time', time_time):
                    os_system.return_value = 0
                    with pytest.raises(SystemExit):
                        r.main([])

            assert open_.call_args_list == [
                mock.call('tmp/in', 'w'),
                mock.call('tmp/out', 'r'),
                mock.call('tmp/in', 'w'),
                mock.call('tmp/out', 'r')
            ]
            open_().write.call_args_list == []

        captured = capsys.readouterr()
        assert captured.out == \
            'task_name T(15) / 2.000 = 30 \n' + \
            'task_func_value1_value2_value3 T(15) / 2.000 = 30 \n'


class TestRunner_function(object):
    def test_runner(self, capsys):
        open_ = mock.mock_open(read_data='answer_data')
        time_time = mock.Mock(side_effect=range(0, 100, 2))

        with mock.patch('six.moves.builtins.open', open_):
            with mock.patch('os.system', mock.Mock()) as os_system:
                with mock.patch('time.time', time_time):
                    os_system.return_value = 0
                    with pytest.raises(SystemExit):
                        with cg_test.runner(Task2, []) as run:
                            run('task_name_1', True)
                            run('task_name_2', False)

                            def task_func(arg1, arg2, arg3):
                                return True

                            run(task_func, 'value1', 'value2', 'value3')

            assert open_.call_args_list == [
                mock.call('tmp/in', 'w'),
                mock.call('tmp/out', 'r'),
                mock.call('tmp/in', 'w'),
                mock.call('tmp/out', 'r')
            ]
            open_().write.call_args_list == []

        captured = capsys.readouterr()
        assert captured.out == \
            'task_name_1 T(15) / 2.000 = 30 \n' + \
            'task_name_2 skip invalid task\n' + \
            'task_func_value1_value2_value3 T(15) / 2.000 = 30 \n'

    def test_runner_filtered(self, capsys):
        open_ = mock.mock_open(read_data='answer_data')
        time_time = mock.Mock(side_effect=range(0, 100, 2))

        with mock.patch('six.moves.builtins.open', open_):
            with mock.patch('os.system', mock.Mock()) as os_system:
                with mock.patch('time.time', time_time):
                    os_system.return_value = 0
                    with pytest.raises(SystemExit):
                        with cg_test.runner(Task2, ['func']) as run:
                            run('task_name_1', True)
                            run('task_name_2', False)

                            def task_func(arg1, arg2, arg3):
                                return True

                            run(task_func, 'value1', 'value2', 'value3')

            assert open_.call_args_list == [
                mock.call('tmp/in', 'w'),
                mock.call('tmp/out', 'r')
            ]
            open_().write.call_args_list == []

        captured = capsys.readouterr()
        assert captured.out == \
            'task_func_value1_value2_value3 T(15) / 2.000 = 30 \n'
