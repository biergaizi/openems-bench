# -*- coding: utf-8 -*-
"""
 Tutorials / radar cross section of a metal sphere

 Tested with
  - python 3.10
  - openEMS v0.0.35+

 (c) 2016-2023 Thorsten Liebig <thorsten.liebig@gmx.de>
"""

### Import Libraries
import os, tempfile, getpass
from pylab import *

from CSXCAD  import ContinuousStructure
from openEMS import openEMS
from openEMS.physical_constants import *
from openEMS.ports  import UI_data

from utils import abort_after, abort_cleanup

### Setup the simulation
Sim_Path = os.path.join(tempfile.gettempdir(), getpass.getuser(), 'RCS_Sphere')
post_proc_only = False

unit = 1e-3 # all length in mm

sphere_rad = 200

inc_angle = 0 #incident angle (to x-axis) in deg

# size of the simulation box
SimBox = 1200
PW_Box = 750

### Setup FDTD parameters & excitation function
FDTD = openEMS(EndCriteria=1e-5)

f_start =  50e6 # start frequency
f_stop  = 1000e6 # stop  frequency
f0      = 500e6
FDTD.SetGaussExcite(  0.5*(f_start+f_stop), 0.5*(f_stop-f_start) )

FDTD.SetBoundaryCond( ['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'] )

### Setup Geometry & Mesh
CSX = ContinuousStructure()
FDTD.SetCSX(CSX)
mesh = CSX.GetGrid()
mesh.SetDeltaUnit(unit)

#create mesh
mesh.SetLines('x', [-SimBox/2, 0, SimBox/2])
mesh.SmoothMeshLines('x', C0 / f_stop / unit / 20) # cell size: lambda/20
mesh.SetLines('y', mesh.GetLines('x'))
mesh.SetLines('z', mesh.GetLines('x'))

### Create a metal sphere and plane wave source
sphere_metal = CSX.AddMetal( 'sphere' ) # create a perfect electric conductor (PEC)
sphere_metal.AddSphere(priority=10, center=[0, 0, 0], radius=sphere_rad)

# plane wave excitation
k_dir = [cos(np.deg2rad(inc_angle)), sin(np.deg2rad(inc_angle)), 0] # plane wave direction
E_dir = [0, 0, 1] # plane wave polarization --> E_z

pw_exc = CSX.AddExcitation('plane_wave', exc_type=10, exc_val=E_dir)
pw_exc.SetPropagationDir(k_dir)
pw_exc.SetFrequency(f0)

start = np.array([-PW_Box/2, -PW_Box/2, -PW_Box/2])
stop  = -start
pw_exc.AddBox(start, stop)

# nf2ff calc
nf2ff = FDTD.CreateNF2FFBox()

### Run the simulation
if 0:  # debugging only
    CSX_file = os.path.join(Sim_Path, 'RCS_Sphere.xml')
    if not os.path.exists(Sim_Path):
        os.mkdir(Sim_Path)
    CSX.Write2XML(CSX_file)
    from CSXCAD import AppCSXCAD_BIN
    os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))


if not post_proc_only:
    for i in range(1, 11):
        print("Benchmark: running with %d threads" % i, flush=True)
        abort_after(Sim_Path, 30)
        FDTD.Run(Sim_Path, cleanup=True, numThreads=i)
        abort_cleanup(Sim_Path)
    os._exit(0)
