#!/usr/bin/env python3

import copy
from dataclasses import dataclass, field
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TextIO, Union
from collections import defaultdict

#: Component parameters
Params = Dict[str, Any]

#: Actual nodes of an instance
Nodes = List[Union[int, str]]


class NodeError(Exception):
    """Error when wrong nodes are provided"""

    def __init__(self, expect, got):
        msg = f"Incorrect nodes supplied. Expected {expect} but got {got}"
        super().__init__(msg)


# @dataclass
# class Element:
#     """Base for all elements of a circuit

#     This is in experimentation process
#     """

#     metadata: Dict[str, Any]

#     def copy(self):
#         return copy.deepcopy(self)


@dataclass
class Directive:
    """Raw SPICE directive

    Directives can be declared directly as a string or by passing the directive name and the required parameters as a dictionary.

    Example:
        >>> from nimphel.core import Directive
        >>> d = Directive('global 0 gnd')
        >>> d = Directive('tran', {'tran': None, 'stop': '100n'})

    Attributes:
        name: Name of the directive or the full directive string
        args: Optional dictionary containing the parameters of the directive
    """

    name: str
    args: Optional[Params] = None

    def __iter__(self):
        yield "name", self.name
        yield "args", self.args

    def copy(self) -> "Directive":
        return copy.deepcopy(self)


@dataclass
class Model:
    """SPICE Model

    Example of a model card:
    .MODEL MOD1 NPN (BF=50 IS=1E-13 VBF=50)

    Attributes:
        name: Name of the model
        base: Base component to create the model
        params: Dictionary with the model parameters
    """

    name: str
    base: str
    params: Params

    def __iter__(self):
        yield "name", self.name
        yield "base", self.base
        yield "params", self.params

    def copy(self) -> "Model":
        return copy.deepcopy(self)


@dataclass
class Instance:
    """SPICE Instance

    A typical instance is represented as follows in
    M1 (GND VDD) NMOS vth=1.0

    Attributes:
        name: Descriptive name of the instance
        nodes: Nodes of the instance
        params: Parameters of the instance
        ctx: Context of the instance. None or name of the subcircuit
        cap: Letter of the component for the netlist
        uid: Numerical index of the instance
        metadata: Additional metadata of the instance. Useful mostly for debugging and interfacing with different tools.

    Todo:
        Convert nodes to a Dict containing node names and values
    """

    name: str
    nodes: Nodes
    params: Params
    ctx: Optional[str] = None
    cap: Optional[str] = None
    uid: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __iter__(self):
        yield "name", self.name
        yield "nodes", self.nodes
        yield "params", self.params
        yield "ctx", self.ctx
        yield "cap", self.cap
        yield "uid", self.uid
        yield "metadata", self.metadata

    def copy(self) -> "Instance":
        return copy.deepcopy(self)


class Component:
    """Standard Component Generator

    A Component can be seen as a builder for different components.
    Each different SPICE component should have their own generator that allows creating as
    many instances as desired.

    Attributes:
        name: Component Name
        nodes: Nodes of the component
        params: Default parameters of the device
        metadata: Additional metadata

    Todo:
        If nodes is a Dict, we can set default values for some nodes
    """

    def __init__(
        self,
        name: str,
        nodes: List[str],
        params: Params,
        cap: Optional[str] = None,
        metadata: Optional[Params] = None,
    ):
        self.name = name
        self.nodes = nodes
        self.params = params
        self.cap: Optional[str] = cap or None
        self.metadata: Params = metadata or {}

    def __iter__(self):
        yield "name", self.name
        yield "nodes", self.nodes
        yield "params", self.params
        yield "cap", self.cap
        yield "metadata", self.metadata

    def copy(self) -> "Component":
        return copy.deepcopy(self)

    @classmethod
    def from_instance(cls, inst: Instance) -> "Component":
        """Create a Component from an instance

        Attributes:
            inst: The instance

        Returns:
            A component

        Fixme:
            Instances do not keep track of their node names so we can't access those
        """
        return cls(
            inst.name,
            inst.nodes,
            inst.params,
            # ctx=inst.ctx,
            cap=inst.cap,
            metadata=inst.metadata,
        )

    @classmethod
    def from_subcircuit(cls, subc: "Subcircuit") -> "Component":
        return cls(subc.name, subc.nodes, inst.params)

    def new(self, *args, params: Optional[Params] = None, **kwargs) -> Instance:
        """Create a component at the given nodes.

        R = Component("Res", ['P', 'N'], {'R': 1})
        R.new(P=1, N=0, params = {'R': 0.5})
        R.new([1, 0], params = {'R': 0.5})
        R.new({'P':1, 'N': 0}, {'R': 0.5})

        The keywords `ctx`,`uid` and `metadata` can be supplied.

        If `force` is True, only the parameters passed will be used, and the ones from the component will be ignored.

        Returns:
            The created Instance

        Raises:
            NodeError: If no nodes are provided or if the number of nodes does not match
        """
        if not args and not kwargs:
            NodeError("Nodes object", "[]")

        ctx = kwargs.get("ctx", None)
        context = str(ctx) if ctx else None
        parameters = params or {}

        if not kwargs.get("force", False):
            parameters = {**self.params, **parameters}

        def from_dict(supplied, nodes):
            node_dict = {k: v for k, v in supplied.items() if k in nodes}
            if len(node_dict) != len(nodes):
                raise NodeError(nodes, list(node_dict.keys()))
            return [node_dict[n] for n in self.nodes]

        if args:
            if isinstance(args[0], list):
                nodes: Nodes = args[0]
                if len(nodes) != len(self.nodes):
                    raise NodeError(len(self.nodes), len(nodes))
            if isinstance(args[0], dict):
                nodes = from_dict(args[0], self.nodes)
        else:
            nodes = from_dict(kwargs, self.nodes)

        return Instance(
            self.name,
            nodes,
            parameters,
            context,
            cap=kwargs.get("cap", self.cap),
            uid=kwargs.get("uid", None),
            metadata=kwargs.get("metadata", {}),
        )


class Subcircuit:
    """SPICE Subcircuit


    Attributes:
        name:
        nodes:
        params:
        instances
    """

    def __init__(self, name: str, nodes: List[str], params: Params):
        self.name = name
        self.nodes: List[str] = nodes
        self.params: Params = params
        self.instances: List[Instance] = []

    def __iter__(self):
        yield "name", self.name
        yield "nodes", self.nodes
        yield "params", self.params
        yield "instances", self.instances

    def copy(self) -> "Subcircuit":
        """Create a copy of this Subcircuit"""
        return copy.deepcopy(self)

    def __repr__(self):
        return f"Subcircuit(name={self.name}, nodes={self.nodes}, params={self.params},instances={self.instances})"

    def new(self, *args, params: Optional[Params] = None, **kwargs) -> Instance:
        """Create a component at the given nodes.

        R = Component("Res", ['P', 'N'], {'R': 1})
        R.inst(P=1, N=0, params = {'R': 0.5})
        R.inst([1, 0], {'R': 0.5})
        R.inst({'P':1, 'N': 0}, {'R': 0.5})

        If the keyword `ctx` is present, the instance is created under the provided context.

        Returns:
            The created Instance
        """
        if not args and not kwargs:
            raise ValueError("Nodes should be provided")

        ctx = kwargs.get("ctx", None)
        context = str(ctx) if ctx else None
        parameters: Params = params or {}

        if not kwargs.get("force", False):
            parameters = {**self.params, **parameters}

        def from_dict(supplied, nodes):
            node_dict = {k: v for k, v in supplied.items() if k in nodes}
            if len(node_dict) != len(nodes):
                raise NodeError(nodes, list(node_dict.keys()))
            return [node_dict[n] for n in self.nodes]

        if args:
            if isinstance(args[0], list):
                nodes: Nodes = args[0]
                if len(nodes) != len(self.nodes):
                    raise NodeError(len(self.nodes), len(nodes))
            if isinstance(args[0], dict):
                nodes = from_dict(args[0], self.nodes)
        else:
            nodes = from_dict(kwargs, self.nodes)

        return Instance(self.name, nodes, parameters, context)

    def add(self, other: Union[Instance, List[Instance]]):
        if isinstance(other, (list, set)):
            for o in other:
                other.ctx = self.name
                self.instances.append(other)
        else:
            other.ctx = self.name
            self.instances.append(other)

    def __add__(self, other: Instance):
        self.add(other)
        return self

    def subs(self, subs, pred=Callable[[Instance], bool]) -> "Subcircuit":
        """Substite a parameter name in the instances

        Args:
            pred: Predicate function to allow the substitution.
            **kwargs: List of keyword arguments for the substition.

        Example:
            subckt INV(IN, OUT)
            parameters w_inv=0.4
            M1 (...) NMOS w=0.4
            end
            s = subs(w="w_inv")
        """
        subckt = self.copy()

        for name, base_name in subs:
            for inst in subckt.instances:
                # if name in inst.params and pred_fn(inst):
                if pred and pred(inst):
                    inst.params[name] = base_name

        return subckt


#: Element of a Circuit
Element = Union[Directive, Instance, Subcircuit]


class Circuit:
    """A circuit corresponds to a design/schematic.

    Attributes:
        directives: List of raw SPICE directives
        subcircuits: List of registered subcircuits
        instances: List of component instances
        path: Path to the netlist file
        id_map: Dict containing the uids of each component

    .todo: Automatic registration of the subcircuits into the circuit.
    """

    def __init__(
        self,
        directives: Optional[List[Directive]] = None,
        subcircuits: Optional[List[Subcircuit]] = None,
        instances: Optional[List[Instance]] = None,
        path: Optional[PathLike] = None,
    ):
        self.directives: List[Directive] = directives or []
        self.subcircuits: List[Subcircuit] = subcircuits or []
        self.instances: List[Instance] = instances or []
        self.path = Path(path) if path else None
        self._id_map: Dict[str, int] = defaultdict(int)

    def __iter__(self):
        yield "instances", [dict(i) for i in self.instances]
        yield "subcircuits", [dict(s) for s in self.subcircuits]
        yield "directives", [dict(d) for d in self.directives]
        yield "path", self.path

    def __add_one(self, elem: Element):
        """Internal function to add an element"""
        if isinstance(elem, Subcircuit):
            if elem not in self.subcircuits:
                self.subcircuits.append(elem)
        if isinstance(elem, Directive):
            self.directives.append(elem)
        elif isinstance(elem, Instance):
            elem.uid = self._id_map[elem.name]
            self._id_map[elem.name] += 1
            self.instances.append(elem)

    def add(self, elem: Union[Element, List[Element]]):
        """Add an element to the circuit"""
        if isinstance(elem, (list, tuple)):
            for e in elem:
                self.__add_one(e)
        else:
            self.__add_one(elem)

    def check(self) -> bool:
        """Check that all subcircuits are registered

        Returns:
            True if all subcircuits are registered

        Todo:
            Maybe return None if correct and a list of names for unregistered circuits.
        """
        inst_names = set([i.name for i in self.instances])
        subckt_names = set([i.name for i in self.subcircuits])
        return subckt_names.issubset(inst_names)

    def __add__(self, elem: Union[Element, List[Element]]):
        """
        Todo:
            Make this return a new circuit instead of modifying in place
        """
        self.add(elem)
        return self
