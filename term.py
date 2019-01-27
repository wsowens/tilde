import curses
import logging
from queue import Queue

class Cursor:
    def __init__(self, r, c):
        self.r = r
        self.c = c

class Buffer:
    def __init__(self):
        self.rows = [""] 
        self.new_rows = []

    def append(self, input_string):
        new_rows = input_string.split("\n")
        # add the content of this row directly to the last
        self.rows[0] += new_rows[0]
        # any newlines mean splitting into new row of buffer
        self.rows.extend(new_rows[1:])
    
    def clear(self):
        self.rows = [""]

    def __iadd__(self, input_string):
        '''overriding += with append'''
        self.append(input_string)
        return self

    def __len__(self):
        return len(self.rows)

    #def new(self):
         

#class BoundedBuffer:
     


class InputStream:
    '''wrapping window.getchr() into an input stream'''
    def __init__(self, win):
        self._win = win
        # setting no delay that we don't wait forever
        self._win.nodelay(True)
    
    def __iter__(self):
        char = self._win.getchr()
        if char == -1:
            return
        yield char
    

class Renderer:
    def __init__(self, screen):
        self._scr = screen
    
    def from_buffer(self, buff, wrap=True):
        self._scr.clear()
        logging.info("Attempting to render from buffer:\n{}".format(buff))
        # get the minimum number of lines available
        lines_available = min(curses.LINES, len(buff))
        if isinstance 
            self._scr.addstr(0, 0, buff)
        else:
            lines = buff.split("\n")
            can_render = min(curses.LINES, len(lines))
            for i in range(can_render):
                self._scr.addstr(i, 0, lines[i-can_render][:curses.COLS])
    
    def refresh(self):
        self._scr.refresh()
    
            
class Terminal:
    
    def __init__(self):
        self.scr = curses.initscr()
        #disable input delays
        self.scr.nodelay(False)
        self.render = Renderer(self.scr)
        self._has_echo = True
        self._has_cbreak = False
        self.cbreak()
        self.echo()
        self.last_update = 0
        self.cursor = Cursor(0, 0)
        self.buff = ""
        
    
    def echo(self, to_echo=None):
        '''Turn echo on or off
        if no argument provided, echo is toggled
        '''
        if to_echo is None:
            to_echo = not self._has_echo
        if to_echo:
            curses.echo()
            self._has_echo = True
        else:
            curses.noecho()
            self._has_echo = False
    
    def cbreak(self, to_cbreak=None):
        '''Turn cbreak on or off 
        if no argument is provided, cbreak is toggled
        '''
        if to_cbreak is None:
            to_cbreak = not self._has_cbreak
        if to_cbreak:
            self._has_cbreak = True
            curses.cbreak()
        else:
            curses.nocbreak()
            self._has_cbreak = False
    
    def __del__(self):
        '''Cleaning up all of our curses mess'''
        curses.nocbreak()
        self.scr.keypad(False)
        curses.echo()
        curses.endwin()

    def resize(self):
        y, x = self.scr.getmaxyx()
        curses.resizeterm(y,x)
        self.render.from_buffer(self.buff, wrap=False)
        self.scr.refresh()
        
    def update(self):
        logging.info("Doing update")
        char = self.scr.getch()
        if char == -1:
            return
       
        logging.debug("Keypress: {}".format(char))
        
        if char == ord('w'):
            self.buff += "\nhi there!"
            self.render.from_buffer(self.buff, wrap=False)
            self.render.refresh()
        elif char == curses.KEY_RESIZE:
            self.resize()
            while self.scr.getch() == curses.KEY_RESIZE:
                continue
            self.resize()
        else:
            self.render.from_buffer(self.buff, wrap=False)
            self.render.refresh()
        
    

class Application:
    def __init__(self, win):
        self.win = win
        self.render = Renderer(self.win)
        
    
    def update(self, take_input=True):
        
        self.render.refresh()
        
        
