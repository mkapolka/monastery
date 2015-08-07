import os

import curses

os.environ['ESCDELAY'] = '25'

stdscr = None
message_border = None
message_scr = None
input_border = None
room_scr = None


input_prompt = "[g]o [d]o [l]ook [e]xamine [w]ait [i]nventory [m]ove"


def init(scr):
    global stdscr
    global message_border
    global message_scr
    global input_scr

    stdscr = scr
    height, width = stdscr.getmaxyx()

    input_scr = stdscr.subwin(3, len(input_prompt) + 4, height - 3, 0)
    input_scr.box()
    input_scr.move(1, 2)
    input_scr.addstr(input_prompt)

    message_border = stdscr.subwin(height - 3, width, 0, 0)
    mh, mw = message_border.getmaxyx()
    message_scr = stdscr.subwin(height - 5, width - 2, 1, 1)
    message_scr.scrollok(True)
    message_border.box()


def refresh():
    stdscr.touchwin()
    stdscr.refresh()


def prompt(message, option_struct):
    whole_lines = [
        '[%s] %s' % (c, str) for (c, (str, object)) in option_struct.items()
    ]
    max_width = max(max(len(x) for x in whole_lines), len(message) + 4)
    num_lines = len(whole_lines)
    width = max_width + 4
    height = num_lines + 4

    scr_height, scr_width = stdscr.getmaxyx()
    win = curses.newwin(height, width, scr_height - height - 1, len(input_prompt) / 2 - width / 2)

    win.border()
    win.move(0, width / 2 - len(message) / 2)
    win.addstr(message)
    win.move(2, 2)
    for line in whole_lines:
        y, x = win.getyx()
        win.addstr(line)
        win.move(y + 1, x)
    win.refresh()
    ch = get_char(win)
    win.erase()
    win.refresh()
    stdscr.refresh()
    try:
        return option_struct[ch][1]
    except (ValueError, KeyError):
        return None


def message(message):
    message_scr.scroll()
    height, width = message_scr.getmaxyx()
    message_scr.move(height - 1, 0)
    message_scr.addstr(str(message))


def get_char(scr=None):
    if not scr:
        scr = stdscr
    key = scr.getch()
    if key == 27:  # Esc or Alt
        return 'ESC'
        # Don't wait for another key
        # If it was Alt then curses has already sent the other key
        # otherwise -1 is sent (Escape)
        scr.nodelay(True)
        n = scr.getch()
        scr.nodelay(False)
        if n == -1:
            # Escape was pressed
            return 'ESC'
    try:
        return chr(key)
    except ValueError:
        return -1
