import gymnasium as gym
import numpy as np
import simpy
from collections import OrderedDict
import math

import simplesimmodel as simmodel
from businessprocess import BusinessProcess


class BusinessProcessEnv(gym.Env):
    """
    A class representing an environment for a RL-agent.
    The environment is based on the simulation of a process which a RL-agent can use for its training.
    
    Attributes
    ----------
    ressources : list of int
        numbers of resources

    case : list of int
        indicates how the trace of a case looks like

    activities : int
        number of actions possible
    
    observation_space : gym.spaces.Dict of {str : gym.spaces.MultiDiscrete, str : gym.spaces.MultiDiscrete, str : gym.spaces.Discrete}
        observation space which includes the information from ressources, case, activities
    
    action_space : gym.spaces.Discrete
        action space which corresponds to the number of actions possible

    current_state : gym.spaces.Dict of {str : gym.spaces.MultiDiscrete, str : gym.spaces.MultiDiscrete, str : gym.spaces.Discrete}
        current state of the environment
    
    model_env : simpy.Environment
        environment for the simulation model

    process : businessprocess.BusinessProcess
        business process which is being simulated

    reward : int
        the reward for the current episode in th environment

    """

    # we need to get the number of ressources and activities for the initialization from the business process
    def __init__(self, space, activities):
        """
        Parameters
        ----------
        space : list of list of int
            contains the numbers of resources and indicates how the trace of a case looks like
            
        activities : int
            number of actions possible
        """

        self.ressources = space[0]
        self.case = space[1]
        self.activities = activities
        
        # a sample looks like: 'process': [#resource1, #resource2, ...], 'case': [#activity1, #activity2, ...], event: 4
        self.observation_space = gym.spaces.Dict(
            {
                'process': gym.spaces.MultiDiscrete(self.ressources),
                'case': gym.spaces.MultiDiscrete(self.case),
                'event': gym.spaces.Discrete(self.activities)
            }
        )

        # possible actions are all the activities in the business process
        self.action_space = gym.spaces.Discrete(self.activities)

        # current state is: all ressources available, no activities happened in the case, current event is none (0)
        self.current_state = OrderedDict()
        self.current_state['case'] = np.zeros(len(self.case), dtype=int)
        self.current_state['event'] = 0
        self.current_state['process'] = np.zeros(len(self.ressources), dtype=int)
        for i in range(len(self.current_state['process'])):
            self.current_state['process'][i] += (self.ressources[i]-1)

        # init environment for the simmodel, init busibess process, start the process
        self.model_env = simpy.Environment()
        self.process = BusinessProcess(self.model_env, self.ressources)
        self.model_env.process(simmodel.run_process(self.model_env, self.process))

        # save the reward for the current episode
        self.reward = 0

    
    def get_current_state(self, caseid):
        """Get the current state of the case and process from the simulation model.

        Parameters
        ----------
        caseid : int
            case-id of a case in the process

        Returns
        -------
        collections.OrderedDict of {str : list of int, str : int, str : list of int}
        """

        process, case, event = simmodel.get_current_state(self.process, caseid)
        state = OrderedDict()
        state['case'] = np.asarray(case) 
        state['event'] = event
        state['process'] = np.asarray(process)
        return state
    
 
    def get_ressources(self, caseid, action):
        """Get the number of resources for a certain action.

        Parameters
        ----------
        caseid : int
            case-id of a case in the process
        action : int
            number of an action

        Returns
        -------
        int
            the number of resources for the action
        """
        state = self.get_current_state(caseid)
        if action == 1 or action == 15:
            return state['process'][0]
        elif action == 2 or action == 3:
            return state['process'][1]
        else:
            resource_position = action - 2
            return state['process'][resource_position]

    def step(self, action):
        """The main function of the environment - agent executes an action there, getting a penalty or reward and moving to the next state.
        A step involves doing a ceratin action for a chosen case in the process.
        An episode is done when the agent has completed 10 cases.

        Parameters
        ----------
        action : int
            number of an action

        Returns
        -------
        collections.OrderedDict of {str : list of int, str : int, str : list of int}
            an element of the environment/'s observation_space as the next observation due to the agent actions
        int
            the reward as a result of taking the action
        bool
            whether the agent reaches the terminal state
        bool
            whether the truncation condition outside the scope of the MDP is satisfied
        dict
            contains auxiliary diagnostic information 
        """

        # we save the chosen action in the process's variable for that
        self.process.next = action

        # if the currently chosen case is done, we choose a new one from the active cases
        if self.process.case_id in self.process.done_cases:
            # we only want to choose "interesting" cases - cases which are as early as possible in their execution so we search for such a case
            early_case = self.process.active_cases[0]
            early = 15
            for next_case in self.process.active_cases:
                next_obj = self.process.case_objects[next_case]
                if next_obj.current < early and next_obj.current > 1:
                    early_case = next_obj
                    early = next_obj.current

            self.process.case_id = early_case.case_id
           
        # we find the corresponding to the case_id case object and get its current state
        case_obj = self.process.case_objects[self.process.case_id]
        self.current_state = self.get_current_state(case_obj)

        # we save the starting time 
        start = self.process.env.now

        # set this flag to true in order to be able to execute the case
        self.process.flag = True

        # different execution based in whether the chosen action is valid
        if self.process.is_valid(self.current_state['event'], action, case_obj):

            print(action)
            print(self.current_state['process'])
            print(self.get_ressources(case_obj, action))

            # while the case is doing the chosen action in the simmodel the process_flag is set to true 
            # and we execute this until the activity is done after which we return to this function
            while(self.process.flag):
                self.model_env.step()

            stop = self.process.env.now

            print(f"Agent did case {self.process.case_id} activity {action}.")

            next_state = self.get_current_state(case_obj)
            self.current_state = next_state
            time = stop - start
            if time == 0:
                reward = 4.5
            else:
                reward = 4.5 - math.log(time, 10)
            self.reward += reward
            done = True if (len(self.process.done_cases) == 10 or len(self.process.active_cases) == 0) else False
            truncated = False
            info = {}
            return next_state, reward, done, truncated, info 
        
        else: 
            # if the action was not valid agent gets a penalty and stays in the same state
            reward = -5
            self.reward += reward
            next_state = self.current_state
            done = False
            truncated = False
            info = {}
            return next_state, reward, done, truncated, info
    
         
    def reset(self, seed=None, options=None):
        """Reset the environment to the initial state.

        Parameters
        ----------
        seed : optional int
            the seed that is used to initialize the environment/'s PRNG (default is None)

        options : optional dict
            additional information to specify how the environment is reset (default is None)

        Returns 
        -------
        collections.OrderedDict of {str : list of int, str : int, str : list of int}
            an element of the environment/'s observation_space as the next observation due to the agent actions
        dict
            contains auxiliary diagnostic information 
        """

        super().reset(seed=seed)

        self.current_state = OrderedDict()
        self.current_state['case'] = np.zeros(len(self.case), dtype=int)
        self.current_state['event'] = 0
        self.current_state['process'] = np.zeros(len(self.ressources), dtype=int)
        for i in range(len(self.current_state['process'])):
            self.current_state['process'][i] += (self.ressources[i]-1)

        observation = self.current_state

        self.current_step = 0

        self.model_env = simpy.Environment()
        self.process = BusinessProcess(self.model_env, self.ressources)
        self.model_env.process(simmodel.run_process(self.model_env, self.process))
        rand_time = np.random.randint(10,2000)
        self.model_env.run(until = rand_time)
        self.process.done_cases = set([])

        self.reward = 0

        info = {}

        return observation, info
        

    def render(self, mode='human'):
        """Render the current state of the environment.
        Disclaimer: Not implemented.

        Parameters
        ----------
        mode : str
            default is human
        """
        pass

    
    def flatten_observation(self, observation):
        """Flatten an observation to a a one-dimensional list.

        Parameters
        ----------
        observation : gym.spaces.Dict of {str : gym.spaces.MultiDiscrete, str : gym.spaces.MultiDiscrete, str : gym.spaces.Discrete}
            an observation in the environment

        Returns
        -------
        list of ints
            the observation flattened to a one-dimensional list 
        -------
        """

        flattened = []
        for i in observation['process']: flattened.append(i)
        for j in observation['case']: flattened.append(j)
        flattened.append(observation['event'])

        return flattened

    def flatten_observation_to_int(self, observation):
        """Flatten an observation to unique integer.
        Disclaimer: not functional for big observation space and not used in the final implementation

        Parameters
        ----------
        observation : gym.spaces.Dict of {str : gym.spaces.MultiDiscrete, str : gym.spaces.MultiDiscrete, str : gym.spaces.Discrete}
            an observation in the environment

        Returns
        -------
        int
            the observation flattened to an integer
        -------
        """

        state = 0
        state += observation['event']*pow(2,10)
        state += observation['case'][1]*pow(2,2)
        state += observation['case'][2]*pow(2,2)
        event = observation['event']
        if event == 0:
            state += observation['process'][0]*pow(2,6)
        elif event == 1:
            state += observation['process'][1]*pow(2,6)
        elif 1 < event <=3:
            state += observation['process'][2]*pow(2,6)+observation['process'][3]*pow(2,7)+observation['process'][4]*pow(2,8)
        elif 3 < event <=6:
            state += observation['process'][5]*pow(2,6)+observation['process'][6]*pow(2,7)
        elif 6 < event <= 8:
            state += observation['process'][7]*pow(2,6)+observation['process'][8]*pow(2,7)+observation['process'][9]*pow(2,8)
        elif 8 < event <= 11:
            state += observation['process'][10]*pow(2,6)+observation['process'][11]*pow(2,7)+observation['process'][12]*pow(2,8)
        elif 11 < event <= 14:
            state += observation['process'][0]*pow(2,6)
        else:
            pass
        
        return state
