'''Includes all basic terminal functionality'''
import curses
import logging
import re
def chunk_str(input_str, size):
    if "\n" in input_str:
        output = []
        for item in map(lambda x: chunk_str(x, size), input_str.split("\n")):
            output += item
        return output
    if len(input_str) == 0:
        return []
    return [input_str[:size]] + chunk_str(input_str[size:], size)

NONWHITESPACE = re.compile(r"\S+")
def chunk_word(input_str, size):
    '''makes formatting assumptions, do not use for something like a shell'''
    global WHITESPACE
    if "\n" in input_str:
        output = []
        for item in map(lambda x: chunk_word(x, size), input_str.split("\n")):
            output += item
        return output
    
    words = [str(match) for match in NONWHITESPACE.findall(input_str)]
    print(words)
    output = []
    current = ""
    for word in words:
        print(word)
        print(output)
        remaining = size - len(current)
        if len(word) == remaining:
            current += word 
        elif len(word) < remaining:
            current += word + " "
        elif len(word) == size:
            output.append(current)
            current = ""
            current += word + " "
        elif len(word) < size:
            output.append(current)
            current = ""
            current += word + " "
        else:
            while word:
                remaining = size - len(current)
                if len(word) > remaining:
                    current += (word[:remaining-1] + "-")
                    word = word[remaining-1:]
                    output.append(current)
                    current = ""
                elif len(word) < remaining:
                    current += word + " "
                    output.append(current)
                    word = ""
                    current = ""
                else:
                    current += word
                    output.append(current)
                    word = ""
                    current = ""
                    
    if current != "":
        output.append(current)
    return output

print("12345678901234567890")
for line in chunk_word("Super epic long sentence. Here's a new line.\nAhh, an extrordinarily great day!", 10):
    print(line)
    
print("12345678901234567890")
for line in chunk_str("Super epic long sentence. Here's a new line.\nAhh, an extrordinarily great day!", 10):
    print(line)   
#def wrap_words(input_str, size):

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
        new_buff.append(str(old))
    



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

    def entire_buffer(self, buff, wrap=True):
        '''render an entire buffer, including old data'''
        self._scr.clear()
        height, width = self._scr.getmaxyx()
        logging.info("Attempting to render from buffer:\n%s" % str(buff)[:10])
        # get the minimum number of lines available
        lines_avail = min(height, len(buff))
        for line_no in range(lines_avail):
            self._scr.addstr(line_no, 0, list(buff)[line_no-lines_avail][:width])
    '''
        else:
            lines = buff.split("\n")
            can_render = min(y, len(lines))
            for i in range(can_render):
                self._scr.addstr(i, 0, lines[i-can_render][:x])
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
        self.scr.keypad(True)
        self.render = Renderer(self.scr)
        self._has_echo = None
        self._has_cbreak = None
        self.cbreak(True)
        self.echo(False)
        self.buff = BoundedBuffer(curses.COLS)
        self._updater = self._main_update
        self.modestack = []


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
        self._updater()
    
    def revert_mode(self):
        if self.modestack:
            self._updater = self.modestack.pop()
        else:
            self._updater = self._main_update
    
    def set_mode(self, mode):
        self.modestack.append(self._updater)
        self._updater = mode
    
    curvis = 0 
    def _main_update(self):
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
        elif char == ord('d'):
            self.spawn_dialog("Test", "This is a test. What is your favorite programming language??? Remember, there are no wrong answers, unless you pick java.", ["<Java>", "<Python>", "<Bash>"])
        elif char == ord('v'):
            curses.curs_set(self.curvis)
            self.curvis = (self.curvis + 1 ) % 3
        else:
            self.render.entire_buffer(self.buff)
            self.render.refresh()
   
    def spawn_dialog(self, title, msg, options):
        height,width = self.scr.getmaxyx()
        subheight = height // 2
        subwidth = width // 2
        starty = (height - subheight) // 2
        startx = (width - subwidth) // 2
        subwin = self.scr.subwin(subheight, subwidth, starty, startx)
        dialog = DialogWindow(self, subwin, title, msg, options)


class DialogWindow:
    def __init__(self, term, window, title, msg, options):
        self.term = term
        term.set_mode(self.update)

        self.window = window
        self.window.nodelay(True)
        y, x = window.getmaxyx()
        self.width = x
        self.height = y
        if title is not None:
            spaces = ((x + 1) - len(title) ) // 2  - 1
            spaces = " " * spaces 
            title = spaces + title
        else:
            title = ""
        self.title = title
        self.msg = msg
        self.options = options
        self.selected = 0
        self.done = False
        self.render()
        curses.curs_set(0)

    def update(self): 
        char = self.term.scr.getch()
        logging.info("UPDATE LOOP")
        logging.info("%s\n" %  char)
        logging.info("This is what key_left is:%s" % curses.KEY_LEFT)
        if char == -1:
            return
        elif char == 10:
            self.done = True
            self.term.revert_mode()
            curses.curs_set(2)
            return self.selected
        elif char == curses.KEY_LEFT:
            logging.info("KEY_LEFT")
            self.selected = (self.selected - 1) % len(self.options)
            self.render()
        elif char == curses.KEY_RIGHT:
            self.selected = (self.selected - 1) % len(self.options)
            self.render()
    
    def render(self):
        self.window.clear()
        self.window.border(curses.ACS_BLOCK, curses.ACS_BLOCK , curses.ACS_BLOCK, curses.ACS_BLOCK, curses.ACS_BLOCK, curses.ACS_BLOCK, curses.ACS_BLOCK, curses.ACS_BLOCK)
        self.window.addnstr(1, 1, self.title, self.width - 3, curses.A_BOLD)
        # break msg into chunks
        start_y = 3
        for chunk in chunk_word(self.msg, self.width - 4):
            self.window.addnstr(start_y, 2, chunk, self.width-3)
            start_y += 1
        for index, pos, option in self.spatially_format():
            if index == self.selected:
                self.window.addstr(self.height-3, pos, option, curses.A_REVERSE)
            else:
                self.window.addstr(self.height-3, pos, option)
        self.window.refresh()

    def spatially_format(self):
        lengths = list(map(len, self.options))
        free_space = self.width - sum(lengths) - 2
        inner_space = free_space // (len(self.options))
        output = []
        left_space = (inner_space + free_space % (len(self.options) + 1)) // 2
        start = left_space
        for index, opt in enumerate(self.options):
            output.append((index, start, opt))
            start += inner_space + len(opt)  
        return output

class Application:
    def __init__(self, win):
        self.win = win
        self.render = Renderer(self.win)
        
    
    def update(self, take_input=True):
        
        self.render.refresh()
        
        
