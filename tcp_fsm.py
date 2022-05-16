import sys
import os
sys.path.append(os.path.realpath(os.getcwd()))
from fsm import MealyMachine, State, TransitionError
import constants
# from test_tcp_fsm import test_tcp_fsm

VALID_TCP_EVENTS = (
    constants.TIMEOUT,
    constants.SDATA,
    constants.RDATA,
    constants.FIN,
    constants.ACK,
    constants.SYNACK,
    constants.CLOSE,
    constants.SYN,
    constants.ACTIVE,
    constants.PASSIVE,
)

# Transition outputs
n_out   = '<n>'
fin     = '<fin>'
ack     = '<ack>'
syn_ack = '<syn-ack>'
syn     = '<syn>'
NONE    = u"Λ"

# Setup FSM
state_closed      = State(constants.CLOSED, initial=True)
state_listen      = State(constants.LISTEN)
state_syn_sent    = State(constants.SYN_SENT)
state_syn_rcvd    = State(constants.SYN_RCVD)
state_established = State(constants.ESTABLISHED)
state_fin_wait_1  = State(constants.FIN_WAIT_1)
state_fin_wait_2  = State(constants.FIN_WAIT_2)
state_closing     = State(constants.CLOSING)
state_time_wait   = State(constants.TIME_WAIT)
state_close_wait  = State(constants.CLOSE_WAIT)
state_last_ack    = State(constants.LAST_ACK)

state_established.received_count = 0
state_established.sent_count     = 0

# Transitions
# <state name>[(<input>, <output>)] = <next state>
state_closed[(constants.PASSIVE,    NONE)]    = state_listen
state_closed[(constants.ACTIVE,     syn)]     = state_syn_sent
state_listen[(constants.SYN,        syn_ack)] = state_syn_rcvd
state_listen[(constants.CLOSE,      NONE)]    = state_closed
state_syn_sent[(constants.CLOSE,    NONE)]    = state_closed
state_syn_sent[(constants.SYN,      syn_ack)] = state_syn_rcvd
state_syn_sent[(constants.SYNACK,   ack)]     = state_established
state_syn_rcvd[(constants.ACK,      NONE)]    = state_established
state_syn_rcvd[(constants.CLOSE,    fin)]     = state_fin_wait_1
state_established[(constants.CLOSE, fin)]     = state_fin_wait_1
state_established[(constants.FIN,   ack)]     = state_close_wait
state_established[(constants.RDATA, n_out)]   = state_established
state_established[(constants.SDATA, n_out)]   = state_established
state_fin_wait_1[(constants.FIN,    ack)]     = state_closing
state_fin_wait_1[(constants.ACK,    NONE)]    = state_fin_wait_2
state_fin_wait_2[(constants.FIN,    ack)]     = state_time_wait
state_closing[(constants.ACK,       NONE)]    = state_time_wait
state_time_wait[(constants.TIMEOUT, NONE)]    = state_closed
state_close_wait[(constants.CLOSE,  fin)]     = state_last_ack
state_last_ack[(constants.ACK,      NONE)]    = state_closed


class TCPMachine(MealyMachine):

    def __init__(self, name, start_state):
        # super().__init__(name=name, default=True)
        self.current_state = self.init_state = start_state

    def transition(self, event):
        if self.current_state is None:
            raise TransitionError('Current state is not set.')

        destination_state = self.current_state.get(
            event, self.current_state.default_transition)

        if destination_state:
            self.current_state = destination_state
        else:
            raise TransitionError('Transition cant be happened from state "%s"'
                                  ' on event "%s"' % (self.current_state.name,
                                                      event))
        if event == constants.RDATA:
            assert self.current_state.name == constants.ESTABLISHED
            self.current_state.received_count += 1
        if event == constants.SDATA:
            assert self.current_state.name == constants.ESTABLISHED
            self.current_state.sent_count += 1


def init_tcp_fsm():
    return TCPMachine(name="TCP FSM",
                         start_state=state_closed)

def main():
    tcp_fsm = init_tcp_fsm()
    while True:
        try:
            event = sys.stdin.readline()
            # print(f"event={event!r}")
            if event in ("", "\n"):
                break

            event = event.strip()

            if event == "SEND" and tcp_fsm.current_state.name == constants.LISTEN:
                continue
            elif event not in VALID_TCP_EVENTS:
                print(f"Error: unexpected Event: {event}")
            else:
                tcp_fsm.transition(event)
                if tcp_fsm.current_state.name == constants.ESTABLISHED:
                    if event == constants.SDATA:
                        print(f"DATA Sent count {tcp_fsm.current_state.sent_count}")
                    if event == constants.RDATA:
                        print(f"DATA Received count {tcp_fsm.current_state.received_count}")
                print(f"event received is {event} "
                      f"current state is {tcp_fsm.current_state.name}")
        except TransitionError as e:
            print('FSMException: %s' % (str(e)))

if __name__ == '__main__':
    main()
