#!/usr/bin/env python3
import curses
'''script to fix terminal in case the other program crashes'''

stdscr = curses.initscr()
stdscr.clear()
curses.nocbreak()
curses.echo()
stdscr.keypad(False)
curses.endwin()
print("Fixed!")