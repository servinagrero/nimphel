<figure markdown>
  ![logo](img/logo.svg){ width="150" }
</figure>

# Welcome to NIMPhEL's documentation

Due to the complex specifications of current electronic systems, design decisions need to be explored automatically. However, the exploration process is a complex task given the plethora of design choices such as the selection of components, number of components, operating modes of each of the components, connections between the components and variety of ways in which the same functionality can be implemented. Nimphel is a generic, open-source framework tackling rapid design exploration for the generation of modular and parametric electronic designs that is able to work on any major simulator.

!!! warning
    This project is still in development so expect breaking changes.
    Ideas and contributions are more than welcome.

# Citation

If you use this software, please consider citing the software through the following publication.

> Vinagrero Gutiérrez, Sergio, Giorgio Di Natale, and Elena-Ioana Vatajelu. 2023. "Python Framework for Modular and Parametric SPICE Netlists Generation" Electronics 12, no. 18: 3970. https://doi.org/10.3390/electronics12183970

Or use the following Bibtex source

```text
@Article{electronics12183970,
AUTHOR = {Vinagrero Gutiérrez, Sergio and Di Natale, Giorgio and Vatajelu, Elena-Ioana},
TITLE = {Python Framework for Modular and Parametric SPICE Netlists Generation},
JOURNAL = {Electronics},
VOLUME = {12},
YEAR = {2023},
NUMBER = {18},
ARTICLE-NUMBER = {3970},
URL = {https://www.mdpi.com/2079-9292/12/18/3970},
ISSN = {2079-9292},
DOI = {10.3390/electronics12183970}
}
```

## Documentation structure

This documentation is structured in the following way:

- The [getting started](starting.md) section describes the rationale, installation instructions and road map of this project.
- In the [core](core.md) section, the main mechanics and utilities are described.
- How to read netlists and serialize circuits is described in the [parsing](parsers.md).
- How to serialize and export circuits to different formats and SPICE specifications is described in the [exporting](writers.md).
- Some use cases of this project are displayed in the last [section](usage.md).
