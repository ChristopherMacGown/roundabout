import os
import os.path
import sys
import signal

from roundabout import daemon
from tests import utils


class DaemonTestCase(utils.TestHelper):
    def setUp(self):
        self.fork = os.fork
        self.exit = sys.exit

    def tearDown(self):
        os.fork = self.fork
        sys.exit = self.exit

    def test_that_a_successful__fork_calls_fork_and_exits(self):
        def fake_fork():
            return True
        def fake_exit(*args):
            return True

        os.fork = fake_fork
        sys.exit = fake_exit
        self.assertCalled(os.fork, daemon._fork, 1)
        self.assertCalled(sys.exit, daemon._fork, 1)

    def test_that_a_failed_fork_raises_and_exits(self):
        def fake_fork():
            raise OSError
        def fake_exit(self, *args):
            return True

        os.fork = fake_fork
        sys.exit = fake_exit
        self.assertCalled(os.fork, daemon._fork, 1)
        self.assertCalled(sys.exit, daemon._fork, 1)

    def test_that_decouple_successfully_calls_os_stuff(self):
        def fake_setsid():
            return True

        pwd = os.getcwd()
        os.setsid = fake_setsid
        self.assertCalled(os.chdir, daemon._decouple)
        self.assertCalled(os.umask, daemon._decouple)
        self.assertCalled(os.setsid, daemon._decouple)
        os.chdir(pwd)

    def test_that_daemon_can_write_a_pidfile(self):
        d = daemon.Daemon(pidfile="/tmp/pidfile")
        d._Daemon__write_pid_file(12345)
        self.assertTrue(os.path.isfile(d.pidfile))
        d.remove_pidfile()

    def test_that_we_raise_if_we_cannot_write_pidfile(self):
        d = daemon.Daemon()
        self.assertRaises(Exception, d._Daemon__write_pid_file, 12345)

    def test_daemon_rebind(self):
        d = daemon.Daemon(stdin=utils.testdata('fake'),
                          stdout=utils.testdata('fake'),
                          stderr=utils.testdata('fake'))
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        with open('/tmp/testfile', 'w') as fd:
            sys.stdin  = fd
            sys.stdin.close() # Test to make sure we hit IOError
            sys.stdout = fd
            sys.stderr = fd
            self.assertCalled(file.close, d._Daemon__rebind)

        sys.stdin = old_stdin
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    def test_start_calls_fork_and_everything(self):
        def fake_fork():
            return True
        def fake_exit(*args):
            return True

        decouple = daemon._decouple
        os.fork = fake_fork
        sys.exit = fake_exit
        daemon.Daemon._Daemon__rebind = fake_fork
        daemon._decouple = fake_fork

        d = daemon.Daemon(pidfile="/tmp/pidfile")
        self.assertCalled(daemon._fork, d.start)
        self.assertCalled(daemon._decouple, d.start)
        self.assertTrue(os.path.isfile(d.pidfile))
        d.remove_pidfile()
        daemon._decouple = decouple

    def test_restart_calls_start_and_stop(self):
        def fake_fork():
            return True
        def fake_exit(*args):
            return True
        def fake_kill(*args):
            return True

        decouple = daemon._decouple
        os.fork = fake_fork
        sys.exit = fake_exit
        daemon.Daemon._Daemon__rebind = fake_fork
        daemon._decouple = fake_fork

        d = daemon.Daemon(pidfile="/tmp/pidfile")
        self.assertCalled(daemon.Daemon.start, d.restart)
        self.assertCalled(daemon.Daemon.stop, d.restart)
        daemon._decouple = decouple

    def test_kill_calls_oskill_and_doesnt_raise(self):
        def fake_kill(*args):
            return True
        
        kill, os.kill = os.kill, fake_kill
        d = daemon.Daemon(pidfile="/tmp/pidfile")
        d._Daemon__write_pid_file(12345)
        self.assertNothingRaised(d.stop)
        self.assertCalled(os.kill, d.stop)
        os.kill = kill
        d.remove_pidfile()

    def test_kill_returns_false_if_no_pidfile(self):
        def fake_kill(*args):
            return True
        
        kill, os.kill = os.kill, fake_kill
        d = daemon.Daemon(pidfile="/tmp/pidfile")
        self.assertFalse(d.stop()) # No pidfile, can't kill it.

    def test_handle_signals_calls_properly(self):
        d = daemon.Daemon(pidfile="/tmp/pidfile")
        self.assertCalled(signal.signal, d.handle_signals)

    def test_kill_returns_false_if_no_pid(self):
        def fake_kill(*args):
            return True
        
        kill, os.kill = os.kill, fake_kill
        d = daemon.Daemon(pidfile="/tmp/pidfile")
        d._Daemon__write_pid_file("fake")
        self.assertFalse(d.stop()) # No pid, can't kill.
        d.remove_pidfile()
