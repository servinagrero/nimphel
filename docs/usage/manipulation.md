# Manipulation

Supposing `python Res = R([VDD, net()], {"R": random.randint(10, 1_000)})`

## Chain components

Chained components start in the component input and generate a chain in the following way:

(in, out) -> (out, net()) -> ... (net(), net())

```python 
netlist.add(Res * 3)
```

## Components in parallel

Components in parallel share the same input and output ports.

```python 
netlist.add(Res | 5)
```

## Self loop

A self loop creates a copy of the component and reverses the order of the ports, that is, input is connected to output and viceversa.

```python 
netlist.add(~Res)
```

## Same input different output

```python 
netlist.add(Res ^ 10)
```

## Different input same output

```python
netlist.add(Res & 10)
```

## Manipulation on complex components

For components that are more complex, there are methods to defined the connections.
The ports for chains are defined using masks, that is, a tuple whose non null
positions mark the number of ports to chain. A chain will not work in this case with a Mosfet since the chain will be done, with the ports "out" and "GND". We need to define the chain using the first and second port.

```python
m = Mosfet(["out", "in", GND, GND], name="nsvtlp")
m.chain((1, 1, 0, 0), 3)
```

## Generation of arrays

Components can be generated in arrays. These arrays can be 1D or 2D.

```python
num_y = 3
num_x = 5

def ports_res(p):
    x, y = p
    return [f"Y_{y}", f"X_{x}"]

arr = array((3, 5), R(["", ""]), ports_fn=ports_res)

for y, x in np.ndindex(m.shape):
     print(m[y, x])

netlist.add(m)
```
