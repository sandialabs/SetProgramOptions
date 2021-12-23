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
