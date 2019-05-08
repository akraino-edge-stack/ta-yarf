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

def get_api(req):
    splitted = req.full_path.split("/")
    domain = splitted[1]
    return domain

class VersionHandler(RestResource):
    versions = {}

    def create_api_reference(self, api):
        ref = []
        for version in self.versions[api]:
            ver = {}
            ver['id'] = version
            ver['href'] = "%s%s/%s" %(request.host_url, api, version)
            ref.append(ver)
        return ref

    def get(self):
        api = get_api(request)
        return self.create_api_reference(api)
