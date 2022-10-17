# Creating a subcircuit

```{.py title="Example of creating an AND gate"}
and_gate = Circuit()
out_and = net()
and_gate.add(Mosfet(["A", VDD, "OUT", VDD], name="pmos"))
and_gate.add(Mosfet(["B", VDD, "OUT", VDD], name="pmos"))
and_gate.add(Mosfet(["B", "OUT", out_and, GND], name="nmos"))
and_gate.add(Mosfet(["A", out_and, GND, GND], name="nmos"))
AND_GATE = and_gate.into_subckt("AND", ["A", "B", "OUT"], {})
```

## Global circuit

There is a global circuit called `netlist` that exists within nimphel.


## Dependency graph

```python
graph = netlist.to_graph()
generate_graph(graph)
```

## Number of instances

```python
netlist.coutn_instances()
```

