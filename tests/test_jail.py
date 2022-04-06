# Copyright (C) 2022 Dmitry Marakasov <amdmi3@amdmi3.ru>
#
# This file is part of portester
#
# portester is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# portester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with portester.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
from pathlib import Path

import pytest

from porttester.jail import start_jail


@pytest.mark.skipif(not sys.platform.startswith('freebsd'), reason='jail tests only supported on FreeBSD')
@pytest.mark.skipif(os.getuid() != 0, reason='jail tests must be run as root')
async def test_jail():
    jail = await start_jail(Path('/'), hostname='portester_test_jail')
    assert await jail.is_running()
    assert jail.get_path() == Path('/')
    assert await jail.execute('hostname') == ['portester_test_jail']
    await jail.destroy()
    assert not await jail.is_running()


@pytest.mark.skipif(not sys.platform.startswith('freebsd'), reason='jail tests only supported on FreeBSD')
@pytest.mark.skipif(os.getuid() != 0, reason='jail tests must be run as root')
async def test_nonetwork():
    jail = await start_jail(Path('/'), hostname='portester_test_jail_nonetwork', networking=False)

    # expected to die with "Non-recoverable resolver failure"
    with pytest.raises(RuntimeError):
        await jail.execute('fetch', 'http://example.com/')

    # expected to die with "Protocol not supported"
    with pytest.raises(RuntimeError):
        await jail.execute('fetch', 'http://127.0.0.1/')

    with pytest.raises(RuntimeError):
        await jail.execute('fetch', 'http://[::1]/')

    await jail.destroy()