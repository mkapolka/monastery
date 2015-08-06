stdscr = None


def init(scr):
    global stdscr
    stdscr = scr
    stdscr.scrollok(True)


def message(message):
    stdscr.addstr(str(message))
    y, x = stdscr.getyx()
    stdscr.move(y + 1, 0)


def get_char():
    return chr(stdscr.getch())
