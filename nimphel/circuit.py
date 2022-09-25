#!/usr/bin/env python3

from collections import defaultdict
from os import PathLike
from typing import List, Tuple, Union

import numpy as np

from .component import Component, Params, Ports, net
from .exporter import Exporter, SpectreExporter
from .subcircuit import Subckt


class Circuit:
    """Class to handle the state of the circuit.

    Attributes:
      options: Simulator options.
      instances: Dict to track component ids.
      components: List of component instances.
      subcircuits: Dict to track subcircuit definitions.
      nets: Counter to keep track of the nets.
      exporter: Exporter used to create the netlist.
    """

    def __init__(self):
        self.options: Dict[str, str] = {}

        self.instances = defaultdict(int)
        self.components: List[Component] = []
        self.subcircuits: Dict[str, Subckt] = {}
        self.nets: int = 0

        self.exporter: Exporter = SpectreExporter()

    def add(
        self,
        component: Union[np.ndarray, Tuple[Component], List[Component], Component],
    ):
        """Add a component instance to the circuit.

        Args:
          component: Component or list of component instances.
        """
        if isinstance(component, np.ndarray):
            self.components += np.ravel(component).tolist()
        elif isinstance(component, (tuple, list)):
            self.components += component
        else:
            self.components.append(component)

    def __contains__(self, inst: Union[Component, Subckt]) -> bool:
        """Checks if a component or subcircuit is present inside the circuit."""
        if isinstance(inst, Component):
            return inst in self.components
        return inst in self.subcircuits or any(
            inst.name == c.name for c in self.components
        )

    def into_subckt(self, name: str, ports: Ports, params: Params = None) -> Subckt:
        """Convert the state into a subcircuit.

        TODO: This subckt will register itself to the global netlist. Make this optional or prevent it from happening?

        Args:
          name: Name of the subcircuit.
          ports: Ports of the subcircuit.
          params: Parameters of the subcircuit.

        Returns:
          Subcircuit
        """
        subckt = Subckt(name, ports, params if params else {})

        subckt.add(self.components)
        return subckt

    def export(self) -> str:
        """Export the current circuit.

        The circuit is exported using the assigned exporter.

        Returns:
          The formated circuit as a string.
        """
        subckts = "\n".join(map(self.exporter.fmt_subckt, self.subcircuits.values()))
        components = "\n".join(map(self.exporter.fmt_component, self.components))
        return f"{subckts}\n{components}\n" f'{self.options if self.options else ""}'

    def export_to_file(self, outfile: Union[str, bytes, PathLike]):
        """Export the netlist directly to a file.

        Args:
          outfile: Path to the file.
        """
        with open(outfile, "w+") as file:
            file.write(self.export())
