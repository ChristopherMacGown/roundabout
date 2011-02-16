import os
import signal
import sys


def _fork(id):
    """ Fork ourselves. """
    try:
        if os.fork():
            # Successfully forked child, can exit parent.
            sys.exit(0)
    except OSError, e:
        sys.exit("Couldn't fork %i times: %s" % (id, e))


class Daemon(object):
    """ the Daemon class provides methods for starting and stopping a UNIX daemon. """

    def __init__(self, stdin='/dev/null', stdout='/dev/null',stderr='/dev/null', pidfile=None):
        self.pidfile = pidfile
        pass

    def __decouple(self):
        """ Decouple the child from the parent """
        os.chdir('/')
        os.umask(0)
        os.setsid()

    def __rebind(self):
        """ Rebind stdin/stderr/stdout """
        for fd in [sys.stdin, sys.stderr, sys.stdout]:
            try:
                os.close(fd)
            except:
                pass

        os.open(self.stdin, os.O_RDONLY)
        os.open(self.stdout, os.O_WRONLY)
        os.open(self.stderr, os.O_WRONLY)

    def __write_pid_file(self, pid):
        """ Write our process id to the pidfile """
        if not self.pidfile:
            raise Exception("Couldn't write pidfile")

        with open(self.pidfile, 'w') as fd:
            fd.write(str(pid))

    def handle_signals(self):
        signal.signal(signal.SIGTERM, self.remove_pidfile)

    def start(self):
        """ detach from the parent, decouple everything, and rebind """
        _fork(1) and self.__decouple()
        _fork(2) and self.__rebind()
        self.__write_pid_file(os.getpid())

    def stop(self):
        """ Read the pidfile for the process ID of the daemon and kill it """
        try:
            with open(self.pidfile, 'r') as fd:
                pid = fd.read()
                try:
                    os.kill(int(pid), signal.SIGTERM)
                except ValueError, e:
                    return None
        except OSError:
            return None

    def run(self):
        """ Catch KeyboardError """
        pass
