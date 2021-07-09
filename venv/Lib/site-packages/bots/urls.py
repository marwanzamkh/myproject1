# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from django.contrib import admin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import views as auth_views

from . import views

if django.get_version() > '2':
    from django.urls import re_path

    urlpatterns = [
        # Auth
        re_path(r'^login.*', auth_views.LoginView.as_view(
            template_name='admin/login.html'),
            name='login',
        ),
        re_path(r'^logout.*', auth_views.LogoutView.as_view(
            next_page='/'),
            name='logout',
        ),
        re_path(r'^password_change/$', auth_views.PasswordResetView.as_view(),
                name='password_change'),
        re_path(r'^password_change/done/$', auth_views.PasswordResetDoneView.as_view(),
                name='password_change_done'),
    ]
else:
    from django.conf.urls import url as re_path

    urlpatterns = [
        # Auth
        re_path(
            r'^login.*', auth_views.login,
            {'template_name': 'admin/login.html'},
            name='login'),
        re_path(
            r'^logout.*', auth_views.logout,
            {'next_page': '/'},
            name='logout'),
        re_path(
            r'^password_change/$', auth_views.password_change,
            name='password_change'),
        re_path(
            r'^password_change/done/$', auth_views.password_change_done,
            name='password_change_done'),
    ]

staff_required = user_passes_test(lambda u: u.is_staff)
superuser_required = user_passes_test(lambda u: u.is_superuser)
run_permission = user_passes_test(lambda u: u.has_perm('bots.change_mutex'))

urlpatterns += [
    # login required
    re_path(r'^home.*', login_required(views.home)),
    re_path(r'^incoming.*', login_required(views.incoming)),
    re_path(r'^detail.*', login_required(views.detail)),
    re_path(r'^process.*', login_required(views.process)),
    re_path(r'^outgoing.*', login_required(views.outgoing)),
    re_path(r'^document.*', login_required(views.document)),
    re_path(r'^reports.*', login_required(views.reports)),
    re_path(r'^confirm.*', login_required(views.confirm)),
    re_path(r'^filer.*', login_required(views.filer)),
    re_path(r'^srcfiler.*', login_required(views.srcfiler)),
    re_path(r'^logfiler.*', login_required(views.logfiler)),
    # only staff
    # do not show django admin root page
    re_path(r'^admin/$', login_required(views.home)),
    # do not show django admin root page
    re_path(r'^admin/bots/$', login_required(views.home)),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^runengine.+', run_permission(views.runengine)),
    # only superuser
    re_path(r'^delete.*', superuser_required(views.delete)),
    re_path(r'^plugin/index.*', superuser_required(views.plugin_index)),
    re_path(r'^plugin.*', superuser_required(views.plugin)),
    re_path(r'^plugout/index.*', superuser_required(views.plugout_index)),
    re_path(r'^plugout/backup.*', superuser_required(views.plugout_backup)),
    re_path(r'^plugout.*', superuser_required(views.plugout)),
    re_path(r'^sendtestmail.*', superuser_required(views.sendtestmailmanagers)),
    # catch-all
    re_path(r'^.*', views.index),
]

handler500 = 'bots.views.server_error'
