from django.conf.urls import url, patterns
from octonyan import views

urlpatterns = patterns(
    "",
    url(r"^$", views.RepositoriesListView.as_view(), name='index'),
    url(r'^page(?P<page>\d+)/$', views.RepositoriesListView.as_view()),
    url(r"^add/repo$", views.InitRepositoryView.as_view(), name="init_repo"),
    url(r"^repo/(?P<dir_name>\w[\w-]+)$",
        views.get_statistic_repository, name="repository"),
    url(r"^repo/(?P<dir_name>\w[\w-]+)/(?P<commit_id>\w+)/analysis$",
        views.analysis, name="analysis"),
)
