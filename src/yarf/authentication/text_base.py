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

from yarf.authentication.base_auth import BaseAuthMethod

class TextBase(BaseAuthMethod):
    def __init__(self):
        super(TextBase, self).__init__()
        self.user = ''
        self.password = ''
        with open('/tmp/foo') as f:
            self.user, self.password = f.read().strip().split(':')

    def get_authentication(self, req):
        if req.authorization and req.authorization.username == self.user and req.authorization.password == self.password:
            return (True, "")
        return (False, "")
