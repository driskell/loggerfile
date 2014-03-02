#!/usr/bin/env python

from __future__ import print_function
import fcntl
import os
import signal
import sys
from time import sleep

class AlarmSignal( Exception ):
	def __init__( self ):
		return
	def __str__( self ):
		return repr( self.value )

version = "0.9"
me = os.path.basename( __file__ )

# Check we have specified enough parameters
if len( sys.argv ) < 2:
	print( 'Loggerfile.py v' + version, 'by Driskell <devel@jasonwoods.me.uk>', file=sys.stderr )
	print( file=sys.stderr )
	print( 'Usage:', me, '<filename> [<signal>]', file=sys.stderr )
	print( file=sys.stderr )
	print( 'If signal is unspecified,', me, 'will start a new instance and append stdin to the specified file.', file=sys.stderr )
	print( 'If a signal is specified,', me, 'will locate the', me, 'currently logging to the specified file', file=sys.stderr )
	print( 'and request it to perform the specified action.', file=sys.stderr )
	print( file=sys.stderr )
	print( 'Available signal actions:', file=sys.stderr )
	print( '    reopen   : Closes the log file and reopens it. Useful in log rotation scripts.', file=sys.stderr )
	print( '    stop     : Requests the instance to stop immediately.', file=sys.stderr )
	print( '               Will interrupt any logging happening.', file=sys.stderr )
	print( '    wait     : Waits for the instance to stop gracefully.', file=sys.stderr )
	print( '               Useful in init script restarts where the process on STDIN is exiting as it allows logging to complete.', file=sys.stderr )
	print( '    waitkill : Performs the wait action for 30 seconds. If the proces is still running it is then killed.', file=sys.stderr )
	sys.exit(2)

# We never use STDOUT so close it
sys.stdout.close()

# Store log file
out = sys.argv[1]

def fetch_pid():
	if not os.path.exists( out + '.pid' ):
		print( 'Could not find the .pid file for', out + '. Are you sure there is a', me, 'running to that log file?', file=sys.stderr )
		sys.exit(2)
	with open( out + '.pid' ) as f:
		pid = int( f.read().rstrip( '\r\n' ) )
	try:
		os.kill( pid, 0 )
	except OSError:
		print( 'The .pid for', out, 'exists, but there is no', me, 'running to it.', file=sys.stderr )
		sys.exit(1)
	return pid

def waitkill( pid ):
	checks = 0
	while 42:
		try:
			os.kill( pid, 0 )
		except OSError:
			sys.exit(0)
		checks += 1
		if checks >= 30:
			try:
				os.kill( pid, signal.SIGKILL )
			except OSError:
				pass
			sleep(1)
			break
		sleep(1)

# Are we asking for a reopen?
if len( sys.argv ) > 2:
	if sys.argv[2] == 'reopen':
		pid = fetch_pid()
		try:
			os.kill( pid, signal.SIGUSR1 )
		except OSError:
			print( 'Failed to signal process with PID \'' + pid + '\'. Maybe it terminated as we tried to communicate with it?', file=sys.stderr )
			sys.exit(1)
		sys.exit(0)
	elif sys.argv[2] == 'stop':
		pid = fetch_pid()
		try:
			os.kill( pid, signal.SIGQUIT )
		except OSError:
			print( 'Failed to signal process with PID \'' + pid + '\'. Maybe it terminated as we tried to communicate with it?', file=sys.stderr )
			sys.exit(1)
		waitkill( pid )
		sys.exit(0)
	elif sys.argv[2] == 'wait':
		pid = fetch_pid()
		while 42:
			try:
				os.kill( pid, 0 )
			except OSError:
				break
			sleep(1)
		sys.exit(0)
	elif sys.argv[2] == 'waitkill':
		waitkill( pid )
		sys.exit(0)

# We need to lock the PID file to prevent double running to the same file
pf = open( out + '.pid', 'r+' )
try:
	fcntl.flock( pf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB )
except IOError:
	print( 'Failed to lock the .pid file for', out + '. Is there another', me, 'already running to that log file?', file=sys.stderr )
	sys.exit(1)

# Drop the PID into a file so we can SIGUSR1 the loggerfile
pf.write( str( os.getpid() ) + '\n' )
pf.flush()

# On SIGUSR1 reopen the log file
def open_log():
	sys.stdout.close()
	sys.stdout = open( out, 'a' )

def open_log_signal( signum, frame ):
	open_log()

signal.signal( signal.SIGUSR1, open_log_signal )

# On SIGQUIT or SIGPIPE exit
def do_exit( signum, frame ):
	raise KeyboardInterrupt()

signal.signal( signal.SIGQUIT, do_exit )
signal.signal( signal.SIGPIPE, do_exit )

def do_alarm( signum, frame ):
	raise AlarmSignal()

signal.signal( signal.SIGALRM, do_alarm )
signal.alarm(5)

# Setup log output
open_log()

# Read lines, sleeping for 250ms on read timeout of 5s (timeout handled by alarm signal)
while 42:
	try:
		while 42:
			line = sys.stdin.readline()
			if line == "": # We return on EOF
				break
			print( line.rstrip('\r\n') ) # Received a line
			sys.stdout.flush()
		break
	except AlarmSignal:
		sleep( 0.25 ) # Timeout
	except KeyboardInterrupt:
		break

pf.close()
