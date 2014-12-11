# coding: utf-8
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.conf import settings
from django.template import RequestContext
from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormView, FormMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.dispatch import receiver
from os import path
from dulwich import repo, diff_tree
from difflib import unified_diff

from octonyan import utils
from octonyan.dao import get_cmmt_by_hash, get_by_dir_name, get_repos, \
    get_comm_by_rep, get_committer_by_rep, get_commit_by_rep_commit_id
from octonyan.forms import InitRepositoryForm
from analysis.tasks import create_repo, analysis
from registration.backends.default.views import ActivationView
from registration.signals import user_activated


@receiver(user_activated)
def login_on_activation(sender, user, request, **kwargs):
    """Logs in the user after activation"""
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)


def prepare_context(context, user):
    context["repos"] = get_repos(user)
    return context


class OctonyanActivationView(ActivationView):
    """ Override success_url by ActivationView. """

    def get_success_url(self, request, user):
        """ Redirect to dashboard after activation."""
        return "/octonyan/"


class LoginRequiredView(View, TemplateResponseMixin):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(LoginRequiredView, self).get_context_data(**kwargs)
        context['repos'] = get_repos(self.request.user)
        return context


class InitRepositoryView(FormView):
    """Getting form to add new repository"""

    template_name = "octonyan/init_form.html"
    form_class = InitRepositoryForm
    success_url = "/octonyan/"

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        create_repo.delay(
            form.cleaned_data['repository_url'],
            form.cleaned_data['dir_name'], form.cleaned_data['to_fetch'],
            self.request.user
        )
        return super(InitRepositoryView, self).form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FormView, self).dispatch(*args, **kwargs)


class IndexRepository(LoginRequiredView, FormMixin):
    template_name = 'octonyan/index.html'
    # form_class = CreateForm
    success_url = reverse_lazy("octonyan:index")

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(), **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IndexRepository, self).get_context_data(**kwargs)
        # context['form'] = self.get_form(self.get_form_class(), **kwargs)
        return context


    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        return self.get(self.request)


@login_required
def show_repository(request, dir_name):
    """View basic commits information"""
    commits = get_comm_by_rep(dir_name)
    committers = get_committer_by_rep(dir_name)

    context = {
        "committers": committers,
        "commits": commits,
        "repo": dir_name,
    }
    context = prepare_context(context, request.user)

    return render(
        request,
        "octonyan/detail.html",
        context
    )


class ShowRepository(LoginRequiredView, FormMixin):
    template_name = 'octonyan/detail.html'
    # form_class = CreateForm
    success_url = reverse_lazy("octonyan:index")

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(), **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShowRepository, self).get_context_data(**kwargs)
        context['commits'] = get_comm_by_rep(self.kwargs['dir_name'])
        context['committers'] = get_committer_by_rep(self.kwargs['dir_name'])
        context['dir_name'] = self.kwargs['dir_name']
        return context


    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return HttpResponseRedirect(self.success_url)

    def form_invalid(self, form):
        return self.get(self.request)


# TODO refactoring and change
@login_required
def show_commit(request, dir_name, commit_id, files_extenshion=None):
    """Return changes make in current commit

    data -- include blocks code of each modify files.

    """
    commit = get_commit_by_rep_commit_id(dir_name, commit_id)
    pth = path.join(settings.REPOS_PATH, dir_name)
    repository = repo.Repo(pth)
    data = []
    # used encode('latin-1') below to solve some problem with unicode
    # and bytestring
    commit = repository[commit_id.encode('latin-1')]
    if len(commit.parents) == 0:
        parent = None
    else:
        parent = repository[commit.parents[0]].tree

    delta = diff_tree.tree_changes(repository, parent, commit.tree)

    for item in delta:
        block = []
        old = ""
        if item.old.sha:
            old = repository[item.old.sha].data.split("\n")

        new = repository[item.new.sha].data.split("\n")
        for line in unified_diff(old, new):
            block.append(line)

        data.append(
            (item.old.path, item.new.path, block)
        )
    context = {'data': data}
    context = prepare_context(context, request.user)

    return render(request, "octonyan/commit_info.html", context)


# TODO refactoring and change
@login_required
def analysis(request, dir_name, commit_id):
    pth = path.join(settings.REPOS_PATH, dir_name)
    repository = repo.Repo(pth)
    # used encode('latin-1') below to solve some problem with unicode
    # and bytestring
    repository["HEAD"] = commit_id.encode('latin-1')
    repository._build_tree()
    analysis.delay(commit_id, dir_name)
    report = utils.check_source(pth)
    context = {"report": report, "repo": dir_name}
    context = prepare_context(context, request.user)
    return render(request, "octonyan/analysis.html",
                  context)


def handler404(request):
    response = render_to_response('octonyan/404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response
