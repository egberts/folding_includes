#!/usr/bin/env python3

##############################################################################

import os
import sys
import decomments_isc


def eat_char(text_string, char_set):
    """
    Eats the specified subset of characters from the beginning of the string and returns index when done eating
    :param text_string:
    :param char_set:
    :return: index into its string where no char_set are found
    """
    idx = 0
    for this_char in text_string:
        if this_char in char_set:
            idx = idx + 1
        else:
            break
    return idx


def de_quote(single_line):
    """
    Removes a pair of quote (single or double) in an ISC-style configuration settings.

    - A semicolon can terminate the de_quote, if quote-unclosed it's an error
    - A carriage return can terminate the de_quote, if quote-unclosed it's an error
    :param singleLines:
    :return:
    """
    single_quote_state = False
    double_quote_state = False
    idx_current = idx_start = eat_char(single_line, ' \t')

    for thisChar in single_line[idx_current:]:
        if not double_quote_state and not single_quote_state:
            if thisChar == '"':
                double_quote_state = True
                idx_start = idx_current + 1
            elif thisChar == "'":
                single_quote_state = True
                idx_start = idx_current + 1
            elif thisChar == ";":
                return single_line[idx_start:idx_current]
        elif thisChar == '\n':
            if single_quote_state or double_quote_state:
                print("Syntax Error: unterminated quote: %s" % single_line)
                exit(0)
            else:
                return single_line[idx_start:idx_current]
        elif thisChar == ';':
            if single_quote_state or double_quote_state:
                print("Syntax Error: missing semicolon: %s" % single_line)
                exit(0)
            else:
                return single_line[idx_start:idx_current]
        elif single_quote_state:
            if thisChar == "'":
                return single_line[idx_start:idx_current]
        elif double_quote_state:
            if thisChar == '"':
                return single_line[idx_start:idx_current]
        idx_current = idx_current + 1
    return single_line[idx_start:idx_current]


def read_include_file(inc_file):
    """
    Must be able to parse for enclosed include statement
    - Only top-level 'include' clause
    - Supports nesting of includes
    - No nesting of the statement 'include <filespec>' in any subclauses
    :param filespec:
    :param textData:
    :return:
    """
    # we cannot use s.splitlines(';') here because ';' might be in the quoted filespec  :-/
    # eat any whitespace and carriage-return
    new_filespec = inc_file
    try:
        inc_data = open(inc_file).read()
    except IOError as err:
        print("Error reading the file {0}: {1}\n".format(new_filespec, err))
        exit(1)
    # print("inc_data: %s" % inc_data)
    # Decomment
    inc_data = decomments_isc.isc_comments_blanker(inc_data)
    inc_data = folding_includes(multi_text_lines=inc_data, comment_prefix="subTEST: ")
    return inc_data


def extract_isc_include_filespec(this_inc_line):
    """

    :param this_inc_line:
    :return: filespec
    """
    newdata = ''
    # we cannot use s.splitlines(';') here because ';' might be in the quoted filespec  :-/

    # eat any whitespace and carriage-return
    new_filespec = this_inc_line[0:]
    # pre-check if quote is there
    if new_filespec[0:1] == ' ' or new_filespec[0:1] == "\t" or new_filespec[0:1] == "\n":
        # Expect mandatory whitespaces
        idx = eat_char(new_filespec, ' \t\n')
        this_filespec = de_quote(new_filespec[idx:])
    elif new_filespec[0:1] == '"' or new_filespec[0:1] == "'":
        this_filespec = de_quote(new_filespec)
    else:
        print("SYNTAX Error: missing whitespace between 'include' and its filespec\n")
        exit(1)
    return this_filespec


def folding_includes(multi_text_lines, comment_prefix=""):
    """
    Read in the entire content of the stated include file into a buffer

    - TODO: 'include' statement must support multi-line;
    - terminates with semicolon;
    - might have no whitespaces between 'include' keyword and its quoted filespec
    :param multi_text_lines:
    :param comment_prefix (optional)
    :return: filespec string
    """
    new_multi_text_lines = ""
    # For now, we're doing splitlines using '\n' until we can figure this out
    for this_line in multi_text_lines.splitlines(3):
        idx = eat_char(this_line, ' \t\n;')
        this_line = this_line[idx:]
        if this_line[0:7] == 'include':
            new_multi_text_lines = new_multi_text_lines + "# "
            new_multi_text_lines = new_multi_text_lines + this_line
            this_inc_file = extract_isc_include_filespec(this_line[7:])
            if comment_prefix:
                new_multi_text_lines = new_multi_text_lines + "# " + comment_prefix + "Include " + this_inc_file + " begins:\n"

            new_multi_text_lines = new_multi_text_lines + read_include_file(this_inc_file)

            if comment_prefix:
                new_multi_text_lines = new_multi_text_lines + "# " + comment_prefix + "Include " + this_inc_file + " ends:\n"
        else:
            new_multi_text_lines = new_multi_text_lines + this_line

    return new_multi_text_lines


if __name__ == "__main__":

    test_file = sys.argv[1]
    if not test_file:
        test_file = './test.isc'
    testdata = open(test_file).read()

    print("testdata: ", testdata)

    testdata = decomments_isc.isc_comments_blanker(testdata)
    testdata = folding_includes(multi_text_lines=testdata, comment_prefix="TEST: ")

    print("result: ", testdata)

    exit(0)
