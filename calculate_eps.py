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
    print("1. Zero Field Berry Phase Output:")
    print(bphase_0)
    print("\n2. Clamped-Ion Berry Phase Output:")
    print(bphase_1)
    print("\n3. Relaxed-Ion Berry Phase Output:")
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
    print(f"\nEpsilon_infinity (e_xz, e_yz, e_zz): {eps_inf[0]:0.3f}, {eps_inf[1]:0.3f}, {eps_inf[2]:0.3f}")
    print(f"Epsilon_0 (e_xz, e_yz, e_zz): {eps_0[0]:0.3f}, {eps_0[1]:0.3f}, {eps_0[2]:0.3f}")
    print(f"Born Effective Charges: (Symbol, X, Y, Z, Z_xz, Z_yz, Z_zz)")
    for i, (sym, pos) in enumerate(zip(atoms0.symbols, atoms0.positions)):
        print(f"    {sym:<6}{pos[0]:10.6f}{pos[1]:10.6f}{pos[2]:10.6f}{becs[i, 0]:8.3f}{becs[i, 1]:8.3f}{becs[i, 2]:8.3f}")
    data[job]['eps_inf'] = eps_inf
    data[job]['eps_0'] = eps_0
    data[job]['becs'] = becs
    data[job]['atoms_initial'] = atoms0
    data[job]['atoms_final'] = atoms1
    
    with open("dielectric.pickle", 'wb') as f:
        pickle.dump(data, f)
