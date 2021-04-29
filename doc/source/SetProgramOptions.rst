SetProgramOptions Class Reference
=================================

The SetProgramOptions module is an extension of ``configparserenhanced.ConfigParserEnhanced``
which implements handlers for *environment variable* and *environment modules* rules in
a .ini file.

Supported .ini File Operations
------------------------------
.. csv-table:: Supported Operations
    :file: tbl_setprogramoptions_commands.csv
    :header-rows: 1
    :widths: 20,30,80


API Documentation
-----------------
.. automodule:: setprogramoptions.SetProgramOptions
   :no-members:


Public API
++++++++++
.. autoclass:: setprogramoptions.SetProgramOptions
   :noindex:
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :exclude-members:
      handler_finalize,
      handler_initialize

.. autoproperty:: setprogramoptions.SetProgramOptions.options


Private API
+++++++++++

Properties
~~~~~~~~~~
.. autoproperty:: setprogramoptions.SetProgramOptions._data_shared_key


Handlers
~~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptions._handler_opt_set
.. automethod:: setprogramoptions.SetProgramOptions._handler_opt_remove
.. automethod:: setprogramoptions.SetProgramOptions.handler_initialize
.. automethod:: setprogramoptions.SetProgramOptions.handler_finalize
.. automethod:: setprogramoptions.SetProgramOptions._initialize_handler_parameters


Handler Helpers
~~~~~~~~~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptions._option_handler_helper_add
.. automethod:: setprogramoptions.SetProgramOptions._option_handler_helper_remove


Program Option Handlers
~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptions._program_option_handler_opt_set_bash
.. automethod:: setprogramoptions.SetProgramOptions._generic_program_option_handler_bash

.. automethod:: setprogramoptions.SetProgramOptions._gen_option_entry



