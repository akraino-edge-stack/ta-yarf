# Copyright 2019 Nokia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import logging
import socket
from OpenSSL import SSL
from flask import Flask, request
from flask_restful import Api
from werkzeug.exceptions import InternalServerError
from yarf.handlers.pluginhandler import PluginLoader
from yarf.iniloader import ConfigError
import yarf.restfulargs as restfulconfig
import yarf.restfullogger as restlog
from yarf.helpers import remove_secrets

CRIT_RESP_LEN = 150000

app = Flask(__name__)
api = Api(app)
auth_method = None

def handle_excp(failure):
    if isinstance(failure, socket.error):
        app.logger.warning("Socket error, ignoring")
        return
    elif failure:
        app.logger.error("Internal error: %s ", failure)
    else:
        app.logger.info("Failure not defined... Ignoring.")
        return
    raise InternalServerError()

def get_config(args, logger):
    try:
        config = restfulconfig.RestConfig()
        if args:
            config.parse(sys.argv[1:])
        else:
            config.parse()
    except ConfigError as error:
        logger.error("Failed to start %s" % error)
        return None
    return config

def request_logger():
    app.logger.info('Request: remote_addr: %s method: %s endpoint: %s, user: %s', request.remote_addr,
                    request.method, remove_secrets(request.full_path), get_username())

def response_logger(response):
    app.logger.info('Response: status: %s (Associated Request: remote_addr: %s, method: %s, endpoint: %s, user: %s)',
                    response.status, request.remote_addr, request.method,
                    remove_secrets(request.full_path), get_username())

    if len(response.data) > CRIT_RESP_LEN:
        app.logger.debug('Response\'s data is too big, truncating!')
        app.logger.debug('Response\'s truncated data: %s', response.data[:CRIT_RESP_LEN])
    else:
        app.logger.debug('Response\'s data: %s', response.data)

    response.headers["Server"] = "Restapi"

    return response

def get_username():
    try:
        return auth_method.get_authentication(request)[1]
    except Exception as err: # pylint: disable=broad-except
        app.logger.warn("Failed to get username from request returning empty. Err: %s", str(err))
    return ''


def initialize(config, logger):
    logger.info("Initializing...")
    loglevel = logging.INFO if not config.get_debug() else logging.DEBUG
    app.logger.setLevel(loglevel)
    app.register_error_handler(Exception, handle_excp)
    app.before_request(request_logger)
    app.after_request(response_logger)
    logger.error("%s", config.get_handler_dir())
    p = PluginLoader(config.get_handler_dir(), api, config.get_auth_method())
    auth_handler = p.get_auth_method()
    handlers = p.get_modules()
    for handler in handlers:
        p.init_handler(handler)

    for handler in restlog.get_log_handlers():
        app.logger.addHandler(handler)
    p.create_api_versionhandlers(handlers)
    logger.info("Starting up...")


def get_wsgi_application():
    logger = restlog.get_logger()
    config = get_config(None, logger)
    initialize(config, logger)
    return app

def main():
    logger = restlog.get_logger()
    config = get_config(sys.argv[1:], logger)
    if not config:
        raise ConfigError("Failed to read config file")
    initialize(config, logger)
    run_params = {}
    run_params["debug"] = config.get_debug()
    run_params["port"] = config.get_port()
    run_params["host"] = config.get_ip()
    # When this https://github.com/pallets/werkzeug/issues/954 is fixed then the error handling
    # can be done in the error handler of app level
    passthrough_errors = config.get_passthrough_errors()
    run_params["passthrough_errors"] = passthrough_errors
    run_params["threaded"] = config.is_threaded()
    logger.debug("%s %s %s", run_params["debug"], run_params["port"], run_params["threaded"])
    if config.use_ssl():
        context = SSL.Context(SSL.SSLv23_METHOD)
        context.use_privatekey_file(config.get_private_key())
        context.use_certificate_file(config.get_certificate())
        run_params['ssl_context'] = context
    while True:
        try:
            app.run(**run_params)
        except Exception as err: # pylint: disable=broad-except
            logger.warning("Caught exception but starting again %s", err)
            if passthrough_errors:
                handle_excp(err)
            else:
                raise err
            logger.warning("Die in piece %s", err)
            func = request.environ.get('werkzeug.server.shutdown')
            if func is None:
               raise RuntimeError('Not running with the Werkzeug Server')
            func()

    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:# pylint: disable=broad-except
        print "Failure: %s" % error
        sys.exit(255)
