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
from .SetProgramOptions import SetProgramOptions



# ==============================
#  F R E E   F U N C T I O N S
# ==============================



# ===============================
#   M A I N   C L A S S
# ===============================


class SetProgramOptionsCMake(SetProgramOptions):
    """Extends SetProgramOptions to add in CMake option support.

    - Adds a new **.ini** file command: ``opt-set-cmake-cache``
      which can have the format: ``opt-set-cmake-cache VARNAME [TYPE] : VALUE``
    - Adds a new back-end generator for ``cmake_fragment``
      files for the ``gen_option_list`` method.


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

        Including this function prevents an ``exception_control_event`` WARNING
        from being generated in ``SetProgramOptions``.

        This method is essentially a noop but we can keep it in case someone ever
        turns ``exception_control_level`` to max. This is because if this function
        isn't defined a "SILENT" ``exception_control_event`` will get tripped in
        ``SetProgramOptions``. Normally this would just pass on by but since SILENT
        events are treated as WARNINGS with respect to raising an exception, removing
        this would trigger an exception when ecl is 5.

        That said, keeping this method around could still be seen as *optional* in
        that removing it will not affect application behaviour under *normal* use.

        Args:
            params (list): The list of parameter entries extracted from the
                .ini line item.
            value (str): The value portion from the .ini line item.

        Returns:
            None
        """
        return None


    def _program_option_handler_opt_set_cmake_cache_cmake_fragment(self,
                                                                  params: list,
                                                                  value: str) -> str:
        """
        **cmake fragment** line-item generator for ``opt-set-cmake-cache`` entries when
        the *generator* is set to ``cmake_fragment``.

        This method prepares a ``set(<variable> <value> [CACHE <type> <docstring>])`` entry

        Valid formats for a ``set`` command are:

        - ``set(<variable> <value>)``
        - ``set(<variable> <value> CACHE <type> <docstring>)``


        Note:
            It's ok to modify ``params`` and ``value`` here without concern of
            side-effects since ``_gen_option_entry()`` in ``SetProgramOptions``
            performs a deep-copy of these parameters prior to calling this.
            Any changes we make are ephemeral.
        """
        params.insert(1, value)
        if len(params) > 2:
            params.insert(2, "CACHE")
            params.append('""')

        output = "set({})".format(" ".join(params))
        return output


    def _program_option_handler_opt_set_cmake_cache_bash(self, params, value) -> str:
        """
        **bash** line-item generator for ``opt-set-cmake-cache`` entries when
        the *generator* is set to ``bash``.

        Note:
            It's ok to modify ``params`` and ``value`` here without concern of
            side-effects since ``_gen_option_entry()`` in ``SetProgramOptions``
            performs a deep-copy of these parameters prior to calling this.
            Any changes we make are ephemeral.
        """
        params = ["-D"] + params
        if len(params) >= 3:
            params[2] = ":" + params[2]
        return self._generic_program_option_handler_bash(params, value)


    # ---------------------------------------------------------------
    #   H A N D L E R S  -  C O N F I G P A R S E R E N H A N C E D
    # ---------------------------------------------------------------


    def _handler_opt_set_cmake_cache(self, section_name, handler_parameters) -> int:
        """Handler for ``opt-set-cmake-cache``

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

        # Toss out any extra 'params'
        params = params[:2]

        entry = {'type': [op], 'value': value, 'params': params }

        data_shared_ref.append(entry)
        # -----[ Handler Content End ]---------------------

        self.exit_handler(handler_parameters)
        return 0


    # ---------------------------------
    #   H A N D L E R   H E L P E R S
    # ---------------------------------


    # -----------------------
    #   H E L P E R S
    # -----------------------


