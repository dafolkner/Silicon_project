# Import necessary packages
import ase
from kaldo.conductivity import Conductivity
from kaldo.forceconstants import ForceConstants
from kaldo.phonons import Phonons

# Load in unit cell and super cell in 
uc = ase.io.read('infile.ucposcar', format='vasp')
sc = ase.io.read('infile.ssposcar', format='vasp')

# Define 4-by-4-by supercell
supercell = [4, 4, 4]

# Load in TDEP force constants
folder = '.'
forceconstants = ForceConstants.from_folder(folder=folder, supercell=supercell, format='tdep')

# Compute elastic tensor from
# Born’s long wave method:
# M. Born and K. Huang, Dynamical Theory of Crystal Lattices (Oxford University Press, 1954).
Cij = forceconstants.elastic_prop()
print("C11: %.1f GPa" %Cij[0, 0, 0, 0])
print("C12: %.1f GPa" %Cij[0, 0, 1, 1])
print("C44: %.1f GPa" %Cij[1, 2, 1, 2])

# Derive Bulk modulus for cubic system
print("Bulk Modulus:  %.1f GPa" %((Cij[0, 0, 0, 0] + 2 * Cij[0, 0, 1, 1])/3))

# Use 12-by-12-by-12 k-grids and 50K for BTE calculation
kxy = 12
kz = kxy
kpts = [kxy, kxy, kz]
temperature = 50

# Define phonon object
phonons = Phonons(forceconstants=forceconstants,
                  kpts=kpts,
                  is_classic=False,
                  temperature=temperature,
                  folder='ALD_Si_TDEP')


# Plot phonon dispersion and density of states
plotter.plot_dispersion(phonons,n_k_points=200, is_showing=False)
plotter.plot_dos(phonons,p_atoms=None, bandwidth=0.05, filename='dos')

# Solve BTE using direct inversion of scattering matrix
inv_cond_matrix = (Conductivity(phonons=phonons, method='inverse').conductivity.sum(axis=0))
print('Conductivity from inversion (W/m-K): %.3f' % (np.mean(np.diag(inv_cond_matrix))))
print(inv_cond_matrix)
