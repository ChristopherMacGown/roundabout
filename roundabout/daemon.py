"""
A class for daemonizing
"""

import os
import signal
import sys

from roundabout import log


def _fork(num):
    """ Fork ourselves. """
    try:
        if os.fork():
            # Successfully forked child, can exit parent.
            sys.exit(0)
    except OSError, e:
        sys.exit("Couldn't fork %i times: %s" % (num, e))

def _decouple():
    """ Decouple the child from the parent """
    os.chdir('/')
    os.umask(0)
    os.setsid()


class Daemon(object):
    """ 
    Daemon class provides methods for starting and stopping a UNIX daemon.
    """

    def __init__(self, stdin='/dev/null',
                       stdout='/dev/null',
                       stderr='/dev/null',
                       pidfile=None):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.handle_signals()

    def __write_pid_file(self, pid):
        """ Write our process id to the pidfile """
        if not self.pidfile:
            raise Exception("Couldn't write pidfile")

        with open(self.pidfile, 'w') as fd:
            fd.write(str(pid))

    def __rebind(self):
        """ Rebind stdin/stderr/stdout """
        [f.close() for f in [sys.stdin, sys.stderr, sys.stdout]]

        sys.stdin = os.open(self.stdin, os.O_RDONLY)
        sys.stderr = os.open(self.stdout, os.O_WRONLY)
        sys.stdout = os.open(self.stderr, os.O_WRONLY)

    def remove_pidfile(self):
        """ Remove the pidfile """
        os.unlink(self.pidfile)

    def handle_signals(self):
        """ wire up signal callbacks """
        signal.signal(signal.SIGTERM, self.remove_pidfile)

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        """ detach from the parent, decouple everything, and rebind """
        log.info("Starting roundabout...")
        _fork(1) and _decouple()
        _fork(2) and self.__rebind()
        self.__write_pid_file(os.getpid())
        log.info("Done")

    def stop(self):
        """ Read the pidfile for the process ID of the daemon and kill it """
        try:
            log.info("Stopping roundabout...")
            with open(self.pidfile, 'r') as fd:
                pid = fd.read()
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    log.info("Done...")
                except ValueError:
                    log.info("Couldn't stop roundabout...")
                    return None
        except (IOError, OSError):
            log.info("Couldn't stop roundabout...")
            return None
