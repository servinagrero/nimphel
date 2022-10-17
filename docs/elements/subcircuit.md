# Creating a subcircuit

```{.py3 title="Example of creating an inverter"}
INV = Subckt("INV", ["in", "out"], {})

INV.add(Mosfet(["out", "in", GND, GND], name="nmos"))
INV.add(Mosfet(["out", "in", VDD, VDD], name="pmos"))

INV.fix() # Prevents the subcircuit of adding more components
```

# Instanciating a subcircuit

A subcircuit can be instanciated by usig the 'inst()' method. This method takes the same arguments as ``Component``.

```{.py3 title="Instanciating an inverter"}
inv = INV.inst(["input", net()], {})
```
