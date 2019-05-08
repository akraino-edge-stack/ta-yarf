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

from flask import request
from yarf.restresource import RestResource


class APIHandler(RestResource):
    apis = set()
    authentication_method = None
    def create_api_reference(self):
        ref = []
        for api in self.apis:
            ver = {}
            ver['api'] = api
            ver['href'] = "%s%s" %(request.host_url, api)
            ref.append(ver)
        return ref
    def get(self):
        return self.create_api_reference()
