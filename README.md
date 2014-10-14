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
from simpletest import Test

def double(n):
    return 2 * n

class DoubleTest(Test):
    def run(self):
        self.assert_eq(double(2), 4)
        self.assert_eq(double(3), 7)

DoubleTest()
```

The first assert will pass, but the second will fail, printing

```

left:
6

====================

right:
7

====================

Expected: left == right
Test "DoubleTest" failed on line 12 of
C:\Users\Matt\Dropbox\Programming\Python3\simpletest\_.py:
   10: def run(self):
   11:     self.assert_eq(double(2), 4)
-> 12:     self.assert_eq(double(3), 7)

```

This output can be customized in a number of ways (see the Overriding Behavior section).

## Custom Asserts
If you need to test something not covered by the provided asserts, you can do one of two things:

You can use `assert_eval`:
```python
self.assert_eval('2 * half == whole', half=0.5, whole=1)
```

Or you can create a new assert method. When doing so you must use `_assert_op` or `_assert_eval`. Your new method's name __must__ begin with `assert_` or the calling line will cannot be determined correctly.

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

## Overriding Behavior

The behavior of a `Test` can be changed by setting properties and/or overriding methods.


### Properties
#### Actions

Property | Default | Description
--- | --- | ---
`exit_on_fail` | `True` | Call `sys.exit()` after a failed assert. If false, the exception `simpletest.TestFailed` will be thrown instead. 
`clear_console_on_assert_success` | `False` | Clear the console after each successful assert (useful for debugging)
`write_failed_assert_to_file` | `False` | Write the left and right values to individual files after a failed assert

#### Display

Property | Default | Description
--- | --- | ---
`pretty_print` | `True` | Use the `pprint` module to print values in the failure summary
`id` | class name | The name of the test in the failure summary
`separator` | `'\n====================\n'` | Separates the left value, right value, and extra info in the failure summary
`context_lines_before` | `2` | Number of source code lines to display before the line calling the assert 
`context_lines_after` | `1` | Number of source code lines to display after the line calling the assert
`context_marker` | `'-> '` | Marks the line calling the failed assert
`context_divider` | `': '` | Separates line numbers from the corresponding lines

Note: if you call an assert in the following manner, Python considers the third line to be the calling line. This is why the defaults for `context_lines_before` and `context_lines_after` are what they are.

``` python
assert_eq(
    left_value,
    right_value
)
```

### Methods

`assert_success` is called when an assert method passes. It is called after the console is cleared when `clear_console_on_assert_success` is `True`.

`success` is called after the entire `Test` has run without any asserts failing. By default, this print a simple message indicating success.

`pre_fail` is called after an assert fails but before the failure summary is printed and values are written to file (with `write_failed_assert_to_file`). It can be used to change the displayed values `self.left` and `self.right`. Regardless of what changes in the method, the test will still fail.

`print_fail_summary` is the method that displays the failure summary.

`fail` is called after `print_fail_summary` and after the values are written to file (with `write_failed_assert_to_file`). By default, this will exit or raise `simpletest.TestFailed` based on `exit_on_fail`.

`failed_file_name` generates the filenames when using `write_failed_assert_to_file`. It takes one argument (other than `self`) which will be either `left` or `right` which indicates which value's filename to generate. The members `self.left_name` and `self.right_name` are available for use in the filename.