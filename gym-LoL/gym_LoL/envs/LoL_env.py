import mss
import gym
from gym import spaces
from gym_LoL.envs.LoL_utils import create_custom_game, join_custom_game, leave_custom_game, perform_action, get_stats
from gym_LoL.envs.darknet.x64.darknet import performDetect
from collections import defaultdict
import numpy as np


class LoLEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, player=1):
        assert player == 1 or player == 2
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(69, 26, 26), dtype=float)
        self.player = player
        self.sct = mss.mss()
        self.state = {
            'stats': {
                'kills': 0,
                'deaths': 0,
                'assists': 0,
                'minion_kills': 0
            },
            'positions': defaultdict(lambda: None)
        }
        performDetect(initOnly=True, configPath="./cfg/yolov3-tiny_obj.cfg",
                      weightPath="yolov3-tiny_obj_last.weights", metaPath="./cfg/obj.data")

    def __del__(self):
        self.sct.close()

    def get_observation(self, sct_img):
        return performDetect(imageMSS=sct_img, showImage=False,
                             configPath="./cfg/yolov3-tiny_obj.cfg", weightPath="yolov3-tiny_obj_last.weights",
                             metaPath="./cfg/obj.data")

    def get_reward(self, stats):
        if 'kills' not in stats:
            return 0, False
        if stats['kills'] == 1:
            return 100, True
        elif stats['deaths'] == 1:
            return -100, True
        return 0, False

    def update_stats(self, stats):
        self.state['stats'] = stats

    def update_positions(self, detections):
        self.state['positions'].clear()
        for detection in detections:
            self.state['positions'][detection[0]] = detection[2]

    def step(self, action):
        if self.player == 1:
            perform_action(action, 'Ashe', 'Veigar', self.state['positions'])
        else:
            perform_action(action, 'Veigar', 'Ashe', self.state['positions'])
        sct_img = self.sct.grab(self.sct.monitors[1])
        observation, detections = self.get_observation(sct_img)
        stats = get_stats(sct_img)
        reward, done = self.get_reward(stats)
        self.update_positions(detections)
        self.update_stats(stats)
        return observation, reward, done, {}

    def reset(self):
        try:
            leave_custom_game(self.sct)
        except RuntimeError:
            pass
        if self.player == 1:
            create_custom_game(self.sct, password='lol12345', opponents=['bullse2ye', 'dutse2ye'],
                               champion='Ashe')
        else:
            join_custom_game(self.sct, opponents=['raunaqtr'], champion='Veigar')
        sct_img = self.sct.grab(self.sct.monitors[1])
        observation, detections = self.get_observation(sct_img)
        self.update_positions(detections)
        return observation

    def render(self):
        pass
