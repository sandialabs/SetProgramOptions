#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
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

In the case of bash command entries the ``FORCE`` and ``PARENT_SCOPE`` optional
parameters are ignored.

See CMake documentation on the `set() <https://cmake.org/cmake/help/latest/command/set.html>`_
command for more information on how fragment file entries are generated.

We do not support the *environment variable* variation of ``set()`` at this time.


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

from pathlib import Path
from pprint import pprint
import shlex

from configparserenhanced import *
from .SetProgramOptions import SetProgramOptions



# ==============================
#  F R E E   F U N C T I O N S
# ==============================



# ===============================
#   M A I N   C L A S S
# ===============================


class SetProgramOptionsCMake(SetProgramOptions):
    """Extends SetProgramOptions to add in CMake option support.

    - Adds a new **.ini** file command: ``opt-set-cmake-var``
      which can have the format: ``opt-set-cmake-var VARNAME [TYPE] : VALUE``
    - Adds a new back-end generator for ``cmake_fragment``
      files for the ``gen_option_list`` method.
    """
    def __init__(self, filename=None):
        if filename is not None:
            self.inifilepath = filename



    # -----------------------
    #   P R O P E R T I E S
    # -----------------------



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
        varname    = params[0]
        params     = params[1:4]
        param_opts = self._helper_cmake_set_entry_parser(params)

        params = [varname, value]

        if param_opts["TYPE"] is not None:
            params.append("CACHE")
            params.append(param_opts["TYPE"])
            params.append('"from .ini configuration"')
        if param_opts['PARENT_SCOPE']:
            params.append("PARENT_SCOPE")
        if param_opts['FORCE']:
            params.append("FORCE")

        output = "set({})".format(" ".join(params))

        return output


    def _program_option_handler_opt_set_cmake_var_bash(self, params, value) -> str:
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
        """
        varname = params[0]
        params  = params[1:4]

        param_opts = self._helper_cmake_set_entry_parser(params)

        params = ["-D", varname]
        if param_opts['TYPE'] is not None:
            params.append(":" + param_opts['TYPE'])

        return self._generic_program_option_handler_bash(params, value)



    # ---------------------------------------------------------------
    #   H A N D L E R S  -  C O N F I G P A R S E R E N H A N C E D
    # ---------------------------------------------------------------


    def _handler_opt_set_cmake_var(self, section_name, handler_parameters) -> int:
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


    def _helper_cmake_set_entry_parser(self, params: list):
        """
        Processes the list of parameters to detect the existence of
        flags for variables. This is consumed when generating option lists
        because the relevance of some options depends on the back-end
        generator. For example, ``PARENT_SCOPE`` is relevant to a ``cmake_fragment``
        generator but does not get used for a ``bash`` option that would be
        provided to the ``camke`` application on the command line.

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
        output = {'FORCE': False,
                  'PARENT_SCOPE': False,
                  'TYPE': None}
        for option in params[:4]:
            if option == "FORCE":
                output['FORCE'] = True
            elif option == "PARENT_SCOPE":
                output['PARENT_SCOPE'] = True
            elif option in ["BOOL", "FILEPATH", "PATH", "STRING", "INTERVAL"]:
                output['TYPE'] = option

        return output


