from django.test import TestCase


class InitRepositoryViewTest(TestCase):

    def test_repo_url_processing(self):
        """ basic test with wrong url"""
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
