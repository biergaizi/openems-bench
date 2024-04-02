#!/usr/bin/env python3

import os
import sys
import numpy as np
from pyems.boundary import BoundaryConditions
from pyems.simulation import Simulation
from pyems.structure import PCB, Microstrip, ViaWall
from pyems.coordinate import Coordinate2, Coordinate3, Box2, Box3, Axis
from pyems.pcb import common_pcbs
from pyems.mesh import Mesh
from pyems.utilities import print_table, mil_to_mm
from pyems.field_dump import FieldDump
from utils import abort_after, abort_cleanup, min_thread, max_thread

freq = np.arange(0, 18e9, 1e7)
sim = Simulation(
    freq=freq,
    unit=1e-3,
    boundary_conditions=BoundaryConditions(
        (("PEC", "PEC"), ("PEC", "PEC"), ("PEC", "PEC")),
    )
)
pcb_prop = common_pcbs["oshpark4"]
pcb_len = 20
pcb_width = 5
trace_width = 0.34
gap = mil_to_mm(6)
via_gap = 0.4

pcb = PCB(
    sim=sim,
    pcb_prop=pcb_prop,
    length=pcb_len,
    width=pcb_width,
    layers=range(3),
)
box = Box2(
    Coordinate2(-pcb_len / 2, -trace_width / 2),
    Coordinate2(pcb_len / 2, trace_width / 2),
)
Microstrip(
    pcb=pcb,
    position=box.center(),
    length=box.length(),
    width=box.width(),
    propagation_axis=Axis("x"),
    trace_layer=0,
    gnd_layer=1,
    gnd_gap=(gap, gap),
    port_number=1,
    ref_impedance=50,
    excite=True,
)

ViaWall(
    pcb=pcb,
    position=Coordinate2(0, trace_width / 2 + gap + via_gap),
    length=pcb_len,
    width=via_gap / 2,
)

ViaWall(
    pcb=pcb,
    position=Coordinate2(0, -trace_width / 2 - gap - via_gap),
    length=pcb_len,
    width=via_gap / 2,
)

dump = FieldDump(
    sim=sim,
    box=Box3(
        Coordinate3(-pcb_len / 2, -pcb_width / 2, 0),
        Coordinate3(pcb_len / 2, pcb_width / 2, 0),
    ),
)

mesh = Mesh(
    sim=sim,
    metal_res=1 / 120,
    nonmetal_res=1 / 40,
    smooth=(1.1, 1.5, 1.5),
    min_lines=25,
    expand_bounds=((0, 0), (24, 24), (24, 24)),
)

if os.getenv("_PYEMS_PYTEST"):
    sys.exit(0)


for i in range(min_thread, max_thread + 1):
    print("Benchmark: running with %d threads" % i, flush=True)
    abort_after(sim, 30)
    sim.run(csx=False, threads=i)
    abort_cleanup(sim)

os._exit(0)
