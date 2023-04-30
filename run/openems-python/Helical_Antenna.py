# -*- coding: utf-8 -*-
"""
 Helical Antenna Tutorial

 Tested with
  - python 3.10
  - openEMS v0.0.35+

 (c) 2015-2023 Thorsten Liebig <thorsten.liebig@gmx.de>

"""

### Import Libraries
import os, tempfile, getpass
from pylab import *

from CSXCAD import CSXCAD

from openEMS import openEMS
from openEMS.physical_constants import *
from utils import abort_after, abort_cleanup


### Setup the simulation
Sim_Path = os.path.join(tempfile.gettempdir(), getpass.getuser(), 'Helical_Ant')
post_proc_only = False

unit = 1e-3 # all length in mm

f0 = 2.4e9 # center frequency, frequency of interest!
lambda0 = round(C0/f0/unit) # wavelength in mm
fc = 0.5e9 # 20 dB corner frequency

Helix_radius = 20 # --> diameter is ~ lambda/pi
Helix_turns = 10  # --> expected gain is G ~ 4 * 10 = 40 (16dBi)
Helix_pitch = 30  # --> pitch is ~ lambda/4
Helix_mesh_res = 3

gnd_radius = lambda0/2

# feeding
feed_heigth = 3
feed_R = 120    #feed impedance

# size of the simulation box
SimBox = array([1, 1, 1.5])*2.0*lambda0

### Setup FDTD parameter & excitation function
FDTD = openEMS(EndCriteria=1e-4)
FDTD.SetGaussExcite( f0, fc )
FDTD.SetBoundaryCond( ['MUR', 'MUR', 'MUR', 'MUR', 'MUR', 'PML_8'] )

### Setup Geometry & Mesh
CSX = CSXCAD.ContinuousStructure()
FDTD.SetCSX(CSX)
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

max_res = floor(C0 / (f0+fc) / unit / 20) # cell size: lambda/20

# create helix mesh
mesh.AddLine('x', [-Helix_radius, 0, Helix_radius])
mesh.SmoothMeshLines('x', Helix_mesh_res)
# add the air-box
mesh.AddLine('x', [-SimBox[0]/2-gnd_radius,  SimBox[0]/2+gnd_radius])
# create a smooth mesh between specified fixed mesh lines
mesh.SmoothMeshLines('x', max_res, ratio=1.4)

# copy x-mesh to y-direction
mesh.SetLines('y', mesh.GetLines('x'))

# create helix mesh in z-direction
mesh.AddLine('z', [0, feed_heigth, Helix_turns*Helix_pitch+feed_heigth])
mesh.SmoothMeshLines('z', Helix_mesh_res)

# add the air-box
mesh.AddLine('z', [-SimBox[2]/2, max(mesh.GetLines('z'))+SimBox[2]/2 ])
# create a smooth mesh between specified fixed mesh lines
mesh.SmoothMeshLines('z', max_res, ratio=1.4)

### Create the Geometry
## * Create the metal helix using the wire primitive.
## * Create a metal gorund plane as cylinder.
# create a perfect electric conductor (PEC)
helix_metal = CSX.AddMetal('helix' )

ang = linspace(0,2*pi,21)
coil_x = Helix_radius*cos(ang)
coil_y = Helix_radius*sin(ang)
coil_z = ang/2/pi*Helix_pitch

Helix_x=np.array([])
Helix_y=np.array([])
Helix_z=np.array([])
zpos = feed_heigth
for n in range(Helix_turns-1):
    Helix_x = r_[Helix_x, coil_x]
    Helix_y = r_[Helix_y, coil_y]
    Helix_z = r_[Helix_z ,coil_z+zpos]
    zpos = zpos + Helix_pitch

p = np.array([Helix_x, Helix_y, Helix_z])
helix_metal.AddCurve(p)

# create ground circular ground
gnd = CSX.AddMetal( 'gnd' ) # create a perfect electric conductor (PEC)

# add a box using cylindrical coordinates
start = [0, 0, -0.1]
stop  = [0, 0,  0.1]
gnd.AddCylinder(start, stop, radius=gnd_radius)

# apply the excitation & resist as a current source
start = [Helix_radius, 0, 0]
stop  = [Helix_radius, 0, feed_heigth]
port = FDTD.AddLumpedPort(1 ,feed_R, start, stop, 'z', 1.0, priority=5)

# nf2ff calc
nf2ff = FDTD.CreateNF2FFBox(opt_resolution=[lambda0/15]*3)

### Run the simulation
if 0:  # debugging only
    CSX_file = os.path.join(Sim_Path, 'helix.xml')
    if not os.path.exists(Sim_Path):
        os.mkdir(Sim_Path)
    CSX.Write2XML(CSX_file)
    from CSXCAD import AppCSXCAD_BIN
    os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

if not post_proc_only:
    for i in range(1, 5):
        print("Benchmark: running with %d threads" % i, flush=True)
        abort_after(Sim_Path, 30)
        FDTD.Run(Sim_Path, cleanup=True, numThreads=i)
        abort_cleanup(Sim_Path)
    os._exit(0)
