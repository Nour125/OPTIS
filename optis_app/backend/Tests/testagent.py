"""Script to train and test the agent on an event log.

To train uncomment line 52. 
To see the logs run the following command on the terminal: tensorboard --logdir logs
"""

import simpy
import numpy as np
import simplesimmodel as model
import eventlog as log
import dqn
import testonstate


# file we used to train and test our agent before connecting to the frontend

ressources = [] 
num_s = 1
ressources.append(num_s+1)
num_ot = 4
ressources.append(num_ot+1)
num_sh_a = 2
ressources.append(num_sh_a+1)
num_sh_b = 2
ressources.append(num_sh_b+1)
num_sh_c = 2
ressources.append(num_sh_c+1)
num_m_a = 4
ressources.append(num_m_a+1)
num_m_b = 10
ressources.append(num_m_b+1)
num_p_a = 2
ressources.append(num_p_a+1)
num_p_b = 3
ressources.append(num_p_b+1)
num_p_c = 3
ressources.append(num_p_c+1)
num_ds_a = 30
ressources.append(num_ds_a+1)
num_ds_b = 45
ressources.append(num_ds_b+1)
num_ds_c = 45
ressources.append(num_ds_c+1)

case = []
for i in range(15):
    case.append(2)
    
space = [ressources, case]
activities = 16


# dqn.train(space, activities)


''''''
# generate event log
env = simpy.Environment()
business_process = model.BusinessProcess(env, ressources)
business_process.event_log_flag = True
env.process(model.run_process(env, business_process))
env.run(until = 30000)
log.export_to_csv(business_process, r'..\Frontend\export\testeventlog')

# extract active cases from event log
active_cases = log.get_active_cases("testeventlog.csv")
print(active_cases)


for i in range(20):
    caseid = np.random.choice(active_cases)
    # print(caseid)

    state = log.get_state(caseid)

    print(dqn.deploy(state))


testonstate.test_agent()
