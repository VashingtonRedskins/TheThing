from django.conf.urls import url, patterns
from octonyan import views

urlpatterns = patterns(
    "",
    url(r"^$", views.index_repository, name='index'),
    url(r"^add/repo/$", views.InitRepositoryView.as_view(), name="init_repo"),
    url(r"^repo/(?P<dir_name>\w[\w-]+)/$",
        views.show_repository, name="repository"),
    url(r"^repo/(?P<dir_name>\w[\w-]+)/(?P<commit_id>\w+)$",
        views.show_commit, name="commit_view"),
    # show method by commit
    url(r"^repo/(?P<dir_name>\w[\w-]+)/(?P<commit_id>\w+)/analysis/$",
        views.analysis, name="analysis"),
    # analysis commit
)
