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

import configparser
from yarf.exceptions import ConfigError


class INILoader(dict):
    def __init__(self, inifile, defaults=None, defaultsection=None):
        super(INILoader, self).__init__(self)
        self.inifile = inifile
        self.handlers = 'handlers'
        self.configparser = configparser.ConfigParser(defaults)
        self.config = self.configparser.read(inifile)
        self.defaultsection = defaultsection
        if inifile not in self.config:
            raise ConfigError("Failed to read config file: %s" % inifile)

    def get_sections(self):
        return self.configparser.sections()

    def get_handlers(self, section):
        return self[section][self.handlers].split(',')

    def __getitem__(self, key):
        try:
            return self.configparser[key]
        except KeyError:
            raise ConfigError("No such key %s" % key)

    def get(self, key, section=None, type_of_value=str):
        if section is None and self.defaultsection is not None:
            section = self.defaultsection
        else:
            return None

        if type_of_value is int:
            return self.configparser.getint(section, key)
        elif type_of_value is bool:
            return self.configparser.getboolean(section, key)
        elif type_of_value is float:
            return self.configparser.getfloat(section, key)
        return self.configparser.get(section, key)

    def keys(self):
        return self.configparser.sections()

    def get_section(self, section, format='list'):
        if section in self.keys():
            items = self.configparser.items(section)
            if format == 'dict':
                return dict(items)
            return items
        return None
