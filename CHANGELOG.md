Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [X.Y.Z] - YYYY-MM-DD or [Unreleased]
#### Added
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Internal
#### Todo (for Unreleased)
-->

## [0.3.1] <!-- YYYY-MM-DD --> [Unreleased]
#### Added
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Internal
- Changed `VariableFieldData` so that it won't use `dataclasses` to keep our
  Python compatibilty to 3.6 (`dataclasses` requires 3.7 and higher).
#### Todo (for Unreleased)


## [0.3.0] - 2021-06-15
#### Added
#### Changed
- Relocated `setprogramoptions` package to `src/`
- Relocated _examples_ into `examples/` directory.
- Improved `gitlab-ci.yml` pipeline.
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Internal
#### Todo (for Unreleased)



## [0.2.0] - 2021-06-08
#### Added
- `common.py` - moved some free-functions to this.
- Improved *variable* processing. Variables should now be encoded in our pseudo-langauge
  that has a syntax like this: `${VARNAME|VARTYPE}`.
  - `ENV` - is the only 'type' that is known to `SetProgramOptions`
  - `CMAKE` - is known to `SetProgramOptionsCMake`, which denotes a "CMake" variable
    which would be part of the internal state. This mostly makes sense when generating
    CMake Fragments, but we also attempt to track variables that are set when generating
    BASH output and will perform expansions when a prevoulsly set value is known.
  - A `ValueError` will be raised if "BASH" output generation is attempted with a "CMAKE"
    var type still embedded in the .ini file.
#### Changed
- _values_ containing spaces in them will have double quotes (`"`) added to them.
#### Internal
- Modified `_gen_option_entry` to detect values with spaces in them and add quotes (`"`) to the string.



## [0.1.0] - 2021-04-29
#### Added
- Initial version release. From now on changes should be noted in the
  CHANGELOG.


