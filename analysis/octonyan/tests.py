from django.test import TestCase
from django.utils import unittest

from octonyan import utils
import os


class InitRepositoryViewTest(TestCase):

    def test_repo_url_processing(self):
        """ Basic test with wrong url."""
        repo_url = "https://github/lorem_ipsum/foo"
        response = self.client.post(
            "/octonyan/init/", {"repository_url": repo_url})
        self.assertFormError(
            response, 'form', "repository_url", "Incorrect url to repository.")

        repo_url = "https://git/lorem_ipsum/foo.git"
        response = self.client.post(
            "/octonyan/init/", {"repository_url": repo_url})
        self.assertFormError(
            response, 'form', "repository_url", "Something went wrong.")


class PyCheckerTest(unittest.TestCase):

    TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), "data_tests")

    def setUp(self):
        self.checker = utils.PyChecker(
            PyCheckerTest.TEST_DATA_PATH,
            cur_file=os.path.join(
                PyCheckerTest.TEST_DATA_PATH, "code_to_test_checker1.py"))

    def test_get_lloc(self):
        self.assertEqual(self.checker.get_lloc(), 28)
        self.checker.set_current_file(
            os.path.join(
                PyCheckerTest.TEST_DATA_PATH, "code_to_test_checker2.py")
        )
        self.assertEqual(self.checker.get_lloc(), 17)

    def test_get_count_defines(self):
        self.assertEqual(self.checker.get_count_defines(), 23)
        self.checker.set_current_file(
            os.path.join(
                PyCheckerTest.TEST_DATA_PATH, "code_to_test_checker2.py")
        )
        self.assertEqual(self.checker.get_count_defines(), 10)

    def test_get_metrics(self):
        metric = self.checker.get_metrics()
        self.assertNotEqual(metric, None)
        style, docstr, docstr_cover = metric
        self.assertEqual(style, 0.7857)
        self.assertEqual(docstr, 0.087)
        self.assertEqual(docstr_cover, 0.6957)

        self.checker.set_current_file(
            os.path.join(PyCheckerTest.TEST_DATA_PATH,
                         "code_to_test_checker2.py")
        )

        metric = self.checker.get_metrics()
        self.assertFalse(None)
        style, docstr, docstr_cover = metric
        self.assertEqual(style, 0.9412)
        self.assertEqual(docstr, 0.3)
        self.assertEqual(docstr_cover, 0.4)

        self.checker.set_current_file(
            os.path.join(PyCheckerTest.TEST_DATA_PATH,
                         "code_to_test_checker3.py")
        )
        self.assertEqual(self.checker.get_metrics(), None)

    def test_get_root_metrics(self):
        gen_metrics = self.checker.get_root_metrics()
        self.assertTrue(gen_metrics)
        style, docstr, docstr_cover = gen_metrics
        self.assertEqual(style, 0.8635)
        self.assertEqual(docstr, 0.1935)
        self.assertEqual(docstr_cover, 0.5478)
