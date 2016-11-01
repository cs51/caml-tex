"""
Wrapper class to write beautiful
generic LaTeX files.
"""

from pygments import highlight
from pygments.formatters import LatexFormatter
from pygments.lexers.functional import OcamlLexer

class CamlTexFileWriter(object):
    """
    Wrapper class to manage listings in OCaml.
    """
    def __init__(self, filepath):
        self.fname = filepath
        self.fpointer = open(filepath, 'w')

    def write_tex(self, line):
        """
        Return a line of LaTeX to the file.
        """
        self.fpointer.write(line)
        return True

    def write_ocaml(self, ml_block):
        print "WRITING OCAML", ml_block
        pass

    def close(self):
        """Close the file writer"""
        self.fpointer.close()

    def __repr__(self):
        return "<CamlWriter {}>".format(self.fname)
