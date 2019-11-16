import gym
import gym_LoL
from baselines import ppo2
from baselines.common.models import lstm
from baselines.common.vec_env.subproc_vec_env import SubprocVecEnv

#something here to load model 
#model = ppo2.load("ppo2_lol")

n_cpu = 1 # setup how many cpu's to run on 
env = gym.make('LoL-v0') 

model = ppo2(lstm, env, verbose = 1)
model.learn(total_timesteps=25000) #configure this
model.save("ppo2_lol")

