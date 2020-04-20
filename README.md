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
