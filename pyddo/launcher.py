

from os.path import isfile, normpath
from os import sep, chdir
from pipes import quote
from subprocess import Popen
import signal

class LauncherError(RuntimeError):
    pass

class LaunchContext:
    def __init__(self):
        self.p = []
        self._language = 'English'
        self._outport = str(5200)
        self._gamedir = ""
        self._client = ""
        
    @property
    def client(self):
        return self._client

    @property
    def game_directory(self):
        return self._gamedir

    @game_directory.setter
    def game_directory(self, value):
        client = normpath(value) + sep + "dndclient.exe"
        if not isfile(client):
            raise LauncherError('Invalid game directory set: No dndclient in %0'.format(value))
        self._gamedir = value
        self._client = client

    def build(self, loginresponse):
        self.p = []
        self.append('-h', loginresponse.world.login_server)
        self.append('-a', loginresponse.subscription.name)
        self.append('--glsticketdirect', loginresponse.gls_ticket)
        self.append('--chatserver', loginresponse.world.chat_server)
        self.append('--rodat', 'on')
        self.append('--gametype', loginresponse.datacenter.game_name)
        self.append('--supporturl', 'https://tss.turbine.com/TSSTrowser/trowser.aspx')
        self.append('--supportserviceurl', 'https://tss.turbine.com/TSSTrowser/SubmitTicket.asmx')
        self.append('--authserverurl', 'https://gls.ddo.com/GLS.AuthServer/Service.asmx')
        self.append('--glsticketlifetime', '21600')
        self.append('--outport', self._outport)
        self.append('--language', self._language)

    @property
    def outport(self):
        return self._outport

    @outport.setter
    def outport(self, value):
        self._outport = value

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, language):
        self._language = language

    def append(self, param, value):
        self.p.append(param)
        v = quote(value)
        self.p.append(v)

    @property
    def params(self):
        return self.p

class NativeDDOLauncher:
    def __init__(self):
        self.handle_ = None

    def launch(self, launchcontext):
        chdir(launchcontext.game_directory)
        p = launchcontext.params
        p.insert(0, launchcontext.client)
        # Spawn
        self.handle_ = Popen(p)

    @property
    def is_running(self):
        if self.handle_ is None:
            return False
        self.handle_.poll()
        return self.handle_.returncode is None

    def wait(self):
        if self.is_running:
            self.handle_.wait()

    def kill(self):
        if not self.is_running:
            raise LauncherError('DDO is not running')
        self.handle_.kill()
        self.handle_ = None
    

class GameLauncher:
    def __init__(self):
        # Used to abstract, in case we ever have different
        # implementations on the different *NIXes and Windows.
        # I hope that subprocess is robust and portable enough to work on
        # all platforms, but (especially with Windows) you never know.
        self._launcher = NativeDDOLauncher()
        self._context = LaunchContext()
        
    @property
    def context(self):
        return self._context

    @property
    def game_directory(self):
        return self._context.game_directory

    @game_directory.setter
    def game_directory(self, value):
        self._context.game_directory = value

    @property
    def is_running(self):
        return self._launcher.is_running

    def wait(self):
        return self._launcher.wait()

    def kill(self):
        return self._launcher.kill()
    
    def launch(self, loginresponse):
        if not loginresponse.valid:
            raise LauncherError('Invalid login response passed.')
        self._context.build(loginresponse)
        self._launcher.launch(self._context)
        
class MultiGameLauncher(GameLauncher):
    def __init__(self):
        self._outports = []
        self._baseoutport = 5200
        self._nextoutport = 5200
        self._launchers = []
        # used to verify game directory
        self._context = LaunchContext()

    def _getnextoutport(self):
        port = self._nextoutport
        # Port is now used, append to list of used ports
        self._outports.append(port)
        self._outports.sort()

        neuport = self._baseoutport
        while self._outports.count(neuport) > 0:
            neuport = neuport + 1
        self._nextoutport = neuport
        # Return stringified version of the next outport in queue
        return str(port)

    def launch(self, loginresponse):
        launcher = GameLauncher()
        # Set game directory
        launcher.game_directory = self.context.game_directory
        launcher.context.outport = self._getnextoutport()
        launcher.launch(loginresponse)
        self._launchers.append(launcher)

    def wait(self):
        for l in self._launchers:
            l.wait()

    def kill(self):
        for l in self._launchers:
            l.kill()
        update()

    @property
    def running(self):
        return any(l.running for l in self._launchers)

    def update(self):
        for l in self._launchers:
            if not l.is_running:
                # A launcher has terminated, remove it
                port = int(launcher.context.outport)
                self._outports.remove(port)
                self._launchers.remove(l)
