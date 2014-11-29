from django.contrib.auth.models import User
from django.db import models
# Create your models here.


class Commit(models.Model):
    repo = models.ForeignKey('Repository')
    update_at = models.DateTimeField()
    pep8_average = models.IntegerField(default=0)
    pep257_average = models.IntegerField(default=0)
    commit_author = models.ForeignKey(User)


class Repository(models.Model):
    repo_dir_name = models.FilePathField()
    url = models.URLField(unique=True)
    user = models.ForeignKey(User)
    last_cheking_commit = models.ForeignKey(Commit)
    last_update = models.DateTimeField(auto_now=True)
