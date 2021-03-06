# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.parsing import DataLoader
from ansible.playbook.attribute import Attribute, FieldAttribute
from ansible.playbook.play import Play
from ansible.playbook.playbook_include import PlaybookInclude
from ansible.plugins import push_basedir


__all__ = ['Playbook']


class Playbook:

    def __init__(self, loader):
        # Entries in the datastructure of a playbook may
        # be either a play or an include statement
        self._entries = []
        self._basedir = os.getcwd()
        self._loader  = loader

    @staticmethod
    def load(file_name, variable_manager=None, loader=None):
        pb = Playbook(loader=loader)
        pb._load_playbook_data(file_name=file_name, variable_manager=variable_manager)
        return pb

    def _load_playbook_data(self, file_name, variable_manager):

        if os.path.isabs(file_name):
            self._basedir = os.path.dirname(file_name)
        else:
            self._basedir = os.path.normpath(os.path.join(self._basedir, os.path.dirname(file_name)))

        # set the loaders basedir
        self._loader.set_basedir(self._basedir)

        # also add the basedir to the list of module directories
        push_basedir(self._basedir)

        ds = self._loader.load_from_file(os.path.basename(file_name))
        if not isinstance(ds, list):
            raise AnsibleParserError("playbooks must be a list of plays", obj=ds)

        # Parse the playbook entries. For plays, we simply parse them
        # using the Play() object, and includes are parsed using the
        # PlaybookInclude() object
        for entry in ds:
            if not isinstance(entry, dict):
                raise AnsibleParserError("playbook entries must be either a valid play or an include statement", obj=entry)

            if 'include' in entry:
                entry_obj = PlaybookInclude.load(entry, variable_manager=variable_manager, loader=self._loader)
            else:
                entry_obj = Play.load(entry, variable_manager=variable_manager, loader=self._loader)

            self._entries.append(entry_obj)

    def get_loader(self):
        return self._loader

    def get_entries(self):
        return self._entries[:]
