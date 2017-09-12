import sys
import platform


# https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
if sys.platform.startswith('win'):
    print("Applying Windows hacks ..."); sys.stdout.flush()
    # Module multiprocessing is organized differently in Python 3.4+
    try:
        # Python 3.4+
        if sys.platform.startswith('win'):
            import multiprocessing.popen_spawn_win32 as forking
        else:
            import multiprocessing.popen_fork as forking
    except ImportError:
        import multiprocessing.forking as forking

    # First define a modified version of Popen.
    class _Popen(forking.Popen):
        def __init__(self, *args, **kw):
            if hasattr(sys, 'frozen'):
                # We have to set original _MEIPASS2 value from sys._MEIPASS
                # to get --onefile mode working.
                os.putenv('_MEIPASS2', sys._MEIPASS)
            try:
                super(_Popen, self).__init__(*args, **kw)
            finally:
                if hasattr(sys, 'frozen'):
                    # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                    # available. In those cases we cannot delete the variable
                    # but only set it to the empty string. The bootloader
                    # can handle this case.
                    if hasattr(os, 'unsetenv'):
                        os.unsetenv('_MEIPASS2')
                    else:
                        os.putenv('_MEIPASS2', '')

    # Second override 'Popen' class with our modified version.
    forking.Popen = _Popen

import multiprocessing

print("""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
If this message is printed multiple times, the process has forked
and re-loaded all the modules. This happens in Python2 on Windows. It sucks,
because the end user program will start another process too. This will also
break prorgams that don't use if __name__ == '__main__' checks on start.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
"""); sys.stdout.flush()

def crash_runtime(queue):
	import os, sys
	import ctypes

	# Stop this process from printing to standard output
	#sys.stdout = open(os.devnull, 'w')
	#sys.stderr = open(os.devnull, 'w')
	print("Running crash_runtime function ..."); sys.stdout.flush()

	# Crash the runtime by trying to write to the start of memory
	memmove = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)(ctypes._memmove_addr)
	memmove(0, b'crash', 100)

	# Return a message
	queue.put("Success!")

def main():
	print("Running main ..."); sys.stdout.flush()
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
		print("The subprocess failed!"); sys.stdout.flush()

	# Return the result, only if there is something to read
	if not queue.empty():
		output = queue.get()
		print("The subprocess returned: {0}".format(output)); sys.stdout.flush()
	else:
		print("The subprocess didn't return anything"); sys.stdout.flush()

	print("Done!"); sys.stdout.flush()


if __name__ == '__main__':
	multiprocessing.freeze_support()
	main()
