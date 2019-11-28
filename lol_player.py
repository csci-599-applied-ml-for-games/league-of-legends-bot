import gym
import gym_LoL

from stable_baselines.common.policies import MlpLstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from notify_run import Notify

def update model (model = None, time):
    if model == None :
        env = DummyVecEnv([lambda: gym.make('LoL-v0')])
        model = PPO2(MlpLstmPolicy, env, verbose=1, nminibatches=1)
    
    model.learn(total_timesteps=time)
    model.save('ppo_lol')
    
    return model
   

if __name__ == "__main__":
    notify = Notify(endpoint='https://notify.run/1GQn88vSML1rmxdz')
    try:
        model = None
        for i in range (10000) :
            model = update_model(model, 10)

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        notify.send('Training Failed for LoL-v0')
    else:
        notify.send('Training Completed for LoL-v0')
