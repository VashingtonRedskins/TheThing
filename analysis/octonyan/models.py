from django.contrib.auth.models import User
from django.db import models
# Create your models here.


class Analysis(models.Model):
    commit_hash = models.CharField(max_length=50)
    repo = models.ForeignKey('Repository')
    update_at = models.DateTimeField()
    pep8_average = models.IntegerField(default=0)
    pep257_average = models.IntegerField(default=0)
    commit_author = models.ForeignKey(User)


class Repository(models.Model):
    title = models.CharField(max_length=79)
    url = models.URLField(unique=True)
    user = models.ForeignKey(User)
    last_update = models.DateTimeField(auto_now=True)
