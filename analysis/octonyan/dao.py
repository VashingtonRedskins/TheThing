import json
from octonyan.models import Commit, Repository, UserRepository, \
    CommitterRepository
from django.core.serializers.json import DjangoJSONEncoder

__author__ = 'akhmetov'


def get_statistic_json(dir_name):
    repo = get_repo_by_dir_name(dir_name)
    rep = []
    for author in Commit.objects.values('author').filter(repo=repo).distinct():

        commits = []
        for commit in Commit.objects.values(
                'pep8_average', 'pep257_average',
                'total_docstr_cover', 'create_date'
        ).filter(author=author['author'], repo=repo):
            commits.append({
                'pep8': commit['pep8_average'],
                'pep257': commit['pep257_average'],
                'docstring': commit['total_docstr_cover'],
                'date': commit['create_date'].strftime('%Y-%m-%dT%H:%M:%S')

            })
        data = {'name': author['author'], 'commit': commits}

        rep.append(data)
    # lol['rep']['total'] = last_check
    # print json.dumps(lol, ensure_ascii=False)
    return json.dumps(rep, cls=DjangoJSONEncoder)


def get_repo_by_dir_name(dir_name):
    return Repository.objects.filter(dir_name=dir_name).first()


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
