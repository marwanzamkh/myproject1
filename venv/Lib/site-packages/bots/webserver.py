#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import os
import sys
try:
    from cheroot.server import get_ssl_adapter_class
    from cheroot.wsgi import Server, PathInfoDispatcher
except ImportError:
    from cherrypy.wsgiserver import (
        get_ssl_adapter_class,
        CherryPyWSGIServer as Server,
        WSGIPathInfoDispatcher as PathInfoDispatcher
    )
import cherrypy
from django.core import management
from django.core.handlers.wsgi import WSGIHandler
from django.utils.translation import ugettext as _

from . import botsinit, botsglobal


def start():
    # NOTE: bots directory should always be on PYTHONPATH - otherwise it will not start.
    # ***command line arguments**************************
    usage = """
    This is "%(name)s" version %(version)s,
    part of Bots open source edi translator (http://bots.sourceforge.net).
    The %(name)s is the web server for bots; the interface (bots-monitor) can be accessed in a
    browser, eg 'http://localhost:8080'.
    Usage:
        %(name)s  -c<directory>
    Options:
        -c<directory>   directory for configuration files (default: config).

    """ % {'name': os.path.basename(sys.argv[0]), 'version': botsglobal.version}
    configdir = 'config'
    for arg in sys.argv[1:]:
        if arg.startswith('-c'):
            configdir = arg[2:]
            if not configdir:
                print('Error: configuration directory indicated, but no directory name.')
                sys.exit(1)
        else:
            print(usage)
            sys.exit(0)
    # ***end handling command line arguments**************************
    # find locating of bots, configfiles, init paths etc.
    botsinit.generalinit(configdir)
    settings = botsglobal.settings
    process_name = 'webserver'
    # initialise file-logging for web-server.
    # This logging only contains the logging from bots-webserver, not from cherrypy.
    botsglobal.logger = botsinit.initserverlogging(process_name)

    # ***init cherrypy as webserver*********************************************
    # global configuration for cherrypy
    cherrypy.config.update({
        'global': {
            'log.screen': False,
            'server.environment': botsglobal.ini.get('webserver', 'environment', 'production')
        }
    })

    # /static
    static_root = settings.STATIC_ROOT.rstrip(os.path.sep)
    if not os.path.isdir(static_root) and not os.access(os.path.dirname(static_root), os.W_OK):
        botsglobal.logger.warning(_('Invalid STATIC_ROOT: %s' % settings.STATIC_ROOT))
    else:
        management.call_command('collectstatic', '--noinput')

    # cherrypy handling of static files
    staticdir = settings.STATIC_ROOT.split(os.sep)
    conf = {'/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': staticdir[-1],
        'tools.staticdir.root': os.sep.join((staticdir[:-1])),
    }}
    # None: no cherrypy application (as this only serves static files)
    servestaticfiles = cherrypy.tree.mount(None, settings.STATIC_URL.rstrip('/'), conf)

    # cherrypy handling of django
    servedjango = WSGIHandler()
    # cherrypy uses a dispatcher in order to handle the serving of static files and django.
    # UNICODEPROBLEM: needs to be binary
    dispatcher = PathInfoDispatcher({
        '/': servedjango,
        str(settings.STATIC_URL.rstrip('/')): servestaticfiles})
    botswebserver = Server(
        bind_addr=('0.0.0.0', botsglobal.ini.getint('webserver', 'port', 8080)),
        wsgi_app=dispatcher,
        server_name=botsglobal.ini.get('webserver', 'name', 'bots-webserver'))
    botsglobal.logger.log(
        25, _('Bots %(process_name)s started.'),
        {'process_name': process_name})
    botsglobal.logger.log(
        25, _('Bots %(process_name)s configdir: "%(configdir)s".'),
        {'process_name': process_name, 'configdir': botsglobal.ini.get('directories', 'config')})
    botsglobal.logger.log(
        25, _('Bots %(process_name)s serving at port: "%(port)s".'),
        {
            'process_name': process_name,
            'port': botsglobal.ini.getint('webserver', 'port', 8080)
        })
    ssl_certificate = botsglobal.ini.get('webserver', 'ssl_certificate', None)
    ssl_private_key = botsglobal.ini.get('webserver', 'ssl_private_key', None)
    if ssl_certificate and ssl_private_key:
        adapter_class = get_ssl_adapter_class('builtin')
        botswebserver.ssl_adapter = adapter_class(ssl_certificate, ssl_private_key)
        botsglobal.logger.log(
            25, _('Bots %(process_name)s uses ssl (https).'),
            {'process_name': process_name})
    else:
        botsglobal.logger.log(
            25, _('Bots %(process_name)s uses plain http (no ssl).'),
            {'process_name': process_name})

    # start the cherrypy webserver.************************************************
    try:
        botswebserver.start()
    except KeyboardInterrupt:
        botswebserver.stop()


if __name__ == '__main__':
    start()
