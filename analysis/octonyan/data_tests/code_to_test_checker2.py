""" Data to test get_lloc method of PyChecker."""
# lloc_count = 17.
# count defines = 9 + 1 itself module.
# docstring missing = 6
# pep257 = 7
# pep8 = 1

# General:
# pep8 = 0.9412
# pep257 = 0.3
# docstr_cover = 0.4

from octonyan import utils


def foo():
    """Lorem ipsum dolor sit amet, consectetur adipisicing elit.
    Ex temporibus alias ipsa aperiam facere a aut adipisci
    repudiandae dignissimos sequi!

    """
    a = "foo"
    checker = utils.PyChecker(a)
    print type(checker)


class A:

    @staticmethod
    def foo():
        pass

    def __init__(self):
        pass

    def get_a(self, *argv, **kwargs):
        pass

    def set_a(self, a="Foo"):
        """Lorem ipsum dolor sit amet, consectetur adipisicing."""
        for i in xrange(10):
            print i


class B(object, A):

    """Lorem ipsum dolor sit amet, consectetur adipisicing elit."""

    def foo_bar(self):
        pass

# wrong example
def _wrong:
    pass


class C():
    pass
