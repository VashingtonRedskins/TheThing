import os
import re

import pep257
import pep8


# TODO fix situation when style checker doesn't exist
# def check_source(path_str, style="pep8"):
#     """Docs"""

#     checker = get_checker(path_str, style)

#     return checker.get_all_stat()


class PEP8Checker:

    """docstring for Checker"""

    reg_to_count = {
        "functions": "def [a - zA - Z]\w * (\(\): |\(.*\):)\n",
        "classes": "class [a-zA-Z]\w*(:|\(\):|\(.*\):)\n",
    }

    # FEATURE add ability to using custom config file
    def __init__(self, root, cur_file=None, config_file=None):
        self.root = root.rstrip('/')
        self.config = config_file
        self.current_file = cur_file

    def set_current_file(self, cur_file):
        self.current_file = cur_file

    def check_docstr(self, ignore=None):

        report = pep257.check([self.current_file, ])
        if report:
            result = [i for i in report]
            return (result, len(result))

        return ([], 0)

    def check_style(self):
        pep8style = pep8.StyleGuide(quiet=True)
        report = pep8style.check_files([self.current_file, ])

        return (report.get_statistics(), report.total_errors)

    def get_count_prop(self):
        code_count_lines = 0
        counter = dict()

        for line in open(self.current_file):
            code_count_lines += 1

            for prop, reg in PEP8Checker.reg_to_count.items():

                if PEP8Checker.match_by_reg(line, reg):
                    counter[prop] = counter.get(prop, 0) + 1

        counter["count line of code"] = code_count_lines

        return counter

    def get_all_stat(self):
        extension = ".*.py"
        report_data = []
        for dirpath, dirs, filenames in os.walk(self.root):
            for f in filenames:
                if PEP8Checker.match_by_reg(f, extension):
                    self.set_current_file(os.path.join(dirpath, f))
                    style, total_er = self.check_style()
                    docs, total_doc_er = self.check_docstr()
                    tpl = (
                        f,
                        dirpath,
                        docs,
                        self.get_count_prop(),
                        total_doc_er,
                        style,
                        total_er,
                    )

                    report_data.append(tpl)

        return report_data

    @staticmethod
    def match_by_reg(line, regex):
        current = re.compile(regex)

        return current.match(line)


def get_checker(path_str, checker_name="pep8"):
    checkers = dict(pep8=PEP8Checker,)

    return checkers[checker_name](path_str)


if __name__ == "__main__":
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

    path = ("/home/ram1rez/Repos/"
            "TheThing/analysis/media/"
            "repos/russian_word/"
            "input_over_picture/"
            )

    checker = PEP8Checker(path)
    for f, dirpath, docs, count_func_class, total_docs, style, total_err \
            in checker.get_all_stat():
        print "=============================="
        print "Dirpaht   :", dirpath
        print "Filename  :", f
        print "DOC WARNING AND ERROR"
        for doc in docs:
            print "   ", doc
        print "TOTAL COUNT ERROR DOCS", total_docs
        print "FILE count of function, lines of code, classes"
        for key, val in count_func_class.items():
            print "<<<<<<>>>>>>"
            print key, val
            print "<<<<<<>>>>>>"
        print "PEP CONV WARNING AND ERROR"
        for st in style:
            print st
        print "<<<<<<STYLE>>>>"
        print style
        print "TOTAL STYLE =====>>>", total_err
        print "=============================="
