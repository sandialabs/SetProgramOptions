SetProgramOptionsCMake Class Reference
======================================

The SetProgramOptionsCMake module is an extension of :py:class:`setprogramoptions.SetProgramOptions`
which adds handling for CMake specific properties.

SetProgramOptionsCMake also adds an additional ``generator`` type,
``cmake_fragment``, to the :py:meth:`setprogramoptions.SetProgramOptions.gen_option_list`
method, enabling the ability to generate CMake fragment files.

Supported .ini File Operations
------------------------------
.. csv-table:: Supported Operations
    :file: tbl_setprogramoptionscmake_commands.csv
    :header-rows: 1
    :widths: 20,30,80


Useful Links
------------
- `Sphinx docstrings reference <https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html>`_
- `Google docstrings reference <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html>`_
- `CMake set() reference <https://cmake.org/cmake/help/latest/command/set.html>`_


API Documentation
-----------------
.. automodule:: setprogramoptions.SetProgramOptionsCMake
   :no-members:


Public API
++++++++++
.. autoclass:: setprogramoptions.SetProgramOptionsCMake
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :exclude-members:
      handler_finalize,
      handler_initialize


Private API
+++++++++++


Handlers
~~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptionsCMake._handler_opt_set_cmake_var


Handler Helpers
~~~~~~~~~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptionsCMake._helper_cmake_set_entry_parser


Program Option Handlers
~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_fragment
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_var_cmake_fragment
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_var_bash





