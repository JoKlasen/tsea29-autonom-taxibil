
import inspect
import time
import threading

from typing import Dict, List, Tuple, Optional, Union


class NoExecTimer:
	
	def start(self,suffix=""):
		return 

	def end(self, suffix=""):
		return

	def print_time(self, suffix=""):
		return
		
	def print_memory(self):
		return


class ExecTimer(NoExecTimer):

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
	thread_stack: Dict[int, List[List[Union[str, float]]]]
	
	def __init__(self):
		self.thread_stack = {}
		self.memory = {}
	
	
	def thread_title(self, thread):
		return f"{thread.name}:{thread.ident}"
	

	def get_caller(self, suffix):
		
		caller_frame = inspect.stack()[2][0]

		ret = caller_frame.f_code.co_name + suffix
		
		if "self" in caller_frame.f_locals: 
			class_name = caller_frame.f_locals["self"].__class__.__name__
			ret = class_name + '.' + ret
			
		return ret
		
	
	def start(self, suffix=""):
		caller = self.get_caller(suffix)
				
		# Get stack for this thread
		thread = threading.current_thread()
		if thread.ident not in self.thread_stack:
			self.thread_stack[thread.ident] = []				

		# If to print during execution, mark this as a start
		if self.PRINT_DURING_EXECUTION:
			print(len(self.thread_stack[thread.ident])*"|  " + f"{caller}.start")		
		
		# Add item to stack with the current time (start measuring)
		self.thread_stack[thread.ident].append([caller, time.time(), 0])
				
	def end(self, suffix=""):
		# Finish measuring time
		now = time.time()
		caller = self.get_caller(suffix)
		
		# Get stack for this thread
		thread = threading.current_thread()
		thread_id = thread.ident
		thread_title = self.thread_title(thread)
		if thread_id not in self.thread_stack:
			self.thread_stack[thread_id] = []				
		
		# Get corresponding item from stack
		while self.thread_stack[thread_id]:
			top = self.thread_stack[thread_id].pop(-1)
			if top[0] == caller:
				break 
				
		start = top[1]
		
		# Calculate measured time
		execution_time = now-start
		children_execution_time = top[2]

		# If have parent, then time in children for parent is increased 
		# by this measured time
		if self.thread_stack[thread_id]:
			over = self.thread_stack[thread_id][-1]
			over[2] += execution_time

		# Add to memory
		if not caller in self.memory:
			self.memory[(thread_title, caller)] = self.ExecMemory(caller)
		memory_slot = self.memory[(thread_title, caller)]
		memory_slot.add_execution(execution_time, children_execution_time)
		
		if self.PRINT_DURING_EXECUTION:
			print(len(self.thread_stack[thread_id])*"|  " + f"{caller}.end\t\t\texec_time:{execution_time}\tnot_children:{execution_time-children_execution_time}")
		
		return execution_time
		
	def print_time(self, suffix=""):
		caller = self.get_caller(suffix)
		thread = threading.current_thread()
		thread_title = self.thread_title(thread)
		
		if (thread_title, caller) in self.memory:
			obj = self.memory[(thread_title, caller)]
			
			print(f"____TIME:_{caller}_(Thread:{thread_title})____")
			print(f"|     avrg_exec_time: {obj.average_exec_time():.8f}")
			print(f"|  avrg_time_in_func: {obj.average_exec_time(False):.8f} ({(1/obj.average_exec_time(False)):.8f}fps)")		

		else:
			print(f"No time measured for {caller}, Thread: {thread_title}")


	def print_memory(self):
		print("___EXECUTION_MEMORY___")
		
		for name, obj in sorted(self.memory.items(), key=lambda x: -x[1].average_exec_time(False)):			
			print("|\n>___" + f"{name[1]}_(Thread:{name[0]})".ljust(76, "_"))
			print(f"|     avrg_exec_time: {obj.average_exec_time():.8f}   ({1/obj.average_exec_time():.8f}fps)")
			print(f"|  avrg_time_in_func: {obj.average_exec_time(False):.8f}   ({1/obj.average_exec_time(False):.8f}fps)")


exec_timer = ExecTimer()
