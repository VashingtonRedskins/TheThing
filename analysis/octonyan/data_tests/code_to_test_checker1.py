# No docstring, so we can test D100
# 23 - number of definitions.
# 6 - pep8 erros/warning appropriate line
# 21 - pep257 erros/warning appropriate line
# 7 - docstring missing cound.
# 28 - lloc.

# General:
# pep8 = 0.7857
# pep257 = 0.087
# docstr_cover = 0.6957

#expect 'class_', 'D101: Docstring missing.


class class_:

    # expect 'meta', D101: Docstring missing.

    class meta:
        """"""

    # expect D102: Docstring missing.
    def method():
        foo = "foo bar"
        # comment to test lloc
        for i in [1, 2, 3]:
            print i
            print foo

        return []

    def _ok_since_private():
        pass

    # expect D102: Docstring missing.
    def __init__(self=None):
        pass


# expect D103: Docstring missing.
def function():
    """ """
    def ok_since_nested():
        pass

    # expect D103: Docstring missing.
    def nested():
        ''


# expect D200: One-line docstring should not occupy 3 lines.
def asdlkfasd():
    """
    Wrong.
    """


# expect D201: No blank lines allowed *before* function docstring, found 1.
def leading_space():

    """Leading space."""


# expect D202: No blank lines allowed *after* function docstring, found 1.
def trailing_space():
    """Leading space."""

    pass


# expect'D201: No blank lines allowed *before* function docstring, found 1.
# expect'D202: No blank lines allowed *after* function docstring, found 1.
def trailing_and_leading_space():

    """Trailing and leading space."""

    pass


# expect LeadingSpaceMissing.
      # D203: Expected 1 blank line *before* class docstring, found 0.


class LeadingSpaceMissing:
    """Leading space missing."""


# expect TrailingSpace.
       # 'D204: Expected 1 blank line *after* class docstring, found 0'.
class TrailingSpace:

    """TrailingSpace."""
    pass


# expect (LeadingAndTrailingSpaceMissing.
       # D203: Expected 1 blank line *before* class docstring, found 0.
# expect LeadingAndTrailingSpaceMissing.
       # D204: Expected 1 blank line *after* class docstring, found 0.
class LeadingAndTrailingSpaceMissing:
    """Leading and trailing space missing."""
    pass


# expect D205: Blank line missing between one-line summary and description.
def asdfasdf():
    """Summary.
    Description.
    """


# expect D207: Docstring is under-indented.
def asdfsdf():
    """Summary.
Description.
    """


# expect D207: Docstring is under-indented.
def asdsdfsdffsdf():
    """Summary.
    Description.
"""


# expect D208: Docstring is over-indented.
def asdfsdsdf24():
    """Summary.
       Description.
    """


# expect D208: Docstring is over-indented.
def asdfsdsdfsdf24():
    """Summary.
    Description.
        """


# expect D208: Docstring is over-indented.
def asdfsdfsdsdsdfsdf24():
    """Summary.
        Description.
    """


#'D209: Put multi-line docstring closing quotes on separate line'
def asdfljdf24():
    """Summary.
    Description."""
