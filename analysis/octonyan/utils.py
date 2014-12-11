"""
Utils and helpers to web app.

Checker class implementaion check of quality code,
 simple docstring quality and coverage.

"""
import os
import re

import pep8
import pep257




class StyleGuideCustomReport(pep8.StandardReport):

    """Overide behavior get_file_results method."""

    def get_file_results(self):
        """Return list of line of code with pep8 errors, warnings and etc."""
        result = []
        if self._deferred_print:
            self._deferred_print.sort()
            for line_number, offset, code, text, doc in self._deferred_print:
                s = '%d| %s    %s' % (line_number, code, text)
                result.append(s)

            return result


class PyChecker(object):

    """Python code checker for PEP257 and PEP8."""

    MATCHING_STR = ("(def\ [a-zA-Z_]\w*(\(\):|\(.*\):)|"
                    "class\ [a-zA-Z_]\w*(:|\(\):|\(.*\):))\n")

    IGNORE = ('D200', 'D201', 'D202', 'D203', 'D204',
              'D205', 'D206', 'D207', 'D208', 'D209',
              'D300', 'D301', 'D302',
              'D400', 'D401', 'D402',)

    @staticmethod
    def match_by_reg(line, regex=MATCHING_STR):
        """Check on match regex and giving line."""
        current = re.compile(regex)

        return current.search(line)

    def __init__(self, root, cur_file=None):
        """Get instance of checker.

        Keyword arguments:
        root -- directory for checking modules,
        cur_file -- (optional) checking file.

        """
        self.root = root.rstrip('/')
        self.current_file = os.path.join(cur_file)

    def set_current_file(self, cur_file):
        """Set current file for checker methods."""
        self.current_file = cur_file

    def check_docstr_wrap(self, ignore=()):
        """Return pep257 instance of report of module."""
        report = pep257.check([self.current_file, ], ignore)

        return report

    def check_style_wrap(self, reporter=StyleGuideCustomReport):
        """Return instance of pep8 report of module."""
        pep8style = pep8.StyleGuide(reporter=reporter)
        report = pep8style.check_files(
            [self.current_file, ]).get_file_results()

        if report:
            return report
        return []

    def get_lloc(self):
        """Implementaion of counting logical line of code(lloc)."""
        docstr = False
        count_logic_line = 0
        try:
            f = open(self.current_file)
            lines = [line.strip() for line in f]
            for line in lines:
                if line == "" \
                        or PyChecker.match_by_reg(line, "pass") \
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
        finally:
            f.close()

        return count_logic_line

    def get_count_defines(self):
        """Return number of defines python class and function."""
        count_defines = 1
        for line in open(self.current_file):
            if PyChecker.match_by_reg(line):
                count_defines += 1

        return count_defines

    def get_metrics(self):
        """Check current file and return metrics.

        Return tuple of percentage values:,
          pep8 quality,
          doc string quality(pep257),
          doc string coverage.

        """
        lloc = self.get_lloc()
        if lloc != 0:
            line_error_identifier = set()
            for message in self.check_style_wrap():
                line_code = message.split('|')[0]
                line_error_identifier.add(line_code)
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

            style_quality = round(1 - float(style_quality) / lloc, 4)
            count_def = self.get_count_defines()
            docstr_quality = round(1 - float(docstr_quality) / count_def, 4)
            docstr_cover = round(1 - float(docstr_cover) / count_def, 4)

            return (style_quality, docstr_quality, docstr_cover, )

    def get_root_metrics(self):
        """Check all files in setting root and get general metrics."""
        extension = ".*.py"
        file_counter = 0
        total_style = 0.0
        total_docstr = 0.0
        total_docstr_cover = 0.0

        for dirpath, dirs, filenames in os.walk(self.root):
            for f in filenames:
                if PyChecker.match_by_reg(f, extension):
                    self.set_current_file(os.path.join(dirpath, f))
                    metrics = self.get_metrics()
                    if metrics:
                        file_counter += 1
                        style, docstr, docstr_cover = metrics
                        total_style += style
                        total_docstr += docstr
                        total_docstr_cover += docstr_cover

        total_style = round(float(total_style) / file_counter, 4)
        total_docstr = round(float(total_docstr) / file_counter, 4)
        total_docstr_cover = round(float(total_docstr_cover) / file_counter, 4)

        return total_style, total_docstr, total_docstr_cover


def get_checker(path_str, checker_name="pep8"):
    """Return appropriate checker instance(fabric method)."""
    checkers = dict(pep8=PyChecker,)

    return checkers[checker_name](path_str)


def check_source(path_str, style="pep8"):
    """Check all files in setting path, use appropriate checker."""
    checker = get_checker(path_str, style)

    return checker.get_root_metrics()
