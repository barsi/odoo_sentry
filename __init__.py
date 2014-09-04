# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo - Sentry connector
#    Copyright (C) 2014 Mohammed Barsi.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import traceback
import logging
import sys
import openerp.service.wsgi_server
import openerp.addons.web.controllers.main
import openerp.addons.report.controllers.main
import openerp.http
import openerp.tools.config as config
import openerp.osv.osv
import openerp.exceptions
from openerp.http import request
from raven import Client
from raven.handlers.logging import SentryHandler
from raven.middleware import Sentry
from raven.conf import setup_logging, EXCLUDE_LOGGER_DEFAULTS


_logger = logging.getLogger(__name__)


CLIENT_DSN = config.get('sentry_client_dsn', '').strip()
ENABLE_LOGGING = config.get('sentry_enable_logging', False)
ALLOW_ORM_WARNING = config.get('sentry_allow_orm_warning', False)
INCLUDE_USER_CONTEXT = config.get('sentry_include_context', False)

def get_user_context():
    '''
        get the current user context, if possible
    '''
    cxt = {}
    session = getattr(request, 'session', {})
    cxt.update({
        'session': {
            'context': session.get('context', {}),
            'db': session.get('db', None),
            'login': session.get('login', None),
            'password': session.get('uid', None),
        },
    })
    return cxt


def serialize_exception(e):
    '''
        overrides `openerp.http.serialize_exception`
        in order to log orm exceptions.
    '''
    if isinstance(e, (
        openerp.osv.osv.except_osv,
        openerp.exceptions.Warning,
        openerp.exceptions.AccessError,
        openerp.exceptions.AccessDenied,
        )):
        if INCLUDE_USER_CONTEXT:
            client.extra_context(get_user_context())
        client.captureException(sys.exc_info())
    return openerp.http.serialize_exception(e)


class ContextSentryHandler(SentryHandler):
    '''
        extends SentryHandler, to capture logs only if 
        `sentry_enable_logging` config options set to true
    '''
    def emit(self, rec):
        if INCLUDE_USER_CONTEXT:
            client.extra_context(get_user_context())
        super(ContextSentryHandler, self).emit(rec)



client = Client(CLIENT_DSN)


if ENABLE_LOGGING:
    # future enhancement: add exclude loggers option
    EXCLUDE_LOGGER_DEFAULTS += ('werkzeug', )
    handler = ContextSentryHandler(client)
    setup_logging(handler, exclude=EXCLUDE_LOGGER_DEFAULTS)

if ALLOW_ORM_WARNING:
    openerp.addons.web.controllers.main._serialize_exception = serialize_exception
    openerp.addons.report.controllers.main._serialize_exception = serialize_exception

# wrap the main wsgi app
openerp.service.wsgi_server.application = Sentry(openerp.service.wsgi_server.application, client=client)

if INCLUDE_USER_CONTEXT:
    client.extra_context(get_user_context())
# fire the first message
client.captureMessage('Starting Odoo Server')
