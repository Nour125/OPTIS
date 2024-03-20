""" Environment Checker

Script to check whether the environment is suitable for training an agent from the stable_baselines3library.
"""

from stable_baselines3.common.env_checker import check_env
import environment


process = [] 
num_s = 1
process.append(num_s+1)
num_ot = 5
process.append(num_ot+1)
num_sh_a = 3
process.append(num_sh_a+1)
num_sh_b = 3
process.append(num_sh_b+1)
num_sh_c = 3
process.append(num_sh_c+1)
num_m_a = 3
process.append(num_m_a+1)
num_m_b = 2
process.append(num_m_b+1)
num_p_a = 4
process.append(num_p_a+1)
num_p_b = 5
process.append(num_p_b+1)
num_p_c = 4
process.append(num_p_c+1)
num_ds_a = 7
process.append(num_ds_a+1)
num_ds_b = 7
process.append(num_ds_b+1)
num_ds_c = 7
process.append(num_ds_c+1)

case = []
for i in range(15):
    case.append(2)
    
space = [process, case]
activities = 16

env = environment.BusinessProcessEnv(space, activities)

check_env(env)

