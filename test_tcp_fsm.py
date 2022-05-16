"""
Tests for TCP FSM.
Run tests:

    python3 -m pytest tcp_fsm.py -v
"""
import sys
import os
import pytest

sys.path.append(os.path.realpath(os.getcwd()))
from tcp_fsm import init_tcp_fsm, TransitionError

# ([transitions], expected state)
TEST_DATA = (
(["ACTIVE","SYNACK","FIN"],  "CLOSE_WAIT"),
(["PASSIVE",  "SYN","ACK"],  "ESTABLISHED"),
(["ACTIVE","SYNACK","FIN","CLOSE"],  "LAST_ACK"),
(["ACTIVE"],  "SYN_SENT"),
(["PASSIVE","SYN","ACK","CLOSE","SEND"],  "ERROR"),
(["PASSIVE",  "SYN","ACK",   "CLOSE"],  "FIN_WAIT_1"),
(["PASSIVE",  "SYN","ACK"],  "ESTABLISHED"),
(["PASSIVE",  "SYN"],  "SYN_RCVD"),
(["PASSIVE"],  "LISTEN"),
(["ACTIVE","CLOSE"],  "CLOSED"),
(["ACTIVE","SYN","CLOSE","FIN","ACK"],  "TIME_WAIT"),
(["ACTIVE","SYN","CLOSE","FIN","ACK","TIMEOUT"],  "CLOSED"),
(["SYN","ACK","CLOSE"],  "ERROR"),
(["ACTIVE","SYN","CLOSE","ACK"],  "FIN_WAIT_2"),
(["ACTIVE","SYNACK","FIN"],  "CLOSE_WAIT"),
(["ACTIVE","SYNACK","FIN","CLOSE"],  "LAST_ACK"),
(["ACTIVE"],  "SYN_SENT"),
(["PASSIVE","CLOSE"],  "CLOSED"),
(["ACTIVE","SYNACK","CLOSE"],  "FIN_WAIT_1"),
(["PASSIVE","SYN","ACK","PASSIVE"],  "ERROR"),
(["PASSIVE","SYN","ACK","CLOSE","ACK","FIN"],  "TIME_WAIT"),
(["PASSIVE","SYN","ACK","CLOSE","SYN"],  "ERROR"),
(["PASSIVE","CLOSE","SYN"],  "ERROR"),
(["PASSIVE","SYN","ACK","CLOSE"],  "FIN_WAIT_1"),
(["PASSIVE","SYN","ACK","CLOSE","FIN"],  "CLOSING"))


@pytest.mark.parametrize("transitions, expected_state", TEST_DATA)
def test_tcp_fsm(transitions, expected_state):
    flag = 0
    tcp_fsm = init_tcp_fsm()
    for event in transitions:
        try:
            flag = 0
            tcp_fsm.transition(event)
        except TransitionError as err:
            if expected_state == "ERROR":
                flag = 1
                return
            else:
                if flag == 2:
                    print(event, expected_state)
                raise err
    assert tcp_fsm.current_state.name == expected_state, (transitions, expected_state)