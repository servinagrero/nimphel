#!/usr/bin/env python3

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple, Union

import nimphel

from .component import Component, Params, Ports


class Subckt:
    """Class to handle a subcircuit.

    Attributes:
      name: Name of the subcircuit.
      components: List of component instances inside the subcircuit.
      ports: List of ports of the subcircuit.
      params: List of parameters of the subcircuit.
      fixed: If True, no more components can be added to the subcircuit.
    """

    def __init__(self, name: str, ports: Ports, params: Optional[Params] = None):
        self.name: str = name
        self.components: List[Component] = []
        self.ports: Ports = ports
        self.params: Optional[Params] = params
        self.__fixed: bool = False

        nimphel.netlist.subcircuits[self.name] = self

    def __contains__(self, comp: Component):
        return comp in self.components

    def fix(self):
        """Fix the subcircuit to prevent adding more components."""
        self.__fixed = True

    def add(self, component: Union[List[Component], Component]):
        """Add a component instance to the list of components.

        If the subcircuit is fixed, a warning is printed and nothing happens.

        Args:
            component: Component or list of components to add.
        """
        if self.__fixed:
            print(f"WARNIG: Subcircuit {self.name} is fixed")
        else:
            if isinstance(component, list):
                self.components += component
            else:
                self.components.append(component)

    def inst(self, ports: Ports, params: Optional[Params] = None) -> Component:
        """Create a component instance from the subcircuit.

        Args:
          ports: Ports of the subcircuit instance.
          params: Parameters for the subcircuit instance.

        Returns:
          Component instance.

        Raises:
          KeyError: The number of ports given is checked against the defined ones.
          KeyError: There are default parameters that haven't been supplied.
          KeyError: The parameters given do not match the default ones.
        """

        if len(ports) != len(self.ports):
            raise KeyError(
                f"Wrong number of ports supplied. "
                f"Needed {len(self.ports)} ports but {len(ports)} were given."
            )

        nil_params: Params = {}
        if self.params:
            nil_params = {k: v for k, v in self.params.items() if v is None}

        if nil_params and params is None:
            raise KeyError(
                f"Must supply non default parameters. "
                f"Needed {list(nil_params.keys())}"
            )

        if nil_params and params and (params.keys() != nil_params.keys()):
            raise KeyError(
                f"Parameters do not match with default params. "
                f"Needed {list(nil_params.keys())} but got {list(params.keys())}"
            )

        user_params = params if params else {}
        return Component(ports, {**nil_params, **user_params}, name=self.name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "ports": self.ports,
            "params": self.params,
            "components": [c.to_dict() for c in self.components],
            "fixed": self.__fixed,
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict())
