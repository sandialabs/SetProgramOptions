<!-- Github Badges -->
[![SetProgramOptions Testing](https://github.com/sandialabs/SetProgramOptions/actions/workflows/test-driver-core.yml/badge.svg)](https://github.com/sandialabs/SetProgramOptions/actions/workflows/test-driver-core.yml)
[![Documentation Status](https://readthedocs.org/projects/setprogramoptions/badge/?version=latest)](https://setprogramoptions.readthedocs.io/en/latest/?badge=latest)


SetProgramOptions
=================
The `SetProgramOptions` package extends [`ConfigParserEnhanced`][2] to enable the processing
of **.ini** files that specify *Program Options*.

`SetProgramOptions` supports all the _operations_ that [`ConfigParserEnhanced`][2] supports
and adds some of its own.

| Operation    | Format                                        | Defined By                  |
| ------------ | --------------------------------------------- | --------------------------- |
| `use`        | `use <section>`                               | [`ConfigParserEnhanced`][2] |
| `opt-set`    | `opt-set Param1 [Param2..ParamN] [: <VALUE>]` | `SetProgramOptions`         |
| `opt-remove` | `opt-remove Param [SUBSTR]`                   | `SetProgramOptions`         |


INI File Format
---------------
A **.ini** file that can be processed by `SetProgramOptions` can be formatted like this:
```ini
[COMMAND_LS]
opt-set ls
```
This is perhaps the most simple thing we could do. Using `gen_option_list('COMMAND_LS', generator="bash")`
would generate the command `ls` from this.

A more complex section which creates a CMake command call might look like this:
```ini
[COMMAND_CMAKE]
opt-set cmake
opt-set -G : Ninja
opt-set -D CMAKE_CXX_FLAGS : "-O3"
```
and this would generate the command `cmake -G=Ninja -DCMAKE_CXX_FLAGS="-O3"` when processed for _bash_ output.

We can further epxand the CMake example with multiple sections, such as:

```ini
[CMAKE_COMMAND]
opt-set cmake
opt-set -G : Ninja

[CMAKE_OPTIONS_COMMON]
opt-set -D CMAKE_CXX_FLAGS : "-fopenmp"

[CMAKE_OPTIONS_APPLICATION]
opt-set -D MYAPP_FLAG1 : "foo"
opt-set -D MYAPP_FLAG2 : "bar"

[APPLICATION_PATH_TO_SOURCE]
opt-set /path/to/source/.

[APPLICATION_CMAKE_PROFILE_01]
use CMAKE_COMMAND
use CMAKE_OPTIONS_COMMON
use CMAKE_OPTIONS_APPLICATION
use APPLICATION_PATH_TO_SOURCE

[APPLICATION_CMAKE_PROFILE_02]
use APPLICATION_PROFILE_01
opt-remove MYAPP_FLAG2
```
This example is fairly simple but follows a pattern that larger projects might wish to follow when there
are many configurations that may be getting tested. In this case we set up some common option groups and
then create aggregation sections that will include the other sections to compose a full command line.

If we generate _bash_ output for `APPLICATION_CMAKE_PROFILE_01` we'll get
`cmake -G=Ninja -DCMAKE_CXX_FLAGS="-fopenmp" -DMYAPP_FLAG1="foo" -DMYAPP_FLAG2="bar" /path/to/source/.`

Generating _bash_ output for `APPLICATION_CMAKE_PROFILE_02` clones `APPLICATION_CMAKE_PROFILE_01` and then
_removes_ any entry containing the parameter `MYAPP_FLAG2`. This will result in a generated comand
`cmake -G=Ninja -DCMAKE_CXX_FLAGS="-fopenmp" -DMYAPP_FLAG1="foo" /path/to/source/.`.

Hopefully, this example shows some of the capabilities that `SetProgramOptions` provides for managing
many build configurations within a single .ini file.


### Variable Expansion within VALUE fields
Variables can be added to the VALUE fields in handled instructions, but they have their
own format that must be used:
```
${VARNAME|VARTYPE}
```
- `VARNAME` is the variable name that you might expect for a bash style environment variable
  that might be defined like this: `export VARNAME=VALUE`.
- `VARTYPE` is the **type** of the variable that is being declared. For `SetProgramOptions`
  the only recognized type is `ENV` which defines _environment variables_. Subclasses such
  as `SetProgramOptionsCMake` define their own types.

We do not provide a **default** type for this because we wish it to be _explicit_ that this
is a pseudo-type and do not want it to be confused with some specific variable type since that
meaning can change depending on the kind of generator being used. For example, `${VARNAME}`
is an _environment variable_ within a bash context but in a CMake fragment file it would be
an _internal CMake variable_ and `$ENV{VARNAME}` would be an _environment variable_.
By not providing a default we force type consideration to be made explicitly during the creation
of the .ini file.


Operations Explained
--------------------

### `use`
The `use` operation is provided by [`ConfigParserEnhanced`][2]. Please see its documentation on this command and its use.

### `opt-set`
Sets a generic _command line_ style option.

The format of this is `opt-set Param1 [Param2] [Param3] ... [ParamN] : [VALUE]`

In a _bash_ context, this operation attempts to generate an option for some command that will be executed.
`SetProgramOptions` will concactenate the _Params_ together and then append `=VALUE` if a VALUE field is present.
For example, `opt-set Foo Bar : Baz` will become `FooBar=Baz`.


### `opt-remove`
_Removes_ existing entries that have been processed up to the point the `opt-remove` is encountered that match a pattern.

The format of this is `opt-remove Param [SUBSTR]`

When a _remove_ is encountered, `SetProgramOptions` will search through all processed options and will delete any
that contain any _Param-i_ that matches `Param`. By default the parameters much be an _exact match_ of `Param`, but
if the optional `SUBSTR` parameter is provided then `SetProgramOptions` will treat `Param` as a substring and will
remove all existing options if _any parameter contains Param_.


SetProgramOptions Examples
--------------------------

### [example-01.ini](examples/example-01.ini)
```ini
[BASH_VERSION]
opt-set bash
opt-set --version

[LS_COMMAND]
opt-set ls

[LS_LIST_TIME_REVERSED]
opt-set "-l -t -r"

[LS_CUSTOM_TIME_STYLE]
opt-set --time-style : "+%Y-%m-%d %H:%M:%S"

[MY_LS_COMMAND]
use LS_COMMAND
use LS_LIST_TIME_REVERSED
use LS_CUSTOM_TIME_STYLE
```

### [example-01.py](examples/example-01.py)

```python
#!/usr/bin/env python3
import setprogramoptions

filename = "example-01.ini"
section  = "MY_LS_COMMAND"

# Create SetProgramOptions instance
popts = setprogramoptions.SetProgramOptions(filename)

# Parse section
popts.parse_section(section)

# Generate the list of bash options for the command
bash_options = popts.gen_option_list(section, generator="bash")

# Print out the commands
print(" ".join(bash_options))
```

generates the output:

```bash
ls -l -t -r --time-style="+%Y-%m-%d %H:%M:%S"
```

SetProgramOptionsCMake
======================
`SetProgramOptionsCMake` is a subclass of `SetProgramOptions` that adds additional additional
operations and generators to handle processing CMake options:
- Adds `opt-set-cmake-var`.
- Adds `cmake_fragment` generator.
- Adds `CMAKE` type to variables.

New operations defined in `SetProgramOptionsCMake`:

| Operation           | Format                                                           | Defined By               |
| ------------------- | ---------------------------------------------------------------- | ------------------------ |
| `opt-set-cmake-var` | `opt-set-cmake-var VARNAME [TYPE] [FORCE] [PARENT_SCOPE]: VALUE` | `SetProgramOptionsCMake` |


INI File Format
---------------
A **.ini** file that can be processed by `SetProgramOptions` can be formatted like this:
```ini
[SECTION_A]
opt-set cmake
opt-set-cmake-var MYVARIABLENAME  : VALUE
opt-set-cmake-var MYVARIABLENAME2 PARENT_SCOPE : VALUE
```

### Variable Expansion for CMake Variables
`SetProgramOptionsCMake` extends the variable expansion options provided by `SetProgramOptions` by adding a new _vartype_: `CMAKE`
which designates a variable as a "CMake variable":
```
${VARNAME|CMAKE}
```
A _CMake variable_ in this context would be an _internal variable_ that is known to CMake.
Because this is not a variable that would be known outside of the context of `.cmake` files, this kind of
variable is only applicable when generating CMake fragment files.

It is necessary to provide a CMake variant for variable expansions because the CMake syntax for variables is different than
that used by Bash. In CMake fragment files:
- environment variables are written as `$ENV{VARNAME}`
- internal CMake variables are written as: `${VARNAME}`

We can attempt to still allow these to be used if generating _bash_ output but only if it can be resolved to something that
is known to the calling environment (i.e., either a string or an environment variable). In this case, we cache the _known_ values
of the VARAIBLE as we process the .ini file and perform substitutions with the _last known value_. An exception should be thrown
if the generator encounteres an _unhandled_ CMake variable when generating _bash_ output.

For example, to append `-fopenmp` to the `CMAKE_CXX_FLAGS` variable is something one might wish to do:
```ini
opt-set-cmake-var CMAKE_CXX_FLAGS : "${CMAKE_CXX_FLAGS|CMAKE} -fopenmp"
```
which is perfectly fine if we're generating a CMake fragment file:
```cmake
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp")
```
but if the generator is Bash, it has no idea what to put in the `-D` option... we can't use `${CMAKE_CXX_FLAGS}` because
bash will think this is an _environment variable_. In this case, if `CMAKE_CXX_FLAGS` had already been set to something
known then we can handle it. For example:
```ini
[COMMON_FLAGS]
opt-set-cmake-var CMAKE_CXX_FLAGS FORCE : "-O0 -g"
# ... many lines later ...
[SOME_CONFIGURATION]
use COMMON_FLAGS
opt-set-cmake-var CMAKE_CXX_FLAGS FORCE : "${CMAKE_CXX_FLAGS|CMAKE} -fopenmp"
```
might generate this _cmake fragment_:
```cmake
set(CMAKE_CXX_FLAGS "-O0 -g" FORCE)
set(CMAKE_CXX_FLAGS "-O0 -g -fopenmp" FORCE)
```
or _bash_ options:
```bash
-DCMAKE_CXX_FLAGS="-O0 -g"
-DCMAKE_CXX_FLAGS="-O0 -g -fopenmp"
```
We currently don't try and disambiguate these options internally within `SetProgramOptions`. This is something that is
left up to the application using the tool. The reason is that in our testing it appears that the _last value wins_ for
_bash_ commands... but within a CMake script there could be some command that uses the intermediate value of this variable
and we don't currently perform any sort of use-def chain tracking. In the future, we may add some use-def awareness that could
allow some optimization here.


Operations Explained
--------------------
### `opt-set-cmake-var`
This adds a CMake variable program option. These have a special syntax in _bash_ that looks like `-DVARNAME:TYPE=VALUE` where the `:TYPE`
is an optional parameter. If the *type* is left out then CMake assumes the value is a _STRING_.

We may not wish to generate bash only output though. For CMake files, we might wish to generate a _cmake fragment_ file which is
basically a snippet of CMake that can be loaded during a CMake call using the `-S` option: `cmake -S cmake_fragment.cmake`. The
syntax within a CMake fragment file is the same as in a CMake script itself.

If the back-end generator is creating a CMake fragment file, the _set_ command generated will use [CMake set syntax].
This looks something like `set(<variable> <value>)` but can also contain additional options. These extra options can
be provided in the `opt-set-cmake-var` operation in the .ini file:

- `FORCE` -
    - By default, a `set()` operation does not overwrite entries in a CMake file. This can be added to
      _force_ the value to be saved.
    - This is only applicable to generating _cmake fragment_ files.
- `PARENT_SCOPE` - If provided, this option instructs CMake to set the variable in the scope that is above the current scope.
    - This is only applicable to generating _cmake fragment_ files.
- `TYPE` - Specifies the _TYPE_ the variable can be.
    - This is a _positional_ argument and must always come after _VARNAME_.
    - Valid options for this are `STRING` (default), `BOOL`, `PATH`, `INTERNAL`, `FILEPATH`.
    - Adding a _TYPE_ option implies that the _CACHE_ and _docstring_ parameters will be added to a `set()` command
      in a CMake fragment file according to the syntax: `set(<variable> <value> CACHE <type> <docstring> [FORCE])`
      as illustrated on the [CMake `set()` documentation][1].
    - This is applicable to both _cmake fragment_ and _bash_ generation.


SetProgramOptionsCMake Examples
-------------------------------

### Example 02

**example-02.ini**
```ini
#
# example-02.ini
#
[CMAKE_COMMAND]
opt-set cmake

[CMAKE_GENERATOR_NINJA]
opt-set -G : Ninja

[CMAKE_GENERATOR_MAKEFILES]
opt-set -G : "Unix Makefiles"

[MYPROJ_OPTIONS]
opt-set-cmake-var  MYPROJ_CXX_FLAGS       STRING       : "-O0 -fopenmp"
opt-set-cmake-var  MYPROJ_ENABLE_OPTION_A BOOL   FORCE : ON
opt-set-cmake-var  MYPROJ_ENABLE_OPTION_B BOOL         : ON

[MYPROJ_SOURCE_DIR]
opt-set /path/to/source/dir

[MYPROJ_CONFIGURATION_NINJA]
use CMAKE_COMMAND
use CMAKE_GENERATOR_NINJA
use MYPROJ_OPTIONS
use MYPROJ_SOURCE_DIR

[MYPROJ_CONFIGURATION_MAKEFILES]
use CMAKE_COMMAND
use CMAKE_GENERATOR_MAKEFILES
use MYPROJ_OPTIONS
use MYPROJ_SOURCE_DIR
```

**example-02.py**
```python
#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
from pathlib import Path
import setprogramoptions

print(80*"-")
print(f"- {Path(__file__).name}")
print(80*"-")


filename = "example-02.ini"
popts = setprogramoptions.SetProgramOptionsCMake(filename)

section = "MYPROJ_CONFIGURATION_NINJA"
popts.parse_section(section)

# Generate BASH output
print("")
print("Bash output")
print("-----------")
bash_options = popts.gen_option_list(section, generator="bash")
print(" \\\n   ".join(bash_options))

# Generate a CMake Fragment
print("")
print("CMake fragment output")
print("---------------------")
cmake_options = popts.gen_option_list(section, generator="cmake_fragment")
print("\n".join(cmake_options))

print("\nDone")
```
Generates the output:
```bash
$ python3 example-02.py
--------------------------------------------------------------------------------
- example-02.py
--------------------------------------------------------------------------------

**Bash output**
cmake \
   -G=Ninja \
   -DMYPROJ_CXX_FLAGS:STRING="-O0 -fopenmp" \
   -DMYPROJ_ENABLE_OPTION_A:BOOL=ON \
   -DMYPROJ_ENABLE_OPTION_B:BOOL=ON \
   /path/to/source/dir

CMake fragment output
---------------------
set(MYPROJ_CXX_FLAGS "-O0 -fopenmp" CACHE STRING "from .ini configuration")
set(MYPROJ_ENABLE_OPTION_A ON CACHE BOOL "from .ini configuration" FORCE)
set(MYPROJ_ENABLE_OPTION_B ON CACHE BOOL "from .ini configuration")

Done
```

[1]: https://cmake.org/cmake/help/latest/command/set.html
[2]: https://github.com/sandialabs/ConfigParserEnhanced
[3]: https://github.com/sandialabs/SetProgramOptions/blob/master/CHANGELOG.md
[4]: https://setprogramoptions.readthedocs.io/en/latest/

