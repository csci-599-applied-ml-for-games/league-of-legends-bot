import gym
import gym_LoL

from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2


if __name__ == "__main__":
    model = PPO2.load("ppo_lol")

    env = DummyVecEnv([lambda: gym.make('LoL-v0')])
    obs = env.reset()
    sum_rewards = 0
    while True:
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)

        sum_rewards += 0
        if done :
            print("Final Reward = " + sum_rewards)
            break
