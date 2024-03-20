""" DQN-Agent

This module includes the training and deployment of a DQN, which uses a custom environment and simulation model of a process
to learn to optimize that process by recommending the optimal next activity (in terms of saving time). 

It includes the following functions:

    * train(space, activities)
    * deploy(state)
"""

from stable_baselines3 import DQN
import os
import time


from environment import BusinessProcessEnv


def train(space, activities):
    """Train a DQN on a simulation model of a process and save the model and its logs.

    Parameters
    ----------
    space : list of list of int
        contains the numbers of resources and indicates how the trace of a case looks like
    activities : int
        the number of allowed activities in the process
    """

    # initialize environment
    env = BusinessProcessEnv(space, activities)
    env.reset()

    # create directories fro saving the models and logs
    models_dir = f"models/{int(time.time())}/"
    logdir = f"logs/{int(time.time())}/"

    if not os.path.exists(models_dir):
        os.makedirs(models_dir)

    if not os.path.exists(logdir):
        os.makedirs(logdir)

    # create and train the DQN model
    model = DQN('MultiInputPolicy', env, verbose=1, exploration_fraction = 0.33, learning_starts = 10000, tensorboard_log=logdir)

    # save a model every TIMESTEPS 
    TIMESTEPS = 1000000
    iters = 0
    while True:
        iters += 1
        model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name=f"DQN")
        model.save(f"{models_dir}/{TIMESTEPS*iters}")

# choose a working model and use it to recommend the next action for the given state
def deploy(state):
    """Deploy a DQN-model by using it to recommend the best next activity for a certain state.

    Parameters
    ----------
    state : collections.OrderedDict of {str : list of int, str : int, str : list of int}
        the state of a case in a process (the trace of the case, the current event in the case, the available resources)

    Returns
    -------
    int
        number of the encoded optimal action to take
    
    """
    model = DQN.load(r'../models/1687176631/2000000')
    action, _ = model.predict(state, deterministic=True)

    return action


