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
    section_name = "TEST_VAR_EXPANSION_UPDATE"

    parse_section(parser, section_name)

    print("")
    print("parser.options")
    print("--------------")
    pprint(parser.options, width=200, sort_dicts=False)

    option_list = parser.gen_option_list(section_name, generator="bash")
    print("")
    print("Bash Output")
    print("-----------")
    print( " \\\n    ".join(option_list) )

    # generate CMake fragment
    option_list = parser.gen_option_list(section_name, generator="cmake_fragment")
    print("")
    print("CMake Fragment")
    print("--------------")
    if len(option_list) > 0:
        print("\n".join(option_list))
    else:
        print("-")
    #pprint(option_list)
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

import dataclasses


class VariablesInStringsFormatter(object):

    @dataclasses.dataclass(frozen=True)
    class fieldinfo:
        varfield: str
        varname : str
        vartype : str
        start   : int
        end     : int


    def _expandvar_ENV_bash(self, field):
        """ Expand an Envvar for BASH
        """
        return "${" + field.varname + "}"


    def _expandvar_CMAKE_bash(self, field):
        msg = "`{}`: is invalid in a `bash` context.".format(field.varfield)
        # Todo: can we keep track of CMake vars that we know about already
        #       and if we _know_ what they'll be then we expand, otherwise
        #       we'd throw our hands in the air... like we just don't care.
        raise NotImplementedError(msg)


    def _expandvar_ENV_cmake(self, field):
        return "$ENV{" + field.varname + "}"


    def _expandvar_CMAKE_cmake(self, field):
        return "${" + field.varname + "}"


    def format_vars_in_string(self, text, sep='|', generator="bash"):
        """
        Format variables that are formatted like ``${VARNAME|TYPE}`` according
        to the proper generator.

        Args:
            text (str): The string we wish to modify.
            sep (str): The separator character to distinguish VARNAME from TYPE.
            generator (str): The kind of generator to use (i.e., are we generating
                output for a bash script, a CMake fragment, Windows, etc.)

        Raises:
            Exception: An exception is raised if the appropriate generator helper
                method is not found.
        """
        generator = generator.lower()

        pattern = r"\$\{([a-zA-Z0-9_" + sep + r"\*\@\[\]]+)\}"

        matches = re.finditer(pattern, text)

        output = ""
        curidx = 0
        for m in matches:
            varfield = m.groups()[0]
            idxsep  = varfield.index(sep) if sep in varfield else None

            vartype = "ENV"
            if idxsep:
                vartype = varfield[idxsep + len(sep):]
                vartype = vartype.upper().strip()
            varname = varfield[:idxsep]

            varfield = "${" + m.groups()[0] + "}"

            field = self.fieldinfo(varfield, varname, vartype, m.start(), m.end())
            #print(">>> field =", field)

            handler_name = "_".join(["_expandvar", vartype, generator])
            func = None
            if hasattr(self, handler_name):
                func = getattr(self, handler_name)
            else:
                raise Exception("Missing required generator helper: `{}`.".format(handler_name))

            output += text[curidx:field.start]
            output += func(field)
            curidx = field.end

        output += text[curidx:]
        return output




# _convert_var_<TYPE>_<GENERATOR>
#def _convert_var_ENV_generator(text, fieldinfo):
    #output = ""

    #return output


#def _stringxformvars(text, sep="|", generator="bash"):
    #"""
    #EXPERIMENTAL!
    #"""
##    type_to_generator_map = {
##        "ENV"  : { "bash" },
##        "CMAKE": { "bash", "cmake" }
##    }


    #pattern = r"\$\{([a-zA-Z0-9_|\*\@\[\]]+)\}"
    #matches = re.finditer(pattern, text)

    #generator = generator.lower()

    #new_str = ""
    #curidx  = 0
    #for m in matches:
        #print(">>> {}: {}-{} '{}'".format(m.groups()[0], m.start(), m.end(), text[m.start():m.end()]))

        #varname = m.groups()[0]
        #idxsep  = varname.index(sep) if sep in varname else None

        #vartype = "ENV"
        #if idxsep:
            #vartype = varname[idxsep + len(sep):]
            #vartype = vartype.upper().strip()
        #varname = varname[:idxsep]

        #field = fieldinfo(varname, vartype, m.start(), m.end())

        ##print(">>> varname = {}".format(varname))
        ##print(">>> vartype = {}".format(vartype))
        #print(">>> field  = {}".format(field))



        #str_var_pre  = "${"
        #str_var_post = "}"

        #if vartype == "ENV":
            ## keep the default if it's bash
            #print(">>> Variable is ENV")
            #pass
        #elif vartype == "CMAKE":
            #print(">>> Variable is CMAKE")
            #str_var_pre  = "$ENV{"
            #str_var_post = "}"
        #else:
            ## Unknown `type`, maybe a typo?
            #raise ValueError("`{}` is an unknown variable type.".format(vartype))

        #new_str += text[curidx:m.start()]
        #new_str += "{}{}{}".format(str_var_pre, varname, str_var_post)
        #curidx = m.end()

    #new_str += text[curidx:]
    #return new_str


def experimental(parser, section):

    #text = "foo ${bar}-${baz|CMAKE}-${bif|ENV} XXa"

    #TEST = VariablesInStringsFormatter()
    #new_str = TEST.format_vars_in_string(text, generator="bash")

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

