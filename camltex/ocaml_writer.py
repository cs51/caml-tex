"""
Wrapper class to write beautiful
generic LaTeX files.
"""

from pygments import highlight
from pygments.formatters import LatexFormatter
from pygments.lexers.functional import OcamlLexer

OL = OcamlLexer()

class CamlTexFileWriter(object):
    """
    Wrapper class to manage listings in OCaml.
    """
    def __init__(self, filepath, style = 'default', prompt=None):
        self.formatter = LatexFormatter(style=style)
        self.prompt = prompt

        self.fname = filepath
        self.fpointer = open(filepath, 'w')

    def write_styles(self):
        """
        Make it so that the OCaml looks
        pretty, by outputting the appropriate
        code formatting styles.
        """
        self.fpointer.write('\n\\usepackage{fancyvrb,color}\n')
        self.fpointer.write(self.formatter.get_style_defs())

    def write_tex(self, line):
        """
        Return a line of LaTeX to the file.
        """
        self.fpointer.write(line)
        return True

    def write_ocaml(self, ml_block):
        self.fpointer.write(highlight(ml_block, OL, self.formatter))
        self.fpointer.flush()

    def write_ocaml_with_evals(self, ml_statements):
        
        def clean(s):

            splitted = s.split(';;\n')
            
            if len(splitted) > 1:
                stmnt = splitted[0] + ';;'
                evaled = splitted[1].strip()
                return stmnt + '\n' + evaled
            else:
                return s

        statements = [clean(mls) for mls in ml_statements]
        self.write_ocaml_statements(statements)


    def write_ocaml_statements(self, statements):
        """
        Write stylized OCaml to the output file,
        styling with pygments at the same time.
        """
        if self.prompt:
            statements = ["{} {}".format(self.prompt, s) for s in statements]
        
        self.write_ocaml("\n".join(statements))

        return True

    def close(self):
        """Close the file writer"""
        self.fpointer.close()

    def __repr__(self):
        return "<CamlWriter {}>".format(self.fname)
