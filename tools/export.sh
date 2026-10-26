#!/usr/bin/env bash
set -euo pipefail
root_dir="$(cd "$(dirname "$0")/.." && pwd)"
for name in controller reader emitters; do
 board="$root_dir/hardware/$name/$name.kicad_pcb"
 mkdir -p "$root_dir/hardware/$name/manufacturing" "$root_dir/preview/schematic-$name"
 kicad-cli sch export svg -o "$root_dir/preview/schematic-$name/" "$root_dir/hardware/$name/$name.kicad_sch"
 kicad-cli sch export netlist --format kicadxml -o "$root_dir/verification/$name.net.xml" "$root_dir/hardware/$name/$name.kicad_sch"
 kicad-cli pcb export gerbers -l F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts --subtract-soldermask -o "$root_dir/hardware/$name/manufacturing/" "$board"
 kicad-cli pcb export drill --excellon-separate-th -o "$root_dir/hardware/$name/manufacturing/" "$board"
 kicad-cli pcb export svg -l F.Cu,F.SilkS,Edge.Cuts --page-size-mode 2 --exclude-drawing-sheet -o "$root_dir/preview/pcb-$name.svg" "$board"
 kicad-cli pcb export step --board-only -f -o "$root_dir/mechanical/$name-board.step" "$board"
done
