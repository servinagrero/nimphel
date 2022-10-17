#!/usr/bin/env python3

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import islice
from os import PathLike
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from .component import Component, Params, Ports, net
from .exporters import Exporter
from .subcircuit import Subckt


class Circuit:
    """Class to handle the state of the circuit.

    Attributes:
        instances: Dict to track component ids.
        components: List of component instances.
        subcircuits: Dict to track subcircuit definitions.
        nets: Counter to keep track of the nets.
        exporter: Exporter used to create the netlist.
    """

    def __init__(self):
        self.instances = defaultdict(int)
        self.components: List[Component] = []
        self.subcircuits: Dict[str, Subckt] = {}
        self.nets: int = 0

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
        """Checks if a component or subcircuit is present inside the circuit.

        Args:
            inst: Component or subcircuit to check.

        Returns:
            True if the instance is inside the circuit.
        """
        if isinstance(inst, Component):
            return inst in self.components
        return inst in self.subcircuits or any(
            inst.name == c.name for c in self.components
        )

    def into_subckt(
        self, name: str, ports: Ports, params: Optional[Params] = None
    ) -> Subckt:
        """Convert the state into a subcircuit.

        Args:
            name: Name of the subcircuit.
            ports: Ports of the subcircuit.
            params: Parameters of the subcircuit.

        Returns:
            Subcircuit

        Todo:
            * This subckt will register itself to the global netlist. Make this optional or prevent it from happening?
        """
        subckt = Subckt(name, ports, params if params else {})

        subckt.add(self.components)
        return subckt

    def export(self, exporter: Exporter) -> str:
        """Export the current circuit.

        Args:
            exporter: Exporter class to use.

        Returns:
            The formated circuit as a string.
        """
        subckts = "\n".join(map(exporter.fmt_subckt, self.subcircuits.values()))
        components = "\n".join(map(exporter.fmt_component, self.components))
        return f"{subckts}\n{components}\n"

    def export_to_file(self, outfile: Union[str, bytes, PathLike], exporter: Exporter):
        """Export the netlist directly to a file.

        Args:
            outfile: Path to the file.
        """
        with open(outfile, "w+") as file:
            file.write(self.export(exporter))

    def to_dict(self) -> Dict[str, Any]:
        """Export a circuit to a dict"""
        return {
            "instances": dict(self.instances),
            "components": [c.to_dict() for c in self.components],
            "subcircuits": {k: v.to_dict() for k, v in self.subcircuits.items()},
            "nets": self.nets,
        }

    def to_json(self) -> str:
        """Returns the string representation of the component."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Circuit:
        """ """
        data = json.loads(json_str)
        circuit = cls()
        circuit.instances = defaultdict(int, data.get("instances", {}))

        def create(sub_cls: type, data: dict[str, Any]):
            """Wrapper to call from_json on both Component and Subcircuit."""
            return sub_cls.from_json(json.dumps(data))

        circuit.components = [create(Component, c) for c in data.get("components")]
        circuit.subcircuits = {
            name: create(Subckt, c) for name, c in data.get("subcircuits").items()
        }
        circuit.nets = data.get("nets", 0)
        return circuit

    def to_graph(
        self,
        comps: Optional[List[Component]] = None,
        root: Optional[str] = None,
        *,
        name: str = "circuit",
    ) -> nx.Graph:
        """Create a graph with the instances in the circuit.

        This functions adds connections between the root and every component instance. If the component instance is a subcircuit, this function gets called again with the subcircuit as the root node.

        The weight between the connections represents the number of components that are inside a circuit or subcircuit, that is, the dependencies. The dependencies are normalized for just one subcircuit. To know the real number of instances in the total circuit, see ``count_instances``.

        By default the root of the circuit is called `circuit`. This root name can be changed with the `name` argument.

        Args:
            comps: List of component instances.
            root: Name of the node that serves as the root.
            name: Name of the global root. Defaults to 'circuit'.

        Returns:
            The generated graph with all components, subcircuits and the circuit.
        """
        circuit_graph, visited = nx.Graph(), set()

        if root is None:
            circuit_graph.add_node(name, color="yellow")
            root = name
        components = comps if comps else self.components
        instances = Counter([c.name for c in components])

        for comp_name, count in instances.items():
            if name in visited:
                continue

            subckt = self.subcircuits.get(comp_name, None)
            if subckt:
                circuit_graph.add_node(subckt.name, color="orange")
                circuit_graph.add_edge(root, subckt.name, weight=count)
                graph = self.to_graph(subckt.components, root=subckt.name)
                circuit_graph = nx.compose(circuit_graph, graph)
            else:  # Simple component
                circuit_graph.add_node(comp_name, color="red")
                circuit_graph.add_edge(root, comp_name, weight=count)
                visited.add(comp_name)

        return circuit_graph

    def count_instances(self, root="circuit") -> Dict[str, int]:
        """Count the number of instances in the circuit.

        This functions calculates the total number of instances by traversing the graph generated with the method ``to_graph``.

        Args:
            root: Name of the root node. Has to match the one passed to 'to_graph'.

        Returns:
            A dict containing the instance name and the respective global count.
        """
        instances: Dict[str, int] = {}
        graph = self.to_graph()

        for node in map(lambda n: n[0], graph.nodes(data=True)):
            is_subckt = node in self.subcircuits
            if node == root:
                continue
            valid_paths = []

            for path in nx.all_simple_paths(graph, source=root, target=node):
                route, edges = [], list(nx.utils.pairwise(path))
                for (start, end) in edges:
                    if start == root:
                        route.append((start, end))
                        continue

                    if is_subckt:
                        if not end in self.subcircuits:
                            route.clear()
                            break
                        route.append((start, end))
                    else:
                        if not start in self.subcircuits and end in self.subcircuits:
                            route.clear()
                            break
                        route.append((start, end))
                valid_paths.append(route)

            count = 0
            for path in filter(bool, valid_paths):
                count_path = 1
                for start, end in path:
                    data = graph.get_edge_data(start, end)
                    count_path *= data["weight"]
                count += count_path
            instances[node] = count
        return instances


def create_graph(graph: nx.Graph):
    """Create the plot to visualize the graph generated by a circuit.

    `Matplotlib.pyplot` needs to be imported and the function `show` needs to be called in order to visualize the plot.

    Args:
        graph: The circuit graph to plot.
    """
    pos = nx.spring_layout(graph)
    color_map = [data["color"] for (name, data) in graph.nodes(data=True)]
    nx.draw_networkx(graph, pos, with_labels=True, node_color=color_map)
    labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
