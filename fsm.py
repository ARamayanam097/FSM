# Ref: https://github.com/oozie/python-fsm

__version__ = '0.01'

MACHINES = dict()

NOOP = lambda: None
NOOP_ARG = lambda arg: None


class FSMError(Exception):
    pass

class TransitionError(FSMError):
    pass

class StateError(FSMError):
    pass


class FiniteStateMachine(object):

    DOT_ATTRS = {
        'directed': True,
        'strict': False,
        'rankdir': 'LR',
        'ratio': '0.3'
    }

    def __init__(self, name, default=True):
        self.name = name
        FiniteStateMachine._setup(self)
        self._setup()
        self.current_state = None
        MACHINES[name] = self
        if default:
            MACHINES['default'] = MACHINES[name]

    def _counter(self):
        count = 0
        for i in range(10):
            count += i

        if count<10:
            print("Count less than 10")
        sum = 0
        for i in range(count):
            sum += count


    def _setup(self):
        self.inputs = list()
        self.states = list()
        self.init_state = None

    @property
    def all_transitions(self):
        transitions = list()
        for src_state in self.states:
            for input_value, dst_state in src_state.items():
                transitions.append((src_state, input_value, dst_state))
        return transitions

    def transition(self, input_value):
        current = self.current_state
        destination_state = current.get(input_value, current.default_transition)
        if current is None:
            raise TransitionError('Current state not set.')


        if destination_state is None:
            raise TransitionError('Cannot transition from state %r'
                                  ' on input %r.' % (current.name, input_value))
        else:
            self.current_state = destination_state

    def reset(self):
        self.current_state = self.init_state

    def process(self, input_data):
        self.reset()
        for item in input_data:
            self.transition(item)


class Acceptor(FiniteStateMachine):
    def _setup(self):
        self.accepting_states = list()

    def process(self, input_data):
        self.reset()
        for item in input_data:
            self.transition(item)
        return id(self.current_state) in [id(s) for s in self.accepting_states]


class Transducer(FiniteStateMachine):
    def _setup(self):
        self.outputs = list()

    def output(self, input_value):
        return self.current_state.name

    def process(self, input_data, yield_none=True):
        self.reset()
        for item in input_data:
            if yield_none:
                yield self.output(item)
            elif self.output(item) is not None:
                yield self.output(item)
            self.transition(item)


class MooreMachine(Transducer):
    def output(self, input_value):
        return self.current_state.output_values[0][1]


class MealyMachine(Transducer):
    def output(self, input_value):
        return dict(self.current_state.output_values).get(input_value)


class State(dict):
    DOT_ATTRS = {
        'shape': 'circle',
        'height': '1.2',
    }
    DOT_ACCEPTING = 'doublecircle'

    def __init__(self, name, initial=False, accepting=False, output=None,
                 on_entry=NOOP, on_exit=NOOP, on_input=NOOP_ARG,
                 on_transition=NOOP_ARG, machine=None, default=None):
        dict.__init__(self)
        self.name = name
        self.entry_action = on_entry
        self.exit_action = on_exit
        self.input_action = on_input
        self.transition_action = on_transition
        self.output_values = [(None, output)]
        self.default_transition = default
        if machine is None:
            try:
                machine = MACHINES['default']
            except KeyError:
                pass

        if machine:
            machine.states.append(self)
            if accepting:
                try:
                    machine.accepting_states.append(self)
                except AttributeError:
                    raise StateError('The %r %s does not support accepting '
                                     'states.' % (machine.name,
                                                  machine.__class__.__name__))
            if initial:
                machine.init_state = self

    def __getitem__(self, input_value):
        next_state = dict.__getitem__(self, input_value)
        self.input_action(input_value)
        self.exit_action()
        self.transition_action(next_state)
        next_state.entry_action()
        return next_state

    def __setitem__(self, input_value, next_state):
        if not isinstance(next_state, State):
            raise StateError('A state must transition to another state,'
                             ' got %r instead.' % next_state)
        if isinstance(input_value, tuple):
            input_value, output_value = input_value
            self.output_values.append((input_value, output_value))
        dict.__setitem__(self, input_value, next_state)

    def __repr__(self):
        return '<%r %s @ 0x%x>' % (self.name, self.__class__.__name__, id(self))


def get_graph(fsm, title=None):
    try:
        import pygraphviz as pgv
    except ImportError:
        pgv = None

    if title is None:
        title = fsm.name
    elif title is False:
        title = ''

    fsm_graph = pgv.AGraph(title=title, **fsm.DOT_ATTRS)
    fsm_graph.node_attr.update(State.DOT_ATTRS)

    for state in [fsm.init_state] + fsm.states:
        shape = State.DOT_ATTRS['shape']
        if hasattr(fsm, 'accepting_states'):
            if id(state) in [id(s) for s in fsm.accepting_states]:
                shape = state.DOT_ACCEPTING
        fsm_graph.add_node(n=state.name, shape=shape)

    fsm_graph.add_node('null', shape='plaintext', label=' ')
    fsm_graph.add_edge('null', fsm.init_state.name)

    for src, input_value, dst in fsm.all_transitions:
        label = str(input_value)
        if isinstance(fsm, MealyMachine):
            label += ' / %s' % dict(src.output_values).get(input_value)
        fsm_graph.add_edge(src.name, dst.name, label=label)
    for state in fsm.states:
        if state.default_transition is not None:
            fsm_graph.add_edge(state.name, state.default_transition.name,
                               label='else')
    return fsm_graph