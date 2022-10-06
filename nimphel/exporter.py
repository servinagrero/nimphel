#!/usr/bin/env python3

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple, Union


class Exporter:
    """Interface for a Exporter.

    An exporter needs to implement functions to format a component instance, a subcircuit and a net.
    """

    def fmt_component(self, comp) -> str:
        """Format a component instance."""
        raise NotImplementedError

    def fmt_subckt(self, subckt) -> str:
        """Format a subcircuit definition."""
        raise NotImplementedError

    def fmt_net(self, net) -> str:
        """Format a net."""
        raise NotImplementedError


class SpectreExporter(Exporter):
    """Exporter implementation for Spectre"""

    def __fmt_value(self, value):
        if isinstance(value, list):
            return f'[ {" ".join(map(str, value))} ]'
        if isinstance(value, (float, int)):
            return f"{value:.2F}"
        return f'"{value}"'

    def fmt_component(self, comp) -> str:
        if hasattr(comp, "fmt"):
            return comp.fmt()

        ports = " ".join(map(self.fmt_net, comp.ports))
        params_not_nil = {k: v for k, v in comp.params.items() if v}
        params = " ".join(
            [f"{k}={self.__fmt_value(v)}" for k, v in params_not_nil.items()]
        )
        return f"{comp.letter}{comp.num_id} ({ports}) {comp.name} {params}"

    def fmt_subckt(self, subckt) -> str:
        comps = "\n".join(map(self.fmt_component, subckt.components))
        ports = " ".join(map(self.fmt_net, subckt.ports))
        nil_params = [f"{k}" for k, v in subckt.params.items() if not v]
        val_params = [f"{k}={v}" for k, v in subckt.params.items() if v]
        if val_params or nil_params:
            params = f"parameters {' '.join(nil_params + val_params)}\n"
        else:
            params = ""
        return (
            f"subckt {subckt.name} {ports}\n"
            f"{params}"
            f"{comps}\n"
            f"ends {subckt.name}\n"
        )

    def fmt_net(self, net: Union[str, int]) -> str:
        if isinstance(net, int):
            return f"net{net}"
        return net
