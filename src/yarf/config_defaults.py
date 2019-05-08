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

default_config_file = "/etc/yarf/config.ini"
default_section = "restframe"
config_defaults = {"port":"61200", "ip_address": "127.0.0.1", "use_ssl": "False", "handler_directory": '/usr/lib/python2.7/site-packages/yarf/handlers/', "threaded": "True", "passthrough_errors": "True"}
