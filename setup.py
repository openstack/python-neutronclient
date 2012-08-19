# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 Citrix Systems
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import sys
import setuptools

from quantumclient.openstack.common import setup

Name = 'python-quantumclient'
Url = "https://launchpad.net/quantum"
Version = setup.get_post_version('quantumclient')
License = 'Apache License 2.0'
Author = 'OpenStack Quantum Project'
AuthorEmail = 'openstack-dev@lists.launchpad.net'
Maintainer = ''
Summary = 'CLI and python client library for OpenStack Quantum'
ShortDescription = Summary
Description = Summary

dependency_links = setup.parse_dependency_links()
tests_require = setup.parse_requirements(['tools/test-requires'])

EagerResources = [
]

ProjectScripts = [
]

PackageData = {
}


setuptools.setup(
    name=Name,
    version=Version,
    url=Url,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    scripts=ProjectScripts,
    dependency_links=dependency_links,
    install_requires=setup.parse_requirements(),
    tests_require=tests_require,
    cmdclass=setup.get_cmdclass(),
    include_package_data=False,
    packages=setuptools.find_packages('.'),
    package_data=PackageData,
    eager_resources=EagerResources,
    entry_points={
        'console_scripts': [
            'quantum = quantumclient.shell:main',
        ]
    },
)
