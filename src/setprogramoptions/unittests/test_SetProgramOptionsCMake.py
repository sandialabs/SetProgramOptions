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
try:                             # pragma: no cover
    import unittest.mock as mock # pragma: no cover
except:                          # pragma: no cover
    import mock                  # pragma: no cover

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
# General Utility Data
#
# ===============================================================================
global_gen_new_ground_truth_files = False
# global_gen_new_ground_truth_files = True     # comment this out for production.



class DEFAULT_VALUE(object):
    pass



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



class SetProgramOptionsTestCMake(TestCase):
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

    def test_SetProgramOptionsCMake_Template(self):
        """
        Basic template test for SetProgramOptions.

        This test doesn't really validate any output -- it just runs a basic check.
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "CMAKE_GENERATOR_NINJA"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_property_inifilepath(self):
        """
        Runs a check that loads the filename using `inifilepath` property
        rather than the parameter in the c'tor.
        """
        parser = self._create_standard_parser(filename=None)
        parser.inifilepath = self._filename

        print("-----[ TEST BEGIN ]----------------------------------------")
        # parse all sections
        print("-" * 40)
        print("Execute Parser")
        print("-" * 40)
        sections = parser.configparserenhanceddata.sections(parse=False)

        self.assertGreater(len(sections), 2)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_gen_option_list_bash(self):
        """
        Test the ``gen_option_list`` method using the ``bash`` generator.
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TRILINOS_CONFIGURATION_ALPHA"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        print("-" * 40)
        print("Option List")
        print("-" * 40)
        option_list_expect = [
            'cmake',
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
            '/path/to/source/dir'
        ]

        option_list_actual = parser.gen_option_list(section, generator="bash")
        pprint(option_list_actual, width=200)
        self.assertListEqual(option_list_expect, option_list_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_gen_option_list_bash_expandvars(self):
        """
        Test the ``gen_option_list`` method using the ``bash`` generator.
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_01"
        print("Section  : {}".format(section))

        self._execute_parser(parser, section)

        print("-" * 40)
        print("Option List")
        print("-" * 40)
        option_list_expect = [
            'cmake',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo"',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo -bar"',
        ]

        option_list_actual = parser.gen_option_list(section, generator="bash")
        pprint(option_list_actual, width=200)

        self.assertListEqual(option_list_expect, option_list_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_03"
        print("Section  : {}".format(section))

        self._execute_parser(parser, section)

        print("-" * 40)
        print("Option List")
        print("-" * 40)
        option_list_expect = [
            'cmake',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo"',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo -bar"',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo -bar -bif"',
        ]

        option_list_actual = parser.gen_option_list(section, generator="bash")
        pprint(option_list_actual, width=200)

        self.assertListEqual(option_list_expect, option_list_actual)
        print("-----[ TEST END ]------------------------------------------")
        print("OK")
        return 0

    def test_SetProgramOptionsCMake_gen_option_list_bash_expandvars_with_unknown_cmake_var_ecl3(self):
        """
        Test the ``gen_option_list`` method using the ``bash`` generator when the ECL for
        ExpandVarsInTextCMake is set to 3 or lower. This should generate a WARNING.
        """
        parser = self._create_standard_parser()
        parser.exception_control_level = 3

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_02"
        print("Section  : {}".format(section))

        # parse the section
        self._execute_parser(parser, section)

        # Generate a BASH script representing the instructions in the section.

        # what answer do we EXPECT:
        option_list_expect = [
            'cmake',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo"',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo -bar"',
            '-DCMAKE_F90_FLAGS:STRING=" -baz"'
        ]

        # Generate the BASH entries:
        option_list_actual = parser.gen_option_list(section, generator="bash")

        # Verify the results:
        self.assertListEqual(option_list_actual, option_list_expect)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_gen_option_list_bash_expandvars_with_unknown_cmake_var_ecl4(self):
        """
        Test the ``gen_option_list`` method using the ``bash`` generator when the ECL
        for ExpandVarsInTextCMake is set to 4 or higher. This should raise a ``ValueError``.
        """
        parser = self._create_standard_parser()
        parser.exception_control_level = 5

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_02"
        print("Section  : {}".format(section))

        # parse the section
        self._execute_parser(parser, section)

        # Generate a BASH script representing the instructions in the section.
        with self.assertRaises(ValueError):
            option_list_actual = parser.gen_option_list(section, generator="bash")

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_gen_option_list_cmake_fragment(self):
        """
        Test the ``gen_option_list`` method using the ``cmake_fragment`` generator.
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TRILINOS_CONFIGURATION_ALPHA"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        print("-" * 40)
        print("Option List")
        print("-" * 40)
        option_list_expect = [
            'set(Trilinos_ENABLE_COMPLEX ON CACHE BOOL "from .ini configuration")',
            'set(Trilinos_ENABLE_THREAD_SAFE ON CACHE BOOL "from .ini configuration")',
            'set(Trilinos_PARALLEL_COMPILE_JOBS_LIMIT 20)',
            'set(Trilinos_PARALLEL_LINK_JOBS_LIMIT 4)',
            'set(Trilinos_ENABLE_Kokkos ON CACHE BOOL "from .ini configuration")',
            'set(Trilinos_ENABLE_KokkosCore ON CACHE BOOL "from .ini configuration")',
            'set(Trilinos_ENABLE_KokkosKernels ON CACHE BOOL "from .ini configuration")',
            'set(KokkosKernels_ENABLE_EXAMPLES ON CACHE BOOL "from .ini configuration")',
            'set(Trilinos_ENABLE_Tpetra ON CACHE BOOL "from .ini configuration")',
            'set(Tpetra_INST_DOUBLE ON CACHE BOOL "from .ini configuration")'
        ]

        option_list_actual = parser.gen_option_list(section, generator="cmake_fragment")
        pprint(option_list_actual, width=200)
        self.assertListEqual(option_list_expect, option_list_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_gen_option_list_cmake_fragment_expandvars(self):
        """
        Test the ``gen_option_list`` method using the ``bash`` generator.
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_02"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        parser.gen_option_list(section, generator="cmake_fragment")

        option_list_expect = [
            'set(CMAKE_CXX_FLAGS "$ENV{LDFLAGS} -foo" CACHE STRING "from .ini configuration")',
            'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -bar" CACHE STRING "from .ini configuration")',
            'set(CMAKE_F90_FLAGS "${CMAKE_F90_FLAGS} -baz" CACHE STRING "from .ini configuration")'
        ]

        option_list_actual = parser.gen_option_list(section, generator="cmake_fragment")

        print("Expected Output:\n{}\n".format("\n".join(option_list_expect)))
        print("Actual Output:\n{}\n".format("\n".join(option_list_actual)))

        self.assertListEqual(option_list_expect, option_list_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_param_order_01(self):
        """
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_CMAKE_CACHE_PARAM_ORDER"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        option_list_bash_expect = [
            '-DCMAKE_VAR_A=ON',
            '-DCMAKE_VAR_B=ON',
            '-DCMAKE_VAR_C:BOOL=ON',
            '-DCMAKE_VAR_D=ON',
            '-DCMAKE_VAR_E=ON',
            '-DCMAKE_VAR_F:BOOL=ON',
            '-DCMAKE_VAR_G:BOOL=ON',
            '-DCMAKE_VAR_H:BOOL=ON',
            '-DCMAKE_VAR_I:BOOL=ON',
            '-DCMAKE_VAR_J:BOOL=ON',
            '-DCMAKE_VAR_K:BOOL=ON',
            '-DCMAKE_VAR_L:BOOL=ON',
            '-DCMAKE_VAR_M:BOOL=ON',
            '-DCMAKE_VAR_N:BOOL=ON',
            '-DCMAKE_VAR_O:BOOL=ON'
        ]

        option_list_bash_actual = parser.gen_option_list(section, generator="bash")
        self.assertListEqual(option_list_bash_expect, option_list_bash_actual)

        option_list_cmake_fragment_expect = [
            'set(CMAKE_VAR_A ON FORCE)',
            'set(CMAKE_VAR_B ON PARENT_SCOPE)',
            'set(CMAKE_VAR_C ON CACHE BOOL "from .ini configuration")',
            'set(CMAKE_VAR_D ON PARENT_SCOPE FORCE)',
            'set(CMAKE_VAR_E ON PARENT_SCOPE FORCE)',
            'set(CMAKE_VAR_F ON CACHE BOOL "from .ini configuration" FORCE)',
            'set(CMAKE_VAR_G ON CACHE BOOL "from .ini configuration" FORCE)',
            'set(CMAKE_VAR_H ON CACHE BOOL "from .ini configuration" PARENT_SCOPE)',
            'set(CMAKE_VAR_I ON CACHE BOOL "from .ini configuration" PARENT_SCOPE)',
            'set(CMAKE_VAR_J ON CACHE BOOL "from .ini configuration" PARENT_SCOPE FORCE)',
            'set(CMAKE_VAR_K ON CACHE BOOL "from .ini configuration" PARENT_SCOPE FORCE)',
            'set(CMAKE_VAR_L ON CACHE BOOL "from .ini configuration" PARENT_SCOPE FORCE)',
            'set(CMAKE_VAR_M ON CACHE BOOL "from .ini configuration" PARENT_SCOPE FORCE)',
            'set(CMAKE_VAR_N ON CACHE BOOL "from .ini configuration" PARENT_SCOPE FORCE)',
            'set(CMAKE_VAR_O ON CACHE BOOL "from .ini configuration" PARENT_SCOPE FORCE)'
        ]

        option_list_cmake_fragment_actual = parser.gen_option_list(section, generator="cmake_fragment")
        self.assertListEqual(option_list_cmake_fragment_expect, option_list_cmake_fragment_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return

    def test_SetProgramOptionsCMake_param_order_02(self):
        """
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_CMAKE_CACHE_PARAM_TEST_02"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        option_list_bash_expect = ['-DCMAKE_VAR_A=ON']

        option_list_bash_actual = parser.gen_option_list(section, generator="bash")
        self.assertListEqual(option_list_bash_expect, option_list_bash_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return

    def test_SetProgramOptionsCMake_test_STRING_value_surrounded_by_double_quotes(self):
        """
        Test STRING values are surrounded by double quotes.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_STRING_DOUBLE_QUOTES"
        print("Section  : {}".format(section))

        option_list_expect = [
            '-DPanzer_FADTYPE:STRING="Sacado::Fad::DFad<RealType>"',
            '-DDART_TESTING_TIMEOUT:STRING="600"',
        ]
        option_list_actual = parser.gen_option_list(section, generator="bash")

        print("-" * 40)
        print("Options List Expect")
        print("-" * 40)
        pprint(option_list_expect, width=120)
        print("")
        print("Options List Actual")
        print("-" * 40)
        pprint(option_list_actual, width=120)

        self.assertEqual(option_list_expect, option_list_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def _create_standard_parser(
        self, filename=DEFAULT_VALUE(), debug_level=5, ece_level=4, ece_compact=False
    ):
        if isinstance(filename, DEFAULT_VALUE):
            filename = self._filename

        output = None

        if filename is not None:
            print("\n")
            print("filename: {}".format(filename))
            output = SetProgramOptionsCMake(filename)
        else:
            output = SetProgramOptionsCMake()

        output.debug_level = debug_level
        output.exception_control_level = ece_level
        output.exception_control_compact_warnings = ece_compact

        return output

    def _execute_parser(self, parser, section):
        output = None

        # parse a section
        print("-" * 40)
        print("Execute Parser")
        print("-" * 40)
        output = parser.parse_section(section)

        # pretty print the output
        print("-" * 40)
        print("Output")
        print("-" * 40)
        pprint(output, width=120)

        # pretty print the loginfo
        print("-" * 40)
        print("LogInfo")
        print("-" * 40)
        parser._loginfo_print()

        return output



# TEST_CMAKE_CACHE_PARAM_TEST_02
