from etapes import _1_biomasse as biomasse
from etapes import kerosene as transport
from etapes import _3_FT as ft
from etapes import _4_electrolyseur as elec
from etapes import _5_gazeification as gaz
from etapes import _6_energie as energie
from etapes import _7_compression as comp

def __main__():
    
    print("Calcul des émissions et consommations du processus e-bio-SAF complet, en partant de la biomasse jusqu'au carburant e-bio-SAF.")
    print("---------------------------------------------------------------")
    print("Le calcul se base sur les hypothèses sourcées dans chaque étape du processus.\n On prend en entrée les biomasses suivantes :")
    biomasse_liste = biomasse.biomasse_entree
    for b in biomasse_liste:
        print(f" - {b['masse']} t de biomasse de type {b['type']} à {b['humidité']*100}% d'humidité")
    print("---------------------------------------------------------------\n")
    print("Étape 1 : Biomasse")
    consos_energies, consos_thermiques, emissions_co2 = [], [], []
    conso_elec, conso_chaleur, total_emissions, masse_seche_biomasse = biomasse.main_biomasse(biomasse.param_biomasse, biomasse_liste)
    consos_energies.append(conso_elec)
    consos_thermiques.append(conso_chaleur)
    emissions_co2.append(total_emissions)
    print("---------------------------------------------------------------")
    print("Étape 2 : Gazeification")
    besoin_H2_gazif, besoin_O2_gazif, conso_elec_gaz, emissions_gazif = gaz.gazeificationV2(masse_seche_biomasse, 180000, 32130, gaz.gaz_params, gaz.caract_syngas)
    consos_energies.append(conso_elec_gaz)
    emissions_co2.append(emissions_gazif)
    print("---------------------------------------------------------------")
    print("Étape 3 : Fischer-Tropsch")
    masse_kerosene, emissions_FT, besoin_H2_FT = ft.main_FT(ft.param_FT, ...)
    emissions_co2.append(emissions_FT)
    print("---------------------------------------------------------------")
    print("Étape 4 : Électrolyseur")
    conso_elec_elec = elec.consommation_electrolyseur(elec.param_electrolyseur_PEM, besoin_H2_FT, besoin_O2_gazif, besoin_H2_gazif)
    consos_energies.append(conso_elec_elec)
    print("---------------------------------------------------------------")
    print("Étape 5 : Compression")
    masse_CO_kg, masse_H2_kg, masse_CO2_kg, masse_O2_kg = gaz.gazeificationV2(masse_seche_biomasse, gaz.gaz_params, gaz.caract_syngas)[0:4]*1000
    "Calcul de la consommation électrique de compression de l'O2 entre l'électrolyseur et FT"
    conso_compression_O2 = comp.conso_compression(masse_O2_kg, "O2", 0.8, 1, 20, 288.15)
    "Calcul de la consommation électrique de compression du CO2 capté sortie du réactuer BioTJet et amené à EM-Lacq"
    conso_compression_CO2 = comp.conso_compression(masse_CO2_kg, "CO2", 0.8, 1, 20, 288.15)
    "Calcul de la consommation électrique de compression du syngas entre la gazéification et FT"
    conso_compression_syngas = comp.conso_compression_syngaz(masse_CO2_kg, masse_H2_kg, masse_CO_kg, 0.85, 1, 1.12, 323.15) #hypothèse flux total de gaz à ventiler
    conso_elec_compression = conso_compression_O2 + conso_compression_syngas + conso_compression_CO2
    consos_energies.append(conso_elec_compression)
    print("---------------------------------------------------------------")
    print("Étape 6 : Calcul des émissions totales et consommations énergétiques")
    emissions_2050, emissions_2023 = energie.emissions_energie_totale(consos_energies)
    print(f"Hypothèse thermique : {energie.verif_hypothèse(consos_thermiques)}")
    print("---------------------------------------------------------------")
    print("Résultats finaux :")
    total_emissions_2050 = sum(emissions_2050)
    total_emissions_2023 = sum(emissions_2023)
    total_conso_energie = sum(consos_energies)
    total_conso_thermique = sum(consos_thermiques)
    print(f" - Consommation électrique totale : {total_conso_energie:.2f} kWh")
    print(f" - Consommation thermique totale : {total_conso_thermique:.2f} MJ")
    print(f" - Émissions totales en 2050 : {total_emissions_2050:.2f} gCO2e")
    print(f" - Émissions totales en 2023 : {total_emissions_2023:.2f} gCO2e")
    print(f" - Émissions totales par MJ de e-bio-SAF en 2050 : {total_emissions_2050 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):.4f} gCO2e/MJ")
    print(f" - Émissions totales par MJ de e-bio-SAF en 2023 : {total_emissions_2023 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):.4f} gCO2e/MJ")
    print("------------------------------FIN---------------------------------")
    
    
    
    


if __name__ == "__main__":
    __main__()
