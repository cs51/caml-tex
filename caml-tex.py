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

START_REGEX = r"\s*\\begin{caml_(example|example\*|eval)\s*}"
END_REGEX = r"\\end{caml_(example|example\*|eval|listing)}\s*"

LISTING = r'\s*\\(begin|end){caml_listing}\s*'

ECHO_EXAMPLE = r'\s*\\end{caml_example}\s*'
NOECHO_EXAMPLE = r'\s*\\end{caml_example*}\s*'
EVAL = r'\s*\\end{caml_eval}\s*'

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

def read_ml_block(filepointer, ocaml_session, eval_ml=True, echo_eval=True):
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

            # if we're just parsing ML, continue
            if not eval_ml:
                clean_input = map(process_inline,
                                  [s for s in
                                   [s.strip() for s in ml_accum.split('\r\n')]
                                   if len(s) > 0])
                total_eval += clean_input
                ml_accum = ""

            # send the ML to the ocaml shell
            ocaml_session.sendline(ml_accum)

            # wait for the command to finish evaluating
            ocaml_session.expect('#')

            # get back what we just sent and evaluated
            evaled = ocaml_session.before

            # getting a bit hacky here...
            # find where to split input and output
            semi_indx = evaled.find(';;')

            if semi_indx == -1:
                raise BadMLException("Double Semi-Colon not found.")

            newline_indx = evaled[semi_indx+2:].find('\n')

            if newline_indx == -1:
                raise BadMLException("Newline ending input not found.")

            # input is before the ;;
            inputted = evaled[:(semi_indx + 2 + newline_indx)]

            # output is after the ;;
            outputted = evaled[(semi_indx + 2 + newline_indx):]

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
    ocaml = OCamlSession()

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

            print line, endline

            example_start = bool(re.match(ECHO_EXAMPLE, line))
            example_star_start = bool(re.match(NOECHO_EXAMPLE, line))
            eval_start = bool(re.match(EVAL, line))

            example_end = bool(re.match(ECHO_EXAMPLE, endline))
            example_star_end = bool(re.match(NOECHO_EXAMPLE, endline))
            eval_end = bool(re.match(EVAL, endline))

            pairs = [(statement, ocaml.evaluate(statement)) for statement in statements]

            if example_start:
                if not example_end:
                    raise BadTexException("Imbalanced start and end for caml block.")
                tex_statement = "\n".join([p for p in [s + '\n' + e for (s, e) in pairs]])

            if example_star_start:
                if not example_star_end:
                    raise BadTexException("Imbalanced start and end for caml block.")
                tex_statement = "\n".join([s for s, _ in pairs])

            if eval_start:
                if not eval_end:
                    raise BadTexException("Imbalanced start and end for caml block.")
                tex_statement = None

            if tex_statement is not None:
                writer.write_ocaml(tex_statement)
            else:
                continue

        # case for ocaml listings, which do not interact with the shell
        elif re.search(LISTING, line):

            statements, endline = extract_ml_statements(infile)

            if bool(re.search(LISTING, line)) != bool(re.search(LISTING, endline)):
                raise BadTexException("Imbalanced start and end for caml listing block.")

            tex_statement = "\n".join(statements)
            writer.write_ocaml(tex_statement)

        # otherwise, this line is just .tex and should be echoed
        else:
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
    