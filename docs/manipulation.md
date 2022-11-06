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

A component can also be chained by using a tuple containing the fields `(num components, last net name)` as follows:

```{.py3 title="Chained components with named output"}
Res = R([GND, net()])
netlist.add(Res * (3, "OUT"))

# Will produce 3 resistances with the ports:
# (GND, 1), (1, 2), (2, "OUT")
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

The ports of components in self loop follow this behaviour:
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

For components that are more complex, there are methods to perform the manipulations.
The ports for chains are defined using masks, that is, a tuple whose non null
positions mark the number of ports to manipulate. 

As an example, we cannot chain a Mosfet Mosfet since the chain will be done with the ports "out" and "GND". We need to define the chain using the first and second port.

```python
m = Mosfet(["out", "in", GND, GND], name="nmos")
m.chain((1, 1, 0, 0), 3)
m.parallel((1, 1, 0, 0), 3)
m.self_loop((1, 1, 0, 0), 3)
m.fanout((1, 1, 0, 0), 3)
m.direct((1, 1, 0, 0), 3)
```

### Getting ports

In order to create connections between components that have been manipulated, there are two functions: [`port_getter`][nimphel.utils.port_getter] and [`port_setter`][nimphel.utils.port_setter].

```{.py3 title="Example of getting ports"}
chains = CustomSubckt.inst(["INPUT", "OUT"], {}) ^ 3
chains_out = port_getter(chains, (0, 1), flatten=True)
```

The argument `flatten` removes null values from the ports and returns a tuple containing just the values of the ports requested.

```{.py3 title="Usage of the flatten argument"}
chains_out = port_getter(chains, (0, 1), flatten=False)
# chains_out = [(0, 1), (0, 2), (0, 3)]

chains_out = port_getter(chains, (0, 1), flatten=True)
# chains_out = [(1,), (2,), (3,)]
```

### Setting ports

The function [`port_setter`][nimphel.utils.port_setter] allows to set the ports of a list of components. It receives a list of components and a list of masks, whose values correspond to the final ports of each component


```{.py3 title="Example of setting ports"}
# Components is a list of 3 components with two ports
mask = [("INPUT", "OUT_1"), ("INPUT", "OUT_3"), ("INPUT", "OUT_3")]
port_setter(components, mask)
```

## 1D and 2D Arrays

Components that follow a 1D or 2D configuration can be instanciated by using the function ``make_array``. This function takes 3 arguments.

- Tuple containing the 1D or 2D dimensions of the array. 
    - **For 2D arrays, the coordinates are given as `(Y, X)`**
    - For 1D arrays the dimension `(Y,)` represents the length of the array.
- The component instance that will be used to fill the array.
- If provided, a function whose input is the coordinates of the component returns the ports of that component.


```{.py3 title="Generating a 1D array of resistances"}
def ports_res(p):
    return [f'X_{c[0]}', GND]
    
arr = make_array((5, ), R(["", ""]), ports_fn=ports_res)
netlist.add(arr)
```

```{.py3 title="Generating a 2D array of resistances"}
def ports_res(p):
    x, y = p
    return [f"Y_{y}", f"X_{x}"]

arr = array((3, 5), R(["", ""]), ports_fn=ports_res)
netlist.add(arr)
```

The array is created by using numpy, so we have access to numpy tools.

```{.py3 title="Printing an array of components."}
for y, x in np.ndindex(m.shape):
     print(arr[y, x])
```

## Complex example


```{.py3 title="Creation of a RO PUF."}
class Mosfet(Component):
    def __init__(self, ports: Ports, params: Optional[Params] = None, name=None):
        parameters = params if params else {}
        super(Mosfet, self).__init__(
            ports, parameters, model=NMOS, name=name, letter="M"
        )


@simple_component
class VCounter(Component):
    """Verilog A Counter"""

    name = "counter"
    letter = "I"
    model = models["counter"]


@simple_component
class C(Component):
    defaults: Params = {"C": 1e3, "T": None}


inv = Subckt(
    "INV",
    ["vdd", "gnd", "in", "out"],
    {"vthp": None, "vthn": None, "lp": 0.06, "ln": 0.06},
)

inv.add(Mosfet(["out", "in", GND, GND], name="nsvtlp"))
inv.add(Mosfet(["out", "in", VDD, VDD], name="psvtlp"))
inv.fix()

and_gate = Circuit()
out_and = net()
and_gate.add(Mosfet(["A", VDD, "OUT", VDD], name="psvtlp"))
and_gate.add(Mosfet(["B", VDD, "OUT", VDD], name="psvtlp"))
and_gate.add(Mosfet(["B", "OUT", out_and, GND], name="nsvtlp"))
and_gate.add(Mosfet(["A", out_and, GND, GND], name="nsvtlp"))
AND_GATE = and_gate.into_subckt("AND", ["A", "B", "OUT"], {})

netlist.add(AND_GATE.inst([net(), net(), net()]))

N_RO_PER_CHAIN = 5
N_CHAINS = 3

MUX = Subckt("MUX", [f"IN_{d}" for d in range(N_CHAINS)] + ["Sel", "OUT"], {})
INV = Subckt("INV", ["in", "out"], {})

INV.add(Mosfet(["out", "in", GND, GND], name="nsvtlp"))
INV.add(Mosfet(["out", "in", VDD, VDD], name="psvtlp"))
INV.fix()

inv = INV.inst(["in_chain", net()], {})

chain = Circuit()

chain.add(inv * (N_RO_PER_CHAIN, "OUT"))
ro_chain = chain.into_subckt("RO_CHAIN", ["in_chain", "OUT"], {})

chains = ro_chain.inst(["INPUT", "OUTStable"], {}) ^ N_CHAINS
chains_out = port_getter(chains, (0, 1), flatten=True)
netlist.add(chains)

counters = VCounter([""]) | N_CHAINS
port_setter(counters, chains_out)
netlist.add(counters)
```
