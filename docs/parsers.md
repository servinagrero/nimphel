# Parsing netlists

Parsers allow reading a set of SPICE text formats and convert them into nimphel `Circuits`. Parsing is performed thanks to the [Lark](https://github.com/lark-parser/lark) library.

## Parsing SPICE netlists

In order to parse a netlist, a `Reader` object needs to be created first. A reader needs a Lark grammar and a transformer. Nimphel already comes with some predefined grammars. 

As of today the following parsers are implemented: `Spectre`. 
More grammars and parsers will be added in the future.

!!! info
    These grammars can be found in the `*.lark` files inside the `reader` directory.

The following examples shows how to create a `Reader` object and use it to parse a netlist file or a string.

```python title="Parsing a netlist"
from nimphel.reader import Reader

parser = Reader("grammar")

# Parse a netlist file
circuit = reader.read("/path/to/netlist")

netlist = """
M0 (0 1) R R=100k
...
"""

# Parse a string
circuit = reader.reads(netlist)
```

If the parsing was unsuccessful, the reader will return `None` and will print the exception. The following exceptions can be raised during parsing:

- `UnexpectedEOF`: Raised if unexpected end of file is found.
- `UnexpectedToken`: Raised if an unexpected token is found.
- `UnexpectedCharacters`: Raised if an unexpected character is found when parsing.

Lark allows creating custom `Transformers` that will take a tree (what lark parses) into a new tree where each component has been modified by an user defined function. It can be used for instance to parse text and create python objects directly. To specify the transformer used, provide the `transformer` parameter along with the transformer class. Nimphel already includes the transformer `ToCircuit` that will automatically create a circuit with instances, subcircuit definitions and SPICE directives.

To know more about transformers, please refer to the official [documentation](https://lark-parser.readthedocs.io/en/latest/visitors.html).


```python title="Specifying a transformer when parsing"
reader = Reader("spectre", transformer=CustomTransformer)

custom_circuit = reader.read("/path/to/netlist")
```

## Deserializing circuits

SPICE netlists are the base format of all SPICE simulators, but sometimes we may like to interface with some tools that do not understand this format. To solve this issue, we can create a custo reader class that overloads the `reads` and `read` method to deserialize data into a circuit object.

The following example shows how to create a `JsonReader` that will deserialize a circuit from a JSON file and create the resulting circuit. Since this reader overrides the `read` method, it should also take care of Exceptions that the deserializing process may raise.

```python title="Defining a custom deserializer"
import json

class JsonReader(Reader):
    def read(self, path):
        with open(path, "r") as fp:
            content = json.load(fp)
        return Circuit(**content)

circuit = JsonReader().read("/path/to/circuit.json")
```
