loggerfile
==========

Helper utility to provide reopen_logs functionality to anything that logs to stdout.

Usage
-----

`loggerfile <filename> [<signal>]`

If signal is unspecified, loggerfile will start a new instance and log STDIN to the specified file.
If a signal is specified, loggerfile will locate the process currently logging to the specified file and request it to perform the specified action.

### Available signal actions:

#### reopen

Closes the log file and reopens it. Useful in log rotation scripts.

#### stop

Requests the instance to stop immediately. Will interrupt any logging happening.

#### wait

Waits for the instance to stop gracefully. Useful in init script restarts where the process on STDIN is exiting as it allows logging to complete.

#### waitkill

Performs the wait action for 30 seconds. If the proces is still running it is then killed.
