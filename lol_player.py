import gym
import gym_LoL

from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import SubprocVecEnv
from stable_baselines import PPO2

def main (time): 
    env = SubprocVecEnv([lambda: gym.make('LoL-v0') for i in range(1)])
    model = PPO2 (MlpLstmPolicy, env, verbose=1, nminibatches=1)
    model.learn(total_timesteps=time)
    model.save('ppo_lol')

if __name__ == "__main__":
    main(100000)
