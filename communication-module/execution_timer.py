
import inspect
import time as Time

from typing import List, Tuple



class ExecTimer:
	""" NOTE: Can't handle multithreading. """
	
	stack: List[Tuple[str, float]]
	
	def __init__(self):
		self.stack = []
	
	def start(self):
		caller = inspect.stack()[1].function
		
		print(len(self.stack)*" " + f"{caller}.start")
		
		self.stack.append((caller, Time.time()))
		
		
	def end(self):
		now = Time.time()
		caller = inspect.stack()[1].function
		
		
		while self.stack:
			top = self.stack.pop(-1)
			if top[0] == caller:
				break 
		
		start = top[1]
		
		print(len(self.stack)*" " + f"{caller}.end\t\t\tt: {now-start}")
		


exec_timer = ExecTimer()
