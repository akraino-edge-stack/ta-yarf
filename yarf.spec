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

Name:           yarf
Version:        %{_version}
Release:        1%{?dist}
Summary:        Yet Another Restfulframework
License:        %{_platform_licence}
Source0:        %{name}-%{version}.tar.gz
Vendor:         %{_platform_vendor}

Requires: python-flask, python2-flask-restful, python2-configparser, python2-requests, mod_wsgi, python2-six 
BuildRequires: python
BuildRequires: python-setuptools

%description
Yet Another Restfulframework.

%prep
#./autogen.sh
%autosetup

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}%{_platform_etc_path}/yarf
mkdir -p %{buildroot}%{_platform_etc_path}/required-secrets
mkdir -p %{buildroot}%{_unitdir}/
mkdir -p %{buildroot}/var/log/restapi
cp required-secrets/*.yaml %{buildroot}/%{_platform_etc_path}/required-secrets
#mkdir -p {buildroot}/etc/httpd/conf.d/
#mkdir -p {buildroot}/var/www/yarf/

cd src && python setup.py install --root %{buildroot} --no-compile --install-purelib %{_python_site_packages_path} --install-scripts %{_platform_bin_path} && cd -

rsync -rv systemd/* %{buildroot}%{_unitdir}/

%files
%defattr(0755,root,root,0755)
%{_python_site_packages_path}/yarf*
%attr(0755,restapi, restapi) %{_platform_etc_path}/yarf/
%{_platform_etc_path}/required-secrets/restful.yaml
#/etc/ansible/roles/restful
#/opt/openstack-ansible/playbooks/yarf.yml
%attr(0755,root, root) %{_platform_bin_path}/restapi
# %attr(0644,root, root) %{_unitdir}/restapi.service
%attr(0644,root, root) %{_unitdir}/* 
%dir %attr(0770, restapi,restapi) /var/log/restapi

%pre
/usr/bin/getent passwd restapi > /dev/null||/usr/sbin/useradd -r -s /sbin/nologin -M restapi

%post
if [ $1 -eq 2 ]; then
    if [ -f %{_platform_etc_path}/restful/config.ini ]; then
        sudo /usr/bin/systemctl restart restapi
    fi
fi

%postun

#Uninstall
if [ $1 -eq 0 ];then
    /usr/sbin/userdel restapi
fi
