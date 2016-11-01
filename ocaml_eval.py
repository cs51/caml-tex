"""
Module containing wrapper class for an
OCamlSession, built on pexpect.
"""


import pexpect

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
        Given an ML block, return the result of evaluating the ML block
        in the toplevel.
        """
        self.ocaml.sendline(ml_block)
        self.ocaml.expect('#')
        statement = self.ocaml.before.strip().split('\r\n')

        return statement

    def reset(self):
        """
        Return the session to an clean state by
        resetting the underlying OCaml process.
        """
        self.ocaml_interactive = pexpect.spawn('ocaml')
        self.ocaml_interactive.expect('#')

        return True

    def __repr__(self):
        return "<OCaml Session>"
