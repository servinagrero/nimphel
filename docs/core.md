This section will show the different. It is important to state that since this framework is still in development, some mechanisms and classes could change in the future.

!!! note
    Although this framework is simulator agnostic, the next examples will be focused for the Spectre simulator.

## SPICE Directives

Directives refer to raw SPICE statements normally used to control the simulator. Directives need to be added to a circuit object to be added in the netlist.

Directives are created through the `Directive` class and can be created in 2 ways:

- A single string containing the raw directive
- The directive name and a dictionary containing the parameters of the directive. Usually, directives are formatted as `name param1=value param2=value ...`, depending on the simulator used.

When supplying a dictionary with the parameters of the directive, the value `None` can be used to indicate that a parameter should only use the key instead of the key value pair. The following examples show the different ways of definining directives.

```python title="Creating directives"
from nimphel import Directive, Circuit

# Raw string directive
Directive("global 0 gnd")
# global 0 gnd

# Directive with parameters
Directive("simulator", {"lang": "spectre"})
# simulator lang=spectre

# The info parameter is None
Directive(
    "modelParameter",
    {"info": None, "what": "models", "where": "rawfile"}
    )
# modelParameter info what=models where=rawfile

# Adding a directive to a circuit
d = Directive("global 0 gnd")
circuit = Circuit()
circuit.add(d)
```

It is important to keep in mind that directives are always created as the name and the dictionary of parameters when reading a circuit from a netlist file.

## Instances

Instances are one the the core constituents of SPICE and therefore this framework. As the name implies, they refer to specific instances of electronic components inside a SPICE netlist. The way instances are described depends on the SPICE specificiation used, but they usually follow this structure.

```text title="Instance in SPICE format"
M1 (GND VDD) NMOS vth=1.0
```

In nimphel, the previous instance would be created in the following manner:

```python title="Creating a simple instance"
from nimphel import Instance, Circuit

inst = Instance(
    name="NMOS", nodes=["GND", "VDD"],
    params={"vth": 1.0}, cxt=None,
    cap="M", uid=1, metadata=None
    )
Circuit().add(inst)
```

The `ctx` keyword allows defining the context under which an instance is created. If an instance is created at the top level (e.g. directly in the circuit) it defaults to `None`. However, when an instance is created as part of a subcircuit, the context is the name of the subcircuit. This allows us to create sort of a dependency graph of each of the components and subcircuits.

The metadata contains a dictionary of values that can be useful when translating components from and to different tools. By default, all instances have no metadata.

Instances can also be copied and modified once they have been created.

```python title="Copying and updating an instance"
nmos = Instance(
    name="NMOS", nodes=list("DGSB"),
    params={"vth": 1.0}, cxt=None,
    cap="M", uid=1, metadata=None
    )

pmos = nmos.copy()
pmos.name = "PMOS"
pmos.params["vth"] = -1.0
```

However, creating instances in this way can become cumbersome very quickly, specially if we are instanciating the same electronic component multiple times. The following section shows how to create components to allow creating multiple instances of the same component in a simple and reusable manner.

## Components

Components in nimphel can be seen as _instance generators_ for a desired electronic component. To create instances of the same type of component, a `Component` object needs to be created, that will be later used to create new instances. A `Component` needs the following parameters:

- The component name (e.g. _resistor_, _capacitor_, _nmos_, ...)
- A list containing the names of the nodes. The order is important when exporting to an actual netlist.
- A dictionary of default parameters. If not default parameters can be set up, an empty dictionary should be passed.

```python title="Creating a component"
from nimphel import Component

# No default parameters
nmos = Component("nmos", list("DGSB"), {})

# Width and length as default parameters
pmos = Component("pmos", list("DGSB"), {"w": 65e-9, "l": 100e-9})
```

### Creating Instances

Once a component has been generated, it can be directly used to spawn new instances. Each instance can be generated and customized in various ways. The following example provides some of the ways of generating instances of the `nmos` and `pmos` components that have been created in the previous example.

```python title="Creating instances from a component"
from nimphel import Component

nodes = ["Drain", "Gate", "Source", 0]

# Update the default parameters
pmos.new(nodes, params={'w': 30e-9})
# Instance(
#   name='nsvtlp',
#   nodes=["Drain", "Gate", "Source", 0],
#   params={'w': 30e-9, 'l': 100e-9},
#   ctx=None, cap=None, uid=None, metadata={}
# )

# Use only the parameter supplied
pmos.new(nodes, params={'w': 30e-9}, force=True)
# Instance(
#   name='nsvtlp',
#   nodes=["Drain", "Gate", "Source", 0],
#   params={'w': 30e-9},
#   ctx=None, cap=None, uid=None, metadata={}
# )

# Add a context to the instance
pmos.new(nodes, ctx="Subcircuit name")
# Instance(
#   name='nsvtlp',
#   nodes=["Drain", "Gate", "Source", 0],
#   params={'w': 65e-9, 'l': 100e-9},
#   ctx="Subcircuit name", cap=None, uid=None, metadata={}
# )

# Add metadata
pmos.new(nodes, metadata={'should_export': False})
# Instance(
#   name='nsvtlp',
#   nodes=["Drain", "Gate", "Source", 0],
#   params={'w': 65e-9, 'l': 100e-9},
#   ctx=None, cap=None, uid=None,
#   metadata={'should_export': False}
# )

# Create an instance with a desired uid
pmos.new(nodes, uid=42)
# Instance(
#   name='nsvtlp',
#   nodes=["Drain", "Gate", "Source", 0],
#   params={'w': 65e-9, 'l': 100e-9},
#   ctx=None, cap=None, uid=42, metadata={}
# )
```

The instance nodes can also be supplied as keyword argumets at the beginning of the `new` method. However, the instance parameters always need to be precedded by the `params` keyword.

```python title="Nodes as keyword arguments"
pmos.new(D="Drain", G="Gate", S="Source", B=0, params={'w': 30e-9})

# Nodes can be supplied in any order
pmos.new(B=0, S="Source", G="Gate", D="Drain")
```

If the number of nodes supplied to `new` does not match with the ones defined in the component, a `NodesError` exception is raised.

```python title="Creating instances from a component"
try:
    pmos.new([0])
except NodesError:
    print("We only supplied 1 node")
```

```python title="Creating a component from an instance"
from nimphel import Component

pmos = Component("pmos", list("DGSB"), {})
pmos_new = Component.from_instance(pmos.new([1, 2, 3, 0]))

assert pmos == pmos_new
```

## Models

Models are a 1 to 1 equivalence of SPICE models. They allow creating new components that inherit from some other components while having different model parameters. The following example shows how to create a model `MOD1` that inherits from `NPN`.

```text title="SPICE model declaration"
model MOD1 NPN (BF=50 IS=1E-13 VBF=50)
```

```python title="Creating a model"
m = Model("MOD1", "NPN", {'BF': 50, 'IS': 1e-13, 'VBF': 50})
```

## Subcircuits

A subcircuit is nimphel is also a 1 to 1 translation of SPICE subcircuits. They allow grouping a number of instances under in order to create a reusable component. Subcircuits, differently from components, need to be registered in a circuit for the simutator to keep track of the different components. This can be accomplished through the `add` method on a `Circuit` object.

The way to build a `Subcircuit` is almost identical to building a `Component`:

- The name of the subcircuit
- The list of nodes
- The parameters of the subcircuit

```python title="Registering a subcircuit"
from nimphel import Subcircuit

inv = Subcircuit("INV", ["in", "out", "vdd", "gnd"], {})

# Adding instances to the subcircuit
inv.add(pmos.new())
inv.add(nmos.new())

# The subcircuit is registered with the 2 instances
circuit.add(inv)

# These changes won't be seen by the circuit
inv.add(pmos.new())
```

We can create a `Component` from a subcircuit in order to create instances and prevent us from modifying the subcircuit. This is performed through the `Component.from_subcircuit` method.

```python title="Creating a component from a subcircuit"
comp = Component.from_subcircuit(inv)
```

We can perform parameter substitution of the instances of a subcircuit by using the `subs` method.

```python title="Parameter substitution"
inv = inv = Subcircuit("INV", ["in", "out", "vdd", "gnd"], {"w_inv": None})
inv.add(nmos.new(nodes, {'w': 0.4}))

inv_new = inv.subs(w="w_inv")
```

## Circuits

In nimphel, circuits are the main interface with SPICE netlists. Directives, Instances and Subcircuits are added to a circuit through the `add` method. A list of elements can be registered in one time by supplying the list directly. 

The `add` method is also overloaded as the `+` operator which creates a new copy of the circuit and the `+=` operator which modifies in place.

```python title="Creating a circuit"
from nimphel import Circuit

circuit = Circuit()

circuit.add(Directive(...))
circuit.add(Instance(...))
circuit.add(Subcircuit(...))

circuit.add([Instance(...) for i in range(100)])
```

The following [section](parsers.md) will show how to parse SPICE netlists to automatically create circuits and write these circuits to a plethora of SPICE specifications or user defined formats.
