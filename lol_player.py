import gym
import gym_LoL

from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from notify_run import Notify


if __name__ == "__main__":
    notify = Notify(endpoint='https://notify.run/1GQn88vSML1rmxdz')
    model = None
    model_path = 'ppo_lol'
    try:
        env = DummyVecEnv([lambda: gym.make('LoL-v0')])
        try:
            model = PPO2.load(model_path, env)
        except ValueError:
            model = PPO2(MlpLstmPolicy, env, verbose=1, nminibatches=1)
        for i in range(100):
            model.learn(total_timesteps=2500)
            model.save(model_path)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        model.save(model_path)
        notify.send('Training Failed for LoL-v0')
        raise
    else:
        notify.send('Training Completed for LoL-v0')
