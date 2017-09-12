
print("""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
If this message is printed multiple times, the process has forked
and re-loaded all the modules. This happens in Python2 on Windows. It sucks,
because the end user program will start another process too. This will also
break prorgams that don't use if __name__ == '__main__' checks on start.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
""")

def crash_runtime(queue):
	import os, sys
	import ctypes

	# Stop this process from printing to standard output
	#sys.stdout = open(os.devnull, 'w')
	#sys.stderr = open(os.devnull, 'w')
	print("Running crash_runtime function ...")

	# Crash the runtime by trying to write to the start of memory
	memmove = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)(ctypes._memmove_addr)
	memmove(0, b'crash', 100)

	# Return a message
	queue.put("Success!")

def main():
	print("Running main ...")
	from multiprocessing import Process, Queue

	# Start running the function in a subprocess
	queue = Queue()
	p = Process(target=crash_runtime, args=(queue,))
	p.start()

	# Wait for the process to end, while it is still alive
	while p.is_alive():
		p.join(0)

	# Check if it failed
	if p.exitcode != 0:
		print("The subprocess failed!")

	# Return the result, only if there is something to read
	if not queue.empty():
		output = queue.get()
		print("The subprocess returned: {0}".format(output))
	else:
		print("The subprocess didn't return anything")

	print("Done!")


if __name__ == '__main__':
	from multiprocessing import freeze_support
	multiprocessing.freeze_support()
	main()
