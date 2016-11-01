"""
Wrapper class to write beautiful
generic LaTeX files.
"""

from pygments import highlight
from pygments.formatters import LatexFormatter
from pygments.lexers.functional import OcamlLexer

LF = LatexFormatter()
OL = OcamlLexer()

class CamlTexFileWriter(object):
    """
    Wrapper class to manage listings in OCaml.
    """
    def __init__(self, filepath):
        self.fname = filepath
        self.fpointer = open(filepath, 'w')

    def write_styles(self):
        """
        Make it so that the OCaml looks
        pretty, by outputting the appropriate
        code formatting styles. 
        """
        self.fpointer.write('\n\usepackage{fancyvrb,color}\n')
        self.fpointer.write(LF.get_style_defs())

    def write_tex(self, line):
        """
        Return a line of LaTeX to the file.
        """
        self.fpointer.write(line)
        return True

    def write_ocaml(self, ml_block):
        """
        Write stylized OCaml to the output file,
        styling with pygments at the same time.
        """
        self.fpointer.write(highlight(ml_block, OL, LF))
        return True

    def close(self):
        """Close the file writer"""
        self.fpointer.close()

    def __repr__(self):
        return "<CamlWriter {}>".format(self.fname)
