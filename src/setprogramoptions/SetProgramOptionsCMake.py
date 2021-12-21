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
SetProgramOptionsCMake
======================

``SetProgramOptionsCMake`` is a subclass of the ``SetProgramOptions``
that adds CMake-specific handlers for the following .ini file operations:

Operation: ``opt-set-cmake-var``
++++++++++++++++++++++++++++++++
The ``opt-set-cmake-var`` operation can have the following format:

.. code-block:: bash
   :linenos:

   opt-set-cmake-var <varname> [<type>] [FORCE] [PARENT_SCOPE] : <value>

This command can result in a generated **bash** output that might look like:
``-DVAR_NAME:BOOL=ON`` using the ``SetProgramOptions`` method ``gen_option_list``
with the ``bash`` generator.

When using the BASH generator to generate command line arguments, CMake
uses the syntax ``-D<VARNAME>[:<TYPE>]=<VALUE>``. The ``TYPE`` field is optional
and if left out CMake will default to a ``STRING`` type. Further, all CMake
variables set via the command line using ``-D`` will be CACHE variables and each
``-D`` operation should be considered a FORCE operation too. For example,
``-DFOO:STRING=BAR`` is roughly equivalent to the CMake command:
``set(FOO CACHE STRING "docstring" FORCE)``.

The ``PARENT_SCOPE`` option applies only to non-cache variables and its presence
will instruct CMake to make that variable non-cache. Care should be taken when
using ``PARENT_SCOPE`` as combining it with the usual CACHE operations results
in CMake creating a non-cached variable whose contents are the list containing
``<varname>;CACHE;<type>;doc string``. As a result, the BASH generator issues
warnings with no generated command line arguments when either 1. ``PARENT_SCOPE``
OR 2. solely a variable name AND variable value are passed in to `opt-set-cmake-var`.

See CMake documentation on the `set() <https://cmake.org/cmake/help/latest/command/set.html>`_
command for more information on how fragment file entries are generated.

We do not support the *environment variable* variation of ``set()`` at this time.


:Authors:
    - William C. McLendon III <wcmclen@sandia.gov>
    - Evan Harvey <eharvey@sandia.gov>
"""
from __future__ import print_function
from enum import Enum

#import inspect
#from pathlib import Path
#from textwrap import dedent

# For type-hinting
# from typing import List, Set, Dict, Tuple, Optional, Iterable

try:                         # pragma: no cover
                             # @final decorator, requires Python 3.8.x
    from typing import final
except ImportError:          # pragma: no cover
    pass

from pathlib import Path
from pprint import pprint
import shlex

from configparserenhanced import *
from configparserenhanced import TypedProperty

from .SetProgramOptions import SetProgramOptions
from .SetProgramOptions import ExpandVarsInText

# ==============================
#  F R E E   F U N C T I O N S
# ==============================

# ===============================
#   H E L P E R   C L A S S E S
# ===============================


class ExpandVarsInTextCMake(ExpandVarsInText):
    """
    Extends ``ExpandVarsInText`` class to add in support for a ``CMAKE`` generator.
    """

    # Typed Property `_bashgen_unhandled_cmake_var_eventtype`:
    # sets the exception_control_event level for when an unresolved
    # `CMake` var is encountered by the BASH generator.
    _bashgen_unhandled_cmake_var_eventtype = \
        TypedProperty.typed_property("_bashgen_unhandled_cmake_var_eventtype",
                                     expected_type=str,
                                     default="MINOR",
                                     internal_type=str)

    def __init__(self):
        self.exception_control_level = 3

    def _fieldhandler_BASH_CMAKE(self, field):
        """
        Format CMAKE fields for the BASH generator.

        Args:
            field (setprogramoptions.VariableFieldData): Stores the action entry's
                parameters and field information.

        Raises:
            ValueError: A ``ValueError`` can be raised if we have an unresolved
                CMake variable in the ``.ini`` file (i.e., ``${FIELDNAME|CMAKE}``).
                By "unresolved" we mean that the CMake does not have some entry in
                the cache that resolves it down to either text or a BASH environment
                variable.
                This exception is skipped if ``self.exception_control_level`` is set
                to 3 or lower. If it is 4 or higher then the exception is raised.
        """
        output = field.varfield
        if field.varname in self.owner._var_formatter_cache.keys():
            output = self.owner._var_formatter_cache[field.varname].strip('"')
        else:
            # If self.exception_control_level is >= 4 then we'll raise the error
            # instead of sending a warning.
            # Change this to `CATASTROPHIC` to always throw the error.
            msg = f"Unresolved variable expansion for `{field.varname}` in a BASH file."
            msg += " CMake variables are only valid in a CMake fragment file."
            self.exception_control_event(self._bashgen_unhandled_cmake_var_eventtype, ValueError, msg)
            output = ""
        return output

    def _fieldhandler_CMAKE_FRAGMENT_ENV(self, field):
        """Format ENV fields for CMAKE_FRAGMENT generators."""
        output = "$ENV{" + field.varname + "}"
        return output

    def _fieldhandler_CMAKE_FRAGMENT_CMAKE(self, field):
        """Format CMAKE fields for CMAKE_FRAGMENT generators."""
        output = "${" + field.varname + "}"
        return output



# ===============================
#   M A I N   C L A S S
# ===============================

class VarType(Enum):
    """Enumeration used to check for CMake variable types in SPOC."""
    CACHE = 1
    NON_CACHE = 2

class SetProgramOptionsCMake(SetProgramOptions):
    """Extends SetProgramOptions to add in CMake option support.

    - Adds a new **.ini** file command: ``opt-set-cmake-var``
      which can have the format: ``opt-set-cmake-var VARNAME [TYPE] : VALUE``
    - Adds a new back-end generator for ``cmake_fragment``
      files for the :py:meth:`setprogramoptions.SetProgramOptions.gen_option_list` method.
    """

    def __init__(self, filename=None):
        if filename is not None:
            self.inifilepath = filename

    # -----------------------
    #   P R O P E R T I E S
    # -----------------------

    # _var_formatter property handles the expansion of var fields in text.
    _var_formatter = typed_property(
        "_varhandler", expected_type=ExpandVarsInTextCMake, default_factory=ExpandVarsInTextCMake
    )

    # -------------------------------
    #   P U B L I C   M E T H O D S
    # -------------------------------

    # ---------------------------------------------------------------
    #   H A N D L E R S  -  P R O G R A M   O P T I O N S
    # ---------------------------------------------------------------

    def _program_option_handler_opt_set_cmake_fragment(self, params: list, value: str) -> str:
        """
        **cmake fragment** line-item handler for ``opt-set`` entries.
        Sine we don't care about that for a CMake fragment this can be a noop.

        Including this function prevents an ``exception_control_event`` warning
        from being generated in :py:class:`setprogramoptions.SetProgramOptions`.

        This method is essentially a noop but we can keep it in case someone ever
        turns ``exception_control_level`` (ecl) to max. This is because if this function
        isn't defined a "SILENT" ``exception_control_event`` will get tripped in
        ``SetProgramOptions``. Normally this would just pass on by but since SILENT
        events are treated as WARNINGS with respect to raising an exception, removing
        this would trigger an exception when ecl is 5.

        That said, keeping this method around could still be seen as *optional* in
        that removing it will not affect application behaviour under *normal* use.

        Called By: :py:meth:`setprogramoptions.SetProgramOptions._gen_option_entry`
        using method name scheme: ``_program_option_handler_<operation>_<generator>()``

        Args:
            params (list): The list of parameter entries extracted from the
                .ini line item.
            value (str): The value portion from the .ini line item.

        Returns:
            None
        """
        return None

    def _program_option_handler_opt_set_cmake_var_bash(self, params: list, value: str) -> str:
        """
        Line-item generator for ``opt-set-cmake-var`` entries when the *generator*
        is set to ``bash``.

        Called By: :py:meth:`setprogramoptions.SetProgramOptions._gen_option_entry`
        using method name scheme: ``_program_option_handler_<operation>_<generator>()``

        Note:
            It's ok to modify ``params`` and ``value`` here without concern of
            side-effects since :py:meth:`setprogramoptions.SetProgramOptions._gen_option_entry`
            performs a deep-copy of these parameters prior to calling this.
            Any changes we make are ephemeral.

        Args:
            params (list): The parameters of the operation.
            value (str): The value of the option that is being assigned.

        Raises:
            ValueError: This can potentially raise a ``ValueError`` if
                ``exception_control_level`` is set to 5 if there are
                operations that are skipped in Bash generation. If ``ecl``
                is less than 5 then warnings are generated to note the
                exclusion.
        """
        varname = params[0]
        params = params[1 : 4]
        param_opts = self._helper_opt_set_cmake_var_parse_parameters(params)

        # Type-1 (non-cached / PARENT_SCOPE / non-typed) entries should not be
        # written to the set of Bash parameters.
        if param_opts['VARIANT'] == VarType.NON_CACHE:
            msg = f"bash generator - `{varname}={value}` skipped because"
            msg += f" it is a non-cached (type-1) operation."
            msg += f" To generate a bash arg for this consider adding FORCE or a TYPE"
            msg += f" and remove PARENT_SCOPE if it exists."
            self.exception_control_event("WARNING", ValueError, message=msg)
            return None

        # If varname has already been assigned and this assignment
        # does not include FORCE then we should skip adding it to the
        # set of command line options.
        if varname in self._var_formatter_cache and not param_opts['FORCE']:
            msg = f"bash generator - `{varname}={value}` skipped because"
            msg += f" CACHE var `{varname}` is already set and CMake requires"
            msg += f" FORCE to be set to change the value."
            self.exception_control_event("WARNING", ValueError, message=msg)
            return None

        # Prepend `-D` to the parameters
        params = ["-D", varname]

        # If the type is provided then include the `:<typename>` argument.
        # Note: CMake defaults to STRING if not provided.
        params.append(":" + param_opts['TYPE'])

        # Save variable to the cache of 'known'/'set' cmake variables
        self._var_formatter_cache[varname] = value

        return self._generic_program_option_handler_bash(params, value)

    def _program_option_handler_opt_set_cmake_var_cmake_fragment(self, params: list, value: str) -> str:
        """
        **cmake fragment** line-item generator for ``opt-set-cmake-var`` entries when
        the *generator* requests a ``cmake_fragment`` entry.

        The generated output for this command should be valid according to
        the CMake `set() <https://cmake.org/cmake/help/latest/command/set.html>`_ command.

        Valid formats for `set() <https://cmake.org/cmake/help/latest/command/set.html>`_ are:

        - `set(<variable> <value> [FORCE] [PARENT_SCOPE]) <https://cmake.org/cmake/help/latest/command/set.html#set-normal-variable>`_
        - `set(<variable> <value> CACHE <type> <docstring> [FORCE] [PARENT_SCOPE]) <https://cmake.org/cmake/help/latest/command/set.html#set-cache-entry>`_

        We do *not* support the
        `set(ENV{<variable>} [<value>]) <https://cmake.org/cmake/help/latest/command/set.html#set-environment-variable>`_
        variant.

        Called By: :py:meth:`setprogramoptions.SetProgramOptions._gen_option_entry`
        using method name scheme: ``_program_option_handler_<operation>_<generator>()``

        Note:
            It's ok to modify ``params`` and ``value`` here without concern of
            side-effects since :py:meth:`setprogramoptions.SetProgramOptions._gen_option_entry`
            performs a deep-copy of these parameters prior to calling this.
            Any changes we make are ephemeral.
        """
        varname = params[0]
        params = params[1 : 4]
        param_opts = self._helper_opt_set_cmake_var_parse_parameters(params)

        params = [varname, value]
        if param_opts['TYPE'] is not None:
            params.append("CACHE")
            params.append(param_opts["TYPE"])
            params.append('"from .ini configuration"')

        if param_opts['PARENT_SCOPE']:
            params.append("PARENT_SCOPE")

        if param_opts['FORCE']:
            params.append("FORCE")

        output = "set({})".format(" ".join(params))
        return output

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
        # Invoke the handler_initialize from SetProgramOptions
        super().handler_initialize(section_name, handler_parameters)
        return 0

    # ---------------------------------------------------------------
    #   H A N D L E R S  -  C O N F I G P A R S E R E N H A N C E D
    # ---------------------------------------------------------------

    @ConfigParserEnhanced.operation_handler
    def _handler_opt_set_cmake_var(self, section_name: str, handler_parameters) -> int:
        """Handler for ``opt-set-cmake-var``

        Called By: ``configparserenhanced.ConfigParserEnhanced`` parser.

        Args:
            section_name (str): The name of the section being processed.
            handler_parameters (HandlerParameters): The parameters passed to
                the handler.

        Returns:
            int: Status value indicating success or failure.

            - 0     : SUCCESS
            - [1-10]: Reserved for future use (WARNING)
            - > 10  : An unknown failure occurred (CRITICAL)
        """
        return self._option_handler_helper_add(section_name, handler_parameters)

    # ---------------------------------
    #   H A N D L E R   H E L P E R S
    # ---------------------------------

    # -----------------------
    #   H E L P E R S
    # -----------------------

    def _helper_opt_set_cmake_var_parse_parameters(self, params: list):
        """
        Processes the list of parameters to detect the existence of
        flags for variables. This is consumed when generating option lists
        because the relevance of some options depends on the back-end
        generator. For example, ``PARENT_SCOPE`` is relevant to a ``cmake_fragment``
        generator but does not get used for a ``bash`` option that would be
        provided to the ``cmake`` application on the command line.

        Called By:

        - :py:meth:`_program_option_handler_opt_set_cmake_var_bash`
        - :py:meth:`_program_option_handler_opt_set_cmake_var_cmake_fragment`

        Args:
            params (:obj:`list` of :obj:`str`): The list of parameters
                pulled out of the .ini file entry.

        Returns:
            dict: A dictinary object that captures the existence or
            omission of flags that are applicable to a CMake Cache
            variable operation.
        """
        default_cache_var_type = "STRING"

        output = {'FORCE': False, 'PARENT_SCOPE': False, 'TYPE': None, 'VARIANT': None}

        for option in params[: 4]:
            if option == "FORCE":
                output['FORCE'] = True
                # If FORCE is found but we have no TYPE yet, set to the default.
                # TODO: Should we be setting the default to STRING here when FORCE
                #       is provided with no explicit type? Future CMake versions might
                #       someday change the default which would possibly break this?
                if output['TYPE'] is None:
                    output['TYPE'] = default_cache_var_type
            elif option == "PARENT_SCOPE":
                output['PARENT_SCOPE'] = True
            elif option in ["BOOL", "FILEPATH", "PATH", "STRING", "INTERVAL"]:
                output['TYPE'] = option

        # Sanity Check(s)

        # Case 1: PARENT_SCOPE and FORCE will cause a CMake Error
        if output['FORCE'] and output['PARENT_SCOPE']:
            msg = "ERROR: CMake does not allow `FORCE` and `PARENT_SCOPE` to both be used."
            self.exception_control_event("CATASTROPHIC", ValueError, message=msg)

        # Case 2: PARENT_SCOPE and CACHE will cause a CMake warning
        #         and the value will include the cache entries as a list:
        #             `set(FOO "VAL" CACHE STRING "docstring" PARENT_SCOPE)`
        #         will result in `FOO` being set to "VAL;CACHE;STRING;docstring"
        #         in the parent module's scope. This is probably not what someone
        #         intended. Let this be a WARNING event though.
        #         TBH: this should probably be a CATASTROPHIC but for now I'll
        #              at least warn about it which is more than CMake does.
        if output['PARENT_SCOPE'] and output["TYPE"] != None:
            msg = "WARNING: Setting `PARENT_SCOPE` with `CACHE` parameters will result\n"
            msg += "         in a non-CACHE variable being set containing a list of the\n"
            msg += "         CACHE options. i.e., '<value>;CACHE;<type>;<docstring>'\n"
            msg += "         which is probably not what is intended, but CMake will\n"
            msg += "         not error or warn on this."
            self.exception_control_event("WARNING", ValueError, message=msg)

        # Determine the variant of the ``set`` operation.
        # Type 1: ``set(<variable> <value>... [PARENT_SCOPE])``
        # Type 2: ``set(<variable> <value>... CACHE <type> <docstring> [FORCE])``

        # PARENT_SCOPE forces Type-1 (i.e., non-cache var)
        # - This will override CACHE, at least as of CMake 3.21.x
        if output['PARENT_SCOPE']:
            output['VARIANT'] = VarType.NON_CACHE

        # FORCE implies CACHE. If type wasn't provided then it's a STRING
        elif output['FORCE']:
            output['VARIANT'] = VarType.CACHE

        # If a TYPE is provided then it's a type-2 (CACHE) assignment.
        elif output['TYPE'] is not None:
            output['VARIANT'] = VarType.CACHE

        # Otherwise, a simple set is a type-1
        else:
            output['VARIANT'] = VarType.NON_CACHE

        return output
