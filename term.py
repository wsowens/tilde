import curses

from time import time
import logging

class Cursor:
	def __init__(self, r, c):
		self.r = r
		self.c = c


class Buffer:
	pass

class BoundedBuffer:
	def __init__(self, rows, cols):
		self.cols = cols
		self.chars = ""
	'''
	def append(self, string):
		current_row = self.rows[:-1]
		for char in string:
			while len(current_row) < self.cols:
	'''
	#def __setattr__(self, name, value):
		
	
	def resize(self):
		pass
		
	
	
	def __iter__(self):
		for row in self.rows:
			yield row

class Viewport:
	pass

class InputStream:
	'''wrapping window.getchr() into an input stream'''
	def __init__(self, win):
		self._win = win
		# setting no delay that we don't wait forever
		self._win.nodelay(True)
	
	def __iter__(self):
		c = self._win.getchr()
		if c == -1:
			return
		yield c
	

class Renderer:
	def __init__(self, screen):
		self._scr = screen
	
	def from_buffer(self, buff, wrap=True):
		self._scr.clear()
		logging.info("Attempting to render from buffer:\n{}".format(buff))
		if wrap:
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
			self.echo =True
		else:
			curses.noecho()
			self.echo = False
	
	def cbreak(self, to_cbreak=None):
		'''Turn cbreak on or off 
		if no argument is provided, cbreak is toggled
		'''
		if to_cbreak is None:
			to_cbreak = not self._has_cbreak
		if to_cbreak:
			self.cbreak = True
			curses.cbreak()
		else:
			curses.nocbreak()
			self.cbreak = False
	
	def __del__(self):
		'''Cleaning up all of our curses mess'''
		curses.nocbreak()
		self.scr.keypad(False)
		curses.echo()
		curses.endwin()

	def resize(self):
		y, x = self.scr.getmaxyx()
		curses.resizeterm(y,x)
		self.render.from_buffer(self.buff)
		
	def update(self):
		logging.info("Doing update")
		char = self.scr.getch()
		if char != -1:
			logging.debug(str(char))
		if char == curses.KEY_RESIZE:
			self.resize()
		if char == ord('w'):
			self.buff += "\nhi there!"
		self.render.from_buffer(self.buff, True)
		self.render.refresh()
		
	

class Application:
	def __init__(self, win):
		self.win = win
		self.render = Renderer(self.win)
		
	
	def update(self, take_input=True):
		
		self.renderer.refresh()
		
		