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

from flask import abort, request
from functools import wraps

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_method = func.__self__.authentication_method
        if auth_method is None:
            return func(*args, **kwargs)

        if isinstance(auth_method, BaseAuthMethod) and auth_method.get_authentication(request)[0]:
            return func(*args, **kwargs)
        else:
            abort(401)
            return None
    return wrapper

class BaseAuthMethod(object):
    def __init__(self):
        pass
    def get_authentication(self, req):
        raise NotImplementedError("Function get_authentication not implemented")
