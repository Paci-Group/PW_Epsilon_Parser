from ase.io.espresso import read_espresso_out
import numpy as np


class BerryInfo:
    """
    Berry Phase information for orthogonal cell.
    """
    def __init__(self, fileobject=None):
        if fileobject is not None:
            self.parse(fileobject)
        else:
            self.efield = None
            self.edipole = None
            self.idipole = None
            self.nberrycyc = None
            self.volume = None
            self.cell = None
            self.alat = None

    def __str__(self):
        return (f"BerryPhase(Efield={self.efield},\n           Edipole={self.edipole},\n           Idipole={self.idipole},\n           " + \
                f"NBerry={self.nberrycyc},\n           Volume (au)={self.volume},\n           Alat (au)={self.alat},\n           Cell={self.cell})") 

    def parse(self, fo):
        line = fo.readline()
        while line:
            if "Using Berry phase electric field" in line:
                fo.readline()
                self.efield = []
                for _ in range(3):
                    self.efield.append(float(fo.readline().strip()))
                self.efield = np.array(self.efield)
            elif "Number of iterative cycles:" in line:
                self.nberrycyc = int(line.split(":")[1].strip())
            elif "Electronic Dipole on Cartesian axes" in line:
                self.edipole = []
                for _ in range(3):
                    self.edipole.append(float(fo.readline().split()[1].strip()))
                self.edipole = np.array(self.edipole)
            elif "Ionic Dipole on Cartesian axes" in line:
                self.idipole = []
                for _ in range(3):
                    self.idipole.append(float(fo.readline().split()[1].strip()))
                self.idipole = np.array(self.idipole)
            elif "unit-cell volume" in line:
                self.volume = float(line.split()[3])
            elif "lattice parameter (alat)" in line:
                self.alat = float(line.split()[4])
            elif "crystal axes: (cart. coord. in units of alat)" in line:
                self.cell = []
                for i in range(3):
                    self.cell.append(float(fo.readline().split()[i+3].strip()))
                self.cell = np.array(self.cell)
            line = fo.readline()


def read_espresso(pwo, berry=False):
    with open(pwo, 'r') as fo:
        atoms_gen = read_espresso_out(fo, index=slice(None))
        atoms = next(atoms_gen)
        fo.seek(0)
        if berry:
            berry_info = BerryInfo(fo)
        else:
            berry_info = None
    return atoms, berry_info

(pybec) [bhenders@login1 pw_epsilon_parser]$ cat postprocess.py 
from parser import BerryInfo, read_espresso
import os
import pickle
import numpy as np

directions = {"X": 0, "Y": 1, "Z": 2}
force_conversion = 25.7105  # eV / Angstrom to Ry au


def extract_dielectric_info(job, direction="Z", pquant=(0, 0)):
    # 0 field
    at_0, bphase_0 = read_espresso(job + ".scf.out", berry=True)

    # clamped ion
    at_1, bphase_1 = read_espresso(job + ".efield.out", berry=True)

    # relaxed ion
    at_2, bphase_2 = read_espresso(job + ".relax.out", berry=True)
    print(bphase_1)
    print(bphase_2)

    becs = calculate_bec(at_0, at_1, bphase_1.efield[directions[direction]])
    eps_inf = calculate_eps(bphase_0, bphase_1, pquant=pquant[0])
    eps_0 = calculate_eps(bphase_0, bphase_2, pquant=pquant[1])

    return at_0, at_2, eps_inf, eps_0, becs

def calculate_bec(atoms_initial, atoms_final, emag):
    f0 = atoms_initial.calc.get_forces() / force_conversion
    f1 = atoms_final.calc.get_forces() / force_conversion
    return 1/np.sqrt(2) * (f1 - f0) / emag

def calculate_eps(bphase_initial, bphase_final, direction="Z", pquant=0):
    add_pol = pquant * np.sqrt(2) * bphase_final.cell[directions[direction]] * bphase_final.alat
    efield = bphase_final.efield[directions[direction]]
    p_final = bphase_final.edipole + bphase_final.idipole + add_pol
    p_initial = bphase_initial.edipole + bphase_initial.idipole
    return 1 + 4*np.pi * (p_final - p_initial) / (bphase_final.volume * efield)


if __name__ == "__main__":
    job = "bao"
    pquant = (0, 0)
    data = {'bao': {}}
    print(f"Computing Dielectric Properties for {job}")
    atoms0, atoms1, eps_inf, eps_0, becs = extract_dielectric_info(job, pquant=pquant)
    print(f"Epsilon_infinity (e_xz, e_yz, e_zz): {eps_inf[0]}, {eps_inf[1]}, {eps_inf[2]}")
    print(f"Epsilon_0 (e_xz, e_yz, e_zz): {eps_0[0]}, {eps_0[1]}, {eps_0[2]}")
    print(f"Born Effective Charges: (Symbol, X, Y, Z, Z_xz, Z_yz, Z_zz")
    for i, (sym, pos) in enumerate(zip(atoms0.symbols, atoms0.positions)):
        print(f"    {sym:<10}    {pos[0]:10.6f}    {pos[1]:10.6f}    {pos[2]:10.6f}    {becs[i, 0]:5.3f}     {becs[i, 1]:5.3f}    {becs[i, 2]:5.3f}")
    data[job]['eps_inf'] = eps_inf
    data[job]['eps_0'] = eps_0
    data[job]['becs'] = becs
    data[job]['atoms_initial'] = atoms0
    data[job]['atoms_final'] = atoms1
    
    with open("dielectric.pickle", 'wb') as f:
        pickle.dump(data, f)
