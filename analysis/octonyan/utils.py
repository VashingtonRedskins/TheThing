import os


def check_repo(path_str, style="pep8", config_file=None):
    path_str = path_str.rstrip('/')

    for dirpath, dirs, filenames in os.walk(path_str):
        pass

    checker = get_checker(path_str)


class PEP8Checker:

    """docstring for Checker"""

    EXTENSION = ".py"
    reg_to_count = [
        "def [a - zA - Z]\w * (\(\): |\(.*\):)\n",
        "class [a-zA-Z]\w*(:|\(\):|\(.*\):)\n", ]

    def __init__(self, path):
        self.path = path

    def check_doc():
        pass

    def check_style():
        pass


def get_checker(path_str, check_name="pep8"):
    checkers = dict(pep8=PEP8Checker,)

    return checkers[check_name](path_str)


if __name__ == "__main__":
    import re
    test_data = [
        "class Foo(a, b, c=14):\n",
        "pass",
        "sdfsd class Fo14_14_bar(a = \"Foo.txt\"):\n"
        "    class Fo-Bar():\n"
        "class FoBar():\n",
        "class FoBar:\n",
        "    def foo():\n",
        "        def foo():\n",
        "def foo_bar:\n",
        "def foo_bar():\n",
        "def foo_bar(a=15, b=\"Hello\", c=\"None\")",
    ]

    path = "/home/ram1rez/Repos/TheThing/analysis/media/repos/russian_word/"
    reg = "class [a-zA-Z]\w*(:|\(\):|\(.*\):)\n"

    p = re.compile(reg)

    for line in test_data:
        line += "\n"
        m = p.match(line)
        if m:
            print m.group()
        else:
            pass

    # check_repo(path)
    # p = PEP8Checker("foo")
    # for reg in p.reg_to_count:
    #     print reg
