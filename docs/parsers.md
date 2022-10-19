# Parsers

Parsers allow the generation of models automatically from files. Nimphel comes with some parsers by default. If some technology file is not supported file it's very easy to create your custom parser.

Parsing a definition file requires two things.

- The function ``parse_model_file()``
- The parser that will be used for the file.

The parser has the signature `#!python def parser(lib: TextIO) -> Dict[str, Model]`

```{.py3 title="Loading models from a YAML file"}
models = parse_model_file("/path/to/models.yaml", yaml_parser)

@simple_component
class NMosfet(Component):
    model = models['NMOS']
```

As of today the following parsers are implemented: ``eldo_parser()``, ``veriloga_parser()``, ``yaml_parser()``.

!!! info

    More parsers may be added in the future. The current parsers can be used as a refernce to create a custom parser.


## Models in YAML

The ``yaml_parser()`` allows reading models from a YAML file. Each document inside the file represents a single model.

A different YAML file can be created for a different technology, so that the same netlist can be created with the same code for different technologies just by changing the file.


```{.yaml title="Example of a YAML configuration" hl_lines="15"}
name: NMOS
params:
    w: 0.135
    nfing: 1
    mult: 1
    srcefirst: 1
    ngcon: 1
    mismatch: 1
    lpe: 0
    dnoise_mdev: 0
    dmu_mdev: 0
    dvt_mdev: 0
    numcos: 1
    numcod: 1
--- # Used to separate models
name: PMOS
params:
    from: NMOS # Use the parameters of NMOS
    w: 0.27 # Parameters can be updated
    new_val: 42 # New parameters can be added
    mismatch: ~ # Values can also be deleted
```

The second document inside the YAML file shows the functionalities added to the file.

- Params can be copied from another defined model by using the key ``from``.
- Parameters can be added, updated or even removed when referencing another model.
