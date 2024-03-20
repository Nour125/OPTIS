""" Script to test the agent on custom states.
"""

from collections import OrderedDict
import numpy as np

import dqn


def test_agent():
    case = [1,1,0,1,0,0,0,0,0,0,0,0,0,0,0]
    event = 4
    process = [0,2,1,2,0,0,3,2,3,3,7,6,0]

    state = OrderedDict()
    state['case'] = np.asarray(case) 
    state['event'] = event
    state['process'] = np.asarray(process)
    print(state)

    print(dqn.deploy(state))

test_agent()
