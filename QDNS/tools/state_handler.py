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

GENERAL_STATE_NOT_STARTED = "GENERAL_STATE_NOT_STARTED"
GENERAL_STATE_IS_RUNNING = "GENERAL_STATE_IS_RUNNING"
GENERAL_STATE_IS_STOPPED = "GENERAL_STATE_IS_STOPPED"
GENERAL_STATE_IS_FINISHED = "GENERAL_STATE_IS_FINISHED"
GENERAL_STATE_IS_TERMINATED = "GENERAL_STATE_IS_TERMINATED"
GENERAL_STATE_MAY_END = "GENERAL_STATE_MAY_END"
GENERAL_STATE_IS_PAUSED = "GENERAL_STATE_IS_PAUSED"

GENERAL_STATE_FLAGS = (
    GENERAL_STATE_NOT_STARTED,
    GENERAL_STATE_IS_RUNNING,
    GENERAL_STATE_IS_STOPPED,
    GENERAL_STATE_IS_FINISHED,
    GENERAL_STATE_IS_TERMINATED,
    GENERAL_STATE_MAY_END,
    GENERAL_STATE_IS_PAUSED
)


class StateHandler(object):
    COUNT_STATES = "count_states"

    def __init__(self, layer_id: int, must_report_state, *states, **flags):
        """
        State handler for layered objects.

        Args:
            layer_id: Layer ID.
            must_report_state: State report flag.
            states: All layer states.
            flags: State flags.

        Raise:
            ValueError If state lenght is zero.
            ValueError If flags do not recognized.
            TypeError If counter state is not bool.

        Kwargs:
            counter_states = bool
            GENERAL_STATE_NOT_STARTED = state
            GENERAL_STATE_IS_RUNNING = state
            GENERAL_STATE_IS_STOPPED = state
            GENERAL_STATE_IS_FINISHED = state
            GENERAL_STATE_IS_TERMINATED = state
            GENERAL_STATE_MAY_END = state
            GENERAL_STATE_IS_PAUSED = state

        """

        if states.__len__() <= 0:
            raise ValueError("State object excepts at least 1 state.")

        self._states = states
        self._layer_id = layer_id

        self._current_state = states[0]
        self._count_states = False

        self._not_started_state = None
        self._is_running_state = None
        self._is_stopped_state = None
        self._is_finished_state = None
        self._is_terminated_state = None
        self._may_end_state = None
        self._is_paused_state = None

        self._state_counter_dict = dict()
        for state in self._states:
            self._state_counter_dict[state] = 0
        self._state_counter_dict[self._current_state] += 1

        for value in flags:
            if value == GENERAL_STATE_NOT_STARTED:
                self._not_started_state = flags[value]

            elif value == GENERAL_STATE_IS_RUNNING:
                self._is_running_state = flags[value]

            elif value == GENERAL_STATE_IS_STOPPED:
                self._is_stopped_state = flags[value]

            elif value == GENERAL_STATE_IS_FINISHED:
                self._is_finished_state = flags[value]

            elif value == GENERAL_STATE_IS_TERMINATED:
                self._is_terminated_state = flags[value]

            elif value == GENERAL_STATE_MAY_END:
                self._may_end_state = flags[value]

            elif value == GENERAL_STATE_IS_PAUSED:
                self._is_paused_state = flags[value]

            elif value == self.COUNT_STATES:
                if not isinstance(flags[value], bool):
                    raise TypeError("Excepted a bool for count_states but got {}".format(flags[value]))
                self._count_states = flags[value]

            else:
                raise ValueError("Exepted a general state but got {}.".format(value))

        self._must_report_state = must_report_state

    def change_state(self, new_state, _raise=True) -> bool:
        """
        Changes state of layer

        Args:
            new_state: New state of layer.
            _raise: Raise if not successfull.

        Raise:
            ValueError If state is not in dict.

        Return:
            Boolean.
        """

        if new_state not in self._states:
            if _raise:
                raise ValueError("Exepted a state for layer {} but got {}".format(self._layer_id, new_state))
            else:
                return False

        else:
            if self._current_state == new_state:
                return False

            if self._count_states:
                self._state_counter_dict[new_state] += 1

            self._current_state = new_state
            return True

    def is_state_counter_active(self) -> bool:
        """ Returns if state counter active. """

        return self._count_states

    def is_not_started_active(self) -> bool:
        """ Returns if is not started active. """

        if self._not_started_state is None:
            return False
        return True

    def is_running_active(self) -> bool:
        """ Returns if is running active. """

        if self._is_running_state is None:
            return False
        return True

    def is_stopped_active(self) -> bool:
        """ Returns if is running active. """

        if self._is_stopped_state is None:
            return False
        return True

    def is_finished_active(self) -> bool:
        """ Returns if is finished active. """

        if self._is_finished_state is None:
            return False
        return True

    def is_terminated_active(self) -> bool:
        """ Returns if is terminated active. """

        if self._is_terminated_state is None:
            return False
        return True

    def is_may_end_active(self) -> bool:
        """ Returns if may end active. """

        if self._may_end_state is None:
            return False
        return True

    def is_paused_active(self) -> bool:
        """ Returns if is paused active. """

        if self._is_paused_state is None:
            return False
        return True

    def is_started(self) -> bool:
        """ Returns if state is started. """

        exptected = (self._is_paused_state, self._may_end_state, self._is_running_state)
        if self._current_state in exptected:
            return True
        return False

    def is_running(self) -> bool:
        """ Returns if state is running. """

        expected = (self._is_running_state,)
        if self._current_state in expected:
            return True
        return False

    def is_finished(self) -> bool:
        """ Returns if state is finished. """

        expected = (self._is_finished_state,)
        if self._current_state in expected:
            return True
        return False

    def is_terminated(self) -> bool:
        """ Returns if state is terminated. """

        expected = (self._is_terminated_state,)
        if self._current_state in expected:
            return True
        return False

    def may_end(self) -> bool:
        """ Returns if state may end. """

        expected = (self._may_end_state,)
        if self._current_state in expected:
            return True
        return False

    def is_stopped(self) -> bool:
        """ Returns if state is stopped. """

        expected = (self._is_terminated_state, self._is_finished_state, self._not_started_state)
        if self._current_state in expected:
            return True
        return False

    def is_breakable(self) -> bool:
        """ Returns if state is breakable. """

        expected = (self._is_terminated_state, self._is_finished_state, self._not_started_state, self._may_end_state)
        if self._current_state in expected:
            return True
        return False

    @property
    def layer_id(self) -> int:
        return self._layer_id

    @property
    def state(self):
        return self._current_state

    @property
    def all_states(self):
        return self._states

    @property
    def state_not_started(self):
        return self._not_started_state

    @property
    def state_is_running(self):
        return self._is_running_state

    @property
    def state_is_stopped(self):
        return self._is_stopped_state

    @property
    def state_is_finished(self):
        return self._is_finished_state

    @property
    def state_is_terminated(self):
        return self._is_terminated_state

    @property
    def state_may_end(self):
        return self._may_end_state

    @property
    def state_is_paused(self):
        return self._is_paused_state

    @property
    def state_count(self):
        return self.all_states.__len__()

    @property
    def state_change_counts(self) -> dict:
        return self._state_counter_dict

    @property
    def is_reports_state(self) -> bool:
        return self._must_report_state

    def __int__(self):
        return self.state_count

    def __str__(self):
        to_return = str()
        to_return += "State Object\n"
        to_return += "------------------\n"
        to_return += "Owned Layer ID: {}\n".format(self.layer_id)
        to_return += "State Counter Acive: {}\n".format(self.is_state_counter_active())
        to_return += "Not Started Defined: {}\n".format(self.is_not_started_active())
        to_return += "Is Running Defined: {}\n".format(self.is_running_active())
        to_return += "Is Stopped Defined: {}\n".format(self.is_stopped_active())
        to_return += "Is Finished Defined: {}\n".format(self.is_finished_active())
        to_return += "Is Terminated Defined: {}\n".format(self.is_terminated_active())
        to_return += "May End Defined: {}\n".format(self.is_may_end_active())
        to_return += "Is Paused Defined: {}\n".format(self.is_paused_active())
        to_return += "Is Reports State: {}\n".format(self.is_reports_state)
        to_return += "All States:\n"
        to_return += "------------------\n"
        to_return += "{}\n".format(self.all_states)

        if self.is_state_counter_active():
            to_return += "------------------\n"
            to_return += "{}\n".format(self.state_change_counts)

        return to_return
