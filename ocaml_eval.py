
class OCamlSession():
    """
    Wrapper around the pexpect class to run an OCaml session.

    Might make it easier to this to be a generalized tool! 
    """

    def __init__(self):
        self.ocaml_interactive = pexpect.spawn('ocaml')
        self.ocaml_interactive.expect('#')

    def evaluate(self, ml_block):
        pass

    def add_to_session(self, ml_block):
        pass

    def reset(self)
        self.ocaml_interactive = pexpect.spawn('ocaml')
        self.ocaml_interactive.expect('#')

        return True