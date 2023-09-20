#!/usr/bin/env python3

from nimphel.core import Instance, Subcircuit, Directive
from abc import ABC


class Writer(ABC):
    """Allows export a Circuit into different text formats.

    Todo:
        Add context manager to use a writer in a with block
    """

    def __init__(self):
        pass

    def __default__(self, o: object) -> str:
        return str(o)

    def _call_write(self, o: object) -> str:
        fn_name = str(type(o).__name__).lower()
        try:
            f = getattr(self, fn_name)
        except AttributeError:
            f = self.__default__
        return f(o)

    def writes(self, c) -> str:
        instances = "\n".join(map(self._call_write, c.instances))
        subcircuits = "\n".join(map(self._call_write, c.subcircuits))
        directives = "\n".join(map(self._call_write, c.directives))
        return "\n".join([directives, subcircuits, instances])

    def write(self, c, path):
        """
        todo: Accept a fp instead of a path
        """
        with open(path, "w+") as fp:
            fp.write(self.writes(c))


class SpectreWriter(Writer):
    "Writer for Spectre format"

    def instance(self, o):
        nodes = " ".join(map(str, o.nodes))
        cap = o.cap or "M"
        if o.params:
            params = " ".join(f"{k}={v}" for k, v in o.params.items())
            return f"{cap}{o.uid} ({nodes}) {o.name} {params}"
        return f"{cap}{o.uid} ({nodes}) {o.name}"

    def subcircuit(self, o):
        return f"subckt {o.name} {o.nodes}\n" f"ends {o.name}"

    def directive(self, o):
        if o.args is None:
            return f"{o.name}"
        fmt = lambda k, v: str(k) if v is None else f"{k}={v}"
        return f'{o.name} {" ".join([fmt(k,v) for k,v in o.args.items()])}'
