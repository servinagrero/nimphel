#!/usr/bin/env python3

from nimphel.core import Instance, Directive, Subcircuit, Circuit
from lark import Lark, Transformer
from lark import UnexpectedToken, UnexpectedEOF, UnexpectedCharacters
from lark.exceptions import VisitError
from rich import print as rprint
from pathlib import Path

from typing import Optional, Type


class ToCircuit(Transformer):
    """Transform a Tree into a circuit"""

    NAME = str
    ESCAPED_STRING = lambda _, x: str(x[1:-1])
    value_list = list
    directive = lambda _, x: Directive(*x)

    # NUMBER = float
    def NUMBER(self, x):
        try:
            return int(x)
        except ValueError:
            return float(x)

    def start(self, x):
        return Circuit(
            instances=[i for i in x if isinstance(i, Instance)],
            subcircuits=[i for i in x if isinstance(i, Subcircuit)],
            directives=[i for i in x if isinstance(i, Directive)],
        )

    def param_value(self, x):
        return {x[0]: x[1]}

    def node(self, x):
        if isinstance(x[0], str):
            return str(x[0])
        return int(x[0])

    nodes = list
    subcircuit_nodes = list

    def instance_params(self, x):
        p = {}
        for d in x:
            for k, v in d.items():
                p[k] = v
        return p

    def instance_id(self, x):
        t = x[0].value
        return (t[0], int(t[1:]))

    def instance(self, x):
        _, uid = x.pop(0)
        return Instance(x[1], x[0], x[2], uid=uid)

    directive_params = instance_params
    subcircuit_params = instance_params

    def subcircuit(self, x):
        assert x[0] == x[-1]
        t = x[:-1]
        s = Subcircuit(t.pop(0), t.pop(0), t.pop(0) or {})
        for i in t:
            s.add(i)
        return s


class Reader:
    """Create a reader for an specific language

    The grammars are read from this directory and must end with `.lark`

    Args:
        name: Name of the language. It should not contain the suffix `.lark`

    Returns:
        A Lark parser configured for the given language

    .todo: Allow creating parsers from user defined grammars
    """

    def __init__(self, name: str, transformer: Type[Transformer] = ToCircuit):
        grammars_path = Path(__file__).parents[0]
        grammars = [f for f in grammars_path.iterdir() if f.suffix == ".lark"]
        grammar_names = [f.stem for f in grammars]
        if not name in grammar_names:
            raise ValueError(
                f'Language "{name}" not available. Available languages are {grammar_names}'
            )
        grammar = next(g for g in grammars if g.stem == name)
        self.parser = Lark.open(str(grammar), maybe_placeholders=True, rel_to=__file__)
        self.transformer = transformer

    def parse(self, source: str, path: Optional[str] = None) -> Optional[Circuit]:
        """Parse a netlist file

        Args:
            source:

        Returns:
            The Circuit if the parsing is successful and None if there were errors during parsing
        """
        try:
            tree = self.parser.parse(source)
            circuit = self.transformer().transform(tree)
            if path:
                circuit.path = Path(path).resolve()
            return circuit
        except UnexpectedEOF as u:
            context = u.get_context(source)
            print(f"Unexpected end of file at line {u.line}:{u.column}")
        except UnexpectedToken as u:
            context = u.get_context(source)
            print(f'Unexpected "{u.token}" at line {u.line}:{u.column}')
        except UnexpectedCharacters as u:
            context = u.get_context(source)
            print(f'Unexpected "{u.char}" at line {u.line}:{u.column}')
        return None

    def reads(self, netlist: str) -> Optional[Circuit]:
        """ """
        return self.parse(netlist)

    def read(self, path: str) -> Optional[Circuit]:
        """ """
        with open(path, "r") as fp:
            return self.parse(fp.read(), path=path)
