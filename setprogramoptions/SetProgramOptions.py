#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
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
from __future__ import print_function

#import inspect
#from pathlib import Path
#from textwrap import dedent

# For type-hinting
from typing import Dict,Iterable,List,Optional,Set,Tuple,Union

try:                  # pragma: no cover
    # @final decorator, requires Python 3.8.x
    from typing import final
except ImportError:   # pragma: no cover
    pass

import copy
import dataclasses
from pathlib import Path
from pprint import pprint
import re
import shlex

from configparserenhanced import *



# ==============================
#  F R E E   F U N C T I O N S
# ==============================


# ===============================
#   H E L P E R   C L A S S E S
# ===============================


class VariablesInStringsFormatter(object):

    @dataclasses.dataclass(frozen=True)
    class fieldinfo:
        varfield: str
        varname : str
        vartype : str
        start   : int
        end     : int


    def _expandvar_ENV_bash(self, field):
        """ Expand an Envvar for BASH
        """
        return "${" + field.varname + "}"


    # Todo: these will be used for SetProgramOptionsCMake
    #def _expandvar_CMAKE_bash(self, field):
        #msg = "`{}`: is invalid in a `bash` context.".format(field.varfield)
        ## Todo: can we keep track of CMake vars that we know about already
        ##       and if we _know_ what they'll be then we expand, otherwise
        ##       we'd throw our hands in the air... like we just don't care.
        #raise NotImplementedError(msg)


    #def _expandvar_ENV_cmake(self, field):
        #return "$ENV{" + field.varname + "}"


    #def _expandvar_CMAKE_cmake(self, field):
        #return "${" + field.varname + "}"


    def _format_vars_in_string(self, text, sep='|', generator="bash"):
        """
        Format variables that are formatted like ``${VARNAME|TYPE}`` according
        to the proper generator.

        Args:
            text (str): The string we wish to modify.
            sep (str): The separator character to distinguish VARNAME from TYPE.
            generator (str): The kind of generator to use (i.e., are we generating
                output for a bash script, a CMake fragment, Windows, etc.)

        Raises:
            Exception: An exception is raised if the appropriate generator helper
                method is not found.
        """
        generator = generator.lower()

        pattern = r"\$\{([a-zA-Z0-9_" + sep + r"\*\@\[\]]+)\}"

        matches = re.finditer(pattern, text)

        output = ""
        curidx = 0
        for m in matches:
            varfield = m.groups()[0]
            idxsep  = varfield.index(sep) if sep in varfield else None

            vartype = "ENV"
            if idxsep:
                vartype = varfield[idxsep + len(sep):]
                vartype = vartype.upper().strip()
            varname = varfield[:idxsep]

            varfield = "${" + m.groups()[0] + "}"

            field = self.fieldinfo(varfield, varname, vartype, m.start(), m.end())
            #print(">>> field =", field)

            handler_name = "_".join(["_expandvar", vartype, generator])
            func = None
            if hasattr(self, handler_name):
                func = getattr(self, handler_name)
            else:
                raise Exception("Missing required generator helper: `{}`.".format(handler_name))

            output += text[curidx:field.start]
            output += func(field)
            curidx = field.end

        output += text[curidx:]
        return output



# ===============================
#   M A I N   C L A S S
# ===============================


class SetProgramOptions(ConfigParserEnhanced, VariablesInStringsFormatter):
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


        for option_entry in section_data:
            line = self._gen_option_entry(option_entry, generator=generator)
            if line is not None:
                output.append(line)

        return output



    # ---------------------------------------------------------------
    #   H A N D L E R S  -  P R O G R A M   O P T I O N S
    # ---------------------------------------------------------------


    def _gen_option_entry(self, option_entry: dict, generator='bash') -> Union[str,None]:
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

            # if there's a space in value, inject quotes
            if value is not None and " " in value:
                value = '"' + value + '"'

            output = method_ref(params, value)

        return output


    def _generic_program_option_handler_bash(self, params:list, value:str) -> str:
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
            output += "=" + self._format_vars_in_string(value, generator="bash")
        return output


    def _program_option_handler_opt_set_bash(self, params:list, value:str) -> str:
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
    def handler_initialize(self, section_name:str, handler_parameters) -> int:
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
        # -----[ Handler Content Start ]-------------------

        self._initialize_handler_parameters(section_name, handler_parameters)

        # -----[ Handler Content End ]---------------------
        return 0


    @ConfigParserEnhanced.operation_handler
    def handler_finalize(self, section_name:str, handler_parameters) -> int:
        """Finalize a recursive parse search.

        Returns:
            int: Status value indicating success or failure.

            - 0     : SUCCESS
            - [1-10]: Reserved for future use (WARNING)
            - > 10  : An unknown failure occurred (SERIOUS)
        """
        # -----[ Handler Content Start ]-------------------

        # save the results into the right `options_cache` entry
        self.options[section_name] = handler_parameters.data_shared[self._data_shared_key]

        for entry in self.options[section_name]:
            pprint(entry, width=200, sort_dicts=False)

        # -----[ Handler Content End ]---------------------
        return 0


    @ConfigParserEnhanced.operation_handler
    def _handler_opt_set(self, section_name:str, handler_parameters) -> int:
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
    def _handler_opt_remove(self, section_name:str, handler_parameters) -> int:
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
        # -----[ Handler Content Start ]-------------------
        data_shared_ref = handler_parameters.data_shared[self._data_shared_key]

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

        handler_parameters.data_shared[self._data_shared_key] = data_shared_ref
        # -----[ Handler Content End ]---------------------
        return 0


    def _option_handler_helper_add(self, section_name:str, handler_parameters) -> int:
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
        # -----[ Handler Content Start ]-------------------
        data_shared_ref = handler_parameters.data_shared[self._data_shared_key]
        op     = handler_parameters.op
        value  = handler_parameters.value
        params = handler_parameters.params

        entry = {'type'   : [op],
                 'value'  : value,
                 'params' : params
                }

        data_shared_ref.append(entry)
        # -----[ Handler Content End ]---------------------
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
        """
        self._validate_parameter(section_name, (str))
        self._validate_handlerparameters(handler_parameters)

        data_shared_ref = handler_parameters.data_shared
        if self._data_shared_key not in data_shared_ref.keys():
            data_shared_ref[self._data_shared_key] = []

        return 0

