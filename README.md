# fgraph

A visualization of functions executed in a binary.

## Usage

./fgraph [sai]r | [s]p [save_name] [input_file] binary [args ...]

Options:

  - s - indicate a name for the save file of the graph
  
  - a - provide command line arguments into the binary (cannot be used with option p)
  
  - i - provide a file to redirect stdin (cannot be used with option p)
  
  - r - get a graph of the executed functions within a run of the binary (cannot be used with option p)
  
  - p - get a graph of the functions explicitly called in the assembly code (cannot be used with option r)
  
## Requirements

Bash

Python

GDB with Python support

Networkx
```bash
pip install networkx
```

GraphViz
```bash
sudo apt-get install graphviz libgraphviz-dev
```

pygraphviz
```bash
pip install pygraphviz
```
