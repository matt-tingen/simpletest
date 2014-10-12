import sys
import inspect
import os
from pprint import pprint
import textwrap


class TestFailed(Exception):
    pass


class Test:
    _id = None
    pretty_print = True
    exit_on_fail = True
    clear_console_on_assert_success = False
    write_failed_assert_to_file = False
    context_lines_before = 2
    context_lines_after = 1
    left_name = 'left'
    right_name = 'right'
    separator = '\n' + '=' * 20 + '\n'
    context_marker = '-> '
    context_divider = ': '

    def __init__(self, **kwargs):
        for key, value in kwargs:
            setattr(self, key, value)

        try:
            self.run() # pure virtual
        except TestFailed:
            self._fail()
        else:
            self.success()

    @property
    def id(self):
        return self._id or self.__class__.__name__
    @id.setter
    def id(self, value):
        self._id = value

    def failed_file_name(self, left_or_right):
        suffix = self.left_name if left_or_right == 'left' else self.right_name
        filename = 'test_value_' + suffix + '.txt'
        return filename

    def write_value_to_file(self, value, filename):
        with open(filename, 'w') as f:
            f.write(repr(value))

    def get_frame_info(self):
        for frame, filename, line_num, fn_name, context, line_index in inspect.stack():
            module_name = inspect.getmodule(frame).__name__

            if module_name != 'simpletest' and not fn_name.startswith('assert_'):
                break

        self.frame = frame
        self.filename = filename
        self.line_num = line_num
        self.fn_name = fn_name

        # The inspect module only supports getting context centered around the calling line.
        # When doing something like
        # assert_eq(
        #     left_value,
        #     right_value
        # )
        # the third line (`    right value`) is considered the calling line so we want
        # two lines before and one after. The get_context method supports this.
        self.get_context()

    def get_context(self):
        context, start_line_num = inspect.getsourcelines(self.frame)
        adjusted_line_num = self.line_num - start_line_num
        start = max(0, adjusted_line_num - self.context_lines_before)
        end = min(len(context), adjusted_line_num + self.context_lines_after + 1)
        self.context = ''.join(context[start:end]).rstrip()
        self.format_context()

    def format_context(self):
        # Determine how much space will be needed to the left of each line.
        # We must accomodate the line numbers, plus the line marker where the assertion failed,
        # and the divider that separates the line number from the code.
        line_num_width = len(str(self.line_num + self.context_lines_after + 1))
        padding_width = line_num_width + len(self.context_marker + self.context_divider)

        # Add line numbers, the line marker, and dividers to the beginning of lines.
        unindented = textwrap.dedent(self.context)
        line_num = self.line_num - self.context_lines_before
        lines = []

        for line in unindented.split('\n'):
            prefix = '{marker:>{marker_width}}{num:{num_width}}{div}'.format(
                marker = self.context_marker if line_num == self.line_num else '',
                marker_width = len(self.context_marker),
                num = line_num,
                num_width = line_num_width,
                div = self.context_divider
            )
            lines.append('{:>{width}}{}'.format(prefix, line, width=padding_width))
            line_num += 1

        self.context = '\n'.join(lines)

    def success(self):
        pass

    def _assert_success(self):
        if self.clear_console_on_assert_success:
            os.system('cls' if os.name == 'nt' else 'clear')

        self.assert_success()

    def assert_success(self):
        pass

    def pre_fail(self):
        pass

    def _fail(self):
        self.print_fail_summary()

        if self.write_failed_assert_to_file:
            self.write_value_to_file(self.left, self.failed_file_name('left'))
            self.write_value_to_file(self.right, self.failed_file_name('right'))

        self.fail()
        
    def fail(self):
        if self.exit_on_fail:
            sys.exit()
        else:
            raise TestFailed

    def print_fail_summary(self):
        if self.pretty_print:
            pretty_print = pprint
        else:
            pretty_print = print

        print('\n{}:'.format(self.left_name))
        pretty_print(self.left)

        print(self.separator)

        print('{}:'.format(self.right_name))
        pretty_print(self.right)

        print(self.separator)

        print('Expected: ' + self.code)
        print('Test "{}" failed on line {} of\n{}:'.format(self.id, self.line_num, self.filename))
        print(self.context)

    def _assert_fail(self):
        self.get_frame_info()
        self.pre_fail()
        raise TestFailed

    def _assert_op(self, left, right, op):
        self._assert_eval('left ' + op + ' right', left, right)

    def _assert_eval(self, code, left, right):
        self.code = code
        self.left = left
        self.right = right

        locals()[self.left_name] = left
        locals()[self.right_name] = right

        if eval(code):
            self._assert_success()
        else:
            self._assert_fail()

    def assert_eval(self, code, **kwargs):
        # Since kwargs is a dict, we can't determine which was listed first in the 
        # function call so left_name and right_name may be reversed, but it will 
        # only change which is listed first in the failure output
        try:
            left = kwargs['left']
            right = kwargs['right']
        except KeyError:
            items = list(kwargs.items())

            try:
                self.left_name, left = items[0]
                self.right_name, right = items[1]
            except IndexError:
                raise TypeError('assert_code takes 1 positional argument and 2 keyword arguments')

        self._assert_eval(code, left, right)

    def assert_lt(self, left, right):
        self._assert_op(left, right, '<')

    def assert_le(self, left, right):
        self._assert_op(left, right, '<=')

    def assert_eq(self, left, right):
        self._assert_op(left, right, '==')

    def assert_ne(self, left, right):
        self._assert_op(left, right, '!=')

    def assert_gt(self, left, right):
        self._assert_op(left, right, '>')

    def assert_ge(self, left, right):
        self._assert_op(left, right, '>=')

    def assert_is(self, left, right):
        self._assert_op(left, right, 'is')

    def assert_isnot(self, left, right):
        self._assert_op(left, right, 'is not')

    def assert_len(self, item, length):
        self.left_name = 'item'
        self.right_name = 'length'
        self._assert_eval('len(item) == length', item, length)

    def assert_instance(self, instance, cls):
        self.left_name = 'instance'
        self.right_name = 'cls'
        self._assert_eval('isinstance(instance, cls)', instance, cls)
