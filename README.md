# PW Permittivity Calculator

The code calculate_eps.py computes the clamped- and relaxed-ion permittivity of a material
from calculations using the QuantumEspresso PW module. In order to work, three output files
are necessary:

1. <prefix>.scf.out - A zero field calculation with Berry Phase calculated: `lelfield = .true., lberry = .true.`.
3. <prefix>.efield.out - A finite field clamped-ion calculation.
4. <prefix>.relax.out - A finite field relaxed-ion calculation.

## Output
The script will calculate the permittivity and Born effective charges and give the output some format.
Here is an example output for a conventional unit cell of BaO:

```
Computing Dielectric Properties for bao
1. Zero Field Berry Phase Output:
BerryPhase(Efield=[0. 0. 0.],
           Edipole=[1.73410341e-09 4.76154358e-08 4.44577535e-08],
           Idipole=[234.97256031 234.97256031 234.97256031],
           NBerry=1,
           Volume (au)=1119.8156,
           Alat (au)=10.3844,
           Cell=[1. 1. 1.])

2. Clamped-Ion Berry Phase Output:
BerryPhase(Efield=[0.    0.    0.002],
           Edipole=[-1.50651791e-07 -4.30106724e-07  5.72780476e-01],
           Idipole=[234.97256031 234.97256031 234.97256031],
           NBerry=3,
           Volume (au)=1119.8156,
           Alat (au)=10.3844,
           Cell=[1. 1. 1.])

3. Relaxed-Ion Berry Phase Output:
BerryPhase(Efield=[0.    0.    0.002],
           Edipole=[2.73580565e-06 7.03115875e-06 2.00320271e+00],
           Idipole=[234.97256844 234.97258118 238.68012693],
           NBerry=3,
           Volume (au)=1119.8156,
           Alat (au)=10.3844,
           Cell=[1. 1. 1.])

Epsilon_infinity (e_xz, e_yz, e_zz): 1.000, 1.000, 4.214
Epsilon_0 (e_xz, e_yz, e_zz): 1.000, 1.000, 33.043
Born Effective Charges: (Symbol, X, Y, Z, Z_xz, Z_yz, Z_zz)
    Ba      0.000000  0.000000  0.000000   0.000  -0.000   2.771
    O       2.747599  2.747599  2.747599  -0.000  -0.000  -2.771
    Ba      0.000000  2.747599  2.747599   0.000   0.000   2.771
    Ba      2.747599  0.000000  2.747599  -0.000  -0.000   2.771
    Ba      2.747599  2.747599  0.000000  -0.000   0.000   2.771
    O       2.747599  0.000000  0.000000  -0.000   0.000  -2.771
    O       0.000000  2.747599  0.000000   0.000  -0.000  -2.771
    O       0.000000  0.000000  2.747599   0.000   0.000  -2.771
```
