#!/usr/bin/env python
# -*- coding: utf-8; mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
"""
from __future__ import print_function
import sys
sys.dont_write_bytecode = True

import os
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pprint import pprint

import unittest
from unittest import TestCase

# Coverage will always miss one of these depending on the system
# and what is available.
try:                                                                                                # pragma: no cover
    import unittest.mock as mock                                                                    # pragma: no cover
except:                                                                                             # pragma: no cover
    import mock                                                                                     # pragma: no cover

from mock import Mock
from mock import MagicMock
from mock import patch

import filecmp
from textwrap import dedent

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from setprogramoptions import *

from .common import *


# ===============================================================================
#
# General Utility Functions
#
# ===============================================================================
global_gen_new_ground_truth_files = False
# global_gen_new_ground_truth_files = True     # comment this out for production.


# ===============================================================================
#
# General Utility Functions
#
# ===============================================================================


# ===============================================================================
#
# Mock Helpers
#
# ===============================================================================


# ===============================================================================
#
# Tests
#
# ===============================================================================


class SetProgramOptionsTest(TestCase):
    """
    Main test driver for the SetProgramOptions class
    """

    def setUp(self):
        print("")
        self.maxDiff = None
        self._filename = find_config_ini(filename="config_test_setprogramoptions.ini")

        # Get the location of the unit testing scripts (for file writing tests)
        unit_test_path = os.path.realpath(__file__)
        self.unit_test_file = os.path.basename(unit_test_path)
        self.unit_test_path = os.path.dirname(unit_test_path)

    def test_SetProgramOptions_Template(self):
        """
        Basic template test for SetProgramOptions.

        This test doesn't really validate any output -- it just runs a basic check.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_CONFIGURATION_D"
        print("Section  : {}".format(section))

        # parse a section
        print("-" * 40)
        print("Execute Parser")
        print("-" * 40)
        data = parser.parse_section(section)

        # pretty print the output
        print("-" * 40)
        print("Data")
        print("-" * 40)
        pprint(data, width=120)

        # pretty print the loginfo
        print("-" * 40)
        print("LogInfo")
        print("-" * 40)
        parser._loginfo_print()

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return

    def test_SetProgramOptions_gen_option_list(self):
        """
        Basic template test for SetProgramOptions.

        This test doesn't really validate any output -- it just runs a basic check.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TRILINOS_CONFIGURATION_ALPHA"
        print("Section  : {}".format(section))

        # parse a section
        print("-" * 40)
        print("Execute Parser")
        print("-" * 40)
        data = parser.parse_section(section)

        # pretty print the output
        print("-" * 40)
        print("Data")
        print("-" * 40)
        pprint(data, width=120)

        # pretty print the loginfo
        print("-" * 40)
        print("LogInfo")
        print("-" * 40)
        parser._loginfo_print()

        print("-" * 40)
        print("Option List")
        print("-" * 40)
        option_list_expect = ['cmake',
                              '-G=Ninja',
                              '-DTrilinos_ENABLE_COMPLEX:BOOL=ON',
                              '-DTrilinos_ENABLE_THREAD_SAFE:BOOL=ON',
                              '-DTrilinos_PARALLEL_COMPILE_JOBS_LIMIT=20',
                              '-DTrilinos_PARALLEL_LINK_JOBS_LIMIT=4',
                              '-DTrilinos_ENABLE_Kokkos:BOOL=ON',
                              '-DTrilinos_ENABLE_KokkosCore:BOOL=ON',
                              '-DTrilinos_ENABLE_KokkosKernels:BOOL=ON',
                              '-DKokkosKernels_ENABLE_EXAMPLES:BOOL=ON',
                              '-DTrilinos_ENABLE_Tpetra:BOOL=ON',
                              '-DTpetra_INST_DOUBLE:BOOL=ON',
                              '/path/to/build/dir']

        option_list_actual = parser.gen_option_list(section)
        pprint(option_list_actual, width=200)
        self.assertListEqual(option_list_expect, option_list_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return
