# simpletest

simpletest is a simple way to unit test python code.

This project was written largely as an exercise and I couldn't tell you what it offers over the built-in `unittest` module.

## Usage

To create a set of unit tests, subclass `Test` and override the `run` method. The test will run when an instance of your subclass is created.

The below methods are available to assert conditions. Each method takes two arguments to compare. In general, the order of the arguments matters, with the first being on the left of the operator and the second on the right.

Operation | Method | Code
--- | --- | ---
Equal | `assert_eq` | `left == right`
Not Equal | `assert_en` | `left != right` 
Less Than | `assert_lt` | `left < right`
Less Than or Equal | `assert_le` | `left <= right`
Greater Than | `assert_gt` | `left > right`
Greater Than or Equal | `assert_ge` | `left >= right`
Is | `assert_is` | `left is right`
Is Not | `assert_isnot` | `left is not right`
Length | `assert_len` | `len(left) == right`
Is Instance | `assert_instance` | `isinstance(left, right)`

For Example:

```python
from test import Test

def double(n):
	return 2 * n

class SampleTest(Test):
    def run(self):
        self.assert_eq(double(2), 4)

SampleTest()
```

## Custom Asserts
If you need to test something not covered by the provided asserts, you can do one of two things:

You can use `assert_eval`:
```python
self.assert_eval('2 * half == whole', half=0.5, whole=1)
```

Or you can create a new assert method. When doing so you must use `_assert_op` or `_assert_eval`. Due to the way the calling line is currently determined, you cannot use a public assert in another assert.

`_assert_op` takes a left value, a right value, and an operator.
The following will evaluate `left % right`:
```python
def assert_mod(self, left, right):
    self._assert_op(left, right, '%')	
```
`_assert_eval` is more flexible but requires more setup. It takes a string to evaluate and two keyword arguments that match values in the string. You must set `self.left_name` and `self.right_name` to the argument names.
```python
def assert_half(self, half, whole):
    self.left_name = 'half'
    self.right_name = 'whole'
	self._assert_eval('half == whole / 2', half=half, whole=whole)
```

