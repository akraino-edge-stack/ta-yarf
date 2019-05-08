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

import logging
import logging.handlers
restlogger = None


class RestfulLogger(object):
    def __init__(self):
        self.logger = logging.getLogger("Restfulserver")
        self.logger.setLevel(logging.DEBUG)
        # werkzug logs out endpoint in DEBUG level, and aaa feature endpoint contains password
        # in clear text, so log level setting is needed to avoid showing password in journalctl
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        self.handlers = []
        self.sysloghandler = self._get_syslog_handler()
        self.handlers.append(self.sysloghandler)
        self._add_handlers()

    def __del__(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    @staticmethod
    def _get_syslog_handler():
        sh = logging.handlers.SysLogHandler(address='/dev/log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        sh.setFormatter(formatter)
        sh.setLevel(logging.NOTSET)
        return sh

    def _add_handlers(self):
        for handler in self.handlers:
            self.logger.addHandler(handler)

    def get_handlers(self):
        return self.handlers

    def get_logger(self):
        return self.logger

def get_logger():
    global restlogger
    if not restlogger:
        restlogger = RestfulLogger()
    return restlogger.get_logger()

def get_log_handlers():
    global restlogger
    if not restlogger:
        restlogger = RestfulLogger()
    return restlogger.get_handlers()
