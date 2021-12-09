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

# General Layer Queues.
LAYER_STATE_REPORT_QUEUE = "STATE REPORT QUEUE OF LAYER"
LAYER_REQUEST_QUEUE = "REQUEST QUEUE OF LAYER"
LAYER_RESPOND_QUEUE = "RESPOND QUEUE OF LAYER"
LAYER_THREADED_REQUEST_QUEUE = "THREADED REQUEST QUEUE OF LAYER"
LAYER_THREADED_RESPOND_QUEUE = "THREADED RESPOND QUEUE OF LAYER"

# Simulation queues.
SIM_REQUEST_QUEUE = "SIMULATION REQUEST QUEUE"
USER_DUMP_QUEUE = "USER DUMP QUEUE"

# Miner queues.
MINER_REQUEST_QUEUE = "MINER REQUEST QUEUE"

# Device queues.
DEVICE_REQUEST_QUEUE = "DEVICE REQUEST QUEUE"
LOCALHOST_QUEUE = "LOCALHOST QUEUE"

# Socket qeueus.
SOCKET_REQUEST_QUEUE = "SOCKET REQUEST QUEUE"
INCOME_CLASSIC_QUEUE = "SOCKET INCOME CLASSIC QUEUE"
INCOME_QUANTUM_QUEUE = "SOCKET INCOME QUANTUM QUEUE"
PING_HANDLE_QUEUE = "SOKCET PING HANDLE QUEUE"
PING_REQUEST_QUEUE = "PING REQUEST QUEUE"
OBSERVER_QUEUE = "OBSERVER QUEUE"

# Application Queues.
INCOME_QUBIT_QUEUE = "QUBIT QUEUE OF APPLICATION"
INCOME_PACKAGE_QUEUE = "PACKAGE QUEUE OF APPLICATION"


class QueueManager(object):
    def __init__(self, **kwargs):
        """
        'Foreign Queue' Manager mostly used for layers.
        QUEUE_NAME = QUEUE()
        """

        self._queue_dict = dict()
        for args in kwargs:
            self._queue_dict[args] = kwargs[args]

    def get_queue(self, label: str):
        """ Gets the labeled queue. """

        try:
            return self._queue_dict[label]
        except (KeyError, IndexError) as E:
            raise E("Queue manager cannot parse queue for {}.".format(label))

    def add_queue(self, label: str, new_queue):
        """ Adds new queue to manager. """

        if label in self._queue_dict.keys():
            raise KeyError("{} labeled queue is already in manager.".format(label))
        self._queue_dict[label] = new_queue

    def update_queue(self, label: str, new_queue):
        """ Updates existing queue in manager. """

        if label not in self._queue_dict.keys():
            raise KeyError("{} labeled queue is not in manager.".format(label))
        self._queue_dict[label] = new_queue

    def remove_queue(self, label: str):
        """ Removes queue from manager. """

        if label not in self._queue_dict.keys():
            raise KeyError("{} labeled queue is not in manager.".format(label))
        self._queue_dict.pop(label)

    def is_have_this_queue(self, label: str) -> bool:
        if label not in self._queue_dict.keys():
            return False
        return True

    def clear_queues(self):
        """ Clears all queues in manager. """

        self._queue_dict.clear()

    @property
    def queue_count(self) -> int:
        return self._queue_dict.__len__()

    @property
    def queue_dict(self) -> dict:
        return self._queue_dict

    def __len__(self) -> int:
        return self._queue_dict.__len__()

    def __int__(self) -> int:
        return self._queue_dict.__len__()

    def __str__(self) -> str:
        to_return = str()
        to_return += "Queue Manager\n"
        to_return += "----------------\n"
        to_return += "Counts: {}\n".format(self.queue_count)
        to_return += "Queues: {}\n".format(self.queue_dict)
        return to_return
