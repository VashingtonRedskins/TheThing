from django.conf.urls import url, patterns
from octonyan import views

urlpatterns = patterns(
    "",
    url(r"^$", views.index, name='index'),
    url(r"^init/$", views.InitRepoView.as_view(), name="init_repo"),
    url(r"^repo/(?P<repo_dir>\w[\w-]+)/$",
        views.repository, name="repository"),
    url(r"^repo/(?P<repo_dir>\w[\w-]+)/(?P<commit_id>\w+)$",
        views.detail_commit_view, name="commit_view"),
    url(r"^analys/(?P<repo_dir>\w[\w-]+)/(?P<commit_id>\w+)$",
        views.analysis, name="analysis"),
)
