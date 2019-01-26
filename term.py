import curses

class Terminal:
	
	def __init__(self):
		self.scr = curses.initscr()
		self._has_echo = True
		self._has_cbreak = False
		self.cbreak()
		self.echo()
		
	
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