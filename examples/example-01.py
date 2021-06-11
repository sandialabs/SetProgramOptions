#!/usr/bin/env python3
import os
import sys

import setprogramoptions

filename = "example-01.ini"
popts = setprogramoptions.SetProgramOptions(filename)

section  = "MY_LS_COMMAND"
popts.parse_section(section)
bash_options = popts.gen_option_list(section, generator="bash")
print(" ".join(bash_options))

print("Done")
