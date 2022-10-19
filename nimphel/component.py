#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
from dataclasses import asdict, dataclass
from itertools import repeat
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import nimphel

#: A net can be either a number or a user defined name
Net = Union[str, int]

#: A port is a list of nets that serve as a component's inputs and outputs
Ports = List[Net]

#: Value of a parameter
ParamValue = Union[float, int, str, None]

#: A parameter is a list of key value pairs
Params = Dict[str, ParamValue]

#: Coordinates of a circuit in an array. 1D or 2D.
Coords = Union[Tuple[int], Tuple[int, int]]

#: Mask to select ports
Mask = Tuple[Union[Net, Callable[[Coords], str]], ...]


@dataclass
class Model:
    """A model holds default parameters for a specific type of component."""

    name: str
    params: Dict[str, ParamValue]


def net() -> int:
    """Generate a new global net.

    The number of nets is increased in the global circuit.

    Returns:
        The new net.
    """
    nimphel.netlist.nets += 1
    return int(nimphel.netlist.nets - 1)


class Component:
    """Class to save component instances.

    There can be no two instances of the same component with the same id,
    except if one of them is inside a subcircuit.

    The name of the device is the first not null name in the list of names.
    The list of names han the following priority:

      1. User defined name.
      2. Model name.
      3. Name of the subclass.

    Attributes:
        num_id: Numeric id given to the instance.
        name: Name of the component instance.
        ports: List of ports of the component.
        params: Dict of parameters using the model parameters as default if provided.

    Raises:
        AttributeError: The list of ports is empty
    """

    def __init__(
        self,
        ports: Ports,
        params: Optional[Params] = None,
        name: Optional[str] = None,
        letter: Optional[str] = None,
        model: Optional[Model] = None,
    ):
        self._name = [name, model.name if model else None, type(self).__name__]
        self.letter = letter if letter else self.name[0].upper()

        if not ports:
            raise ValueError(f"Ports for {self.name} cannot empty.")
        self.ports = ports

        self.num_id = nimphel.netlist.instances[self.name]
        nimphel.netlist.instances[self.name] += 1

        self.model = model
        user_params = params if params else {}
        if model:
            self.params = {**model.params, **user_params}
        else:
            self.params = user_params

    @property
    def name(self) -> str:
        """Returns the name of the component.

        Returns:
            The actual name of the device.
        """
        return next(filter(bool, self._name), "")

    @name.setter
    def name(self, name: str):
        """The name is set as a user defined name."""
        self._name[0] = name

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Component:
        """Create a component from a Dictionaly."""
        model = data.get("model", None)
        if model:
            model = Model(**model)
        return cls(
            data["ports"],
            params=data.get("params", {}),
            name=data.get("name", None),
            letter=data.get("letter", None),
            model=model,
        )

    @classmethod
    def from_json(cls, json_str: str) -> Component:
        """Create a component from a JSON string."""
        data = json.loads(json_str)
        model = data.get("model", None)
        if model:
            model = Model(**model)
        return cls(
            data["ports"],
            params=data.get("params", {}),
            name=data.get("name", None),
            letter=data.get("letter", None),
            model=model,
        )

    def to_json(self) -> str:
        """Returns the string representation of the component."""
        return json.dumps(self.to_dict())

    def __pos__(self) -> Component:
        """Make a copy and increment the id of the new component.

        The component is copied using deepcopy.

        Returns:
            The new component with num_id increased by 1.
        """
        other = copy.deepcopy(self)
        other.num_id += 1
        nimphel.netlist.instances[self.name] += 1
        return other

    def loop(
        self, mask: Optional[Tuple[int, ...]] = None
    ) -> Tuple[Component, Component]:
        """Create a self loop of a component given a mask.

        Example:
            Given a component with ports [IN, VDD, OUT, GND] and mask (1, 0, 1, 0), loop will return a list of components with ports [IN, VDD, OUT, GND] and [OUT, VDD, IN, GND]

        Args:
            mask: Mask to select the two ports to loop. If None, use the first two ports.

        Returns:
            Tuple containing both elements of the loop.

        Raises:
            ValueError: The mask has more or less than two ports selected.
        """
        if len(self.ports) < 2:
            raise ValueError("Component cannot self loop as it only has one port.")

        if mask is None:
            mask = (1, 1) + (0,) * max(len(self.ports), 0)
        elif sum(mask) != 2:
            raise ValueError("Two ports are needed to create a self loop.")

        other = +self
        first = mask.index(1)
        second = mask.index(1, first + 1)
        other.ports[first], other.ports[second] = (
            other.ports[second],
            other.ports[first],
        )
        return (self, other)

    def __invert__(self) -> Tuple[Component, Component]:
        """Create a self loop of a component.
        Overloaded operator for ``loop``"""
        return self.loop()

    def __lshift__(self, val: int):
        """Shift the ports in the left direction."""
        self.ports = self.ports[:val] + self.ports[val:]

    def __rshift__(self, val: int):
        """Shift the ports in the right direction."""
        self.__lshift__(-val)

    def chain(
        self,
        val: Union[int, Tuple[Net, ...], Tuple[int, Callable[[int], str]]],
        mask: Optional[Mask] = None,
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

        If val is an int, chain `val` times as normal, that is
        (in, out) -> (out, net()) -> ... -> (net(), net())

        Only the global state keeps track of the updated ids, this means that the original component mantains it's id.

        Args:
            val:
            mask:

        Returns:
            List containing the chain of components.

        TODO:
          * Use the mask to select the ports
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
            if i != (nelem - 2):
                last_port, new_out = new_out, net()
            else:
                last_port, new_out = new_out, last_name()

        return components

    def __mul__(
        self, val: Union[int, Tuple[Net, ...], Tuple[int, Callable[[int], str]]]
    ) -> List[Component]:
        """Create components in a chain.
        Overloaded operator for ``chan``.
        """
        return self.chain(val)

    def parallel(self, val: int) -> List[Component]:
        """Create components in parallel.

        Components in parallel share the same input and output ports.

        Args:
            val: Number of components to create.

        Returns:
            List containing the components in parallel.
        """
        components = [self]
        for _ in range(1, val):
            new_comp = +components[-1]
            components.append(new_comp)

        return components

    def __or__(self, val: int) -> List[Component]:
        """Create components in parallel.
        Overloaded operator for ``parallel``"""
        return self.parallel(val)

    def fanout(self, val: int) -> List[Component]:
        """Create components with the same input and different output.

        Args:
            val: Number of components to create.

        Returns:
            List of components.
        """
        self.ports[-1] = net()
        components = [self]
        for _ in range(1, val):
            new_comp = +components[-1]
            new_comp.ports[-1] = net()
            components.append(new_comp)
        return components

    def __xor__(self, val: int) -> List[Component]:
        """Create components with the same input and different output.
        Overloaded operator for ``fanout``."""
        return self.fanout(val)

    def direct(self, val: int) -> List[Component]:
        """Create components with the different inputs and same output.

        The first port of the component used to call the method gets modified.

        Args:
            val: Number of components to create.

        Returns:
            List of components.
        """
        components = [self]
        for _ in range(1, val):
            new_comp = +components[-1]
            new_comp.ports[0] = net()
            components.append(new_comp)

        return components

    def __and__(self, val: int) -> List[Component]:
        """Create components with the different inputs and same output.
        Overloaded operator for ``direct``."""
        return self.direct(val)

    def to_dict(self) -> Dict[str, Any]:
        """Export a component to a dict"""
        model = None if not self.model else asdict(self.model)
        return {
            "letter": self.letter,
            "name": self.name,
            "id": self.num_id,
            "ports": self.ports,
            "model": model,
            "params": self.params,
        }


def simple_component(cls):
    """Wrapper to create components that are very simple.

    Args:
        cls: The class definition

    Returns:
        The class to generate the specified component.

    Todo:
        * Add safety guards for the number of ports.
    """
    cls_name = cls.__dict__.get("name", cls.__name__)
    cls_letter = cls.__dict__.get("letter", None)
    cls_model = cls.__dict__.get("model", None)
    def_params = cls.__dict__.get("defaults", {})

    def init(self, ports, params=None, model=None, name=None, letter=None):
        user_params = {} if params is None else params
        super(cls, self).__init__(
            ports,
            params={**def_params, **user_params},
            name=name or cls_name,
            letter=letter or cls_letter,
            model=model or cls_model,
        )

    setattr(cls, "__init__", init)
    return cls
