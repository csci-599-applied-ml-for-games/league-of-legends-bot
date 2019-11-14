import sys
from PIL import Image, ImageOps
import pytesseract
from pynput import mouse, keyboard, _util
import time
import pygetwindow as gw
import re
import cv2
if sys.platform != 'darwin':
    import ctypes

if sys.platform == 'darwin':
    DIK_ESCAPE, DIK_Y = 0x35, 0x10
else:
    DIK_ESCAPE, DIK_Y = 0x01, 0x15
    SendInput = ctypes.windll.user32.SendInput

MAX_WIDTH, MAX_HEIGHT = 1920, 1080

mouse_controller = mouse.Controller()
keyboard_controller = keyboard.Controller()

def PressKeyPynput(hexKeyCode):
    if sys.platform == 'darwin':
        keyboard_controller.press(keyboard.KeyCode.from_vk(hexKeyCode))
    else:
        extra = ctypes.c_ulong(0)
        ii_ = _util.win32.INPUT_union()
        ii_.ki = _util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
        x = _util.win32.INPUT(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKeyPynput(hexKeyCode):
    if sys.platform == 'darwin':
        keyboard_controller.release(keyboard.KeyCode.from_vk(hexKeyCode))
    else:
        extra = ctypes.c_ulong(0)
        ii_ = _util.win32.INPUT_union()
        ii_.ki = _util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
        x = _util.win32.INPUT(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def no_op(champion, opponent, positions):
    pass


def move_up(champion, opponent, positions):
    if positions[champion] is None:
        return
    x, y, w, h = positions[champion]
    mouse_controller.position = (int(x), max(0, int(y - h)))
    mouse_controller.click(mouse.Button.right)


def move_right(champion, opponent, positions):
    if positions[champion] is None:
        return
    x, y, w, h = positions[champion]
    mouse_controller.position = (min(MAX_WIDTH, int(x + w)), int(y))
    mouse_controller.click(mouse.Button.right)


def move_down(champion, opponent, positions):
    if positions[champion] is None:
        return
    x, y, w, h = positions[champion]
    mouse_controller.position = (int(x), min(MAX_HEIGHT, int(y + h)))
    mouse_controller.click(mouse.Button.right)


def move_left(champion, opponent, positions):
    if positions[champion] is None:
        return
    x, y, w, h = positions[champion]
    mouse_controller.position = (max(0, int(x - w)), int(y))
    mouse_controller.click(mouse.Button.right)


def attack_minion(champion, opponent, positions):
    if positions['Minion_Red'] is None:
        return
    x, y, w, h = positions['Minion_Red']
    mouse_controller.position = (int(x), int(y))
    mouse_controller.click(mouse.Button.right)


def attack_champion(champion, opponent, positions):
    if positions[opponent] is None:
        return
    x, y, w, h = positions[opponent]
    mouse_controller.position = (int(x), int(y))
    mouse_controller.click(mouse.Button.right)


def find_subset_indices(sub, lst):
    indices = []
    ln = len(sub)
    for i in range(len(lst) - ln + 1):
        if lst[i: i + ln] == sub:
            indices.append(i)
    return indices


def start_screen_play(sct, game_window_region):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.071875 * width), int(0.0375 * height), int(0.11875 * width), int(0.075 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['PLAY'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        return
    raise TimeoutError('Retry limit exhausted')


def play_screen_create_custom(sct, game_window_region):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.26875 * width), int(0.1125 * height), int(0.38125 * width), int(0.1625 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['CREATE', 'CUSTOM'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        return
    raise TimeoutError('Retry limit exhausted')


def create_custom_screen_confirm(sct, game_window_region, password):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.43125 * width), int(0.6125 * height), int(0.49375 * width), int(0.65 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['Blind', 'Pick'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(0.5)

        region = (int(0.55625 * width), int(0.775 * height), int(0.65 * width), int(0.825 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['Friends', 'List', 'Only'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(0.5)

        region = (int(0.0203125 * width), int(0.7875 * height), int(0.175 * width), int(0.8375 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['PASSWORD', '(OPTIONAL)'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(0.5)

        with keyboard_controller.pressed(keyboard.Key.cmd if sys.platform == 'darwin' else keyboard.Key.ctrl):
            keyboard_controller.press('a')
            keyboard_controller.release('a')
        time.sleep(0.01)
        for key in password:
            keyboard_controller.press(key)
            keyboard_controller.release(key)
            time.sleep(0.01)
        time.sleep(0.5)

        region = (int(0.3875 * width), int(0.9375 * height), int(0.45625 * width), int(0.9625 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['CONFIRM'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(3)
        return
    raise TimeoutError('Retry limit exhausted')


def party_screen_invite(sct, game_window_region):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.70625 * width), int(0.15 * height), int(0.76875 * width), int(0.1875 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['INVITE'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        return
    raise TimeoutError('Retry limit exhausted')


def invite_popup_send_invites(sct, game_window_region, opponents):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.3625 * width), int(0.1 * height), int(0.64375 * width), int(0.85 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT, config='--psm 11')
        matches = []
        for opponent in opponents:
            matches = matches or find_subset_indices([opponent], words['text'])
            if matches:
                break
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(0.5)

        region = (int(0.45625 * width), int(0.875 * height), int(0.55 * width), int(0.9 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['SEND', 'INVITES'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        return
    raise TimeoutError('Retry limit exhausted')


def party_screen_add_bot(sct, game_window_region):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.715625 * width), int(0.3222222 * height), int(0.759375 * width), int(0.35 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['‘Add', 'Bot'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        yOffset = int(0.0625 * height)
        xOffset = -int(0.165625 * width)
        options_xOffset = int(0.10625 * width)
        options_yOffset = int(0.20416666 * height)

        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2 + options_yOffset / 2))
        mouse_controller.scroll(0, -2000)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2 + options_yOffset))
        mouse_controller.click(mouse.Button.left)
        time.sleep(3)

        y += yOffset
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2 + options_yOffset / 2))
        mouse_controller.scroll(0, -2000)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2 + options_yOffset))
        mouse_controller.click(mouse.Button.left)
        time.sleep(3)

        y += yOffset
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2 + xOffset),
                                     int(y + game_window_region['top'] + h / 2 + options_yOffset / 2))
        mouse_controller.scroll(0, -2000)
        time.sleep(1)

        mouse_controller.scroll(0, 125)
        time.sleep(1)
        return


def bot_options_veigar(sct, game_window_region):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.5203125 * width), int(0.5 * height), int(0.6421875 * width), int(0.697222222 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = []
        for champion in ['Veigar', 'Velgar']:
            matches = matches or find_subset_indices([champion], words['text'])
            if matches:
                break
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(3)
        return


def party_screen_start_game(sct, game_window_region, self_play, opponents):
    retries = 40
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        if self_play:
            region = (int(0.4125 * width), int(0.2625 * height), int(0.8125 * width), int(0.6625 * height))
            words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT, config='--psm 11')
            matches = []
            for opponent in opponents:
                matches = matches or find_subset_indices([opponent], words['text'])
                if matches:
                    break
            if len(matches) == 0:
                retries -= 1
                time.sleep(1)
                continue
            time.sleep(0.5)

        region = (int(0.378125 * width), int(0.9375 * height), int(0.4625 * width), int(0.9625 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['START', 'GAME'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(3)
        return
    raise TimeoutError('Retry limit exhausted')


def champion_screen_search(sct, game_window_region, champion):
    retries = 30
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.4875 * width), int(0.1333333 * height), int(0.553125 * width), int(0.1569444 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['Sort', 'By', 'Name'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0] + 2
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w + 0.04*width),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(0.5)

        with keyboard_controller.pressed(keyboard.Key.cmd if sys.platform == 'darwin' else keyboard.Key.ctrl):
            keyboard_controller.press('a')
            keyboard_controller.release('a')
        time.sleep(0.01)
        for key in champion:
            keyboard_controller.press(key)
            keyboard_controller.release(key)
            time.sleep(0.01)
        time.sleep(1)
        return


def champion_screen_lock_in(sct, game_window_region, champion):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.25 * width), int(0.2875 * height), int(0.75 * width), int(0.3125 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT, config='--psm 6')
        matches = find_subset_indices([champion], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(0.5)

        region = (int(0.46875 * width), int(0.825 * height), int(0.53125 * width), int(0.8625 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['LOCK', 'IN'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(80)
        return
    raise TimeoutError('Retry limit exhausted')


def create_custom_game(sct, self_play=False, password='lol12345', opponents=['bhanuarora05', 'bhanuaroraos'], champion='Ashe'):
    try:
        game_window = gw.getWindowsWithTitle('League of Legends')[0]
        assert game_window.title == 'League of Legends'
    except (IndexError, AssertionError):
        raise RuntimeError('League of Legends not running')
    game_window.minimize()
    game_window.restore()
    time.sleep(1)
    game_window_region = {
        'left': game_window.left,
        'top': game_window.top,
        'width': game_window.width,
        'height': game_window.height
    }
    start_screen_play(sct, game_window_region)
    play_screen_create_custom(sct, game_window_region)
    create_custom_screen_confirm(sct, game_window_region, password)
    if self_play:
        party_screen_invite(sct, game_window_region)
        invite_popup_send_invites(sct, game_window_region, opponents)
    else:
        party_screen_add_bot(sct, game_window_region)
        bot_options_veigar(sct, game_window_region)
    party_screen_start_game(sct, game_window_region, self_play, opponents)
    champion_screen_search(sct, game_window_region, champion)
    champion_screen_lock_in(sct, game_window_region, champion)

    global MAX_WIDTH, MAX_HEIGHT
    MAX_WIDTH = sct.monitors[1]['width']
    MAX_HEIGHT = sct.monitors[1]['height']
    PressKeyPynput(DIK_Y)
    ReleaseKeyPynput(DIK_Y)
    time.sleep(0.5)
    mouse_controller.position = (int(0.9223958 * MAX_WIDTH), int(0.8777777 * MAX_HEIGHT))
    mouse_controller.click(mouse.Button.right)
    time.sleep(20)


def start_screen_join(sct, game_window_region, opponents):
    retries = 40
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.825 * width), int(0.1125 * height), int(0.99375 * width), int(0.25 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT, config='--psm 11')
        matches = []
        if find_subset_indices(['GAME', 'INVITES'], words['text']):
            for opponent in opponents:
                if find_subset_indices([opponent], words['text']):
                    matches = find_subset_indices(['x'], words['text'])
                    break
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0] - 1
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(10)
        return
    raise TimeoutError('Retry limit exhausted')


def join_custom_game(sct, opponents=['bhanuarora05', 'bhanuaroraos'], champion='Ashe'):
    try:
        game_window = gw.getWindowsWithTitle('League of Legends')[0]
        assert game_window.title == 'League of Legends'
    except (IndexError, AssertionError):
        raise RuntimeError('League of Legends not running')
    game_window.minimize()
    game_window.restore()
    time.sleep(1)
    game_window_region = {
        'left': game_window.left,
        'top': game_window.top,
        'width': game_window.width,
        'height': game_window.height
    }
    start_screen_join(sct, game_window_region, opponents)
    champion_screen_search(sct, game_window_region, champion)
    champion_screen_lock_in(sct, game_window_region, champion)

    global MAX_WIDTH, MAX_HEIGHT
    MAX_WIDTH = sct.monitors[1]['width']
    MAX_HEIGHT = sct.monitors[1]['height']
    PressKeyPynput(DIK_Y)
    ReleaseKeyPynput(DIK_Y)
    time.sleep(0.5)
    mouse_controller.position = (int(0.9333333 * MAX_WIDTH), int(0.862037 * MAX_HEIGHT))
    mouse_controller.click(mouse.Button.right)
    time.sleep(20)


def options_screen_exit_game(sct, game_window_region):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.28125 * width), int(0.7898148 * height), int(0.334375 * width), int(0.81574074 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['Exit', 'Game'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(1)
        return
    raise TimeoutError('Retry limit exhausted')


def exit_game_popup_leave_game(sct, game_window_region):
    retries = 20
    while retries:
        sct_img = sct.grab(game_window_region)
        img = ImageOps.invert(Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX'))
        width, height = img.size
        region = (int(0.40625 * width), int(0.49074074 * height), int(0.4625 * width), int(0.5175925 * height))
        words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT)
        matches = find_subset_indices(['Leave', 'Game'], words['text'])
        if len(matches) == 0:
            retries -= 1
            time.sleep(1)
            continue
        index = matches[0]
        (x, y, w, h) = (words['left'][index] + region[0], words['top'][index] + region[1],
                        words['width'][index], words['height'][index])
        mouse_controller.position = (int(x + game_window_region['left'] + w / 2),
                                     int(y + game_window_region['top'] + h / 2))
        mouse_controller.click(mouse.Button.left)
        time.sleep(5)
        return
    raise TimeoutError('Retry limit exhausted')


def leave_custom_game(sct):
    try:
        gw.getWindowsWithTitle('League of Legends (TM) Client')[0]
    except IndexError:
        raise RuntimeError('League of Legends client not running')

    PressKeyPynput(DIK_ESCAPE)
    ReleaseKeyPynput(DIK_ESCAPE)
    time.sleep(1)
    options_screen_exit_game(sct, sct.monitors[1])
    exit_game_popup_leave_game(sct, sct.monitors[1])


def get_stats(sct_img):
    stats = {}
    orig_img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
    img = ImageOps.invert(orig_img)
    width, height = img.size
    region = (int(0.8671875 * width), int(0.0009259 * height), int(0.915625 * width), int(0.0259259 * height))
    words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT, config='--psm 6')
    matches = [i for i, word in enumerate(words['text']) if re.match(r'^[0-9]+\/[0-9]+\/[0-9]+$', word) is not None]
    if len(matches) > 0:
        data = words['text'][matches[0]].strip().split('/')
        stats['kills'] = int(data[0])
        stats['deaths'] = int(data[1])
        stats['assists'] = int(data[2])
    region = (int(0.925 * width), int(0.0009259 * height), int(0.95625 * width), int(0.0259259 * height))
    words = pytesseract.image_to_data(img.crop(region), output_type=pytesseract.Output.DICT, config='--psm 6')
    matches = [i for i, word in enumerate(words['text']) if re.match(r'^[0-9]+$', word) is not None]
    if len(matches) > 0:
        stats['minion_kills'] = int(words['text'][matches[0]].strip())
    region = (int(0.3546875 * width), int(0.9527777 * height), int(0.56875 * width), int(0.96666666 * height))
    hsv = cv2.cvtColor(np.array(orig_img.crop(region))[:, :, ::-1], cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, (36, 25, 25), (70, 255, 255))
    labels, statistics = cv2.connectedComponentsWithStats(mask, 4)[1:3]  # step 4
    largest_label = 1 + np.argmax(statistics[1:, cv2.CC_STAT_AREA])
    stats['health'] = int(round(np.max(np.argwhere(labels == largest_label)[:, 1])*100/mask.shape[1]))
    return stats


actions = [
        no_op,
        move_up,
        move_right,
        move_down,
        move_left,
        attack_minion,
        attack_champion
    ]


def perform_action(action, champion, opponent, positions):
    global actions
    actions[action](champion, opponent, positions)

'''
print(words)
img = np.array(img.crop(region))[:, :, ::-1]
n_boxes = len(words['level'])
for i in range(n_boxes):
    if words['text'][i].strip() == '' or int(words['conf'][i]) < 0:
        continue
    (x, y, w, h) = (words['left'][i], words['top'][i], words['width'][i], words['height'][i])
    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
cv2.imshow('img', img)
cv2.waitKey(0)
'''
'''
class ExtractImageWidget(object):
    def __init__(self, sct, game_window_region):
        self.original_image = np.array(sct.grab(game_window_region))
        print(self.original_image.shape)

        self.clone = self.original_image.copy()

        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.extract_coordinates)

        # Bounding box reference points and boolean if we are extracting coordinates
        self.image_coordinates = []
        self.extract = False

    def extract_coordinates(self, event, x, y, flags, parameters):
        # Record starting (x,y) coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.image_coordinates = [(x,y)]
            self.extract = True

        # Record ending (x,y) coordintes on left mouse bottom release
        elif event == cv2.EVENT_LBUTTONUP:
            self.image_coordinates.append((x,y))
            self.extract = False
            print('top left: {}, bottom right: {}'.format(self.image_coordinates[0], self.image_coordinates[1]))

            # Draw rectangle around ROI
            cv2.rectangle(self.clone, self.image_coordinates[0], self.image_coordinates[1], (0,255,0), 2)
            cv2.imshow("image", self.clone)

        # Clear drawing boxes on right mouse button click
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.clone = self.original_image.copy()

    def show_image(self):
        return self.clone

extract_image_widget = ExtractImageWidget(sct, game_window_region)
while True:
    cv2.imshow('image', extract_image_widget.show_image())
    key = cv2.waitKey(1)

    # Close program with keyboard 'q'
    if key == ord('q'):
        cv2.destroyAllWindows()
        exit(1)
'''