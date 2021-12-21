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

from configparserenhanced import HandlerParameters
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
        return

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
        section = "TEST_OPTION_REMOVAL_VARIABLES"
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

        # pretty print the options data
        print("-" * 40)
        print("Options")
        print("-" * 40)
        pprint(parser.options, width=120)

        # pretty print the options list
        print("-" * 40)
        print("Options List")
        print("-" * 40)
        pprint(parser.gen_option_list(section, generator='bash'), width=120)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_property_inifilepath(self):
        """
        Runs a check that loads the filename using `inifilepath` property
        rather than the parameter in the c'tor.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions()
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False
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

    def test_SetProgramOptions_property_options_setter(self):
        """
        Test the ``setter`` for property: ``options``
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        # Set options to a valid type
        new_options_value = {}
        parser.options = new_options_value
        self.assertEqual(new_options_value, parser.options)
        print("-----[ TEST END ]------------------------------------------")

        print("-----[ TEST BEGIN ]----------------------------------------")
        # Set options to an invalid type
        new_options_value = None
        with self.assertRaises(TypeError):
            parser.options = new_options_value
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_method_gen_options_list_01(self):
        """
        Test the ``gen_options_list`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_OPTION_REMOVAL_VARIABLES"
        print("Section  : {}".format(section))

        option_list_expect = [
            '-AParam1Param2Param3=VALUE_A', '-BParam4Param5Param6=VALUE_B', '-CArg1Arg2Arg3=VALUE_C'
        ]

        # parse a section
        print("-" * 40)
        print("Execute Parser")
        print("-" * 40)
        option_list_actual = parser.gen_option_list(section)

        # pretty print the loginfo
        print("-" * 40)
        print("LogInfo")
        print("-" * 40)
        parser._loginfo_print()

        # pretty print the options data
        print("-" * 40)
        print("Options")
        print("-" * 40)
        pprint(parser.options, width=120)

        # pretty print the expected output
        print("-" * 40)
        print("Option List Expected")
        print("-" * 40)
        pprint(option_list_expect, width=120)

        # pretty print the actual output
        print("-" * 40)
        print("Option List Actual")
        print("-" * 40)
        pprint(option_list_actual, width=120)

        # Validate the results
        self.assertListEqual(option_list_expect, option_list_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_method_gen_options_list_02(self):
        """
        Test the ``gen_options_list`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 5
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_GEN_OPTION_LIST_ERROR_01"
        print("Section  : {}".format(section))

        option_entry = {'type': ['opt_set_undefined_type'], 'value': None, 'params': ['cmake']}

        with self.assertRaises(ValueError):
            parser._gen_option_entry(option_entry)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_handler_opt_remove_no_params(self):
        """
        Test the ``gen_options_list`` method.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_OPT_REMOVE_NO_PARAMS_01"
        print("Section  : {}".format(section))

        with self.assertRaises(IndexError):
            data = parser.parse_section(section)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_initialize_handler_parameters_01(self):
        """
        Test some coverage on ``_initialize_handler_parameters``.
        Calls the initialize_handler_parameters function a 2nd time,
        which would have the private attribute defined.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_OPTION_REMOVAL_VARIABLES"
        print("Section  : {}".format(section))

        handler_parameters = HandlerParameters.HandlerParameters()
        handler_parameters.data_internal['processed_sections'] = set()
        handler_parameters.data_shared[parser._data_shared_key] = []
        parser._initialize_handler_parameters(section, handler_parameters)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_handler_opt_remove_01(self):
        """
        Testing for opt_remove
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_OPTION_REMOVAL_VARS_01"
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

        # pretty print the options data
        print("-" * 40)
        print("Options")
        print("-" * 40)
        pprint(parser.options, width=120)

        # pretty print the options list
        print("-" * 40)
        print("Options List")
        print("-" * 40)
        options_list_expect = ['-BParam4Param5Param6=VALUE_B', '-CArg1Arg2Arg3=VALUE_C']
        options_list_actual = parser.gen_option_list(section, generator='bash')

        print("Expected Options List:")
        pprint(options_list_expect)
        print("Actual Options List:")
        pprint(options_list_actual)
        self.assertListEqual(options_list_expect, options_list_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_handler_opt_remove_02(self):
        """
        Testing for opt_remove
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_OPTION_REMOVAL_VARS_02"
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

        # pretty print the options data
        print("-" * 40)
        print("Options")
        print("-" * 40)
        pprint(parser.options, width=120)

        # pretty print the options list
        print("-" * 40)
        print("Options List")
        print("-" * 40)
        options_list_expect = ['-CArg1Arg2Arg3=VALUE_C']
        options_list_actual = parser.gen_option_list(section, generator='bash')

        print("Expected Options List:")
        pprint(options_list_expect)
        print("Actual Options List:")
        pprint(options_list_actual)
        self.assertListEqual(options_list_expect, options_list_actual)
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_method__gen_option_entry_method_not_found(self):
        """
        Test ``_gen_option_entry`` when the app can't locate a suitable
        line generator method and ``exception_control_level`` is less than
        5, thus ensuring the ``exception_control_event`` triggers a "SILENT"
        event that won't be raised.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_OPTION_REMOVAL_VARIABLES"
        print("Section  : {}".format(section))

        option_entry = {'type': ['nonexistent_command'], 'value': None, 'params': ['cmake']}

        output_expected = None
        output_actual = parser._gen_option_entry(option_entry, generator="bash")
        self.assertEqual(output_expected, output_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_method__gen_option_entry_generator_not_found(self):
        """
        Test ``_gen_option_entry`` the requested generator isn't found.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_OPTION_REMOVAL_VARIABLES"
        print("Section  : {}".format(section))

        option_entry = {'type': ['opt_set'], 'value': None, 'params': ['cmake']}
        output_expected = None
        output_actual = parser._gen_option_entry(option_entry, generator="foobar")
        self.assertEqual(output_expected, output_actual)

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0

    def test_SetProgramOptions_test_spaces_in_value(self):
        """
        Test values with spaces to verify that quotes get added.
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_SPACES_IN_VALUE"
        print("Section  : {}".format(section))

        option_list_expect = ['TEST_OPTIONS="-ldl -fsanitize=address"']
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

    def test_SetProgramOptions_test_var_exansion(self):
        """
        Test var expansion
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        #section = "TEST_VAR_EXPANSION_DEFAULT"
        section = "TEST_VAR_EXPANSION_ENV"
        print("Section  : {}".format(section))

        option_list_expect = ['FOO="${FOOBAR} -baz"']

        #with self.assertRaises(ValueError):
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

    def test_SetProgramOptions_test_var_exansion_no_type_given(self):
        """
        Test var expansion
        """
        print("\n")
        print("Load file: {}".format(self._filename))
        parser = SetProgramOptions(self._filename)
        parser.debug_level = 5
        parser.exception_control_level = 4
        parser.exception_control_compact_warnings = False

        print("-----[ TEST BEGIN ]----------------------------------------")
        section = "TEST_VAR_EXPANSION_NO_TYPE"
        print("Section  : {}".format(section))

        with self.assertRaises(ValueError):
            parser.gen_option_list(section, generator="bash")

        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0



class SetProgramOptionsTestCommon(TestCase):
    """
    Test free function(s) in the ``common.py`` file.
    """

    def test_common_freefunction_get_function_ref(self):
        """
        Test var expansion
        """

        class test_class(object):

            def testme(self):
                # create a class member called 'foobar'
                self.foobar = None
                # This should raise an error because self.foobar is not callable.
                get_function_ref(self, 'foobar')

        print("-----[ TEST BEGIN ]----------------------------------------")
        ccc = test_class()

        with self.assertRaises(TypeError):
            ccc.testme()
        print("-----[ TEST END ]------------------------------------------")

        print("OK")
        return 0



#
