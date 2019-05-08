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

import argparse
import sys

import yarf.config_defaults as config_defaults
import yarf.restfullogger as restfullogger

from yarf.iniloader import INILoader
from yarf.exceptions import ConfigError


def exception_handler(func):
    def exception_wrapper(*args, **kwargs):
        try:
            restlogger = restfullogger.get_logger()
            restlogger.debug("calling {}".format(func.__name__))
            ret = func(*args, **kwargs)
            return ret
        except Exception as error:
            restlogger.info("Exception from function {} (error: {})".format(func.__name__, str(error)))
            if isinstance(error, ConfigError):
                raise error
            else:
                raise ConfigError(str(error))
    return exception_wrapper


class RestConfig(object):
    __restinstance = None

    def __new__(cls):
        if RestConfig.__restinstance is None:
            RestConfig.__restinstance = object.__new__(cls)
        return RestConfig.__restinstance

    def __init__(self):
        self.default_section = config_defaults.default_section
        self.config_default = config_defaults.config_defaults
        self.default_config_file = config_defaults.default_config_file

        self.config = None
        self.config_file = None

    @exception_handler
    def parse(self, args=sys.argv[1:]):
        parser = argparse.ArgumentParser(description='Restful server')
        parser.add_argument('--config',
                            type=str,
                            default=self.default_config_file,
                            help="Configuration file",
                            dest='config_file')

        args = parser.parse_args(args)
        self.config_file = args.config_file
        self.config = INILoader(self.config_file, defaults=self.config_default, defaultsection=self.default_section)

    @exception_handler
    def get_port(self):
        return self.config.get('port', type_of_value=int)

    @exception_handler
    def get_ip(self):
        return self.config.get('ip_address')

    @exception_handler
    def use_ssl(self):
        return self.config.get('use_ssl', type_of_value=bool)

    @exception_handler
    def get_private_key(self):
        if self.use_ssl():
            return self.config.get('ssl_private_key')
        return None

    @exception_handler
    def get_certificate(self):
        if self.use_ssl():
            return self.config.get('ssl_certificate')
        return None

    @exception_handler
    def get_handler_dir(self):
        return self.config.get('handler_directory')

    def get_section(self, section, format='list'):
        return self.config.get_section(section, format=format)

    def get_debug(self):
        return self.config.get('debug', type_of_value=bool)

    @exception_handler
    def get_passthrough_errors(self):
        return self.config.get('passthrough_errors', type_of_value=bool)

    @exception_handler
    def is_threaded(self):
        return self.config.get('threaded', type_of_value=bool)

    @exception_handler
    def get_auth_method(self):
        return self.config.get('auth_method')


def get_config():
    return RestConfig()
