# Circuits

## Generation of a subcircuit from a circuit

```python
localnet = Circuit()
localnet.add(Mosfet(["out", "in", GND, GND], name="nmos"))
localnet.add(Mosfet(["out", "in", VDD, VDD], name="pmos"))
test = localnet.into_subckt("TEST_CTK", ["INPUT", "OUTPUT"], {})
```

## Global circuit

There is a global circuit called `netlist` that exists within nimphel.
