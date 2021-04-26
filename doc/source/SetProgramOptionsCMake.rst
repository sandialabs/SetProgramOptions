SetProgramOptionsCMake Class Reference
======================================

The SetProgramOptionsCMake module is an extension of ``setprogramoptions.SetProgramOptions``
which adds special command line option handling for CMake options and adds a new back-end
generator for CMake "fragment" files.

API Documentation
-----------------
.. automodule:: setprogramoptions.SetProgramOptionsCMake
   :no-members:

Public Methods
++++++++++++++
.. autoclass:: setprogramoptions.SetProgramOptionsCMake
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :exclude-members:
      handler_finalize,
      handler_initialize

Private Methods
+++++++++++++++
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_fragment
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_cache_cmake_fragment
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_cache_bash
.. automethod:: setprogramoptions.SetProgramOptionsCMake._handler_opt_set_cmake_cache
.. automethod:: setprogramoptions.SetProgramOptionsCMake._helper_cmake_set_entry_parser



