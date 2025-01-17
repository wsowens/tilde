#!/usr/bin/env python3
'''Main script to launch the game'''
import logging
import sys
import traceback
import term

logging.basicConfig(filename='backup.log', level=logging.DEBUG, filemode='w')

myterm = term.Terminal()

LIPSUM='''Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
'''

text = sys.argv[1] if len(sys.argv) > 1 else LIPSUM
myterm.buff += text + "\n"
try:
    while True:
        #handle background events
        myterm.update()
        '''
        Un-comment this out later
        try:
            myterm.update()
        except KeyboardInterrupt:
            myterm.buff += "\nLeave? Nobody is allowed to leave."
        '''
except Exception as ex:
    logging.critical(str(ex))
    logging.critical(traceback.format_exc())
