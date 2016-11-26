# -*- coding: utf-8 -*-
#
# Copyright © 2016 Mathieu Duponchelle <mathieu.duponchelle@opencreed.com>
# Copyright © 2016 Collabora Ltd
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=missing-docstring

import unittest
import os
import shutil

from hotdoc.core.project import CoreExtension
from hotdoc.utils.utils import touch


class HotdocTest(unittest.TestCase):
    def setUp(self):
        self._here = os.path.dirname(__file__)
        self._md_dir = os.path.abspath(os.path.join(
            self._here, 'tmp-markdown-files'))
        self._priv_dir = os.path.abspath(os.path.join(
            self._here, 'tmp-private'))
        self._src_dir = os.path.abspath(os.path.join(
            self._here, 'tmp-src-files'))
        self._output_dir = os.path.abspath(os.path.join(
            self._here, 'tmp-output'))
        self._remove_tmp_dirs()
        os.mkdir(self._md_dir)
        os.mkdir(self._priv_dir)
        os.mkdir(self._src_dir)
        self._core_ext = CoreExtension(self)

    def tearDown(self):
        self._remove_tmp_dirs()
        del self._core_ext

    def _remove_tmp_dirs(self):
        shutil.rmtree(self._md_dir, ignore_errors=True)
        shutil.rmtree(self._priv_dir, ignore_errors=True)
        shutil.rmtree(self._src_dir, ignore_errors=True)
        shutil.rmtree(self._output_dir, ignore_errors=True)

    def _create_md_file(self, name, contents):
        path = os.path.join(self._md_dir, name)
        with open(path, 'w') as _:
            _.write(contents)

        # Just making sure we don't hit a race condition,
        # in real world situations it is assumed users
        # will not update source files twice in the same
        # microsecond
        touch(path)
        return path

    def _create_src_file(self, name, symbols):
        path = os.path.join(self._src_dir, name)
        with open(path, 'w') as _:
            for symbol in symbols:
                _.write('%s\n' % symbol)

        # Just making sure we don't hit a race condition,
        # in real world situations it is assumed users
        # will not update source files twice in the same
        # microsecond
        touch(path)

        return path
