
import inspect
import time

from typing import Dict, List, Tuple, Optional, Union


class ExecTimer:
	""" NOTE: Can't handle multithreading. Execution stored in a stack.
	"""

	PRINT_DURING_EXECUTION = False
	
	class ExecMemory:
		name: str
		times_called: float
		total_exec_time: float
		total_children_exec_time: float
		
		def __init__(self, name:str):
			self.name = name
			self.times_called = 0
			self.total_exec_time = 0
			self.total_children_exec_time = 0
		
		def add_execution(self, exec_time, children_exec_time):
			self.times_called += 1
			self.total_exec_time += exec_time
			self.total_children_exec_time += children_exec_time
		
		def average_exec_time(self, count_children_exec_time=True) -> float:
			exec_time = self.total_exec_time

			if not count_children_exec_time:
				exec_time -= self.total_children_exec_time
				
			return exec_time / self.times_called
		
	memory: Dict[str, 'ExecMemory']
	stack: List[List[Union[str, float]]]
	
	def __init__(self):
		self.stack = []
		self.memory = {}
	
	
	def start(self, suffix=""):
		caller = inspect.stack()[1].function + suffix
		
		if self.PRINT_DURING_EXECUTION:
			print(len(self.stack)*"|  " + f"{caller}.start")
		
		self.stack.append([caller, time.time(), 0])
		
		
	def end(self, suffix=""):
		now = time.time()
		caller = inspect.stack()[1].function + suffix
		
		while self.stack:
			top = self.stack.pop(-1)
			if top[0] == caller:
				break 
		
		start = top[1]
		execution_time = now-start
		children_execution_time = top[2]

		if self.stack:
			over = self.stack[-1]
			over[2] += execution_time

		# Add to memory
		if not caller in self.memory:
			self.memory[caller] = self.ExecMemory(caller)
		memory_slot = self.memory[caller]
		memory_slot.add_execution(execution_time, children_execution_time)
		
		if self.PRINT_DURING_EXECUTION:
			print(len(self.stack)*"|  " + f"{caller}.end\t\t\texec_time:{execution_time}\tnot_children:{execution_time-children_execution_time}")
		
		return execution_time
		

	def print_memory(self):
		
		print("___EXECUTION_MEMORY___")
		
		for name, obj in sorted(self.memory.items(), key=lambda x: -x[1].average_exec_time(False)):			
			print("|\n>___" + f"{name}".ljust(76, "_"))
			print(f"|     avrg_exec_time: {obj.average_exec_time():.8f}")
			print(f"|  avrg_time_in_func: {obj.average_exec_time(False):.8f}")


exec_timer = ExecTimer()
