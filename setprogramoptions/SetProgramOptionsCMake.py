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
        """
        params = params[1:]
        params.insert(1, value)
        params.append( "CACHE" )
        output = "set({})".format(" ".join(params))
        return output


    def _program_option_handler_opt_set_cmake_cache_bash(self, params, value) -> str:
        """
        **bash** line-item generator for ``opt-set-cmake-cache`` entries when
        the *generator* is set to ``bash``.
        """
        if len(params) >= 3:
            params[2] = ":" + params[2]
        return self._generic_program_option_handler_bash(params,value)

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

        # Toss out extra 'params'
        params = params[:2]

        # prepend the ":" to the TYPE specifier if we have one.
        if len(params) == 2 and params[1] is not None:
            params[1] = str(params[1])

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


    # -----------------------
    #   H E L P E R S
    # -----------------------


