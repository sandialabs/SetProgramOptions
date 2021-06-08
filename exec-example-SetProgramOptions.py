#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Example app for SetProgramOptions
"""
from __future__ import print_function  # python 2 -> 3 compatiblity

import os
from pprint import pprint
import re

import setprogramoptions



def find_config_ini(filename="config.ini", rootpath="." ):
    """
    Recursively searches for a particular file among the subdirectory structure.
    If we find it, then we return the full relative path to `pwd` to that file.

    The _first_ match will be returned.

    Args:
        filename (str): The _filename_ of the file we're searching for. Default: 'config.ini'
        rootpath (str): The _root_ path where we will begin our search from. Default: '.'

    Returns:
        String containing the path to the file if it was found. If a matching filename is not
        found then `None` is returned.

    """
    output = None
    for dirpath,dirnames,filename_list in os.walk(rootpath):
        if filename in filename_list:
            output = os.path.join(dirpath, filename)
            break
    if output is None:
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd()))  # pragma: no cover
    return output



def test_setprogramoptions(filename="config.ini"):
    print("filename    : {}".format(filename))
    print("")

    parser = setprogramoptions.SetProgramOptionsCMake(filename=filename)
    parser.debug_level = 5
    parser.exception_control_level = 4
    parser.exception_control_compact_warnings = True

    # pre-parse all sections
    # parser.parse_all_sections()

    #section_name = "TEST_CONFIGURATION_A"
    #section_name = "TEST_CONFIGURATION_D"
    section_name = "TRILINOS_CONFIGURATION_ALPHA"
    #section_name = "TEST_CMAKE_CACHE_PARAM_ORDER"
    section_name = "TEST_EXPANSION_IN_ARGUMENT"
    section_name = "TEST_SPACES_IN_VALUE"
    section_name = "TEST_SPACES_AND_EXPANSION"
    #section_name = "TEST_VARIABLE_EXPANSION_IN_CMAKE_VAR"
    #section_name = "TEST_SECTION"
    section_name = "TEST_VAR_EXPANSION_UPDATE_01"

    parse_section(parser, section_name)

    print("")
    print("parser.options")
    print("--------------")
    pprint(parser.options, width=200, sort_dicts=False)

    print("")
    print("Bash Output")
    print("-----------")
    option_list = parser.gen_option_list(section_name, generator="bash")
    print( " \\\n    ".join(option_list) )

    # generate CMake fragment

    print("")
    print("CMake Fragment")
    print("--------------")
    option_list = parser.gen_option_list(section_name, generator="cmake_fragment")
    if len(option_list) > 0:
        print("\n".join(option_list))
    else:
        print("-")
    print("")

    return 0



def parse_section(parser, section):

    # Test out something that might be experimental
    experimental(parser, section)

    #data = parser.parse_section(section)
    data = parser.configparserenhanceddata[section]

    print("\nData")
    print("----")
    pprint(data, width=120)

    # Print the loginfo from the last search
    if(False):
        print("\nLogInfo")
        print("-------")
        #parser._loginfo_print(pretty=True)
        handler_list = [ (d['type'], d['name']) for d in parser._loginfo if d['type'] in ['handler-entry','handler-exit']]
        pprint(handler_list, width=120)

    return data



def experimental(parser, section):
    #text = "foo ${bar}-${baz|CMAKE}-${bif|ENV} XXa"
    #print("old:", text)
    #print("new:", new_str)
    return 0



def main():
    """
    main app
    """
    fname_ini = "config_test_setprogramoptions.ini"
    fpath_ini = find_config_ini(filename=fname_ini)

    test_setprogramoptions(filename=fpath_ini)



if __name__ == "__main__":
    main()
    print("Done.")

