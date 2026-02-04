from etapes import _1_biomasse as biomasse
from etapes import kerosene
from etapes import _3_FT as ft
from etapes import _4_electrolyseur as elec
from etapes import _5_gazeification as gaz
from etapes import _6_energie as energie
from etapes import _7_compression as comp

## Variables d'entrée
# TODO : ajouter des :.2f pour arrondir les affichages des flottants
# TODO : harmoniser /an
#biomasse_entree
"""Exemple : 
    biomasse_entree = [
        {"type" : "ligneuse", "masse": 1.0, "humidité": 0.10},  # 1 tonne de biomasse ligneuse à 10% d'humidité
        {"type" : "agricole", "masse": 2.0, "humidité": 0.20},  # 2 tonnes de biomasse agricole à 20% d'humidité
    ]
"""

# section a compléter une fois les fonctions implémentées dans chaque étape

###################

biomasse_entree = [
    {"type" : "bois_vert", "masse": 300000, "humidité": 0},  # 300 000 tonnes de biomasse ligneuse à 0% d'humidité
    {"type" : "bois_vert", "masse": 0, "humidité": 0.30},  # 0 tonnes de biomasse ligneuse à 30% d'humidité
]

kerosene_produit = 97209  # en tonnes de e-bio-SAF produites (actuellement, nombre arbitraire pour tester le calcul inverse)

sens_physique = True  # True : calcul biomasse -> carburant, False : calcul sens inverse

def __main__():
    if sens_physique == True:  # Cas calcul biomasse -> carburant
        print("Calcul des émissions et consommations du processus e-bio-SAF complet, en partant de la biomasse jusqu'au carburant e-bio-SAF.")
        print("-"*60)
        print("Le calcul se base sur les hypothèses sourcées dans chaque étape du processus.\n On prend en entrée les biomasses suivantes :")
        for b in biomasse_entree:
            print(f" - {b['masse']} t de biomasse de type {b['type']} à {b['humidité']*100}% d'humidité")
        consos_energies, consos_thermiques, emissions_co2 = [], [], []
        
        print("-"*60,"\n")
        print("Étape 1 : Biomasse")
        conso_chaleur, total_emissions, masse_seche_biomasse = biomasse.main_biomasse(biomasse.param_biomasse, biomasse_entree, sens_physique)
        consos_thermiques.append(conso_chaleur)
        emissions_co2.append(total_emissions)
        
        print("-"*60)
        print("Étape 2 : Gazeification")
        CO_gazif, besoin_H2_gazif, emissions_gazif, besoin_O2_gazif,dechets_gazif = gaz.gazeificationV2(masse_seche_biomasse, gaz.gaz_params, gaz.caract_syngas)
        conso_elec_gaz = gaz.conso_elec_gazeification(emissions_gazif, besoin_H2_gazif, masse_seche_biomasse, gaz.gaz_params) #Fonction pas implémentée
        consos_energies.append(conso_elec_gaz)
        emissions_co2.append(emissions_gazif)
        print("Consommation électrique : ", conso_elec_gaz, " en kWh")
        
        print("-"*60)
        print("Étape 3 : Fischer-Tropsch")
        consommation_totale_FT, emissions_FT, masse_kerosene = ft.Fischer_Tropsch(ft.param_FT, CO_gazif)
        emissions_co2.append(emissions_FT)
        consos_energies.append(consommation_totale_FT )
        
        print("-"*60)
        print("Étape 4 : Électrolyseur")
        conso_elec_elec = elec.consommation_electrolyseur(elec.param_electrolyseur_PEM, besoin_O2_gazif, besoin_H2_gazif)
        # Prise en compte des pertes en lgne sur le réseau de distribution haute tension (valeur de RTE)
        conso_elec_elec *= (1/0.979)
        consos_energies.append(conso_elec_elec)
        
        print("-"*60)
        print("Étape 5 : Compression")
        masse_CO_kg = CO_gazif * 1000  # Conversion en kg
        masse_H2_kg = besoin_H2_gazif * 1000  # Conversion en kg
        masse_CO2_kg = emissions_gazif * 1000
        masse_O2_kg = besoin_O2_gazif * 1000  # Conversion en kg
        "Calcul de la consommation électrique de compression de l'O2 entre l'électrolyseur et FT"
        conso_compression_O2 = comp.conso_compression(masse_O2_kg, "O2", 0.8, 1, 20, 288.15)
        "Calcul de la consommation électrique de compression du CO2 capté sortie du réactuer BioTJet et amené à EM-Lacq"
        conso_compression_CO2 = comp.conso_compression(masse_CO2_kg, "CO2", 0.8, 1, 20, 288.15)
        "Calcul de la consommation électrique de compression du syngas entre la gazéification et FT"
        conso_compression_syngas = comp.conso_compression_syngaz(masse_CO2_kg, masse_H2_kg, masse_CO_kg, 0.85, 1, 1.12, 323.15) #hypothèse flux total de gaz à ventiler
        conso_elec_compression = conso_compression_O2 + conso_compression_syngas + conso_compression_CO2
        consos_energies.append(conso_elec_compression)
        
        print("-"*60)
        print("Étape 6 : Calcul des émissions totales et consommations énergétiques")
        emissions_2050, emissions_2023 = energie.emissions_energie_totale(consos_energies)
        print(f"Hypothèse thermique : {energie.verif_hypothèse(consos_thermiques)}")
        
        print("-"*60)
        print("Résultats finaux :")
        total_emissions_2050 = emissions_2050[-1]
        total_emissions_2023 = emissions_2023[-1]
        total_conso_energie = sum(consos_energies)
        total_conso_thermique = sum(consos_thermiques)
        print("élec : ", consos_energies)
        print("détail :", emissions_2023)
        print(f" - Consommation électrique totale : {total_conso_energie:.2f} kWh")
        print(f" - Consommation thermique totale : {total_conso_thermique:.2f} MJ")
        print(f" - Émissions totales en 2050 : {total_emissions_2050/1000000:.2f} tCO2e")
        print(f" - Émissions totales en 2023 : {total_emissions_2023/1000000:.2f} tCO2e")
        print(f" - Émissions totales par MJ de e-bio-SAF en 2023 : {total_emissions_2023 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):.4f} gCO2e/MJ")
        print(f" - Émissions totales par MJ de e-bio-SAF en 2050 : {total_emissions_2050 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):.4f} gCO2e/MJ")
        print("------------------------------FIN---------------------------------")

    else: # Cas calcul carburant -> biomasse
        print("Calcul des émissions et consommations du processus e-bio-SAF complet, en partant du carburant e-bio-SAF produit jusqu'à la biomasse.")
        print("-"*60)
        print("Le calcul se base sur les hypothèses sourcées dans chaque étape du processus.")
        print(f"\n On part de {kerosene_produit} t de e-bio-SAF produites.\n")
        
        consos_energies, consos_thermiques, emissions_co2 = [], [], []

        print("-"*60)
        print("Étape 1 : Fischer-Tropsch")
        consommation_totale_FT, emissions_FT, masseCO_sortie = ft.Inv_Fischer_Tropsch(ft.param_FT, kerosene_produit)
        emissions_co2.append(emissions_FT)
        consos_energies.append(consommation_totale_FT)

        print("-"*60)
        print("Étape 2 : Gazeification")
        masse_seche_biomasse, besoin_H2_gazif, besoin_O2_gazif, emissions_gazif = gaz.Inv_gazeificationV1(masseCO_sortie, gaz.gaz_params, gaz.caract_syngas)
        conso_elec_gaz = gaz.conso_elec_gazeification(emissions_gazif, besoin_H2_gazif, masse_seche_biomasse, gaz.gaz_params)
        consos_energies.append(conso_elec_gaz)
        emissions_co2.append(emissions_gazif)
        print("Consommation électrique : ", conso_elec_gaz, " kWh")


        print("-"*60)
        print("Étape 3 : Électrolyseur")
        conso_elec_elec = elec.consommation_electrolyseur(elec.param_electrolyseur_PEM, besoin_O2_gazif, besoin_H2_gazif)
        # Prise en compte des pertes en lgne sur le réseau de distribution haute tension (valeur de RTE)
        conso_elec_elec *= (1/0.979)
        consos_energies.append(conso_elec_elec)
        print("Consommation électrique électrolyseur : ", conso_elec_elec, " kWh")

        print("-"*60,"\n")
        print("Étape 4 : Biomasse")
        conso_chaleur, total_emissions, _ = biomasse.main_biomasse(biomasse.param_biomasse, masse_seche_biomasse, sens_physique)
        consos_thermiques.append(conso_chaleur)
        emissions_co2.append(total_emissions)

        print("-"*60)
        print("Étape 5 : Compression")
        masse_CO_kg = masseCO_sortie * 1000  # Conversion en kg
        masse_H2_kg = besoin_H2_gazif * 1000  # Conversion en kg
        masse_CO2_kg = emissions_gazif * 1000 # Conversion en kg
        masse_O2_kg = besoin_O2_gazif * 1000  # Conversion en kg
        "Calcul de la consommation électrique de compression de l'O2 entre l'électrolyseur et FT"
        conso_compression_O2 = comp.conso_compression(masse_O2_kg, "O2", 0.8, 1, 20, 288.15)
        "Calcul de la consommation électrique de compression du CO2 capté sortie du réactuer BioTJet et amené à EM-Lacq"
        conso_compression_CO2 = comp.conso_compression(masse_CO2_kg, "CO2", 0.8, 1, 20, 288.15)
        "Calcul de la consommation électrique de compression du syngas entre la gazéification et FT"
        conso_compression_syngas = comp.conso_compression_syngaz(masse_CO2_kg, masse_H2_kg, masse_CO_kg, 0.85, 1, 1.12, 323.15) #hypothèse flux total de gaz à ventiler
        conso_elec_compression = conso_compression_O2 + conso_compression_syngas + conso_compression_CO2
        consos_energies.append(conso_elec_compression)
        print("Consommation électrique compression : ", conso_elec_compression, " kWh")
        

        print("-"*60)
        print("Étape 6 : Calcul des émissions totales et consommations énergétiques")
        emissions_2050, emissions_2023 = energie.emissions_energie_totale(consos_energies)
        print(f"Hypothèse thermique : {energie.verif_hypothèse(consos_thermiques)}")

        print("-"*60)
        print("Résultats finaux :")
        total_emissions_2050 = emissions_2050[-1]
        total_emissions_2023 = emissions_2023[-1]
        total_conso_energie = sum(consos_energies)
        total_conso_thermique = sum(consos_thermiques)
        print(f" - Consommation électrique totale : {total_conso_energie:.2f} kWh")
        print(f" - Consommation thermique totale : {total_conso_thermique:.2f} MJ")
        print(f" - Émissions totales en 2050 : {total_emissions_2050/1000000:.2f} tCO2e")
        print(f" - Émissions totales en 2023 : {total_emissions_2023/1000000:.2f} tCO2e")        
        print(f" - Émissions totales par MJ de e-bio-SAF en 2023 : {total_emissions_2023 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):.4f} gCO2e/MJ")
        print(f" - Émissions totales par MJ de e-bio-SAF en 2050 : {total_emissions_2050 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):.4f} gCO2e/MJ")
        print("------------------------------FIN---------------------------------")
    
    
    
    


if __name__ == "__main__":
    __main__()
