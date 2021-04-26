#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
:Authors:
    - William C. McLendon III <wcmclen@sandia.gov>
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

import copy
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
    def options(self) -> dict:
        """
        The ``options`` property contains the set of parsed options that has
        been processed so far stored as a dictionary. For example, the following
        .ini snippet:

        .. code-block:: ini
            :linenos:

            [SECTION_A]
            opt-set cmake
            opt-set -G : Ninja

        might generate the folllowing result in ``options``:

            >>> parser.options
            {'SECTION_A':
                [
                    {'type': ['opt_set'], 'params': ['cmake'], 'value': None },
                    {'type': ['opt_set'], 'params': ['-G'], 'value': 'Ninja' }
                ]
            }

        would encode the reults of a ``.ini`` file *section* "SECTION_A" which
        encoded the command: ``cmake -G Ninja``.

        This data is used by the ``gen_option_list`` method to generate snippets
        according to the requested generator, such as "bash" or "cmake_fragment".

        Raises:
            TypeError: A TypeError can be raised if a non-dictionary is assigned
                to this property.

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


    def gen_option_list(self, section, generator='bash') -> list:
        """Generate a list of options for a section.

        Generates a list of strings that captures the requested
        operation based on the entries in the .ini file that is
        stored in ``options`` during parsing.

        The ``bash`` generator will generate a set of 'bash' like
        entries that could be concactenated to generate a bash command.

        For  example, the .ini section:

        .. code-block:: ini
            :linenos:

            [SECTION_A]
            opt-set cmake
            opt-set -G : Ninja
            opt-set /path/to/source/dir

        will generate this output:

            >>> option_list = parser.gen_option_list("SECTION_A", "bash")
            >>> option_list
                [
                    'cmake',
                    '-G=Ninja',
                    '/path/to/source/dir'
                ]

        Which can be joined easily to create a bash instruction, such as:

            >>> " ".join(option_list)
            cmake -G=Ninja

        or we could generate a multi-line bash command with continuation
        lines like this:

            >>> " \\\\\\n    ".join(option_list)
            cmake \\
                -G=Ninja \\
                /path/to/source/dir

        This can then be executed in a bash shell or saved to a script file that could
        be executed separately.

        Args:
            section (str): The section name that contains the options
                we wish to process.
            generator (str): What kind of generator are we to use to
                build up our options list? Currently we allow ``bash``
                but subclasses can define their own functions using the
                format ``_gen_option_entry_<generator>(option_entry:dict)``

        Returns:
            list: A ``list`` containing the processed options text.
        """
        self._validate_parameter(section, (str))
        self._validate_parameter(generator, (str))

        output = []

        if section not in self.options.keys():
            self.parse_section(section)

        section_data = self.options[section]

        for option_entry in section_data:
            gen_method_name = "_gen_option_entry"
            (method_name,method_ref) = self._locate_class_method(gen_method_name)
            line = method_ref(option_entry, generator)
            if line is not None:
                output.append(line)

        return output


    # ---------------------------------------------------------------
    #   H A N D L E R S  -  P R O G R A M   O P T I O N S
    # ---------------------------------------------------------------


    def _gen_option_entry(self, option_entry: dict, generator='bash') -> str:
        """
        Takes an ``option_entry`` and looks for a specialized handler
        for that option **type**.

        This looks for a method named ``_program_option_handler_<typename>_<generator>``
        where ``typename`` comes from the ``option_entry['type']`` field. For example,
        if ``option_entry['type']`` is ``opt_set`` and ``generator`` is ``bash`` then
        we look for a method called ``_program_option_handler_opt_set_bash``, which
        is executed and returns the line-item entry for the given ``option_entry``.

        Args:
            option_entry (dict): A dictionary storing a single *option* entry.

        Returns:
            str: A string containing the single entry for this option.
            None: Can also return ``NoneType`` IF the ``type`` field in ``option_entry``
                  does not resolve to a proper method and the *exception control level*
                  is not set sufficiently high to trigger an exception.

        Raises:
            ValueError: A ``ValueError`` is raised if we aren't able to locate
                the options formatter.
        """
        self._validate_parameter(option_entry, (dict))
        self._validate_parameter(generator, (str))

        output = None

        method_name = None
        method_ref  = None

        method_name_list = []

        # Look for a matching method in the list of 'types' that
        # this operation can map to.
        for typename in option_entry['type']:
            method_name = "_".join(["_program_option_handler", str(typename), generator])
            (method_name, method_ref) = self._locate_class_method(method_name)
            if method_ref is not None:
                break
            method_name_list.append(method_name)
        else:
            # The for did _not_ exit via the break...
            message = ["ERROR: Unable to locate an option formatter named:"]
            for method_name in method_name_list:
                message.append("- `{}()`".format(method_name))
            self.exception_control_event("SILENT", ValueError, "\n".join(message))

        # Found a match.
        if method_ref is not None:
            params = copy.deepcopy(option_entry['params'])
            value  = copy.deepcopy(option_entry['value'])
            output = method_ref(params, value)

        return output


    def _generic_program_option_handler_bash(self, params, value) -> str:
        """Generic processer for generic bash options.

        This is the simplest kind of option handler for bash-like commands
        where we just concatenate all the ``params`` together and set them
        equal to the ``value``.

        Args:
            params (list): A ``list`` of strings containing the parameters
                that would be to the LHS or the ``=`` when constructing an
                option entry.
            value (str): A ``str`` that is placed to the RHS of the option
                assignment expression.

        Returns:
            str: A ``str`` object representing an option.
        """
        output = "".join(params)
        if value is not None:
            output += "={}".format(value)
        return output


    def _program_option_handler_opt_set_bash(self, params, value) -> str:
        """BASH generator for ``opt-set`` operations.
        """
        return self._generic_program_option_handler_bash(params, value)


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
        """Handler for ``opt-set`` operations

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
        """Handler for ``opt-remove`` operations.

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

        params = handler_parameters.params

        if params is None or len(params) == 0:
            self.exception_control_event("CATASTROPHIC", IndexError)

        removal_key = params[0]

        if len(params) == 1:
            self.debug_message(2, " -> Remove all options containing:`{}`".format(removal_key))
            data_shared_ref = list(filter(lambda x: removal_key not in x['params'], data_shared_ref))

        if len(params) >= 2 and params[1]=="SUBSTR":
            self.debug_message(2, " -> Remove all options containing SUBSTRING:`{}`".format(removal_key))
            data_shared_ref = list(filter(lambda entry, rkey=removal_key:
                                          all(rkey not in item for item in entry['params']),
                                          data_shared_ref))

        handler_parameters.data_shared['setprogramoptions'] = data_shared_ref
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

