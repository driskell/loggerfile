loggerfile
==========

Helper utility to provide reopen_logs functionality to anything that logs to stdout.

Loggerfile is intended as a replacement for `logger` in instances where you need to direct logs straight into their own file and rotate them separately. This avoids the modification of the syslog configuration with potentially complex filters, and even nightly truncation of logs potentially causing lost data and `tail -f` truncation detection complaints. You heard me right, **truncation**. Don't do it. Just... don't.

Usage
-----

`loggerfile <filename> [<signal>]`

If signal is unspecified, loggerfile will start a new instance and append stdin to the specified file.
If a signal is specified, loggerfile will locate the loggerfile currently logging to the specified file and request it to perform the specified action.

### Available signal actions:

#### reopen

Closes the log file and reopens it. Useful in log rotation scripts.

#### stop

Requests the instance to stop immediately. Will interrupt any logging happening.

#### wait

Waits for the instance to stop gracefully. Useful in init script restarts where the process on STDIN is exiting as it allows logging to complete.

#### waitkill

Performs the wait action for 30 seconds and then, if the instance is still running, kills it.


