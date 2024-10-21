from ase.build import bulk
from ase.constraints import StrainFilter
from ase.optimize import BFGS
from ase.io import read
from calorine.calculators import CPUNEP
from kaldo.conductivity import Conductivity
from kaldo.forceconstants import ForceConstants
from kaldo.phonons import Phonons
import kaldo.controllers.plotter as plotter
import os
from pylab import *
import numpy as np


# We start from the atoms object
raw_atoms = read("infile.ucposcar", format="vasp")

# Config super cell and calculator input
supercell = np.array([4, 4, 4])

# Set up calcualtor using calorine
nep_calculator = CPUNEP('Si_nep.txt')
raw_atoms.calc = nep_calculator

# Pefrom geometry optimization
sf = StrainFilter(raw_atoms)
dyn = BFGS(sf, trajectory='Si.traj')
dyn.run(fmax=0.001)
atoms = read('Si.traj')

# Create a finite difference object
forceconstants_config  = {'atoms':atoms,'supercell': supercell, 'folder':'fd_NEP/'}
forceconstants = ForceConstants(**forceconstants_config)

# Compute 2nd and 3rd IFCs with the defined calculators
forceconstants.second.calculate(calculator = nep_calculator, delta_shift=1e-4)
forceconstants.third.calculate(calculator = nep_calculator, delta_shift=1e-4)

# Compute elastic tensor from
# Born’s long wave method:
# M. Born and K. Huang, Dynamical Theory of Crystal Lattices (Oxford University Press, 1954).
Cij = forceconstants.elastic_prop()
print("C11: %.1f GPa" %Cij[0, 0, 0, 0])
print("C12: %.1f GPa" %Cij[0, 0, 1, 1])
print("C44: %.1f GPa" %Cij[1, 2, 1, 2])

# Derive Bulk modulus for cubic system
print("Bulk Modulus:  %.1f GPa" %((Cij[0, 0, 0, 0] + 2 * Cij[0, 0, 1, 1])/3))

# Define k-point grids, temperature
# and the assumption for the
# phonon poluation (i.e classical vs. quantum)
kxy = 12
kz = kxy
kpts = [kxy, kxy, kz]
temperature = 50

is_classic = False

# Create a phonon object
phonons = Phonons(forceconstants=forceconstants,
                kpts=kpts,
                is_classic=is_classic,
                temperature=temperature,
                folder='ALD_Si_NEP',
                storage='numpy')


# Plot phonon dispersion and density of states (DOS)
plotter.plot_dispersion(phonons,n_k_points=200, is_showing=False)
plotter.plot_dos(phonons,p_atoms=None, bandwidth=0.05, filename='dos')

# Calculate conductivity with direct inversion approach (inverse)
print('\n')
inv_cond_matrix = (Conductivity(phonons=phonons, method='inverse').conductivity.sum(axis=0))
print('Bulk thermal conductivity (W/m/K): ', np.mean([inv_cond_matrix[0,0], inv_cond_matrix[1,1], inv_cond_matrix[2,2]]))
print('\n')
print('Thermal condutivity tensor: \n')
print(inv_cond_matrix)
