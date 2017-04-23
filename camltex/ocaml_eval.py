"""
Module containing wrapper class for an
OCamlSession, built on pexpect.
"""


import pexpect
import re
import sys

ANSI_RE = re.compile(r'\x1b[^m]*m')
ANSI_RE2 = re.compile(r'\x1b\[A')

class OCamlSession(object):
    """
    Wrapper around the pexpect class to run an OCaml session.

    Might make it easier to this to be a generalized tool!
    """

    def __init__(self):
        self.ocaml = pexpect.spawn('ocaml')
        self.ocaml.expect('#')

    def evaluate(self, ml_block):
        """
        Given an ML block, return the result 
        of evaluating the ML block
        in the toplevel.
        """
        if '#' in ml_block:
            count = len([c for c in ml_block if c == '#'])
        else:
            count = 0

        # self.ocaml.sendline(unicode(ml_block))
        self.ocaml.sendline(ml_block)

        statement = ""
        self.ocaml.expect(r'#\s')
        statement +=  ANSI_RE2.sub('', ANSI_RE.sub('', self.ocaml.before))

        statement = statement.strip()
        statement = statement.replace('\r\n', '\n')
        statement = statement.replace('\n\n', '\n')

        return statement.strip()

    def reset(self):
        """
        Return the session to an clean state by
        resetting the underlying OCaml process.
        """
        self.ocaml = pexpect.spawn('ocaml', encoding='ascii')
        # self.ocaml = pexpect.spawnu('ocaml -stdin') # , encoding='ascii')

        self.ocaml.expect('#')

        return True

    def __repr__(self):
        return "<OCaml Session>"
