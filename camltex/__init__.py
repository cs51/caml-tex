#! /usr/bin/env python

"""
A python version of caml-tex.

Known problems:
    - Trailing comments are not handled properly
        (anything after ;; is treated as output)
    - -n, -w arguments do nothing (need to understand what they did previously)
"""

import re
from optparse import OptionParser
from ocaml_eval import OCamlSession
from ocaml_writer import CamlTexFileWriter
import os

def read_options():
    """Parse options for the program. """
    parser = OptionParser()

    parser.add_option('-o', '--outfile', dest='outfile',
                      default="",
                      help='set the output .tex file')

    return parser.parse_args()

# Regular Expressions
DOC_START = r"\s*\\begin{document}\s*"
START_REGEX = r"\s*\\begin{caml_(example|example\*|eval)\s*}"
END_REGEX = r"\\end{caml_(example|example\*|eval|listing)}\s*"
LISTING = r'\s*\\(begin|end){caml_listing}\s*'
ECHO_IN = r'\s*\\end{caml_example\*?}\s*'
ECHO_OUT = r'\s*\\end{caml_example}\s*'

class BadMLException(Exception):
    """
    Class to represent exceptions related
    to parsing ML from the .mlt file.
    """
    def __init__(self, message):
        self.message = message
        super(BadMLException, self).__init__()

    def __repr__(self):
        return "BadMLException: {}".format(self.message)

class BadTexException(Exception):
    """
    Class to represent exceptions related
    to parsing TeX from the .mlt file.
    """
    def __init__(self, message):
        self.message = message
        super(BadTexException, self).__init__()

    def __repr__(self):
        return "BadTexException: {}".format(self.message)

def extract_ml_statements(filepointer):
    """
    Extract ML statements from the filepointer.
    Assumed that an block starts here.
    """

    statements = []

    statement = ""

    while True:
        line = filepointer.readline()

        if line is None:
            raise BadTexException("Opened Caml Statement never closed.")

        elif re.search(END_REGEX, line):
            return statements, line

        statement += line

        if ";;" in line:
            statements.append(statement)
            statement = ""

def convert_to_tex(filename, outfilename):
    """ Convert the MLT file at the path filename
        to a .tex file.
    """

    # start up and wait for the shell to be ready
    ocaml = OCamlSession()

    # try to open the outfile as a relative path first
    try:
        writer = CamlTexFileWriter(os.getcwd() + '/' + outfilename)
    except IOError:
        try:
            writer = CamlTexFileWriter(outfilename)
        except IOError as excep:
            print "Could not open output file: {}".format(excep)
            exit(1)

    # get the source file and the output file
    try:
        infile = open(filename, 'r')
    except IOError as excep:
        print "Input file error: {}".format(excep)
        exit(1)

    while True:

        line = infile.readline()

        # if we've hit end of line, get out of here
        if not line:
            infile.close()
            writer.close()
            return

        # case for ocaml statements that interact with the shell
        if re.search(START_REGEX, line):
            statements, endline = extract_ml_statements(infile)

            echo_in = bool(re.match(ECHO_IN, endline))
            echo_out = bool(re.match(ECHO_OUT, endline))

            evals = [ ocaml.evaluate(statement) for statement in statements]

            if echo_in and echo_out:
                writer.write_ocaml("".join(evals))
            elif echo_in:
                writer.write_ocaml("".join(statements))

        # case for ocaml listings, which do not interact with the shell
        elif re.search(LISTING, line):

            statements, _ = extract_ml_statements(infile)
            tex_statement = "".join(statements)
            writer.write_ocaml(tex_statement)

        # otherwise, this line is just .tex and should be echoed
        else:
            if re.search(DOC_START, line):
                writer.write_styles()

            writer.write_tex(line)

def run():
    """
    Drive the whole program.
    """
    options, args = read_options()

    for arg in args:
        print arg

        if options.outfile is "":
            out = arg + '.tex'
        else:
            out = options.outfile

        convert_to_tex(arg, out)


if __name__ == '__main__':
    run()
    
