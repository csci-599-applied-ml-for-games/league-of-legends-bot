from gym.envs.registration import register

register(
    id='LoL-v0',
    entry_point='gym_LoL.envs:LoLEnv',
)