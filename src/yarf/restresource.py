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

import inspect
import six
from flask import request
from flask_restful import reqparse
from werkzeug.exceptions import BadRequest

from yarf.baseresource import BaseResource

class RequestArgument(object):
    """ More advanced arguments
        Parameters:
            name: Name of the argument
            default: The default value if not defined
            validate: function pointer to a validation function that will
                      be called to validate the argument.
                      The function should return tuple containing
                      status: (boolean) True if validation passed
                                        False if not
                      reason: (string) Setting the reasoning for the
                                       failure
            typeof: The typeof the argument. The argument will be converted
                    to the type you define. Should be a function pointer
    """
    def __init__(self, name, default=None, validate=None, typeof=lambda x: six.text_type(x)):
        self.argument_class = reqparse.Argument(name=name, default=default, type=typeof)
        if validate and inspect.isfunction(validate):
            self.validate_func = validate
        else:
            self.validate_func = None
        self.name = name

    def validate(self, value):
        if not self.validate_func:
            return
        status, reason = self.validate_func(value)
        if not status:
            raise BadRequest(description=reason)

class RestResource(BaseResource):
    """ Class from which the plugins should inherit
        Variables:
        extra_wrappers: are function wrappers that will
                        be executed when any function is
                        executed by the frame (for example
                        get)
        parser_arguments: Are the arguments that can be defined
                          if you need arguments for your plugin
                          these arguments can be fetched with
                          get_args
    """
    extra_wrappers = []
    parser_arguments = []
    endpoints = None
    int_arg_class = RequestArgument

    """ Function to get arguments from request
        The function will call validate to the
        arguments if they are of type RequestArgument
        Returns: A dictionary of the arguments
    """
    @classmethod
    def get_args(cls):
        args = cls.parser.parse_args()
        for arg in args.keys():
            for parg in cls.parser_arguments:
                if isinstance(parg, cls.int_arg_class) and parg.name == arg:
                    parg.validate(args[arg])
        return args

    @classmethod
    def get_token(cls):
        token = ""
        try:
            token = request.headers.get("X-Auth-Token", type=str)
        except KeyError as err:
            cls.logger.info("Failed to get auth token from request.")
        return token

