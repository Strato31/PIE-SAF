import math
import os
import sys

import pytest

# Ensure workspace root is on sys.path so `etapes` can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etapes import _7_compression as comp


def test_param_temp_variable_returns_valid_values():
    Cp, gamma, Rs = comp.param_temp_variable(300, "H2")
    assert isinstance(Cp, float)
    assert Cp > 0
    assert isinstance(gamma, float)
    assert gamma > 1
    assert isinstance(Rs, float)
    assert Rs > 0


def test_calcul_echauffement_isenthropique_increases_temperature():
    T0 = 288.15
    P0 = 1.0
    P1 = 10.0
    gamma = 1.4
    T1 = comp.calcul_echauffement_isenthropique(T0, P0, P1, gamma)
    assert T1 > T0


def test_compression_isentropique_consistent():
    T0 = 288.15
    T1 = comp.compression_isentropique("CO2", 1.0, 10.0, T0)
    assert T1 > T0


def test_conso_compression_non_negative():
    val = comp.conso_compression(1.0, "CH4", 0.8, 1.0, 10.0, 288.15)
    assert isinstance(val, float)
    assert val >= 0


def test_conso_compression_syngaz_equivalence_single_gas():
    mCO2 = 2.0
    val_mix = comp.conso_compression_syngaz(mCO2, 0.0, 0.0, 0.8, 1.0, 10.0, 288.15)
    val_single = comp.conso_compression(mCO2, "CO2", 0.8, 1.0, 10.0, 288.15)
    assert math.isclose(val_mix, val_single, rel_tol=1e-8, abs_tol=1e-12)
