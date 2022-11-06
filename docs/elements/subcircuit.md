A subcircuit is a collection of basic components or other subcircuits.

## Creating a subcircuit

```{.py3 title="Example of creating an inverter"}
INV = Subckt("INV", ["in", "out"], {})
INV.add(Mosfet(["out", "in", GND, GND], name="nmos"))
INV.add(Mosfet(["out", "in", VDD, VDD], name="pmos"))
INV.fix()
```

Subcircuits can be *fixed* with the [`fix`][nimphel.subcircuit.Subckt.fix] metohd to prevent adding more components.

## Instanciating a subcircuit

A subcircuit can be instanciated by using the [`inst`][nimphel.subcircuit.Subckt.inst] method. This method returns a [`Component`][nimphel.component.Component] so we can manipulate the results as with any other component.

The same subcircuit can be instanciated multiple times with different ports or parameters.

```{.py3 title="Instanciating an inverter"}
inv = INV.inst(["input", net()], {})
```
