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
import pexpect

def read_options():
    """Parse options for the program. """
    parser = OptionParser()

    parser.add_option('-n', '--length', dest="linelength",
                      default=72,
                      help="set the line length.")
    parser.add_option('-o', '--outfile', dest='outfile',
                      default="",
                      help='set the output .tex file')
    parser.add_option('-w', '--cut', dest='cut_at_blanks',
                      default=0,
                      help='set the cut at blanks value.')

    return parser.parse_args()

def escape_latex_special(line):
    """Replace OCaml special characters with LaTeX specials"""
    line = line.replace('\\', r'\\camlbslash')
    line = line.replace('{', r'\\{')
    line = line.replace('}', r'\\}')
    return line


def process_inline(line):
    """Wrap a line of input ML in the special OCaml characters."""
    line = escape_latex_special(line)

    joined = '\\?{' + line + '}\n'
    return joined

def process_outline(line):
    """Wrap a line of evaluated ML in the special OCaml characters."""
    line = escape_latex_special(line)

    return '\\:{' + line + '}\n'

END_REGEX = r"\\end{caml_(example|example\*|eval)}\s*"

START_ECHO_EXAMPLE = r'\s*\\begin{caml_example}\s*'

START_NOECHO_EXAMPLE = r'\s*\\begin{caml_example*}\s*'

START_EVAL = r'\s*\\begin{caml_eval}\s*'

START_LISTING = r'\s*\\begin{caml_listing}\s*'

def read_ml_block(filepointer, ocaml_session, echo_eval=True):
    """
    Assuming that an OCaml block has been detected,
    reads the file until it sees that a block,
    has been ended. Evaluates the code in ocaml_session,
    which it expects is a pexpect object. echo_eval
    determines whether or not the evaluation should be
    returned, as well.
    """
    total_eval = ''

    ml_accum = ""

    while True:
        line = filepointer.readline()

        # unexpected EOF
        if line is None:
            print "Opened ML expression never closed."
            exit(1)

        # found the end of the block
        elif re.search(END_REGEX, line):
            break

        # if an ocaml expression ends here
        elif ";;" in line:
            ml_accum = ml_accum + line

            # send the ML to the ocaml shell
            ocaml_session.sendline(ml_accum)

            # wait for the command to finish evaluating
            ocaml_session.expect('#')

            # get back what we just sent and evaluated
            evaled = ocaml_session.before

            # getting a bit hacky here...
            # find where to split input and output
            indx = evaled.find(';;')

            # input is before the ;;
            inputted = evaled[:indx + 2]

            # output is after the ;;
            outputted = evaled[indx + 2:]

            clean_input = map(process_inline,
                              [s for s in
                               [s.strip() for s in inputted.split('\r\n')]
                               if len(s) > 0])

            clean_output = map(process_outline,
                               [s for s in
                                [s.strip() for s in outputted.split('\r\n')]
                                if len(s) > 0])

            if echo_eval:
                total_eval += ''.join(clean_input) + ''.join(clean_output)
            else:
                total_eval += ''.join(clean_input)

            ml_accum = ""

        # seeing more ML

        else:
            ml_accum = ml_accum + line

    return total_eval


def convert_to_tex(filename, outfilename):
    """ Convert the MLT file at the path filename
        to a .tex file.
    """

    # start up and wait for the shell to be ready
    ocaml_session = pexpect.spawn('ocaml')
    ocaml_session.expect("#")

    # get the source file and the output file
    try:
        infile = open(filename, 'r')
    except IOError as excep:
        print "Input file error: {}".format(excep)
        exit(1)

    try:
        outfile = open(outfilename, 'w')
    except IOError as excep:
        print "Output file error: {}".format(excep)
        exit(1)

    while True:

        line = infile.readline()

        # if we've hit end of line, get out of here
        if not line:
            infile.close()
            outfile.close()
            return

        if re.search(START_ECHO_EXAMPLE, line):
            evaled = read_ml_block(infile, ocaml_session)

            outfile.write('\\begin{caml}\n')
            outfile.write(evaled)
            outfile.write('\\end{caml}\n')

        elif re.search(START_NOECHO_EXAMPLE, line):
            evaled = read_ml_block(infile, ocaml_session, echo_eval=False)

            outfile.write('\\begin{caml}\n')
            outfile.write(evaled)
            outfile.write('\\end{caml}\n')

        # add the evaled block through the session
        # but don't echo the output
        elif re.search(START_EVAL, line):
            read_ml_block(infile, ocaml_session)

        # otherwise, this line is just .tex and should be echoed
        else:
            outfile.write(line)

def run():
    """
    Drive the whole program.
    """
    options, args = read_options()

    for arg in args:
        print arg

        if options.outfile is "":
            print 'h'
            out = arg + '.tex'
        else:
            out = options.outfile

        convert_to_tex(arg, out)


if __name__ == '__main__':
    run()
    