import sys
import inspect
from datetime import datetime
import os
from pprint import pprint


class TestFailed(Exception):
	pass


class Test:
	_id = None
	pretty_print = True
	exit_on_fail = True
	clear_console_on_assert_success = True
	write_failed_assert_to_file = True
	source_lines_before = 2
	source_lines_after = 1
	left_name = 'left'
	right_name = 'right'
	divider = '\n' + '=' * 20 + '\n'

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
		frame = inspect.currentframe()

		for _ in range(self.frame_depth):
			frame = frame.f_back

		self.line_num = frame.f_lineno
		self.filename = frame.f_code.co_filename
		self.get_source_lines(frame)

	def get_source_lines(self, frame):
		source_lines, start_line_num = inspect.getsourcelines(frame)
		adjusted_line_num = self.line_num - start_line_num
		start = max(0, adjusted_line_num - self.source_lines_before)
		end = min(len(source_lines), adjusted_line_num + self.source_lines_after + 1)
		self.source_lines = ''.join(source_lines[start:end])

	def success(self):
		pass

	def _assert_success(self):
		if self.clear_console_on_assert_success:
			os.system('cls' if os.name == 'nt' else 'clear')

		self.assert_success()

	def assert_success(self):
		pass

	def _fail(self):
		self.fail()

		if self.exit_on_fail:
			sys.exit()
		else:
			raise TestFailed

	def fail(self):
		if self.pretty_print:
			pretty_print = pprint
		else:
			pretty_print = print

		print('\n{}:'.format(self.left_name))
		pretty_print(self.left)
		print(self.divider)
		print('{}:'.format(self.right_name))
		pretty_print(self.right)
		print(self.divider)
		print('Expected: ' + self.code)
		print('Test "{}" failed on line {} of\n{}:'.format(self.id, self.line_num, self.filename))
		print(self.source_lines)

	def _assert_fail(self):
			self.get_frame_info()

			if self.write_failed_assert_to_file:
				self.write_value_to_file(self.left, self.failed_file_name('left'))
				self.write_value_to_file(self.right, self.failed_file_name('right'))

			self.assert_fail()
			raise TestFailed

	def assert_fail(self):
		pass
		
	def _assert_op(self, left, right, op):
		self.frame_depth = 4
		self._assert_eval('left ' + op + ' right', left, right)

	def _assert_eval(self, code, left, right):
		self.code = code
		self.left = left
		self.right = right
		self.frame_depth = 4

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
