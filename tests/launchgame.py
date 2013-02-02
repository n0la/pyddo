#!/usr/bin/python3

import sys
sys.path.insert(0, '..')

from pyddo.login import query_datacenters
from pyddo.launcher import MultiGameLauncher
from getpass import getpass

def main():
    sys.stdout.write('Username: ')
    sys.stdout.flush()
    user = sys.stdin.readline().strip()
    pairs = {}

    names = user.split(',')
    for n in names:
        n = n.strip()
        pairs[n] = getpass('Provide a password for {0}: '.format(n))

    launcher = MultiGameLauncher()
    launcher.game_directory = "C:\\Program Files (x86)\\Turbine\\DDO Unlimited\\"
    world = query_datacenters()[0].worlds[1]

    for name in pairs.keys():
        print('Logging in {0}...'.format(name))
        lr = world.login(name, pairs[name])
        lr.wait_queue()
        print('Launching...')
        launcher.launch(lr)

    launcher.wait()
    print('DDO has exited.')

if __name__ == '__main__':
    main()
