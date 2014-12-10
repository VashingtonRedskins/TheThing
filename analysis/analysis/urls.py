from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from django.views.generic.base import RedirectView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView
from octonyan.views import OctonyanActivationView, handler404


urlpatterns = patterns(
    '',
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/activate/complete/$',
        RedirectView.as_view(url="/octonyan/")),
    url(r'^accounts/register/complete/$',
        TemplateView.as_view(
            template_name="registration/registration_complete.html")),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/accounts/login/'}, name="logout"),
    url(r'^accounts/activate/(?P<activation_key>w+)/$',
        OctonyanActivationView.as_view()),
    url(r'^accounts/register',
        RegistrationView.as_view(
            form_class=RegistrationFormUniqueEmail,
            template_name="registration/registration.html")),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^octonyan/',
        include('octonyan.urls', namespace="octonyan")),
)
handler404 = handler404


from django.conf import settings

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)', 'serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
