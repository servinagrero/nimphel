#!/usr/bin/env python3

from typing import Tuple, Callable, Optional, List, Iterable, Union
from nimphel.component import Component, Net, Coords

import numpy as np


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


def make_array(
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
