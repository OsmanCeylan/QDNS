# Copyright (c) 2021, COMU Team, Osman Ceylan and etc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the COMU Team organization nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from typing import Any


class AnySettings(object):
    def __init__(self, **kwargs):
        """
        Any setting constructor.
        This class is template class, must inherit from this.

        Notes:
            {variable_name} = variable_value\n
            {variable_name_2} = variable_value\n
            ...

        Upmost settings template.
        """

        self._kwargs = kwargs

    def change_paramater(self, param: Any, new_value: Any):
        """
        Changes a setting.

        Args:
            param: Parameter of setting.
            new_value: New value of setting.

        Raises:
            KeyError: If parameter is not found.
        """

        try:
            self._kwargs[param] = new_value
        except (KeyError, IndexError) as E:
            raise E("Expected layer settings but got {}.".format(param))

    def details(self) -> str:
        """ Returns setting details as __str__. """

        return str(self._kwargs)

    def get_setting(self, param: Any) -> Any:
        """ Gets the setting. """

        try:
            return self._kwargs[param]
        except KeyError:
            raise KeyError("Setting {} is not found.".format(str(param)))

    def create_new_setting(self, param: Any, value: Any):
        """ Creates new setting. """

        try:
            _ = self._kwargs[param]
        except KeyError:
            self._kwargs[param] = value
        else:
            raise AttributeError("Parameter {} is exist in setting.".format(str(param)))

    @property
    def kwargs(self):
        return self._kwargs

    def __len__(self) -> int:
        return self._kwargs.__len__()

    def __str__(self) -> str:
        return self.details()


default_any_setting = AnySettings()
