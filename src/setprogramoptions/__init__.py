#!/usr/bin/env python
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Init script for the SetProgramOptions package
"""
from .version import __version__

from .SetProgramOptions import SetProgramOptions
from .SetProgramOptionsCMake import SetProgramOptionsCMake

# Helpers and Free Functions
from .common import get_function_ref
