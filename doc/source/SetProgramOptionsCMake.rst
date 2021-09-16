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

``opt-set-cmake-var``
+++++++++++++++++++++
**Usage**: ``opt-set-cmake-var <varname> [TYPE] [PARENT_SCOPE] [FORCE] : <value>``

A CMake variable set operation. This can be used to genrate bash command line options
of the form ``-D<varname>[:<type>]=<value>`` or in a CMake fragment we may generate
a ``set()`` command.

For information related to CMake Fragment generation of ``set()`` commands, see
the `CMake docs <https://cmake.org/cmake/help/latest/command/set.html#command:set>`_ .

``PARENT_SCOPE`` and ``FORCE`` are mutually exclusive options and will result in an
error being thrown.

An additional thing to note is that ``PARENT_SCOPE`` should not be used with ``CACHE``
variables (i.e., *typed* variables). CMake will happily process this but you will likely
get a result that you do not want. In a CMake fragment file:

.. code-block:: cmake
  :linenos:

  set(FOO FOO_VALUE CACHE STRING "my docstring" PARENT_SCOPE)

Will result in the value of ``FOO`` being set to ``FOO_VALUE;CACHE;STRING;my docstring``
which is unlikely to match expectations, but that is what CMake will do. In this case,
``SetProgramOptionsCMake`` will raise a warning and will generate a string to match what
CMake generates when sent to a bash options generator
(i.e., ``-DFOO="FOO_VALUE;CACHE;STRING;my docstring"``).
When sent through the *cmake fragment* generator the output will be the equivalent ``set()``
call.


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
.. automethod:: setprogramoptions.SetProgramOptionsCMake.handler_initialize
.. automethod:: setprogramoptions.SetProgramOptionsCMake._handler_opt_set_cmake_var


Helpers
~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptionsCMake._helper_opt_set_cmake_var_parse_parameters


Program Option Handlers
~~~~~~~~~~~~~~~~~~~~~~~
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_fragment
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_var_cmake_fragment
.. automethod:: setprogramoptions.SetProgramOptionsCMake._program_option_handler_opt_set_cmake_var_bash





