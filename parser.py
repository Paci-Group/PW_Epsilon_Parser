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
