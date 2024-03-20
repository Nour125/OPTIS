"""The initial Q-learning algorithm we tried
Note: doesn't work on the current environment
"""

import numpy as np
import environment 


def q_learning(space, activities):
    """ Q-learning Algorithm

    Parameters
    ----------
    space : list of list of int
        contains the numbers of resources and indicates how the trace of a case looks like
    activities : int
        the number of allowed activities in the process
    
    Returns
    -------
    numpy.NDArray of int64
    """
    
    # Define the business process environment
    env = environment.BusinessProcessEnv(space, activities)

    # Define the Q-table
    num_states = 1

    process_space = env.observation_space['process'].nvec 
    # case_space = env.observation_space['case'].nvec 
    event_space = env.observation_space['event'].n
    
    for i in process_space: num_states *= i
    # for i in case_space: num_states *= (i+1)
    num_states *= event_space 
    
    # num_states = pow(2,14)

    """
    process_space = env.observation_space['process'] 
    case_space = env.observation_space['case'] 
    event_space = env.observation_space['event'] 

    state_shape = []
    for i in process_space: state_shape.append(i.n + 1)
    for j in case_space: state_shape.append(j.n + 1)
    state_shape.append(event_space.n)
    state_shape = tuple(state_shape)
    """
    
    num_actions = env.action_space.n


    # Q = np.zeros(state_shape + (num_actions,), dtype=np.int8)
    Q = np.zeros((num_states, num_actions), dtype = np.int64)

    # Set the hyperparameters
    alpha = 0.1   # learning rate
    gamma = 0.1  # discount factor
    epsilon = 0.1 # exploration rate

    mean_time = 0
    mean_reward = 0

    # Train the agent using Q-learning
    num_episodes = 1000
    for episode in range(num_episodes):
        state, _ = env.reset()
        state = env.flatten_observation_to_int(state)
        done = False
        start = env.process.env.now
        while not done:
            # Choose an action based on the epsilon-greedy policy
            if np.random.uniform(0, 1) < epsilon:
                action = env.action_space.sample()
            else:
                action = np.argmax(Q[state])
            
            
            # Execute the action and observe the next state and reward
            next_state, reward, done, _ = env.step(action)

            # Update the Q-value for the current state-action pair
            Q[state][action] = (1-alpha)*Q[state][action] + alpha * (reward + gamma * np.max(Q[next_state]) - Q[state][action])
            #Q[state][action] = (1-alpha)*Q[state][action] + alpha*reward 
            
            # Transition to the next state
            old_state = state
            state = next_state
            

        time = env.process.env.now - start 
        mean_time += time
        mean_reward += reward


        if (episode % 20 == 19):
            mean_reward /= 20
            mean_time /= 20 
            print(f"Episode {episode-19} to episode {episode}: mean time = {mean_time}, mean reward: {mean_reward}")
        
        if episode == 19:
            start_reward = mean_reward

        # print(f"Episode {episode}: time = {time}, reward = {reward}")
        
        if episode == 999:
            end_reward = mean_reward
            improvement = end_reward - start_reward
            print(f"Reward improved by {improvement}")

    return Q
