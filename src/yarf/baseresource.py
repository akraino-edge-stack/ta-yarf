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

from flask_restful import Resource, reqparse
from yarf.authentication.base_auth import login_required

class BaseResource(Resource):
    # THESE VALUES ARE FILLED BY THE FRAMEWORK
    method_decorators = None
#   authentication_method = None
    api_versions = []
    subarea = "none"
    parser = None
    logger = None
    
    # USED INTERNALLY ONLY
    @classmethod
    def add_wrappers(cls):
        cls.method_decorators = [login_required]
        for extra_wrapper in cls.extra_wrappers:
            if extra_wrapper not in cls.method_decorators:
                cls.logger.debug("Adding wrapper %s", extra_wrapper)
                cls.method_decorators.append(extra_wrapper)
            else:
                cls.logger.debug("Not added %s", extra_wrapper)

    @classmethod
    def add_parser_arguments(cls):
        cls.parser = reqparse.RequestParser()
        for argument in cls.parser_arguments:
            if isinstance(argument, cls.int_arg_class):
                cls.parser.add_argument(argument.argument_class)
            else:
                cls.parser.add_argument(argument)
