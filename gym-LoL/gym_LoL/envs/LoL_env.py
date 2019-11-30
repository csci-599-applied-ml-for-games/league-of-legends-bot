import mss
import gym
from gym import spaces
from gym_LoL.envs.LoL_utils import create_custom_game, join_custom_game, leave_custom_game, perform_action, get_stats, check_champion
from gym_LoL.envs.darknet.x64.darknet import performDetect
from collections import defaultdict
import numpy as np
import rpyc
import cv2
from threading import Thread
import time


class Service(rpyc.Service):
    def on_connect(self, conn):
        self.conn = conn

    def exposed_foo(self):
        print("foo")
        return

    def exposed_bar(self):
        print("bar")
        return


class LoLEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, self_play=False, player=1):
        assert player == 1 or player == 2
        self.action_space = spaces.Discrete(7)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(69, 26, 26), dtype=float)
        self.player = player
        self.self_play = self_play
        self.sct = mss.mss()
        self.state = {
            'stats': {
                'kills': 0,
                'deaths': 0,
                'assists': 0,
                'minion_kills': 0,
                'health': 100,
                'opponent_health': 100
            },
            'positions': defaultdict(lambda: None)
        }
        self.champion = 'Ashe'
        self.opponent = 'Veigar'
        self.opponent_template = cv2.imread(self.opponent+'.jpg', 0)
        performDetect(initOnly=True, configPath="./cfg/yolov3-tiny_obj.cfg",
                      weightPath="yolov3-tiny_obj_last.weights", metaPath="./cfg/obj.data")
        if self_play:
            self.service = Service()
            if player == 1:
                self.conn = rpyc.OneShotServer(self.service, port=18861)
                self.server = Thread(target=self.conn.start)
                self.server.start()
            else:
                self.champion = 'Veigar'
                self.opponent = 'Ashe'
                self.conn = rpyc.connect("localhost", 18861, service=self.service)
                self.bgsrv = rpyc.BgServingThread(self.conn)

    def connect(self):
        if self.player == 1:
            self.service.conn.root.bar()
        else:
            self.service.conn.root.foo()

    def close(self):
        self.sct.close()
        if self.self_play:
            if self.player == 2:
                self.bgsrv.stop()
            self.conn.close()

    def get_observation(self, sct_img, featureMapLayer=22):
        return performDetect(imageMSS=sct_img, showImage=False,
                             configPath="./cfg/yolov3-tiny_obj.cfg", weightPath="yolov3-tiny_obj_last.weights",
                             metaPath="./cfg/obj.data", featureMapLayer=featureMapLayer)

    def get_reward(self, stats):
        done = False
        reward = -1
        mk_scaler, health_scaler, opponent_health_scaler = 1, 1, 1.5
 
        reward += (stats['minion_kills'] - self.state['stats']['minion_kills']) * mk_scaler
        reward += (self.state['stats']['opponent_health'] - stats['opponent_health']) * opponent_health_scaler
        reward -= max(self.state['stats']['health'] - stats['health'], 0) * health_scaler
        if time.time() - self.away_time > 120:
            reward -= 10

        if stats['kills'] == 1:
            reward += 1000
            done = True

        elif stats['deaths'] == 1:
            reward -= 1000
            done = True
        
        return reward, done

    def update_stats(self, stats):
        self.state['stats'] = stats

    def update_positions(self, detections):
        champion_position = self.state['positions'][self.champion]
        self.state['positions'].clear()
        self.state['positions'][self.champion] = champion_position
        for detection in detections:
            self.state['positions'][detection[0]] = detection[2]
        if (self.state['positions']['Minion_Red'] is not None) or (self.state['positions']['Minion_Blue'] is not None):
            self.away_time = time.time()

    def step(self, action):
        perform_action(action, self.champion, self.opponent, self.state['positions'])
        sct_img = self.sct.grab(self.sct.monitors[1])
        observation, detections = self.get_observation(sct_img)
        stats = self.state['stats']
        if time.time() - self.start_time > 600:
            reward, done = -10001, True
        else:
            try:
                stats = get_stats(sct_img, self.state['stats'].copy(), self.opponent_template)
                reward, done = self.get_reward(stats)
            except RuntimeError:
                reward, done = -10001, True
        self.update_positions(detections)
        self.update_stats(stats)
        return observation, reward, done, {}

    def reset(self):
        try:
            leave_custom_game(self.sct)
        except RuntimeError:
            pass
        if self.self_play:
            if self.player == 1:
                create_custom_game(self.sct, self.self_play, password='lol12345', opponents=['bullse2ye', 'dutse2ye'],
                                   champion=self.champion, opponent_template=self.opponent_template)
            else:
                join_custom_game(self.sct, opponents=['raunaqtr'], champion=self.champion)
        else:
            create_custom_game(self.sct, self.self_play, password='lol12345', opponents=[],
                               champion=self.champion, opponent_template=self.opponent_template)
        if not check_champion(self.sct.grab(self.sct.monitors[1]), self.champion):
            return self.reset()
        self.start_time = time.time()
        self.away_time = time.time()
        self.state = {
            'stats': {
                'kills': 0,
                'deaths': 0,
                'assists': 0,
                'minion_kills': 0,
                'health': 100,
                'opponent_health': 100
            },
            'positions': defaultdict(lambda: None)
        }
        sct_img = self.sct.grab(self.sct.monitors[1])
        observation, detections = self.get_observation(sct_img)
        self.update_positions(detections)
        return observation

    def render(self, mode='human'):
        pass
