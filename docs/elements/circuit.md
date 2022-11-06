A [`circuit`][nimphel.circuit.Circuit] is a top level object. It allows the aggregation of multiple components.

The main difference between a subcircuit and a circuit is that the circuit also holds the definition of the subcircuits it contains.

## Creating a subcircuit

A circuit can be converted into a subcircuit by using the [`into_subckt`][nimphel.circuit.Circuit.into_subckt] method.

```{.py3 title="Example of creating an AND gate"}
and_gate = Circuit()
out_and = net()
and_gate.add(Mosfet(["A", VDD, "OUT", VDD], name="pmos"))
and_gate.add(Mosfet(["B", VDD, "OUT", VDD], name="pmos"))
and_gate.add(Mosfet(["B", "OUT", out_and, GND], name="nmos"))
and_gate.add(Mosfet(["A", out_and, GND, GND], name="nmos"))
AND_GATE = and_gate.into_subckt("AND", ["A", "B", "OUT"], {})

# Now we can create instances of AND_GATE
# gate = AND_GATE.inst([net(), net(), net()], {})
```


### Global circuit

There is a global circuit called ``netlist`` that exists within nimphel. This circuit behaves as the main SPICE netlist. **Component ids always refer to the global netlist.**


## Dependency graph

A dependency graph holds the different subcircuits and components that make up a circuit and the relationships between them.

```python
graph = netlist.to_graph()
generate_graph(graph)

# To view the graph we need to import some libraries
import matplotlib.pyplot as plt
plt.show()
```

## Number of instances

With the method [`count_intances`][nimphel.circuit.Circuit.count_instances] we can obtain a dictionary containing the names of all components instanciated in a circuit and their total number. This number is calculated from the dependency graph.

```python
instances = netlist.count_instances()
```

