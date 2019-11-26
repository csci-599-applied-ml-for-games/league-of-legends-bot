import gym
import gym_LoL

from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from notify_run import Notify

def main (time): 
    env = DummyVecEnv([lambda: gym.make('LoL-v0')])
    model = PPO2(MlpLstmPolicy, env, verbose=1, nminibatches=1)
    model.learn(total_timesteps=time)
    model.save('ppo_lol')

if __name__ == "__main__":
    notify = Notify(endpoint='https://notify.run/1GQn88vSML1rmxdz')
    try:
        main(100000)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        notify.send('Training Failed for LoL-v0')
    else:
        notify.send('Training Completed for LoL-v0')
