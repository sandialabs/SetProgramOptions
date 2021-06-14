#!/usr/bin/env python3
import os
import sys

import setprogramoptions

filename = "example-02.ini"
popts = setprogramoptions.SetProgramOptionsCMake(filename)

section  = "MYPROJ_CONFIGURATION_NINJA"
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

