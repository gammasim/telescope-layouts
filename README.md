# telescope-layouts

Tools to calculate and plot array layouts and telescope positions

## Install:

```
conda env create -f environment.yml
conda activate telescopes
```

## Examples

Print a simple list of telescopes in all three coordinate systems

```
python ./print_layout.py --telescope_list=data/telescope_positions_south.ecsv --layout_list=data/layouts_south.yaml
```
