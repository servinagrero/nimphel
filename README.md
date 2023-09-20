<div align='center'>
<img src="./docs/img/logo.svg" width="250px">
<h3>Netlist Invention and Manipulation with Python Embedded Language</h3>
</div>

[![Docs](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://servinagrero.github.io/nimphel)
[![LICENSE](https://img.shields.io/github/license/servinagrero/nimphel)](./LICENSE)

Nimphel is a generic, open-source framework tackling rapid design exploration for the generation of modular and parametric electronic designs that is able to work on any major simulator.

This framework was originally conceived from a set of utility functions designed to generate a SPICE netlist while altering the parameters of the different components as a way to bypass the limitations of some simulators when running process variability simulations at large scale. From these tools, this framework was conceived to provide an interface to SPICE that was as frictionless and simple as possible for other people to adapt and use while being powerful enough to generate modular and reusable circuits with ease.

# Installation

Nimphel can be installed by clonning the repository and using poetry to install the project.

```
$ git clone https://github.com/servinagrero/nimphel && cd nimphel
$ poetry install && poetry build
$ pip install .
```

# Usage

For a more in detail documentation of the framework, please take a look at the [documentation](https://servinagrero.github.io/nimphel).

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

## License

MIT License

Copyright © 2022 Sergio Vinagrero

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<div align='center'>
<a href="https://www.buymeacoffee.com/servinagrero"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" width="150px"></a>
</div>
