# MVP_skeleton.py
from dataclasses import dataclass, field
import pandas as pd

@dataclass
class Stage:
    name: str
    params: dict = field(default_factory=dict)
    inputs: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)

    def compute(self):
        raise NotImplementedError
    
    def set_inputs(self, inputs: dict):
        self.inputs = inputs

    def get_outputs(self):
        return self.outputs

class BiomassStage(Stage):
    def compute(self):
        # inputs expected: {'dry_biomass_kg': ...} or {'wet_biomass_kg':..., 'moisture_frac':...}
        p = self.params
        inp = self.inputs
        # Minimal handling: accept wet or dry
        if 'dry_biomass_kg' in inp:
            dry = inp['dry_biomass_kg']
        else:
            wet = inp.get('wet_biomass_kg', 0.0)
            m = inp.get('moisture_frac', p.get('default_moisture', 0.2))
            dry = wet * (1.0 - m)
        # LHV (MJ/kg dry)
        lhv = p.get('LHV_MJ_per_kg', 18.0)
        # simple composition placeholder
        self.outputs = {
            'dry_biomass_kg': dry,
            'moisture_kg': dry * p.get('default_moisture', 0.2) / (1 - p.get('default_moisture', 0.2)),
            'LHV_MJ': dry * lhv,
            'biomass_C_mass_kg': dry * p.get('carbon_frac', 0.5)
        }
        return self.outputs

class TransportStage(Stage):
    def compute(self):
        inp = self.inputs
        p = self.params
        distance_km = p.get('distance_km', 50)
        truck_capacity_t = p.get('truck_capacity_t', 20.0)
        fuel_consumption_L_per_100km = p.get('fuel_L_per_100km', 35)  # heavy truck
        mass_t = inp.get('dry_biomass_kg', 0)/1000.0
        # trips needed
        trips = max(1.0, mass_t / truck_capacity_t)
        fuel_L = trips * (distance_km*2) * (fuel_consumption_L_per_100km/100.0)  # round trip assumption
        # emission: simple CO2 per L diesel
        co2_per_L = p.get('co2_kg_per_L', 2.68)
        co2_emit = fuel_L * co2_per_L
        self.outputs = {
            'mass_transported_kg': inp.get('dry_biomass_kg', 0),
            'fuel_used_L': fuel_L,
            'co2_transport_kg': co2_emit
        }
        return self.outputs

class GasificationStage(Stage):
    def compute(self):
        # inputs: dry_biomass_kg
        inp = self.inputs
        p = self.params
        dry = inp.get('dry_biomass_kg', 0.0)
        # simple yield assumptions
        syngas_yield_m3_per_kg = p.get('syngas_m3_per_kg', 1.2)  # crude
        syngas_m3 = dry * syngas_yield_m3_per_kg
        # syngas composition (vol%): CO, H2, CO2, CH4, N2
        comp = p.get('syngas_comp', {'CO':0.25,'H2':0.35,'CO2':0.25,'CH4':0.05,'N2':0.10})
        # energy for gasification (external heat) MJ/kg_biomass
        heat_MJ = dry * p.get('heat_MJ_per_kg', 0.5)
        # char (solid) fraction
        char_frac = p.get('char_frac', 0.08)
        char_kg = dry * char_frac
        self.outputs = {
            'syngas_m3': syngas_m3,
            'syngas_comp': {k: v*syngas_m3 for k,v in comp.items()},
            'char_kg': char_kg,
            'heat_input_MJ': heat_MJ
        }
        return self.outputs

class ElectrolyseStage(Stage):
    def compute(self):
        # inputs: need H2 demand or compute H2 produced per kWh
        p = self.params
        inp = self.inputs
        # default: user provides electricity_kWh
        elec_kWh = p.get('electricity_kWh_per_kg_H2', 50)  # kWh needed per kg H2 (inverse of efficiency)
        if 'electricity_supplied_kWh' in inp:
            supplied = inp['electricity_supplied_kWh']
            H2_kg = supplied / elec_kWh
            elec_used = supplied
        elif 'H2_demand_kg' in inp:
            H2_kg = inp['H2_demand_kg']
            elec_used = H2_kg * elec_kWh
        else:
            # default small
            H2_kg = p.get('default_H2_kg', 1.0)
            elec_used = H2_kg * elec_kWh
        co2_grid = p.get('co2_kg_per_kWh', 0.5)
        self.outputs = {
            'H2_kg': H2_kg,
            'electricity_kWh': elec_used,
            'co2_elec_kg': elec_used * co2_grid
        }
        return self.outputs

class FischerTropschStage(Stage):
    def compute(self):
        inp = self.inputs
        p = self.params
        # inputs expected: syngas (CO, H2), H2 from electrolyser (kg)
        # minimal: use H2/CO ratio and convert fraction to hydrocarbons
        CO_moles = inp.get('CO_mol', 0.0)
        H2_mol = inp.get('H2_mol', 0.0)
        # For MVP, assume conversion fraction of CO -> hydrocarbons
        conv = p.get('CO_conversion_frac', 0.9)
        CO_consumed = CO_moles * conv
        # assume selectivity to liquid hydrocarbons (mass) per mol CO consumed
        mass_liquid_per_molCO = p.get('mass_liquid_per_molCO_kg', 0.085)  # placeholder
        liquid_kg = CO_consumed * mass_liquid_per_molCO
        # hydrogen consumed estimated via stoichiometric ratio (simplified)
        H2_consumed = CO_consumed * p.get('H2_mol_per_CO', 2.0)
        self.outputs = {
            'liquid_product_kg': liquid_kg,
            'H2_consumed_mol': H2_consumed,
            'CO_consumed_mol': CO_consumed
        }
        return self.outputs

class Pipeline:
    def __init__(self, stages):
        self.stages = stages
        self.history = []

    def run(self, initial_inputs):
        current = initial_inputs
        results = {}
        for st in self.stages:
            st.set_inputs(current)
            out = st.compute()
            results[st.name] = out
            # prepare inputs for next: naive merge
            current = {**current, **out}
            self.history.append((st.name, out))
        return results

# Exemple d'utilisation MVP
if __name__ == "__main__":
    print("Running MVP pipeline example...")
    biomass = BiomassStage(name="Biomass", params={'default_moisture':0.25, 'LHV_MJ_per_kg':17.5})
    transport = TransportStage(name="Transport", params={'distance_km':50, 'truck_capacity_t':20.0})
    gasif = GasificationStage(name="Gasification", params={'syngas_m3_per_kg':1.1, 'char_frac':0.08})
    electro = ElectrolyseStage(name="Electrolyse", params={'electricity_kWh_per_kg_H2':50, 'co2_kg_per_kWh':0.5})
    ft = FischerTropschStage(name="FischerTropsch", params={'CO_conversion_frac':0.85, 'mass_liquid_per_molCO_kg':0.085})

    pipe = Pipeline([biomass, transport, gasif, electro, ft])
    inputs = {'wet_biomass_kg':10000, 'moisture_frac':0.25}
    res = pipe.run(inputs)
    df = pd.DataFrame({k: [v] for k,v in res.items()})
    print("Pipeline results:")
    print(df)
    print("Detailed stage outputs:")
    print(res)
