#!/usr/bin/env python3

from __future__ import annotations

import copy
import json
from collections import ChainMap
from dataclasses import asdict, dataclass
from itertools import repeat
from typing import Any, Callable, Dict, Iterable, List, Optional, Sized, Tuple, Union

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

        self.num_id = nimphel.netlist.instances[self.name]
        nimphel.netlist.instances[self.name] += 1

        self.ports = ports
        self.params: ChainMap[str, ParamValue] = ChainMap(
            params if params else {}, model.params if model else {}
        )

    @property
    def name(self) -> str:
        """Returns the name of the component.

        Returns:
            The actual name of the device.
        """
        return next(filter(bool, self._name))

    @name.setter
    def name(self, name: str):
        """The name is set as a user defined name."""
        self._name[0] = name

    def __str__(self) -> str:
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
        maps = self.params.maps
        return {
            "letter": self.letter,
            "name": self.name,
            "id": self.num_id,
            "ports": self.ports,
            "params": {**maps[0], **maps[1]},
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
            {**def_params, **user_params},
            name=name or cls_name,
            letter=letter or cls_letter,
            model=model or cls_model,
        )

    setattr(cls, "__init__", init)
    return cls


def get_port(
    comp: Component, mask: Tuple[Net, ...], flatten: bool = False
) -> Tuple[Net, ...]:
    """Get a port from a component given a mask.

    This function serves as a helper for ``port_getter``.

    Example:

        Given a component with ports [in, out, VDD] and a mask (1, 0, 0), get_port will return (in, 0, 0). If flatten is True, the result would be (in,).

    Args:
        comp: Component to obtain the ports from.
        mask: Mask to select the ports to obtain.
        flatten: If True, reduce the ports to only the selected ones.

    Returns:
        The tuple containing the ports selected.
    """
    res = map(lambda pair: pair[1] if pair[0] else 0, zip(mask, comp.ports))
    if flatten:
        return tuple(filter(bool, res))
    return tuple(res)


def port_getter(
    comps: Union[Component, Iterable[Component]],
    mask: Tuple[Net, ...],
    flatten: bool = False,
) -> Union[Tuple[Net, ...], List[Tuple[Net, ...]]]:
    """Obtain the ports of a list of components based on a mask.

    This functions automatically maps the function get_port if comps is a list of components. See ``get_port`` to understand how to use the mask.

    Args:
        mask: Tuple containing the ports to obtain.
        comps: Component or list of components.
        flatten: If True, return only the ports requested.

    Returns:
       List of tuples of ports.
    """
    if isinstance(comps, Iterable):
        ports = map(lambda comp: get_port(comp, mask, flatten), comps)
        return list(ports)
    return get_port(comps, mask, flatten)


def set_port(comp: Component, mask: Optional[Tuple[Net, ...]] = None):
    """Modify the ports of a component given a mask.

    The mask is a tuple containing 0 or a string:

        * 0 to keep the original value.
        * A string denoting the new port name.

    This functions serves as a helper for ``port_setter``.

    Example:
        Given a component with ports [vdd, in, out, gnd] and a mask ("INPUT", 0, 0, "OUT"), the ports of the component will be changed to [INPUT, in, out, OUT]

    Args:
        comp: Component to modify.
        mask: Optional mask of ports to modify. If mask is None, do nothing.

    Raises:
        ValueError: The mask length is not equal to the number of ports..
    """
    if mask and len(mask) != len(comp.ports):
        raise ValueError("Wrong mask given")

    if mask:
        comp.ports = list(map(lambda p: p[0] or p[1], zip(mask, comp.ports)))


def port_setter(
    comps: Union[Component, Iterable[Component]],
    mask: Optional[Union[List[Tuple[Net, ...]], Tuple[Net, ...]]] = None,
):
    """Modify the ports of a component or list of components given a mask.

    Args:
      comp: Component or list of components.
      mask: Mask of ports to change.

    Raises:
      ValueError: When a single component is given but a list of masks is supplied.
      ValueError: When the number of masks does not match the number of components.
    """

    if isinstance(comps, Component):
        if mask and isinstance(mask, Iterable):
            raise ValueError("Mask needs to be a single tuple.")
        set_port(comps, mask)
    else:
        if mask is None:
            list(map(set_port, comps, repeat(mask)))
        elif mask and len(comps) != len(mask):
            raise ValueError("Components and mask need to be the same length")
        else:
            list(map(set_port, comps, mask))


def array(
    size: Tuple[int, ...],
    comp: Component,
    ports_fn: Optional[Callable[[Coords], List[Net]]] = None,
) -> np.ndarray:
    """Create a 1D or 2D array of components.

    To modify the ports of each component upon creation, the parameters `ports_fn` can be used. This functions accepts the coordinates of the component as a tuple and should return a list containing the ports of the component. If `ports_fn` is None, the ports are the same as the ones in `comp`.

    Args:
        size: Tuple containing (y,x) or (x,) dimensions.
        comp: Component instance to create the array.
        ports_fn: Function to assign the ports. The function accepts just a tuple containing the coordinates of the component in the array.

    Returns:
       The array with the component instances.
    """

    arr = np.zeros(size, dtype=Component)
    if ports_fn is None:
        ports_fn = lambda c: comp.ports

    last_comp = comp
    for coord in np.ndindex(arr.shape):
        new_comp = +last_comp
        new_comp.ports = ports_fn(tuple(coord))
        arr[coord] = new_comp
        last_comp = new_comp

    return arr
