#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
SetProgramOptions

Todo:
    Fill in the docstring for this file.

:Authors:
    - William C. McLendon III <wcmclen@sandia.gov>

:Version: 0.0.0
"""
from __future__ import print_function

#import inspect
#from pathlib import Path
#from textwrap import dedent

# For type-hinting
from typing import List,Set,Dict,Tuple,Optional,Iterable

try:                  # pragma: no cover
    # @final decorator, requires Python 3.8.x
    from typing import final
except ImportError:   # pragma: no cover
    pass

from pathlib import Path
from pprint import pprint
import shlex

from configparserenhanced import *



# ==============================
#  F R E E   F U N C T I O N S
# ==============================



# ===============================
#   M A I N   C L A S S
# ===============================


class SetProgramOptions(ConfigParserEnhanced):
    """
    Todo:
        Add docstrings to functions and handlers.

    .. configparser reference:
        https://docs.python.org/3/library/configparser.html
    .. docstrings style reference:
        https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html
    """
    def __init__(self, filename=None):
        if filename is not None:
            self.inifilepath = filename


    # -----------------------
    #   P R O P E R T I E S
    # -----------------------


    @property
    def options(self) -> list:
        """
        """
        if not hasattr(self, '_property_options'):
            self._property_options = {}
        return self._property_options


    @options.setter
    def options(self, value) -> dict:
        self._validate_parameter(value, (dict))
        self._property_options = value
        return self._property_options


    # -------------------------------
    #   P U B L I C   M E T H O D S
    # -------------------------------


    def gen_option_list(self, section) -> list:
        """
        """
        output = []

        if section not in self.options.keys():
            self.parse_section(section)

        section_data = self.options[section]

        for option_entry in section_data:
            line = self.gen_option_entry(option_entry)
            if line is None:
                self.exception_control_event("CATASTROPHIC", TypeError,
                        "Failed to process option type {}.".format(option_entry['type']))
            output.append(line)

        return output


    def gen_option_entry(self, option_entry):
        output = None

        method_name = None
        method_ref  = None
        for typename in option_entry['type']:
            method_name = "_program_option_handler_" + str(typename)
            (method_name, method_ref) = self._locate_class_method(method_name)
            if method_ref is not None:
                break
        else:
            return output

        params = option_entry['params']
        value  = option_entry['value']
        output = method_ref(params, value)

        return output


    # ---------------------------------------------------------------
    #   H A N D L E R S  -  P R O G R A M   O P T I O N S
    # ---------------------------------------------------------------


    def _generic_program_option_handler(self, params, value) -> str:
        """
        """
        output = "".join(params)
        if value is not None:
            output += "={}".format(value)
        return output


    def _program_option_handler_opt_set(self, params, value) -> str:
        """
        """
        return self._generic_program_option_handler(params, value)


    def _program_option_handler_opt_set_cmake_cache(self, params, value) -> str:
        """
        """
        return self._generic_program_option_handler(params,value)


    # ---------------------------------------------------------------
    #   H A N D L E R S  -  C O N F I G P A R S E R E N H A N C E D
    # ---------------------------------------------------------------


    def handler_initialize(self, section_name, handler_parameters) -> int:
        """Initialize a recursive parse search.

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            integer value
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

        self._initialize_handler_parameters(section_name, handler_parameters)

        self.exit_handler(handler_parameters)
        return 0


    def handler_finalize(self, section_name, handler_parameters) -> int:
        """Finalize a recursive parse search.

        Returns:
            integer value
                - 0     : SUCCESS
                - [1-10]: Reserved for future use (WARNING)
                - > 10  : An unknown failure occurred (SERIOUS)
        """
        self.enter_handler(handler_parameters)

        # save the results into the right `options_cache` entry
        self.options[section_name] = handler_parameters.data_shared["setprogramoptions"]

        for entry in self.options[section_name]:
            pprint(entry, width=200, sort_dicts=False)

        self.exit_handler(handler_parameters)
        return 0


    def _handler_opt_set(self, section_name, handler_parameters) -> int:
        """Generic Handler Template

        This handler is used for options whose ``key:value`` pair does not
        get resolved to a proper ``<operation>`` and therefore do not get
        routed to a ``handler_<operation>()`` method.

        This method provides a great *template* for subclasses to use when
        creating new custom handlers according to the naming scheme
        ``handler_<operation>()`` or ``_handler_<operation>()``.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        return self._option_handler_helper(section_name, handler_parameters)


    def _handler_opt_remove(self, section_name, handler_parameters) -> int:
        """handler_opt_remove

        Note:
            This method should not be overridden by subclasses.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        self._validate_parameter(section_name, (str) )
        self.enter_handler(handler_parameters)

        # -----[ Handler Content Start ]-------------------
        data_shared_ref = handler_parameters.data_shared['setprogramoptions']

        # value  = handler_parameters.value
        params = handler_parameters.params

        if params is None or len(params) == 0:
            self.exception_control_event("CATASTROPHIC", IndexError)

        removal_key = params[0]

        if len(params) == 1:
            self.debug_message(2, " -> Remove all options containing:`{}`".format(removal_key))
            data_shared_ref = list(filter(lambda x: removal_key not in x['params'], data_shared_ref))

        elif len(params) >= 2 and params[1]=="SUBSTR":
            self.debug_message(2, " -> Remove all options containing SUBSTRING:`{}`".format(removal_key))
            data_shared_ref = list(filter(lambda entry, rkey=removal_key:
                                          all(rkey not in item for item in entry['params']),
                                          data_shared_ref))
        else:
            message = "Malformed instruction `{}`".format(handler_parameters.raw_option)
            self.exception_control_event("CATASTROPHIC", Exception, message)

        handler_parameters.data_shared['setprogramoptions'] = data_shared_ref
        # -----[ Handler Content End ]---------------------

        self.exit_handler(handler_parameters)
        return 0


    def _handler_opt_set_cmake_cache(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        self._validate_parameter(section_name, (str) )
        self.enter_handler(handler_parameters)

        # -----[ Handler Content Start ]-------------------
        data_shared_ref = handler_parameters.data_shared['setprogramoptions']
        op     = handler_parameters.op
        value  = handler_parameters.value
        params = handler_parameters.params

        # Toss out extra 'params'
        params = params[:2]

        # prepend the ":" to the TYPE specifier if we have one.
        if len(params) == 2 and params[1] is not None:
            params[1] = ":" + str(params[1])

        # prepend the "-D" argument to the params list.
        params = ["-D"] + params

        entry = {'type': [op], 'value': value, 'params': params }

        data_shared_ref.append(entry)

        # -----[ Handler Content End ]---------------------

        self.exit_handler(handler_parameters)
        return 0


    # ---------------------------------
    #   H A N D L E R   H E L P E R S
    # ---------------------------------


    def _option_handler_helper(self, section_name, handler_parameters) -> int:
        """

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        self._validate_parameter(section_name, (str) )
        self.enter_handler(handler_parameters)

        # -----[ Handler Content Start ]-------------------
        data_shared_ref = handler_parameters.data_shared['setprogramoptions']
        op     = handler_parameters.op
        value  = handler_parameters.value
        params = handler_parameters.params

        entry = {'type': [op], 'value': value, 'params': params }

        data_shared_ref.append(entry)

        # -----[ Handler Content End ]---------------------

        self.exit_handler(handler_parameters)
        return 0


    # -----------------------
    #   H E L P E R S
    # -----------------------


    def _initialize_handler_parameters(self, section_name, handler_parameters) -> int:
        """Initialize ``handler_parameters``

        Initializes any default settings needed for ``handler_parameters``.
        Takes the same parameters as handlers.

        Args:
            section_name (str): The section name string.
            handler_parameters (object): A HandlerParameters object containing
                the state data we need for this handler.
        """
        self._validate_parameter(section_name, (str))
        self._validate_handlerparameters(handler_parameters)

        data_shared_ref = handler_parameters.data_shared
        if 'setprogramoptions' not in data_shared_ref.keys():
            data_shared_ref['setprogramoptions'] = []

        return 0

