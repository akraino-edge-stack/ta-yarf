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

import os
import os.path
import sys
import inspect
from yarf.iniloader import INILoader
from yarf.restresource import RestResource
from yarf.versionhandler import VersionHandler
from yarf.authentication.base_auth import BaseAuthMethod
from yarf.exceptions import ConfigError
import yarf.restfullogger as restlog

class PluginLoader(object):
    def __init__(self, path, api, auth_method):
        self.logger = restlog.get_logger()
        self.plugin_class_type = RestResource
        self.auth_method = self._get_auth_method(auth_method)
        self.path = path
        self.api = api

    def get_module_dirs(self):
        files = os.listdir(self.path)
        modules = []
        for f in files:
            if os.path.isdir("%s/%s"%(self.path, f)):
                modules.append("%s/%s"%(self.path, f))
        return modules

    def _get_auth_method(self, authmethod):
        auth_class_module = None
        class_name = None
        try:
            auth_class_module, class_name = authmethod.rsplit('.', 1)
        except ValueError:
            error = "Cannot decode the authentication method from configuration file"
            self.logger.error(error)
            raise ConfigError(error)
        auth_classes = self._get_classes_wanted_classes(auth_class_module, [class_name], BaseAuthMethod)
        if auth_classes is None or auth_classes == []:
            error = "Cannot find the authentication class in provided module %s %s" % (auth_class_module, class_name)
            raise ConfigError(error)
        return auth_classes[0]

    def _get_classes_wanted_classes(self, module_name, wanted_modules, class_type):
        classes = []
        try:
            __import__(module_name)
        except ImportError:
            self.logger.error("Failed import in %s, skipping", module_name)
            return None
        module = sys.modules[module_name]
        for obj_name in dir(module):
            # Skip objects that are meant to be private.
            if obj_name.startswith('_'):
                continue
            # Skip the same name that base class has
            elif obj_name == class_type.__name__:
                continue
            elif obj_name not in wanted_modules:
                continue
            itm = getattr(module, obj_name)
            if inspect.isclass(itm) and issubclass(itm, class_type):
                classes.append(itm)
        return classes

    def get_classes_from_dir(self, directory, wanted_modules):
        classes = []
        if directory not in sys.path:
            sys.path.append(directory)
        for fname in os.listdir(directory):
            root, ext = os.path.splitext(fname)
            if ext != '.py' or root == '__init__':
                continue
            module_name = "%s" % (root)

            mod_classes = self._get_classes_wanted_classes(module_name, wanted_modules, self.plugin_class_type)
            if mod_classes:
                classes.extend(mod_classes)
        return classes

    def get_modules_from_dir(self, module_dir):
        modules = {}
        for f in os.listdir(module_dir):
            if not f.endswith(".ini"):
                continue
            root, _ = os.path.splitext(f)
            loader = INILoader("%s/%s" %(module_dir, f))
            sections = loader.get_sections()
            modules[root] = {}
            for section in sections:
                handlers = loader.get_handlers(section)
                if handlers:
                    modules[root][section] = handlers
                else:
                    self.logger.error("Problem in the configuration file %s in section %s: No handlers found", f, section)
        return modules

    def get_auth_method(self):
        return self.auth_method()

    def get_modules(self):
        dirs = self.get_module_dirs()
        auth_class = self.auth_method()
        modules = []
        for d in dirs:
            wanted_modules = self.get_modules_from_dir(d)
            for mod in wanted_modules.keys():
                for api_version in wanted_modules[mod].keys():
                    classes = self.get_classes_from_dir(d, wanted_modules[mod][api_version])
                    if not classes:
                        continue
                    for c in classes:
                        setattr(c, "subarea", mod)
                        if getattr(c, "authentication_method", "EMPTY") == "EMPTY":
                            setattr(c, "authentication_method", auth_class)
                        if getattr(c, "api_versions", None):
                            c.api_versions.append(api_version)
                        else:
                            setattr(c, "api_versions", [api_version])
                    for cls in classes:
                        if cls not in modules:
                            modules.append(cls)
        return modules

    def create_endpoints(self, handler):
        endpoint_list = []
        for endpoint in handler.endpoints:
            for api_version in handler.api_versions:
                self.logger.debug("Registering /%s/%s/%s for %s", handler.subarea, api_version, endpoint, handler.__name__)
                endpoint_list.append("/%s/%s/%s"% (handler.subarea, api_version, endpoint))
        self.api.add_resource(handler, *(endpoint_list))

    def add_logger(self, handler):
        self.logger.info("Adding logger to: %s", handler.__name__)
        handler.logger = self.logger

    def init_handler(self, handler):

        self.add_logger(handler)
        handler.add_wrappers()
        self.create_endpoints(handler)
        handler.add_parser_arguments()

    def create_api_versionhandlers(self, handlers):
        apiversions = {}
        endpoint_list = []
        for handler in handlers:
            subarea = handler.subarea
            if apiversions.get(subarea, False):
                for hapiversion in handler.api_versions:
                    if hapiversion not in apiversions[subarea]:
                        apiversions[subarea].append(hapiversion)
            else:
                apiversions[subarea] = handler.api_versions
                self.logger.debug("Registering /%s/apis for %s", subarea, subarea)
                endpoint_list.append("/%s/apis" % subarea)
        setattr(VersionHandler, "versions", apiversions)
        setattr(VersionHandler, "method_decorators", [])
        self.api.add_resource(VersionHandler, *(endpoint_list))
