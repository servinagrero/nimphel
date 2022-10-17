# Manipulation

The manipulation of components is one of the key features of nimphel. Nimphel makes use of the basic mathematical operators to manipulate components.

## Chain

Chained components start in the component input and generate a chain where the input of a new component is the output of the previous one. The operator ``*`` is used to chain components.

The ports of chained components follow this behaviour:
```text
(in, out) -> (out, net()) -> ... (net(), net())
```

```{.py3 title="Example of chained components"}
Res = R([GND, net()])
netlist.add(Res * 3)

# Will produce 3 resistances with the ports:
# (GND, 1), (1, 2), (2, 3)
```

## Parallel

Components in parallel share the same input and output. The operator ``|`` is used to create components in parallel.

The ports of components in parallel follow this behaviour:
```text
(in, out) -> (in, out) -> ... (in, out)
```

```{.py3 title="Example of components in parallel"}
Res = R([GND, net()])
netlist.add(Res | 3)

# Will produce 3 resistances with the ports
# (GND, 1), (GND, 1), (GND, 1)
```

## Self loop

A self loop creates a copy of the component and reverses the order of the ports, that is, input is connected to output and viceversa. The operator ``~`` is used to create self loops.

The ports of components in self loop this behaviour:
```text
(in, out) -> (out, in)
```

```{.py3 title="Example of self looped components"}
Res = R([GND, net()])
netlist.add(~Res)

# Will produce 2 resistances with the ports
# (GND, 1), (1, GND)
```

## Fan out

Components in fan out share the same input but have a different output port each. The operator ``^`` is used to create fan outs.

The ports of components in fan out follow this behaviour:
```text
(in, out) -> (in, net()) -> ... (in, net())
```

```{.py3 title="Example of components in fan out"}
Res = R([GND, net()])
netlist.add(Res ^ 3)

# Will produce 3 resistances with the ports
# (GND, 1), (GND, 2), (GND, 3)
```

## Direct

Components that are directed, have the same output but have a different input each. It's behaviour is the opposite of `fan out`. The operator ``&`` is used to create self loops.

The ports of components in fan out follow this behaviour:
```text
(in, out) -> (net(), out) -> ... (net(), out)
```

```{.py3 title="Example of directed components."}
Res = R([GND, net()])
netlist.add(Res & 3)

# Will produce 3 resistances with the ports
# (2, 1), (3, 1), (4, 1)
```

## Complex manipulation

For components that are more complex, there are methods to defined the connections.
The ports for chains are defined using masks, that is, a tuple whose non null
positions mark the number of ports to chain. A chain will not work in this case with a Mosfet since the chain will be done, with the ports "out" and "GND". We need to define the chain using the first and second port.

```python
m = Mosfet(["out", "in", GND, GND], name="nmos")
m.chain((1, 1, 0, 0), 3)
m.parallel((1, 1, 0, 0), 3)
m.self_loop((1, 1, 0, 0), 3)
m.fanout((1, 1, 0, 0), 3)
m.direct((1, 1, 0, 0), 3)
```

### Getting ports

### Setting ports


## 1D and 2D Arrays

Components that follow a 1D or 2D configuration can be instanciated quickly by usig the function ``array``. This function takes 3 arguments.

- Tuple containing the 1D or 2D dimensions of the array. **The coordinates are given as (Y, X)**
- The component instance that will be used to fill the array.
- If provided, a function that will received the coordinates of the component and will return the ports of that component.


```{.py3 title="Generating a 1D array of resistances"}
arr = array((5, ), R(["", ""]), ports_fn=lambda c: [f'X_{c[0]}'])
netlist.add(m)
```


```{.py3 title="Generating a 2D array of resistances"}
def ports_res(p):
    x, y = p
    return [f"Y_{y}", f"X_{x}"]

arr = array((3, 5), R(["", ""]), ports_fn=ports_res)

netlist.add(m)
```

The array is created by using numpy, so we have access to numpy tools.
```{.py3 title="Printing an array of components."}
for y, x in np.ndindex(m.shape):
     print(m[y, x])
```
