## Debugging
## Hard Reloader 

import sys, os, signal, pprint, types 
class PeriodicReloader(object): 
    """Forces modules which invoke PeriodicReloader to undergo a
    hard-reload. This is ideal for developing in debug mode where you
    want modifications to an application to occur in realtime
    """

    def __init__(self, interval=1): 
        self.interval = interval 
        self.mtimes = {} 
        self.sig_setup() 

    def sig_setup(self): 
        signal.signal(signal.SIGALRM, self.check) 
        signal.alarm(self.interval) 

    def check(self, signum, frame): 
        for mod in sys.modules.values(): 
            if not isinstance(mod, types.ModuleType): 
                continue 
            path = getattr(mod, '__file__', None) 
            if not path: 
                continue 
            mtime = os.stat(mod.__file__).st_mtime 
            if mod.__file__.endswith('.pyc') and \
                    os.path.exists(mod.__file__[:-1]): 
                mtime = max(os.stat(mod.__file__[:-1]).st_mtime, mtime) 
            if mod not in self.mtimes: 
                self.mtimes[mod] = mtime 
            elif self.mtimes[mod] < mtime: 

                os.execv(sys.executable, [sys.executable] + sys.argv) 
        self.sig_setup() 
