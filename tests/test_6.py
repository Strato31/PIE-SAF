# python
import pytest
from etapes._6_energie import emissions_energie_totale, emissions_energetique_processus

def _compute_expected_mix():
    # Recompute the mix exactly as in etapes._6_energie to derive expected values
    # This mirrors the implementation so tests remain consistent with current code.
    param_mix_2050 = {
        "nucleaire": 0.38,
        "eolien": 0.304,
        "solaire": 0.198,
        "hydraulique": 0.2,
        "biomasse": 0.2,
    }
    facteur_emission = {
        "nucleaire": 5,
        "eolien": 15,
        "solaire": 32,
        "hydraulique": 6,
        "biomasse": 230,
    }
    total = 0.0
    for k in facteur_emission:
        total += param_mix_2050[k] * facteur_emission[k]
    return total

def test_emissions_energetique_processus_1kwh():
    mix = _compute_expected_mix()
    assert emissions_energetique_processus(1) == pytest.approx(mix, rel=1e-9)

def test_emissions_energetique_processus_zero():
    assert emissions_energetique_processus(0) == 0

def test_emissions_energie_totale_liste():
    mix = _compute_expected_mix()
    inputs = [1, 2, 3]
    expected_parts = [mix * v for v in inputs]
    expected_total = sum(expected_parts)
    expected = expected_parts + [expected_total]

    result = emissions_energie_totale(inputs)
    # Ensure same length and compare each element with approx for floats
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert r == pytest.approx(e, rel=1e-9)

def test_emissions_energie_totale_vide():
    # Behavior: returns [0] when input list is empty
    assert emissions_energie_totale([]) == [0]