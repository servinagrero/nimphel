#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
from collections import ChainMap
from dataclasses import asdict, dataclass
from typing import Callable, Dict, List, Optional, Tuple, Union

import numpy as np

import nimphel

#: A net can be either a number or a user defined name
Net = Union[str, int]

#: A port is a list of nets that serve as a component's inputs and outputs
Ports = List[Net]

#: Value of a parameter
ParamValue = Union[float, int, str, None]

#: A parameter is a list of key value pairs
Params = Dict[str, ParamValue]


@dataclass
class Model:
    "A model holds default parameters for a specific type of component."
    name: str
    params: Dict[str, ParamValue]


def net() -> int:
    """Generate a new net.

    TODO: When we generate a local netlist, this function still returns a counter related to the global one. If the local netlist is converted into a subcircuit, it shouldn't matter as the nets inside the subcircuit definition are independent. Still, it would be a good idea to investigate.

    Returns:
      The new net.
    """
    nimphel.netlist.nets += 1
    return int(nimphel.netlist.nets - 1)


class Component:
    """Class to save component instances.

    There can be no two instances of the same component with the same id,
    except if one of them is inside a subcircuit.

    The names are stored in a list to keep the following priority:

    1. User defined name.
    2. Model name.
    3. Name of the subclass.

    Attributes:
      num_id: Numeric id given to the instance.
      name: Name of the component instance.
      ports: List of ports of the instance.
      params: Dict of parameters defaulting to the model parameters if provided.

    Raises:
        AttributeError: The list of ports is empty
    """

    def __init__(
        self,
        ports: Ports,
        params: Optional[Params] = None,
        name: Optional[str] = None,
        model: Optional[Model] = None,
    ):
        self._name = [name, model.name if model else None, type(self).__name__]

        if not ports:
            raise AttributeError(f"Ports for {self.name} are empty.")

        self.num_id = nimphel.netlist.instances[self.name]
        nimphel.netlist.instances[self.name] += 1

        self.ports = ports
        user_params = params if params else {}
        self.params: ChainMap[str, ParamValue] = ChainMap(
            user_params, model.params if model else {}
        )

    @property
    def name(self):
        """Returns the name of the component.

        The name of the device is the first not null name in the list of names.
        """
        return next(filter(bool, self._name))

    @name.setter
    def name(self, name: str):
        """The name is set as a user defined name."""
        self._name[0] = name

    def __str__(self) -> str:
        params = {**self.params}
        d = {
            "name": self.name,
            "id": self.num_id,
            "ports": self.ports,
            "params": self.params.maps,
        }
        return json.dumps(d)

    def __pos__(self) -> Component:
        """Make a copy and increment the num_id"""
        other = copy.deepcopy(self)
        other.num_id += 1
        nimphel.netlist.instances[self.name] += 1
        return other

    def __invert__(self) -> Tuple[Component, Component]:
        """Create a loop of a component"""
        other = +self
        other.ports = self.ports[::-1]
        return (self, other)

    def loop(
        self, ports_mask: Optional[Tuple[Net]] = None
    ) -> Tuple[Component, Component]:
        """Create a loop of a component give a port mask.

        Args:
          ports_mask: Mask to select the two ports to loop. if not supplied, it's assumed the
          component has two ports and the loop is created by flipping the ports.

        Example:
          ports: IN, VDD, OUT, GND
          mask: (1, 0, 1, 0)

          Returns two components with ports:
          IN, VDD, OUT, GND
          OUT, VDD, IN, GND
        """
        if ports_mask is None:
            return ~self

        if sum(ports_mask) != 2:
            raise ValueError("Cannot create loop for more than two ports.")

        other = +self
        first = ports_mask.index(1)
        second = ports_mask.index(1, first + 1)
        other.ports[first], other.ports[second] = (
            other.ports[second],
            other.ports[first],
        )
        return (self, other)

    def __lshift__(self, val: int):
        """Shift the ports and rotates"""
        self.ports = self.ports[:val] + self.ports[val:]

    def __rshift__(self, val: int):
        self.__lshift__(-val)

    def chain(
        self, val: Union[int, Tuple[int, Net]], port_mask: Optional[Tuple] = None
    ) -> List[Component]:
        """If val is a tuple, various things can happen.
        First, len(tuple) == len(comp.ports)

        If the value is 0, that port is fixed and does not change.
        If the value is 1, that port is used for chaining, from left to right.
        comp * (0, 0, 1, 1)

        Following the left to right rule, if the values are strings, they will be used for the first and last name of the nets.
        comp * (0, 0, "first", "out")

        The user can also supply a function instead of a str or int. The function will be given
        the index of the chain and should return a net.

        comp * (0, 0, "Input", lambda d: f'net{d}')
        """
        components = [self]
        if isinstance(val, tuple):
            nelem = val[0]
            if isinstance(val[1], Callable):
                last_name = val[1]
            else:
                last_name = lambda: val[1]
        else:
            nelem = val
            last_name = net

        _, *unchanged, last_port = self.ports

        new_out = net()
        for i in range(1, nelem):
            new_ports = [last_port, *unchanged, new_out]
            new_comp = +components[-1]
            new_comp.ports = new_ports
            components.append(new_comp)
            if i != nelem - 2:
                last_port, new_out = new_out, net()
            else:
                last_port, new_out = new_out, last_name()

        return components

    def __mul__(
        self, val: Union[int, Tuple[int, Net], Tuple[int, Callable[[int], str]]]
    ) -> List[Component]:
        """Components in series.

        If val is an int, chain `val` times as normal, that is
        (in, out) -> (out, net()) -> ... -> (net(), net())

        Component needs to be deepcopied to copy also all methods made by the user.
        If not, self refers always to this object and not the new generated one.

        WARNING: Only the global state keeps track of the updated ids.
        The component mantains it's original id
        """
        return self.chain(val, port_mask=None)

    def __or__(self, val: int) -> List[Component]:
        "Components in parallel."
        components = [self]
        for i in range(1, val):
            new_comp = +components[-1]
            components.append(new_comp)

        return components

    def __xor__(self, val: int) -> List[Component]:
        "Same input different output."
        self.ports[-1] = net()
        components = [self]
        for _ in range(1, val):
            new_comp = +components[-1]
            new_comp.ports[-1] = net()
            components.append(new_comp)
        return components

    def __and__(self, val: int) -> List[Component]:
        "Different input same output."
        self.ports[0] = net()
        components = [self]
        for i in range(1, val):
            new_comp = +components[-1]
            new_comp.ports[0] = net()
            components.append(new_comp)

        return components

    def to_dict(self) -> Dict[str, str]:
        maps = self.params.maps
        return {
            "name": self.name,
            "id": self.num_id,
            "ports": self.ports,
            "params": {**maps[0], **maps[1]},
        }

    def to_json(self) -> str:
        """Export a component to a JSON string."""
        return json.dumps(self.to_dict())


def simple_component(cls):
    """Wrapper to create components that are very simple.

    Args:
      cls: The class definition

    Returns:
      The class with custom init to generate components.

    TODO: Add safety guards with the number of ports
    """
    cls_name = cls.__dict__.get("name", cls.__name__)
    cls_model = cls.__dict__.get("model", None)
    def_params = cls.__dict__.get("defaults", {})

    def init(self, ports, params=None, model=None, name=None):
        user_params = {} if params is None else params
        super(cls, self).__init__(
            ports,
            {**def_params, **user_params},
            name=name or cls_name,
            model=model or cls_model,
        )

    setattr(cls, "__init__", init)
    return cls


def port_getter(
    ports_mask: Tuple[Net, ...], comps: List[Component], flatten=False
) -> List[Tuple[Net]]:
    """Obtain the ports of a list of components based on a mask.

    Args:
      ports_mask: Tuple containing the ports to obtain. A value of 1 in a position means to extract that value and 0 means to ignore it.
      comps: List of components.
      flatten: If True, return only non null values.

    Returns:
       List of tuples of ports.
    """
    ports: List[Tuple[Net]] = []
    for c in comps:
        p = map(lambda pair: pair[1] if pair[0] else 0, zip(ports_mask, c.ports))
        if flatten:
            ports.append(tuple(filter(bool, p)))
        else:
            ports.append(tuple(p))

    return ports


def port_setter(comp: Component, ports_mask: Optional[Tuple[Net]] = None):
    """
    Args:
      comp: Component instance to set the ports.
      ports_mask: Mask of ports to change. A string in a position will change the original port to the value in the mask at that position.

    Example:
        comp.ports = [ "vdd", "in", "out", "gnd"]
        mask = ("INPUT", 0, 0, "OUT")
    """
    if ports_mask is None:
        mask: Tuple[Net] = (1,) * len(comp.ports)
    else:
        if len(ports_mask) != len(comp.ports):
            raise KeyError("Wrong mask given")
        mask = ports_mask

    new_ports = map(lambda p: p[0] or p[1], zip(mask, comp.ports))
    comp.ports = list(new_ports)


def array(
    size: Tuple[int, int],
    comp: Component,
    ports_fn: Optional[Callable[[Tuple[int]], Net]] = None,
) -> np.ndarray:
    """Create a 1D or 2D array of components.

    If ports_fn is supplied, it is used to assign the ports based on the cordinates of the component.

    Args:
      size: Tuple containing (y,x) or (x,) dimensions.
      comp: Component instance to create the array.
      ports_fn: Function to assign the ports. The function should accept a list
      with as many elements as

    """

    m = np.zeros(size, dtype=Component)
    if ports_fn is None:
        ports_fn = lambda c: comp.ports

    last_comp = comp
    if len(size) == 2:
        for y, x in np.ndindex(m.shape):
            new_comp = +last_comp
            new_comp.ports = ports_fn([y, x])
            m[y, x] = new_comp
            last_comp = new_comp
    else:
        for x in np.ndindex(m):
            new_comp = +last_comp
            new_comp.ports = ports_fn([x])
            m[x] = new_comp
            last_comp = new_comp

    return m
