stdscr = None


def init(scr):
    global stdscr
    stdscr = scr
    stdscr.scrollok(True)


def message(message):
    stdscr.scroll()
    height, width = stdscr.getmaxyx()
    stdscr.move(height - 1, 0)
    stdscr.addstr(str(message))


def get_char():
    return chr(stdscr.getch())
