import json
from octonyan.models import Commit, Repository, UserRepository, \
    CommitterRepository

__author__ = 'akhmetov'


def get_statistic_json(repo):
    lol = {
        'rep': {
            'pasan': [],
            'total': {}
        }
    }
    for author in Commit.objects.values('author').filter(repo=repo):
        data = {
            'name': author['author'],
            'commit': Commit.objects.values(
                'pep8_average', 'pep257_average',
                'total_docstr_cover', 'create_date'
            ).filter(author=author['author'], repo=repo)
        }
        lol['rep']['pasan'].append(data)
    last_check = {
        'pep8': repo.last_check.pep8_average,
        'pep257': repo.last_check.pep257_average,
        'total': repo.last_check.total_docstr_cover,
    }
    lol['rep']['total'] = last_check
    return json.dumps(lol, ensure_ascii=False)


def get_cmmt_by_hash(hash):
    cmmt = Commit.objects.filter(id_commit=hash).first()
    if cmmt:
        return cmmt
    return None


def is_rep(repo_url):
    return Repository.objects.filter(url=repo_url).exists()


def get_by_dir_name(repo_dir):
    return Repository.objects.filter(dir_name=repo_dir).first()


def get_head_commit(rep):
    return Commit.objects.filter(repo=rep).first()


def get_repos(user):
    return [ur.repo for ur in UserRepository.objects.filter(
        user=user).select_related('repo').only('repo')]


def get_comm_by_rep(dir_name):
    return Commit.objects.filter(repo__dir_name=dir_name)


def get_committer_by_rep(dir_name):
    return CommitterRepository.objects.filter(
        repo__dir_name=dir_name).order_by("-pep8_average",
                                          "-pep257_average",
                                          "-docstr_cover_average")


def get_commit_by_rep_commit_id(dir_name, commit_id):
    return Commit.objects.filter(repo__dir_name=dir_name, id_commit=commit_id)


def get_last_upd_repo(user):
    return UserRepository.objects.filter(user=user) \
               .order_by('-last_update')[:1]
