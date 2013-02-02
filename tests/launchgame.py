#!/usr/bin/python3

# pyddo - Python classes to access functionality of DDO.
# Copyright (C) 2013  Florian Stinglmayr <fstinglmayr@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

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
