from octonyan.models import Commit, Repository, UserRepository

__author__ = 'akhmetov'


def get_cmmt_by_hash(hash):
    cmmt = Commit.objects.filter(commit_hash=hash).first()
    if cmmt:
        return cmmt
    return None


def is_rep(repo_url):
    return Repository.objects.filter(url=repo_url).exists()


def get_by_dir_name(repo_dir):
    return Repository.objects.filter(dir_name=repo_dir).first()


def get_repos(user):
    return [ur.repo for ur in UserRepository.objects.filter(
        user=user).select_related('repo').only('repo')]

