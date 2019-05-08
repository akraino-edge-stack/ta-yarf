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

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneclient.v3.tokens import TokenManager
from keystoneauth1.exceptions.http import Unauthorized, NotFound

import yarf.restfullogger as logger

from yarf.authentication.base_auth import BaseAuthMethod
from yarf.restfulargs import RestConfig


class KeystoneAuth(BaseAuthMethod):
    def __init__(self):
        super(KeystoneAuth, self).__init__()
        self.logger = logger.get_logger()
        config = RestConfig()
        config.parse()
        conf = config.get_section("keystone", format='dict')
        try:
            self.user = conf["user"]
            self.password = conf["password"]
            self.uri = conf["auth_uri"] + '/v3'
            self.domain = "default"
        except KeyError as error:
            self.logger.error("Failed to find all the needed parameters. Authentication with Keystone not possible: {}"
                              .format(str(error)))
        self.auth = v3.Password(auth_url=self.uri,
                                username=self.user,
                                password=self.password,
                                user_domain_id=self.domain)
        self.sess = session.Session(auth=self.auth)
        self.keystone = client.Client(session=self.sess)
        self.tokenmanager = TokenManager(self.keystone)

    def get_authentication(self, req):
        try:
            token = req.headers.get("X-Auth-Token", type=str)
        except KeyError:
            self.logger.error("Failed to get the authentication token from request")
            return (False, "")

        try:
            tokeninfo = self.tokenmanager.validate(token)
        except Unauthorized:
            self.logger.error("Failed to authenticate with given credentials")
            return (False, "")
        except NotFound:
            self.logger.error("Unauthorized token")
            return (False, "")
        except Exception as error:
            self.logger.error("Failure: {}".format(str(error)))
            return (False, "")

        if 'admin' in tokeninfo.role_names:
            return (True, 'admin')
        return (False, "")
