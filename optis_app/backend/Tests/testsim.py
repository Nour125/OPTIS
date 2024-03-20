"""Script to test the simulation model
"""

import simpy

import simplesimmodel as simmodel
from businessprocess import BusinessProcess


# test the simulation

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

model_env = simpy.Environment()
process = BusinessProcess(model_env, ressources)
model_env.process(simmodel.run_process(model_env, process))

for i in range(10):
    model_env.step()
    print(simmodel.get_ressources(process))


