from simpletest import Test, TestFailed

class SimpleTestTest(Test):

	def success(self):
		print('Passed')

	def run(self):
		self.assert_eq(4, 4)

		try:
			self.assert_eq('test', 'diff')
		except TestFailed:
			pass
		else:
			raise AssertionError

		self.assert_lt(-2, 8)

		try:
			self.assert_lt(28.06, 8)
		except TestFailed:
			pass
		else:
			raise AssertionError

		self.assert_len([1, 2, 3], 3)

		try:
			self.assert_len([1, 2, 3], 4)
		except TestFailed:
			pass
		else:
			raise AssertionError

		class Foo:
			pass
		class Baz:
			pass

		self.assert_instance(Foo(), Foo)

		try:
			self.assert_instance(Baz(), Foo)
		except TestFailed:
			pass
		else:
			raise AssertionError

		self.assert_eval('2 * half == whole', half=0.5, whole=1)

		try:
			self.assert_eval('2 * half == whole', half=0.5, whole=1.1)
		except TestFailed:
			pass
		else:
			raise AssertionError

TestTest()

