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

# TODO(amotoki): Remove this file at the beginning of Nxx cycle.

from debtcollector import moves

from neutronclient import _i18n

message = ("moved to neutronclient._i18n; please migrate to local "
           "oslo_i18n usage, as defined at "
           "http://docs.openstack.org/developer/oslo.i18n/usage.html")

_ = moves.moved_function(_i18n._, '_', __name__, message=message)
_LC = moves.moved_function(_i18n._LC, '_LC', __name__, message=message)
_LE = moves.moved_function(_i18n._LE, '_LE', __name__, message=message)
_LW = moves.moved_function(_i18n._LW, '_LW', __name__, message=message)
_LI = moves.moved_function(_i18n._LI, '_LI', __name__, message=message)
