#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
#===============================================================================
#
# License (3-Clause BSD)
# ----------------------
# Copyright 2021 National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================
"""
"""
from __future__ import print_function
import sys


sys.dont_write_bytecode = True

import contextlib
import io
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
                                                       #            '-DTrilinos_PARALLEL_COMPILE_JOBS_LIMIT=20',
                                                       #            '-DTrilinos_PARALLEL_LINK_JOBS_LIMIT=4',
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
        # parser.exception_control_compact_warnings = True

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
        ]

        option_list_actual = parser.gen_option_list(section, generator="bash")
        pprint(option_list_actual, width=200)

        self.assertListEqual(option_list_expect, option_list_actual)
        print("OK")
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # Update 03 will generate the update option
        section = "TEST_VAR_EXPANSION_UPDATE_03"
        print("Section  : {}".format(section))

        self._execute_parser(parser, section)

        print("-" * 40)
        print("Option List")
        print("-" * 40)
        option_list_expect = [
            'cmake',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo"',
            '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo -bif"',
        ]

        option_list_actual = parser.gen_option_list(section, generator="bash")
        pprint(option_list_actual, width=200)

        self.assertListEqual(option_list_expect, option_list_actual)
        print("OK")
        print("-----[ TEST END ]------------------------------------------")

        return 0

    def test_SetProgramOptionsCMake_gen_option_list_bash_expandvars_with_unknown_cmake_var_ecl3(self):
        """
        Test the ``gen_option_list`` method using the ``bash`` generator when the ECL for
        ExpandVarsInTextCMake is set to 3 or lower. This should generate a WARNING.
        """
        parser = self._create_standard_parser()
        parser.exception_control_compact_warnings = False
        parser.exception_control_level = 3

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_02"
        print("Section  : {}".format(section))

        # parse the section
        self._execute_parser(parser, section)

        # Generate a BASH script representing the instructions in the section.

        # what answer do we EXPECT:
        option_list_expect = [
            'cmake', '-DCMAKE_CXX_FLAGS:STRING="${LDFLAGS} -foo"', '-DCMAKE_F90_FLAGS:STRING=" -baz"'
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
            parser.gen_option_list(section, generator="bash")

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
            'set(CMAKE_F90_FLAGS "${CMAKE_F90_FLAGS} -baz" CACHE STRING "from .ini configuration")'
        ]

        option_list_actual = parser.gen_option_list(section, generator="cmake_fragment")

        print("Expected Output:\n{}\n".format("\n".join(option_list_expect)))
        print("Actual Output:\n{}\n".format("\n".join(option_list_actual)))

        self.assertListEqual(option_list_expect, option_list_actual)

        print("-----[ TEST END ]------------------------------------------")
        print("OK")

        # Test that the CMake generator will generate a sequence of operations
        # that don't include a FORCE option on an update of an existing CACHE
        # value. As far as SPOCM is concerned, it'll generate the CMake as
        # defined in the .ini file.
        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_01"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        parser.gen_option_list(section, generator="cmake_fragment")

        option_list_expect = [
            'set(CMAKE_CXX_FLAGS "$ENV{LDFLAGS} -foo" CACHE STRING "from .ini configuration")',
            'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -bar" CACHE STRING "from .ini configuration")',
        ]

        option_list_actual = parser.gen_option_list(section, generator="cmake_fragment")

        print("Expected Output:\n{}\n".format("\n".join(option_list_expect)))
        print("Actual Output:\n{}\n".format("\n".join(option_list_actual)))

        self.assertListEqual(option_list_expect, option_list_actual)

        print("-----[ TEST END ]------------------------------------------")
        print("OK")

        # Test that the CMake generator will generate a sequence of operations
        # that do include a FORCE option on an update of an existing CACHE
        # value. As far as SPOCM is concerned w/rt to CMake fragments, we will
        # generate what the .ini file tells us to do and respect that the CMake
        # engine will operate as the CMake engine does.
        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_UPDATE_03"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        parser.gen_option_list(section, generator="cmake_fragment")

        option_list_expect = [
                                                                                                           # Sets CMAKE_CXX_FLAGS the _first_ time, CMAKE_CXX_FLAGS would be set.
            'set(CMAKE_CXX_FLAGS "$ENV{LDFLAGS} -foo" CACHE STRING "from .ini configuration")',
                                                                                                           # Tries to update CMAKE_CXX_FLAGS the _second_ time without FORCE.
                                                                                                           # CMake will not save this.
            'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -bar" CACHE STRING "from .ini configuration")',
                                                                                                           # Tries to update CMAKE_CXX_FLAGS again but this time uses FORCE.
                                                                                                           # CMake will save this updated value.
            'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -bif" CACHE STRING "from .ini configuration" FORCE)',
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

        section = "TEST_CMAKE_CACHE_PARAM_ORDER"
        print("Section  : {}".format(section))
        self._execute_parser(parser, section)

        print("-----[ TEST BEGIN ]----------------------------------------")
        option_list_bash_expect = [
            '-DCMAKE_VAR_A:STRING="ON"',
            '-DCMAKE_VAR_C:BOOL=ON',
            '-DCMAKE_VAR_D:BOOL=ON',
            '-DCMAKE_VAR_E:BOOL=ON',
        ]

        option_list_bash_actual = parser.gen_option_list(section, generator="bash")
        self.assertListEqual(option_list_bash_expect, option_list_bash_actual)

        option_list_cmake_fragment_expect = [
            'set(CMAKE_VAR_A ON CACHE STRING "from .ini configuration" FORCE)',
            'set(CMAKE_VAR_B ON PARENT_SCOPE)',
            'set(CMAKE_VAR_C ON CACHE BOOL "from .ini configuration")',
            'set(CMAKE_VAR_D ON CACHE BOOL "from .ini configuration" FORCE)',
            'set(CMAKE_VAR_E ON CACHE BOOL "from .ini configuration" FORCE)',
            'set(CMAKE_VAR_F ON CACHE BOOL "from .ini configuration" PARENT_SCOPE)',
            'set(CMAKE_VAR_G ON CACHE BOOL "from .ini configuration" PARENT_SCOPE)',
        ]

        option_list_cmake_fragment_actual = parser.gen_option_list(section, generator="cmake_fragment")
        self.assertListEqual(option_list_cmake_fragment_expect, option_list_cmake_fragment_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_param_order_02(self):
        """
        Tests that we correctly generate output if extra flags
        are provided such as something to uniqueify a .ini option entry.
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_CMAKE_CACHE_PARAM_TEST_02"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        option_list_bash_expect = ['-DCMAKE_VAR_A:STRING="ON"']

        option_list_bash_actual = parser.gen_option_list(section, generator="bash")
        self.assertListEqual(option_list_bash_expect, option_list_bash_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_bash_generator_ignores_PARENT_SCOPE(self):
        """
        Verify that the bash generator will not add a ``-D`` entry for a
        ``opt-set-cmake-var`` that has the ``PARENT_SCOPE`` flag since that
        will always force CMake to create a type-1 (non-cache) var assignment.
        """
        parser = self._create_standard_parser()

        section = "TEST_CMAKE_PARENT_SCOPE_NOT_BASH"
        print("Section  : {}".format(section))

        print("-----[ TEST BEGIN ]----------------------------------------")
        option_list_bash_expect = []
        option_list_bash_actual = parser.gen_option_list(section, generator="bash")
        self.assertListEqual(option_list_bash_expect, option_list_bash_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        option_list_cmake_fragment_expect = [
            'set(FOO_VAR_A "FOO_VAL A" PARENT_SCOPE)',
            'set(FOO_VAR_B "FOO_VAL B" CACHE STRING "from .ini configuration" PARENT_SCOPE)'
        ]
        option_list_cmake_fragment_actual = parser.gen_option_list(section, generator="cmake_fragment")
        self.assertListEqual(option_list_cmake_fragment_expect, option_list_cmake_fragment_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_fail_on_FORCE_and_PARENT_SCOPE(self):
        """
        Tests the case that both PARENT_SCOPE and FORCE are provided.
        This will cause a CMake error beacuse the existence of PARENT_SCOPE
        forces CMake to use a Type-1 set operation, i.e. a NON-CACHEd
        variable. However ``FORCE`` is only valid for a CACHED variable (Type-2).
        These two options are mutually exclusive and CMake will fail.

        In this case SetProgramOptionsCMake should raise a CATASTROPHIC
        error because the operation provided is invalid.
        """
        parser = self._create_standard_parser()

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_CMAKE_FAIL_ON_PARENT_SCOPE_AND_FORCE"
        print("Section  : {}".format(section))

        # parse a section
        self._execute_parser(parser, section)

        with self.assertRaises(ValueError):
            parser.gen_option_list(section, generator="bash")

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

        option_list_expect = ['-DFOO:STRING="foo::bar::baz<Type>"', '-DBAR:STRING="600"']
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

    def test_SetProgramOptionsCMake_opt_remove(self):
        """
        This test validates that `opt-remove` will correctly remove a CMake var
        that was created using `opt-set-cmake-var`
        """
        parser = self._create_standard_parser()

        section = "TEST_CMAKE_VAR_REMOVE"
        print("Section  : {}".format(section))

        print("-----[ TEST BEGIN ]----------------------------------------")
        option_list_bash_actual = parser.gen_option_list(section, 'bash')
        option_list_bash_expect = ['-DBAR_TEST:STRING="BAR"', '-DBAZ_TEST:STRING="BAZ"']
        self.assertListEqual(option_list_bash_expect, option_list_bash_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        option_list_cmake_fragment_actual = parser.gen_option_list(section, 'cmake_fragment')
        option_list_cmake_fragment_expect = [
            'set(BAR_TEST BAR CACHE STRING "from .ini configuration")',
            'set(BAZ_TEST BAZ CACHE STRING "from .ini configuration")'
        ]
        self.assertListEqual(option_list_cmake_fragment_expect, option_list_cmake_fragment_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_FORCE_only_for_bash(self):
        """
        Test that an ``opt-set-cmake-var`` that has a FORCE but does
        not specify a TYPE will be assigned STRING by default and will
        generate the appropriate ``-D`` entry.

            [TEST_CMAKE_VAR_FORCE_ONLY]
            opt-set-cmake-var FOO FORCE : "BAR"

        should generate:

            -DFOO:STRING="BAR"
        """
        parser = self._create_standard_parser()

        section = "TEST_CMAKE_VAR_FORCE_ONLY"
        print("Section  : {}".format(section))

        print("-----[ TEST BEGIN ]----------------------------------------")
        option_list_bash_actual = parser.gen_option_list(section, 'bash')
        option_list_bash_expect = [
            '-DFOO:STRING="BAR"',
        ]
        self.assertListEqual(option_list_bash_expect, option_list_bash_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        option_list_cmake_fragment_actual = parser.gen_option_list(section, 'cmake_fragment')
        option_list_cmake_fragment_expect = [
            'set(FOO BAR CACHE STRING "from .ini configuration" FORCE)',
        ]
        self.assertListEqual(option_list_cmake_fragment_expect, option_list_cmake_fragment_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptionsCMake_gen_option_list_bash_unresolved_cmake_var_01(self):
        """
        Tests what we do with an unresolved cmake variable encountered in the
        bash generator. The hitch is that if we replace the unresolved cmake
        var with an empty string we may be allowing a ``cmake-fragment`` and a
        ``bash command`` to diverge sicne the cmake fragment would have additional
        context of pre-existing variables that *might exist* versus the bash command
        where a cmake variable *definitely will not exist*.
        """
        parser = self._create_standard_parser()
        section = "TEST_CMAKE_VAR_IN_BASH_GENERATOR"
        print("Section  : {}".format(section))

        print("-----[ TEST BEGIN ]----------------------------------------")
        # Test 1: Validate exception is raised when `exception_control_level`
        #         is the default (4).
        with self.assertRaises(ValueError):
            option_list_actual = parser.gen_option_list(section, generator='bash')
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # Test 2: Reduce the `exception_control_level` so that the exception is
        #         not generated.
        #         - Sets `exception_control_level` to 3
        #         - Sets `exception_control_compact_warnings` to False
        # Note: This test is sensitive to formatting changes to `ExceptionControl`
        #       if this is a big problem we may need to change this in the future
        #       to be less sensitive to stdout.
        option_list_expect = [
            '-DFOO_VAR:STRING="FOO"',
            '-DFOO_VAR:STRING="BAR "'
        ]
        parser.exception_control_level = 3
        parser.exception_control_compact_warnings = False
        with io.StringIO() as m_stdout:
            with contextlib.redirect_stdout(m_stdout):
                option_list_actual = parser.gen_option_list(section, generator='bash')

                # Check that the output matches
                self.assertListEqual(option_list_expect, option_list_actual)

                # Check that the exception-control warning message gets printed
                self.assertIn("EXCEPTION SKIPPED", m_stdout.getvalue())
                self.assertIn("Event Type : MINOR", m_stdout.getvalue())
                self.assertIn("Exception  : ValueError", m_stdout.getvalue())
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # Test 2: Repeat the previous test but with *compact* warnings from
        #         `exception_control_compact_warnings` set to True to enable
        #         compact warnings.
        #         - Sets `exception_control_level` to 3
        #         - Sets `exception_control_compact_warnings` to True
        # Note: This test is sensitive to formatting changes to `ExceptionControl`
        #       if this is a big problem we may need to change this in the future
        #       to be less sensitive to stdout.
        option_list_expect = [
            '-DFOO_VAR:STRING="FOO"',
            '-DFOO_VAR:STRING="BAR "'
        ]
        parser.exception_control_level = 3
        parser.exception_control_compact_warnings = True
        with io.StringIO() as m_stdout:
            with contextlib.redirect_stdout(m_stdout):
                option_list_actual = parser.gen_option_list(section, generator='bash')

                # Check that the output matches
                self.assertListEqual(option_list_expect, option_list_actual)

                # Check that the exception-control warning message gets printed
                self.assertIn("EXCEPTION SKIPPED", m_stdout.getvalue())
                self.assertIn("(MINOR : ValueError)", m_stdout.getvalue())
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



