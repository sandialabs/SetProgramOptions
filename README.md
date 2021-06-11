[![pipeline status](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/SetProgramOptions/badges/master/pipeline.svg)](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/SetProgramOptions/-/commits/master)
[![coverage report](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/SetProgramOptions/badges/master/coverage.svg)](http://10.202.35.89:8080/SetProgramOptions/coverage/index.html)
[![Generic badge](https://img.shields.io/badge/docs-latest-green.svg)](http://10.202.35.89:8080/SetProgramOptions/doc/index.html)

SetProgramOptions
=================
The `SetProgramOptions` package extends `ConfigParserEnhanced` to enable the processing
of **.ini** files that specify *Program Options*.

`SetProgramOptions` supports all the _operations_ that `ConfigParserEnhanced` supports
and adds some of its own.

| Operation    | Format                                        | Defined By             |
| ------------ | --------------------------------------------- | ---------------------- |
| `use`        | `use <section>`                               | `ConfigParserEnhanced` |
| `opt-set`    | `opt-set Param1 [Param2..ParamN] [: <VALUE>]` | `SetProgramOptions`    |
| `opt-remove` | `opt-remove Param [SUBSTR]`                    | `SetProgramOptions`    |


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

We can further exand the CMake example with multiple sections, such as:

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
this example is fairly simple but follows a pattern that larger projects might wish to follow when there
are many configurations that may be getting tested. In this case we set up some common option groups and
then create aggregation sections that will include the other sectiosn to compose a full command line.

If we generate _bash_ output for `APPLICATION_CMAKE_PROFILE_01` we'll get
`cmake -G=Ninja -DCMAKE_CXX_FLAGS="-fopenmp" -DMYAPP_FLAG1="foo" -DMYAPP_FLAG2="bar" /path/to/source/.`

Generating _bash_ output for `APPLICATION_CMAKE_PROFILE_02` clones `APPLICATION_CMAKE_PROFILE_01` and then
_removes_ any entry containing the parameter `MYAPP_FLAG2`. This will result in a generated comand
`cmake -G=Ninja -DCMAKE_CXX_FLAGS="-fopenmp" -DMYAPP_FLAG1="foo" /path/to/source/.`.

Hopefully, this example shows some of the capabilities that `SetProgramOptions` provides for managing
many build configurations within a single *.ini* file.


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
is a pseudo-type and do not with it to be confused with some specific variable type since that
meaning can change depending on the kind of generator being used. For example, `${VARNAME}`
is an _environment variable_ within a bash context but in a CMake fragment file it would be
an _internal cmake variable_ and `$ENV{VARNAME}` would be an _environment variable_.
By not providing a default we force type consideration to be made explicitly during the creation
of the .ini file.


Operations Explained
--------------------

### `use`
The `use` operation is provided by `ConfigParserEnhanced`. Please see its documentation on this command and its use.

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
if the optional `SUBSTR` parameter is provided then `SetProgramOptions` will treat `Param` as a substing and will
remove all existing options if _any parameter contains Param_.


SetProgramOptions Examples
--------------------------

### `Example-01.ini`
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

### `Example-01.py`

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
- Adds `opt-set-cmake-var`
- Adds `cmake_fragment` generator
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

TOOD: FINISH THIS README!
```


Operations Explained
--------------------


### `opt-set-cmake-var`
TODO


SetProgramOptionsCMake Examples
-------------------------------
TODO

