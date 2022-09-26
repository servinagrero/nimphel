# Subcircuits

```python
inv = Subckt(
    "INV",
    ["vdd", "gnd", "in", "out"],
    {"vthp": None, "vthn": None, "lp": 0.06, "ln": 0.06},
)
inv.add(Mosfet(["out", "in", GND, GND], name="nmos"))
inv.add(Mosfet(["out", "in", VDD, VDD], name="pmos"))
inv.fix()
```
