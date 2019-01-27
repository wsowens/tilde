'''Includes all basic terminal functionality'''
import curses
import logging


class Buffer:
    '''Buffer without bounds on the rows'''

    def __init__(self):
        self.rows = [""]

    def append(self, input_string):
        '''append text to the buffer'''
        new_rows = input_string.split("\n")
        # add the content of this row directly to the last
        self.rows[0] += new_rows[0]
        # any newlines mean splitting into new row of buffer
        self.rows.extend(new_rows[1:])

    def __iadd__(self, input_string):
        '''overriding += with append'''
        self.append(input_string)
        return self

    def __iter__(self):
        '''iterate over every row'''
        for line in self.rows:
            yield line
        #while self.new_rows:
        #    yield self.new_rows.pop(0)

    def __len__(self):
        '''return the number of lines'''
        return len(self.rows)

    def clear(self):
        '''clears everything in the buffer'''
        self.rows = [""]
        self.new_rows = []

    def __str__(self):
        return "\n".join(self.rows)


#please tell me this wasn't a waste of time
class BoundedBuffer(Buffer):
    '''a buffer with a hard bound on the length of rows'''
    def __init__(self, bound):
        self._bound = bound
        super().__init__()

    def append(self, input_string):
        # make it flow onto the previous line
        first = True
        for unbound_row in input_string.split("\n"):
            if first:
                first = False
            else:
                self.rows.append("")
            while unbound_row:
                to_add = self._bound - len(self.rows[-1])
                self.rows[-1] += (unbound_row[: to_add])
                #print("To add: " + str(to_add))
                #print("Updated: " + self.rows[-1])
                # take the rest of the string
                unbound_row = unbound_row[to_add:]
                #print("Reduced: " + unbound_row)
                if unbound_row:
                    self.rows.append("")


    @staticmethod
    def convert_unbounded(old, bound):
        new_buff = BoundedBuffer(bound)
        new_buff.append(str(old)
    



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

    def entire_buffer(self, buff):
        '''render an entire buffer, including old data'''
        self._scr.clear()
        logging.info("Attempting to render from buffer:\n%s" % str(buff))
        # get the minimum number of lines available
        lines_avail = min(curses.LINES, len(buff))
        cols_avail = curses.COLS
        for line_no in range(lines_avail):
            self._scr.addstr(line_no, 0, list(buff)[line_no-lines_avail][:cols_avail])
    '''
        else:
            lines = buff.split("\n")
            can_render = min(curses.LINES, len(lines))
            for i in range(can_render):
                self._scr.addstr(i, 0, lines[i-can_render][:curses.COLS])
 '''
    def refresh(self):
        '''refresh the screen'''
        self._scr.refresh()


class Terminal:
    '''class representing the Terminal'''
    def __init__(self):
        self.scr = curses.initscr()
        #disable input delays
        self.scr.nodelay(False)
        self.render = Renderer(self.scr)
        self._has_echo = None
        self._has_cbreak = None
        self.cbreak(True)
        self.echo(False)
        self.buff = Buffer()


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
        '''resize the screen'''
        # move to the renderer
        y, x = self.scr.getmaxyx()
        curses.resizeterm(y, x)
        self.render.entire_buffer(self.buff)
        self.scr.refresh()

    def update(self):
        logging.info("Doing update")
        char = self.scr.getch()
        if char == -1:
            return

        logging.debug("Keypress: {}".format(char))

        if char == ord('w'):
            self.buff += "hi there!"
            self.render.entire_buffer(self.buff)
            self.render.refresh()
        elif char == curses.KEY_RESIZE:
            self.resize()
            while self.scr.getch() == curses.KEY_RESIZE:
                continue
            self.resize()
        else:
            self.render.entire_buffer(self.buff)
            self.render.refresh()


class Application:
    def __init__(self, win):
        self.win = win
        self.render = Renderer(self.win)
        
    
    def update(self, take_input=True):
        
        self.render.refresh()
        
        
