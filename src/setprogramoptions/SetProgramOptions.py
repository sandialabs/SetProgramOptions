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
SetProgramOptions
=================

``SetProgramOptions`` is a subclass of ``ConfigParserEnhanced``
that adds program-option handling capabilities.

Operation: ``opt-set``
++++++++++++++++++++++++++++++++
The ``opt-set`` operation can have the following format:

.. code-block:: bash
   :linenos:

   opt-set Param1 [Param2] ... [ParamN] : <value>

Options are processed using :py:meth:`gen_option_list` to produce a
``list`` or ``strings`` representing a command or set of command line
options that can be processed by the caller.

These options are added to the :py:attr:`options` property.


Operation: ``opt-remove``
++++++++++++++++++++++++++++++++
The ``opt-remove`` operation can have the following format:

.. code-block:: bash
   :linenos:

   opt-remove Param1 [SUBSTR]

This command is used to remove options that have *already* been processed
and added to the :py:attr:`options` property.

Option entries are removed according to the rules:

1. If ``SUBSTR`` is not provided, entries are removed if *any* of
   its *Param* options are exactly matched.
2. If the ``SUBSTR`` parameter is included, the matching criteria
   is relaxed so that an option is removed from the list if any of
   its parameters *contains* ``Param1`` (i.e., ``Param1`` is a
   *sub string* of any paramter in the option).


:Authors:
    - William C. McLendon III <wcmclen@sandia.gov>
"""

# For type-hinting
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

try:                         # pragma: no cover
                             # @final decorator, requires Python 3.8.x
    from typing import final
except ImportError:          # pragma: no cover
    pass

import copy
#from pathlib import Path
#from pprint import pprint
import re
import sys


MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON: # pragma: no cover
    sys.exit("Python %s.%s or later is required.\n" % (MIN_PYTHON))

from configparserenhanced import *
import configparserenhanced.ExceptionControl

from .common import *

# ==============================
#  F R E E   F U N C T I O N S
# ==============================

# ===============================
#   H E L P E R   C L A S S E S
# ===============================



class _VARTYPE_UNKNOWN(object):
    """
    This class serves as a 'default' sentinel type to guard
    against unset variable types in ``ExpandVarsInText``.
    """
    pass



class ExpandVarsInText(ExceptionControl):
    """
    Utility to identify and format variables that are found in a text string.

    This looks for variables embedded in text strings that are formatted like:
    ``${VARNAME|TYPE}`` where ``TYPE`` denotes what kind of variable we are defining.

    The base type that is known is "ENV" for environment variables.

    The ``TYPE`` field MUST BE PRESENT. We do not provide a default to enforce
    users of ``SetProgramOptions`` to be *explicit* in defining the type of variable
    they're declaring.  These are a variables declared in a *pseudo-language* not bash.
    """

    def __init__(self):
        self.exception_control_level = 4

    class VariableFieldData(object):
        """
        This is essentially a dataclass that is used to pass field data around within
        the generators, etc. This captures the relevant fields from a given action
        entry.
        """
        varfield = typed_property('varfield', expected_type=str, req_assign_before_use=True)
        varname = typed_property('varname', expected_type=str, req_assign_before_use=True)
        vartype = typed_property('vartype', expected_type=str, req_assign_before_use=True)
        start = typed_property('start', expected_type=int, req_assign_before_use=True)
        end = typed_property('end', expected_type=int, req_assign_before_use=True)

        def __init__(self, varfield: str, varname: str, vartype: str, start: int, end: int):
            self.varfield = varfield
            self.varname = varname
            self.vartype = vartype
            self.start = start
            self.end = end
            return

        def __str__(self):   # pragma: no cover
            return f"{self.varname}"

    # ---------------------
    #  P R O P E R T I E S
    # ---------------------

    # Default variable type. Default is _VARTYPE_UNKNOWN. If not overridden
    # or changed then a variable string like "${VARNAME}" that does not contain
    # a `|TYPE` component will cause a `ValueError` to be raised.
    default_vartype = TypedProperty.typed_property(
        "default_vartype", expected_type=str, default_factory=_VARTYPE_UNKNOWN, transform=str_toupper
    )

    # Generator type. This is the _kind of output_ that we wish to generate.
    generator = TypedProperty.typed_property(
        "generator", expected_type=str, default="BASH", transform=str_toupper
    )

    # Owner is a link back to the class that instantiated this object.
    # We use this to look back into the owning `SetProgramOptions` class
    # to check for cached information (if needed).
    owner = TypedProperty.typed_property("owner", expected_type=object, default=None)

    # ---------------
    #  M E T H O D S
    # ---------------

    def process(self, text: str) -> str:
        """
        Process a text string and expand any detected ``variables`` in them.

        This function *detects* each of the fields in a text string that are
        formatted like ``${VARNAME|VARTYPE}``. There can be multiple fields
        within a single text entry.

        Each field is converted based on the specified GENERATOR and the VARTYPE of the
        field. These fields are converted using class methods that are named according
        to this naming scheme:
        ``_fieldhandler_GENERATOR_VARTYPE`` where:

        - ``GENERATOR``: The *output* type we're generating, such as "BASH" or "CMAKE".
        - ``VARTYPE``: The kind of variable that is being processed, such as "ENV" for an
            environment variable or "CMAKE" for cmake file variables, etc.

        For example, the field handler to convert an ``ENV`` field using a ``BASH`` generator
        would be named ``_fieldhandler_BASH_ENV(self, field)`` and it accepts an instance
        of the iner class ``VariableFieldData``.
        """
        output = copy.copy(text)

        tokenized_text = self._tokenize_text_string(text)

        for i in range(len(tokenized_text)):
            field = tokenized_text[i]
            if isinstance(field, self.VariableFieldData):
                conversion_method_name = "_fieldhandler_{}_{}".format(self.generator, field.vartype)
                conversion_method_ref = get_function_ref(self, conversion_method_name)
                tokenized_text[i] = conversion_method_ref(field)

        output = "".join(tokenized_text)

        return output

    # ---------------------------------------
    #  C O N V E R S I O N   H A N D L E R S
    # ---------------------------------------

    def _fieldhandler_BASH_ENV(self, field) -> str:
        """
        Format a field containing an ENVVAR as a BASH entry.
        """
        return "${" + field.varname + "}"

    # ---------------
    #  H E L P E R S
    # ---------------

    def _tokenize_text_string(self, text: str):
        """
        Takes a text string and returns a list of text and VariableFieldData entries

        Called By:
            - ``process()``

        """
        output = []

        varfield_list = self._extract_fields_from_text(text)

        curidx = 0
        for varfield in varfield_list:
            output.append(text[curidx : varfield.start])
            output.append(varfield)
            curidx = varfield.end

        output.append(text[curidx :])

        return output

    def _extract_fields_from_text(self, text: str, sep: str = "|"):
        """Extracts the variablefields from a text string.

        Extracts fields from a text string that are formatted like:
        ``${<VARNAME><SEP><VARTYPE>}`` where:

        - VARNAME is the variable name (REQUIRED)
        - SEP is the separator. Default is `|`
        - VARTYPE is the variable type. (REQUIRED)

        Returns:
            list: A list containing text strings and VariableFieldData entries in place
                of variable fields that were detected (these are converted later).
                i.e., ``["foo", VariableFieldData(...), " -a"]``

        Raises:
            ValueError: If the TYPE field is missing.

        Called By:
            - ``_tokenize_text_string()``
        """
        output = []
        pattern = r"\$\{([a-zA-Z0-9_" + sep + r"\*\@\[\]]+)\}"
        matches = re.finditer(pattern, text)

        for m in matches:
            varfield = m.groups()[0]

            vartype = self.default_vartype

            idxsep = varfield.index(sep) if sep in varfield else None
            varname = varfield[: idxsep]

            if idxsep is not None:
                vartype = varfield[idxsep + len(sep):]
                vartype = vartype.upper().strip()

            varfield = "${" + varfield + "}"

            if isinstance(vartype, _VARTYPE_UNKNOWN):
                raise ValueError("Variable missing TYPE field in expansion of `{}`".format(varfield))

            output.append(self.VariableFieldData(varfield, varname, vartype, m.start(), m.end()))

        return output



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

    _var_formatter_cache = typed_property("_varcache", expected_type=dict, default_factory=dict)
    _var_formatter = typed_property(
        "_var_formatter", expected_type=ExpandVarsInText, default_factory=ExpandVarsInText
    )

    @property
    def _data_shared_key(self) -> str:
        """Key used by ``handler_parameters`` for ``shared_data``

        This key is used inside the ``handler_parameters.shared_data[_data_shared_key]``
        as the place we're storing the action list and other data associated with the
        ``ConfigParserEnhanced`` parsing of a given *root* section.

        This information is generally copied out during the :py:meth:`handler_finalize` into
        some class property for accessing beyond the search itself.

        Currently this just uses the current class name.

        Returns:
            str: Default dictionary key internal parser use.

            This property returns a string that is used as the default
            *key* in ``handler_parameters.data_shared`` to bin the data
            being generated during a search.

            This can be used in the :py:meth:`handler_finalize`
            method to extract the shared data captured by the parser before it
            is discarded at the end of a search.

        """
        return self.__class__.__name__

    @property
    def options(self) -> dict:
        """
        The :py:attr:`options` property contains the set of parsed options that has
        been processed so far stored as a dictionary. For example, the following
        .ini snippet:

        .. code-block:: ini
            :linenos:

            [SECTION_A]
            opt-set cmake
            opt-set -G : Ninja

        might generate the folllowing result in :py:attr:`options`:

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
        stored in :py:attr:`options` during parsing.

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

        This can then be executed in a bash shell or saved to a script file
        that could be executed separately.

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

        # Reset the cached vars in the formatter utility
        del self._var_formatter_cache

        for option_entry in section_data:
            line = self._gen_option_entry(option_entry, generator=generator)
            if line is not None:
                output.append(line)

        return output

    # ---------------------------------------------------------------
    #   H A N D L E R S  -  P R O G R A M   O P T I O N S
    # ---------------------------------------------------------------

    def _gen_option_entry(self, option_entry: dict, generator='bash') -> Union[str, None]:
        """
        Takes an ``option_entry`` and looks for a specialized handler
        for that option **type**.

        This looks for a method named ``_program_option_handler_<typename>_<generator>``
        where ``typename`` comes from the ``option_entry['type']`` field. For example,
        if ``option_entry['type']`` is ``opt_set`` and ``generator`` is ``bash`` then
        we look for a method called :py:meth:`_program_option_handler_opt_set_bash`, which
        is executed and returns the line-item entry for the given ``option_entry``.

        Args:
            option_entry (dict): A dictionary storing a single *option* entry.

        Returns:
            Union[str,None]: A ``string`` containing the single entry for this option or ``None``

            ``None`` is returned IF the ``type`` field in ``option_entry``
            does not resolve to a proper method and the *exception control level*
            is not set sufficiently high to trigger an exception.

        Raises:
            ValueError: If we aren't able to locate the options formatter.
        """
        self._validate_parameter(option_entry, (dict))
        self._validate_parameter(generator, (str))

        output = None

        method_name = None
        method_ref = None

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
            value = copy.deepcopy(option_entry['value'])

            if value is not None:
                if " " in value:
                    value = '"' + value + '"'

                # Update the var formatter's ECL to match the current value.
                self._var_formatter.exception_control_level = self.exception_control_level
                self._var_formatter.exception_control_compact_warnings = self.exception_control_compact_warnings

                # format the value
                formatter = self._var_formatter
                formatter.generator = generator
                formatter.owner = self
                value = formatter.process(value)

            output = method_ref(params, value)

        return output

    def _generic_program_option_handler_bash(self, params: list, value: str) -> str:
        """Generic processer for generic bash options.

        This is the simplest kind of option handler for bash-like commands
        where we just concatenate all the ``params`` together and set them
        equal to the ``value``.

        For example:

            >>> params = ['-D','SOMEFLAG',':BOOL']
            >>> value  = "ON"
            >>> _generic_program_option_handler_bash(params,value)
            "-DSOMEFLAG:BOOL=ON"


        Called by: :py:meth:`_program_option_handler_opt_set_bash`

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
            # Make sure STRING flag values are surrounded by double quotes
            if "STRING" in output and not value.startswith('"') and not value.endswith('"'):
                value = f'"{value}"'
            output += "=" + value
        return output

    def _program_option_handler_opt_set_bash(self, params: list, value: str) -> str:
        """Bash generator for ``opt-set`` operations.

        This method handles the generation of an entry for an
        ``opt-set`` operation when the **generator** is set to be ``bash``.

        Called by: :py:meth:`_gen_option_entry`.

        Returns:
            str: A ``string`` containing a generated program option
            with the parameters concactenated together using the format
            ``<param1><param2>...<paramN>=<value>`` will be returned.
        """
        return self._generic_program_option_handler_bash(params, value)

    # ---------------------------------------------------------------
    #   H A N D L E R S  -  C O N F I G P A R S E R E N H A N C E D
    # ---------------------------------------------------------------

    @ConfigParserEnhanced.operation_handler
    def handler_initialize(self, section_name: str, handler_parameters) -> int:
        """Initialize a recursive parse search.

        Args:
            section_name (str): The section name string.
            handler_parameters (:obj:`HandlerParameters`): A HandlerParameters object containing
                the state data we need for this handler.

        Returns:
            int: Status value indicating success or failure.

            - 0     : SUCCESS
            - [1-10]: Reserved for future use (WARNING)
            - > 10  : An unknown failure occurred (SERIOUS)
        """
        self._initialize_handler_parameters(section_name, handler_parameters)
        return 0

    @ConfigParserEnhanced.operation_handler
    def handler_finalize(self, section_name: str, handler_parameters) -> int:
        """Finalize a recursive parse search.

        Returns:
            int: Status value indicating success or failure.

            - 0     : SUCCESS
            - [1-10]: Reserved for future use (WARNING)
            - > 10  : An unknown failure occurred (SERIOUS)
        """
        # save the results into the right `options_cache` entry
        self.options[section_name] = handler_parameters.data_shared[self._data_shared_key]
        return 0

    @ConfigParserEnhanced.operation_handler
    def _handler_opt_set(self, section_name: str, handler_parameters) -> int:
        """Handler for ``opt-set`` operations

        This handler is used for options whose ``key:value`` pair does not
        get resolved to a proper ``<operation>`` and therefore do not get
        routed to a ``handler_<operation>()`` method.

        This method provides a great *template* for subclasses to use when
        creating new custom handlers according to the naming scheme
        ``handler_<operation>()`` or ``_handler_<operation>()``.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (:obj:`HandlerParameters`): The parameters passed to
                the handler.

        Returns:
            int: Status value indicating success or failure.

            - 0     : SUCCESS
            - [1-10]: Reserved for future use (WARNING)
            - > 10  : An unknown failure occurred (CRITICAL)
        """
        return self._option_handler_helper_add(section_name, handler_parameters)

    @ConfigParserEnhanced.operation_handler
    def _handler_opt_remove(self, section_name: str, handler_parameters) -> int:
        """Handler for ``opt-remove`` operations.

        Note:
            This method should not be overridden by subclasses.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (:obj:`HandlerParameters`): The parameters passed to
                the handler.

        Returns:
            int: Status value indicating success or failure.

            - 0     : SUCCESS
            - [1-10]: Reserved for future use (WARNING)
            - > 10  : An unknown failure occurred (CRITICAL)
        """
        return self._option_handler_helper_remove(section_name, handler_parameters)

    # ---------------------------------
    #   H A N D L E R   H E L P E R S
    # ---------------------------------

    def _option_handler_helper_remove(self, section_name: str, handler_parameters) -> int:
        """Removes option(s) from the shared data options list.

        Removes an option or options from the ``handler_parameters.data_shared["{_data_shared_key}"]``
        list, where ``{_data_shared_key}`` is generated from the property :py:attr:`_data_shared_key`.
        Currently, :py:attr:`_data_shared_key` returns the class name of the class object.

        In this case the format is based on the following .ini snippet:

        .. code-block:: ini
            :linenos:

            [SECTION NAME]
            <operation> KEYWORD [SUBSTR]

        where we remove entries from the *shared data options* list according to one of the
        following methods:

        1. Removes entries if one of the parameters matches the provided ``KEYWORD``.
        2. If the optional ``SUBSTR`` parameter is provided, then we remove entries
           if any paramter *contains* the ``KEYWORD`` as either an exact match
           or a substring.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (:obj:`HandlerParameters`): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        data_shared_ref = handler_parameters.data_shared[self._data_shared_key]

        params = handler_parameters.params

        if params is None or len(params) == 0:
            self.exception_control_event("CATASTROPHIC", IndexError)

        removal_key = params[0]

        if len(params) == 1:
            self.debug_message(2, " -> Remove all options containing:`{}`".format(removal_key))
            data_shared_ref = list(filter(lambda x: removal_key not in x['params'], data_shared_ref))

        if len(params) >= 2 and params[1] == "SUBSTR":
            self.debug_message(2, " -> Remove all options containing SUBSTRING:`{}`".format(removal_key))
            data_shared_ref = list(
                filter(
                    lambda entry,
                    rkey=removal_key: all(rkey not in item for item in entry['params']),
                    data_shared_ref
                )
            )

        handler_parameters.data_shared[self._data_shared_key] = data_shared_ref
        return 0

    def _option_handler_helper_add(self, section_name: str, handler_parameters) -> int:
        """Add an option to the shared data options list

        Inserts an option into the ``handler_parameters.data_shared["{_data_shared_key}"]``
        list, where ``{_data_shared_key}`` is generated from the property :py:attr:`_data_shared_key`.
        Currently, :py:attr:`_data_shared_key` returns the class name of the class object.

        Operations with the format such as this:

        .. code-block:: ini
            :linenos:

            [SECTION NAME]
            operation Param1 Param2 ... ParamN : Value

        which result in a ``dict`` entry:

        .. code-block:: python
            :linenos:

            {
                'type'  : [ operation ],
                'params': [ param1, param2, ... , paramN ],
                'value' : Value
            }

        this entry is then appended to the
        ``handler_parameters.data_shared[{_data_shared_key}]`` list, where
        :py:attr:`_data_shared_key` is generated from the property :py:attr:`_data_shared_key`.

        Currently :py:attr:`_data_shared_key` returns the current class name, but
        this can be changed if needed.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (:obj:`HandlerParameters`): The parameters passed to
                the handler.

        Returns:
            int:
            * 0     : SUCCESS
            * [1-10]: Reserved for future use (WARNING)
            * > 10  : An unknown failure occurred (CRITICAL)
        """
        data_shared_ref = handler_parameters.data_shared[self._data_shared_key]
        op = handler_parameters.op
        value = handler_parameters.value
        params = handler_parameters.params

        entry = {'type': [op], 'value': value, 'params': params}

        data_shared_ref.append(entry)
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
            handler_parameters (:obj:`HandlerParameters`): A HandlerParameters
                object containing the state data we need for this handler.

        Called By:
            - ``handler_initialize()``
        """
        self._validate_parameter(section_name, (str))
        self._validate_handlerparameters(handler_parameters)

        data_shared_ref = handler_parameters.data_shared
        if self._data_shared_key not in data_shared_ref.keys():
            data_shared_ref[self._data_shared_key] = []

        return 0
