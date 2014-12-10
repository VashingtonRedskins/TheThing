from django.contrib.auth.models import User
from django.db import models
# Create your models here.


class Commit(models.Model):
    repo = models.ForeignKey('Repository')
    commit_hash = models.CharField(max_length=250, unique=True)
    update_at = models.DateTimeField(auto_now=True)
    pep8_average = models.IntegerField(default=0)
    pep257_average = models.IntegerField(default=0)
    total_docstr_cover = models.IntegerField(default=0)


class Repository(models.Model):
    dir_name = models.CharField(max_length=100)
    repo_dir_name = models.FilePathField()
    url = models.URLField(unique=True)
    last_check = models.ForeignKey(Commit, null=True)
    last_update = models.DateTimeField(auto_now=True)


class UserRepository(models.Model):
    repo = models.ForeignKey(Repository)
    user = models.ForeignKey(User)