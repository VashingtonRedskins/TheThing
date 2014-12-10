from octonyan.models import Commit, Repository, UserRepository, \
    CommitterRepository

__author__ = 'akhmetov'


def get_cmmt_by_hash(hash):
    cmmt = Commit.objects.filter(id_commit=hash).first()
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


def get_comm_by_rep(dir_name):
    return Commit.objects.filter(repo__dir_name=dir_name)


def get_committer_by_rep(dir_name):
    return CommitterRepository.objects.filter(
        repo__dir_name=dir_name).order_by('-count')


def get_commit_by_rep_commit_id(dir_name, commit_id):
    return Commit.objects.filter(repo__dir_name=dir_name, id_commit=commit_id)

