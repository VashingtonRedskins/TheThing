from django.conf.urls import url, patterns
from octonyan import views

urlpatterns = patterns(
    "",
    url(r"^$", views.index, name='index'),
    url(r"^init/$", views.init_repo, name="init_repo"),
    url(r"^repo/(?P<repo>\w+)/$", views.repository, name="repository"),
)
