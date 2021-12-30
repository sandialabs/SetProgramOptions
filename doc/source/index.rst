.. SetProgramOptions documentation master file, created by
   sphinx-quickstart on Wed Jan 13 15:30:46 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SetProgramOptions Python Module
===============================

.. toctree::
   :maxdepth: 1
   :caption: Table of Contents:

   SetProgramOptions
   SetProgramOptionsCMake
   License <License>



Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Overview
========
The ``SetProgramOptions`` package extends the
`ConfigParserEnhanced <https://pypi.org/project/configparserenhanced/>`_
package by adding additional *operations* for handling command-line
options.

The primary use case that provided the impetus to develop SetProgramOptions
was to support complex configuration environments for a software project that
is tested on a variety of platforms and architectures, including GPUs and HPC
systems. This project is several million lines of code and has hundreds of
CMake options in its configuration space.

We developed SetProgramOptions and SetProgramOptions to allow our build system
to use optimized .ini files to manage our configuration space.

This package includes two classes:

1. SetProgramOptions - A general purpose command line handler that handles
   generic command line options.
2. SetProgramOptionsCMake - A subclass of SetProgramOptions, this class further
   extends SetProgramOptions by adding CMake-specific operations to provide
   ease of use for CMake specific options. It also adds an additional generator
   option to allow the generation of either *bash* style command line options
   or a *CMake* source fragment file.

An example .ini file using ``SetProgramOptions`` might look like:

.. code-block:: ini
    :linenos:

    [Directory *nix]
    opt-set ls

This configuration is the SetProgramOptions version of a hello world example.
Here, the ``opt-set ls`` option is specifying a single command line option
which in this case is the command `ls`.

We can expand this to add additional entries:

.. code-block:: ini
    :linenos:

    [Directory *nix]
    opt-set ls
    opt-set -l
    opt-set -r
    opt-set -t
    opt-remove -r

When processed, this example would result in a concactenated string containing
the command ``ls -l -t``. We threw in the ``opt-remove -r`` operation which
*removed* the `-r` entry.

For more details on how this is used, see the Examples section below.


Examples
========
Here we show a few examples of how ``SetProgramOptions`` and
``SetProgramOptionsCMake`` can be used.

Example 1
---------
In example-01 we have a fairly simple .ini file that demostrates utilization
of the ``use`` operation that comes built in with
`ConfigParserEnhanced <https://pypi.org/project/configparserenhanced/>`_.
In this example we are going to demonstrate how the ``opt-set`` operations
in our .ini file can be used to generate a custom bash command with
customizable argument sets added.

In this case, we will process the ``[MY_LS_COMMAND]`` section to generate
a bash command that would generate a directory listing in list form by
reverse time order of last modified with a custom timestamp format.

While this example is quite simple we can see how a complex environment
in a DevOps setting might use this to bundle "common" operations to reduce
the amount of copying and pasting that is used.

example-01.ini
++++++++++++++
.. literalinclude:: ../../examples/example-01.ini
    :language: ini
    :linenos:

example-01.py
+++++++++++++
.. literalinclude:: ../../examples/example-01.py
    :language: python
    :linenos:

Console Output
++++++++++++++
.. literalinclude:: ../../examples/example-01.log
    :language: text
    :linenos:

Example 2
---------
Example 2 demonstrates the use of ``SetProgramOptionsCMake``
which is a *subclass* of ``SetProgramOptions`` and implements
*operations* for handling *CMake* variables in a .ini file.
SetProgramOptionsCMake also introduces a new "CMake fragment"
generator and implements logic to maintain consistency of
behavior between generated BASH scripts and CMake fragments
with knoweldge of how CMake treats ``-D`` operations at the
command line versus ``set()`` operations inside a CMake script.

Here we show the new operation ``opt-set-cmake-var`` which
has the form ``opt-set-cmake-var VARNAME <OPTIONAL PARAMS> : VALUE``.
Details and a comprehensive list of the optional parameters can
be found in the ``SetProgramOptionsCMake`` Class Reference page.

The main elements this example will demonstrate is how to use
``opt-set-cmake-var`` operations and how they can be used.

This example is fairly straightforward since the .ini file
options being defined will generate the same output for both
generator types.

example-02.ini
++++++++++++++
.. literalinclude:: ../../examples/example-02.ini
    :language: ini
    :linenos:

example-02.py
+++++++++++++
.. literalinclude:: ../../examples/example-02.py
    :language: python
    :linenos:

Console Output
++++++++++++++
.. literalinclude:: ../../examples/example-02.log
    :language: text
    :linenos:



Example 3
---------
The last example we show here is a bit more complicated and gets into
some of the differences in how CMake treats a *command line* variable
being set via a ``-D`` option versus a ``set()`` operation within a
CMakeLists.txt file.

The script prints out a notice explaining the nuance but the general
idea is that CMake treats options provided by a ``-D`` option at the
command line as though they are ``CACHE`` variables with the ``FORCE``
option enabled. This is designed to allow command-line parameters to
generally take precedence over what a CMakeLists.txt file might set
as though it's a user-override. The added ``FORCE`` option also ensures
that if there are multiple ``-D`` options setting the same variable the
*last* one will win.

This can have a subtle yet profound effect on how we must process our
``opt-set-cmake-var`` operations within a .ini file if our goal is to
ensure that the resulting ``CMakeCache.txt`` file generated by a CMake
run would be the same for both *bash* and *cmake fragment* generators.

In this case, in order to have a variable be set by the *bash* generator
it must be a ``CACHE`` variable -- which can be accomplished by either
adding a *TYPE* or a *FORCE* option.
We will note here that if ``FORCE`` is given without a *TYPE* then we
use the default type of *STRING*.

If the *same* CMake variable is being assigned, such as in a case where
we have a section that is updating a flag, then the `FORCE` option must
be present on the second and all subsequent occurrences of ``opt-set-cmake-var``
or the *bash* generator will skip over that assignment since a non-forced
``set()`` operation in CMake would not overwrite an existing cache var.
This situation can occur frequently if our .ini file(s) are structured to
have some *common* configuration option set and then a specialization which
updates one of the arguments. One example of this kind of situation might
be where we have a specialization that adds OpenMP and we would want to add
the ``-fopenmp`` flags to our linker flags.

example-03.ini
++++++++++++++
.. literalinclude:: ../../examples/example-03.ini
    :language: ini
    :linenos:

example-03.py
+++++++++++++
.. literalinclude:: ../../examples/example-03.py
    :language: python
    :linenos:

Console Output
++++++++++++++
.. literalinclude:: ../../examples/example-03.log
    :language: text
    :linenos:

We will note here that the *CMake* fragment generator will still generate
all of the commands. In this case the second ``set()`` command would be ignored
by CMake since it's not FORCEd but the main take-away here is that the
*bash* generator omitted the second ``-D`` operation since that would be
a ``FORCE`` operation by default which is not representative of what was
specified in the .ini file.



