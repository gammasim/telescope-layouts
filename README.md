# telescope-layouts

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/89a10451ff2f4b2485e730e650b44a81)](https://app.codacy.com/gh/gammasim/telescope-layouts?utm_source=github.com&utm_medium=referral&utm_content=gammasim/telescope-layouts&utm_campaign=Badge_Grade_Dashboard)

Tools to calculate and plot array layouts and telescope positions

## Install

```bash
conda env create -f environment.yml
conda activate telescopes
```

## Examples

Print a simple list of telescopes in all three coordinate systems

```python
python ./print_layout.py --telescope_list=data/telescope_positions_south.ecsv --layout_list=data/layouts_south.yaml
```

Compare two list of telescopes:

Compare positions:
```python
python compare_layouts.py --telescope_list_1=data/telescope_positions_south.ecsv --telescope_list_2=data/SB.ecsv  --coordinatesystem="utm"
```

Compare altitude of telescopes (print only if differences are >1m)
```python
python compare_layouts.py --telescope_list_1=data/telescope_positions_south.ecsv --telescope_list_2=data/SB2.ecsv  --coordinatesystem="altitude" --tolerance=1.
```
