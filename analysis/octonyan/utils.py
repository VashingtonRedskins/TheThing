"""Utilits and helpers to web app."""

import os
import re

import pep8
import pep257


def check_source(path_str, style="pep8"):
    """Get checker by style arg and run full analysis in giving directory.

    Return tuple of typles properties anylysis.

    """
    checker = get_checker(path_str, style)

    return checker.get_root_stat()


class StyleGuideCustomReport(pep8.StandardReport):

    def get_file_results(self):
        result = []
        if self._deferred_print:
            self._deferred_print.sort()
            for line_number, offset, code, text, doc in self._deferred_print:
                s = '%d| %s    %s' % (line_number, code, text)
                result.append(s)

            return result


class PyChecker(object):

    """Python code checker for PEP257 and PEP8."""

    MATCHING_STR = "(def\ [a-zA-Z_]\w*(\(\):|\(.*\):)| \
              class\ [a-zA-Z_]\w*(:|\(\):|\(.*\):))\n"

    IGNORE = [
        'D200', 'D201', 'D202', 'D203', 'D204',
        'D205', 'D206', 'D207', 'D208', 'D209',
        'D300', 'D301', 'D302',
        'D400', 'D401', 'D402', ]

    @staticmethod
    def match_by_reg(line, regex=MATCHING_STR):
        """Check on match regex and giving line."""
        current = re.compile(regex)

        return current.search(line)

    # FEATURE add ability to using custom config file
    def __init__(self, root, cur_file=None, config_file=None):
        """Get instance of checker.

        Keyword arguments:
        root -- directory for checking modules
        cur_file -- (optional) checking file
        config_file -- (in future) config file path to some patterns

        """
        self.root = root.rstrip('/')
        self.config = config_file
        self.current_file = cur_file

    def set_current_file(self, cur_file):
        """Set current file for checker methods."""
        self.current_file = cur_file

    def check_docstr_wrap(self, ignore=()):
        """Return pep257 report of module."""
        report = pep257.check([self.current_file, ])

        return report

    def check_style_wrap(self, reporter=StyleGuideCustomReport):
        """Return pep8 report of module."""
        pep8style = pep8.StyleGuide(reporter=reporter)
        report = pep8style.check_files([self.current_file, ])

        return report

    def get_lloc(self):
        docstr = False
        count_logic_line = 0
        lines = [line.strip() for line in open(self.current_file)]
        for line in lines:
            if line == "" \
                    or line.startswith("#") \
                    or docstr and not (line.startswith('\"\"\"')
                                       or line.startswith("\'\'\'")) \
                    or (line.startswith("'''") and line.endswith("\'\'\'")
                        and len(line) > 3) \
                    or (line.startswith('"""') and line.endswith('\"\"\"')
                        and len(line) > 3):
                continue

            elif line.startswith('\"\"\"') or line.startswith("\'\'\'"):
                docstr = not docstr
                continue

            else:
                count_logic_line += 1

        return count_logic_line

    def get_count_defines(self):
        """Return number of defines python class and function."""
        count_defines = 1
        for line in open(self.current_file):
            if PyChecker.match_by_reg(line):
                count_defines += 1

        return count_defines

    def get_metrics(self):
        """Check current file and return metrics."""
        line_error_identifier = set()
        for message in self.check_style_wrap():
            line_error_identifier.add(message.split('|'))
        style_quality = len(line_error_identifier)
        line_error_identifier.clear()

        for doc_error in self.check_docstr_wrap():
            line_error_identifier.add(doc_error.line)
        docstr_quality = len(line_error_identifier)
        line_error_identifier.clear()

        for doc_error in \
                self.check_docstr_wrap(ignore=PyChecker.IGNORE):
            line_error_identifier.add(doc_error.line)
        docstr_cover = len(line_error_identifier)

        style_quality = round(float(style_quality) / self.get_lloc(), 2)

        docstr_quality = round(
            float(style_quality) / self.get_count_defines(), 2)

        docstr_cover = round(
            float(style_quality) / self.get_count_defines(), 2)

        return (style_quality, docstr_quality, docstr_cover, )

    def get_root_stat(self):
        extension = ".*.py"
        file_counter = 0
        total_style = 0.0
        total_docstr = 0.0
        total_docstr_cover = 0.0

        for dirpath, dirs, filenames in os.walk(self.root):
            for f in filenames:
                if PyChecker.match_by_reg(f, extension):
                    file_counter += 1
                    self.set_current_file(os.path.join(dirpath, f))
                    style, docstr, docstr_cover = self.get_metrics()
                    total_style += style
                    total_docstr += docstr
                    total_docstr_cover += docstr_cover

        total_style = round(float(total_style) / file_counter, 2)
        total_docstr = round(float(total_docstr) / file_counter, 2)
        total_docstr_cover = round(float(total_docstr_cover) / file_counter, 2)

        return total_style, total_docstr, total_docstr_cover


def get_checker(path_str, checker_name="pep8"):
    """Return appropriate checker instance(fabric method)."""
    checkers = dict(pep8=PyChecker,)

    return checkers[checker_name](path_str)


if __name__ == "__main__":
    # test_data = [
    #     "class Foo(a, b, c=14):\n",
    #     "pass",
    #     "sdfsd class Fo14_14_bar(a = \"Foo.txt\"):\n"
    #     "    class Fo-Bar():\n"
    #     "class FoBar():\n",
    #     "class FoBar:\n",
    #     "    def foo():\n",
    #     "        def foo():\n",
    #     "def foo_bar:\n",
    #     "def foo_bar():\n",
    #     "def foo_bar(a=15, b=\"Hello\", c=\"None\")",
    # ]

    # path = ("/home/ram1rez/Repos/"
    #         "TheThing/analysis/media/"
    #         "repos/russian_word/"
    #         "input_over_picture/"
    #         )

    # checker = PyChecker(path)
    # for f, dirpath, docs, count_func_class, total_docs, style, total_err \
    #         in checker.get_all_stat():
    #     print "=============================="
    #     print "Dirpaht   :", dirpath
    #     print "Filename  :", f
    #     print "DOC WARNING AND ERROR"
    #     for doc in docs:
    #         print "   ", doc
    #     print "TOTAL COUNT ERROR DOCS", total_docs
    #     print "FILE count of function, lines of code, classes"
    #     for key, val in count_func_class.items():
    #         print "<<<<<<>>>>>>"
    #         print key, val
    #         print "<<<<<<>>>>>>"
    #     print "PEP CONV WARNING AND ERROR"
    #     for st in style:
    #         print st
    #     print "<<<<<<STYLE>>>>"
    #     print style
    #     print "TOTAL STYLE =====>>>", total_err
    #     print "=============================="
    s = "/home/ram1rez/Repos/TheThing/analysis/octonyan/utils.py"
    style = pep8.StyleGuide(reporter=StyleGuideCustomReport)
    r = style.check_files([s, ])
    print dir(r)
    print r.get_file_results()
    # checker = pep8.Checker(s)
    # for line in checker.lines:
    #     print line
