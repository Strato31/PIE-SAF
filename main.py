"""
Contient le main du projet, qui orchestre les différentes étapes du processus de production d'e-bio-SAF, 
en partant de la biomasse jusqu'au carburant e-bio-SAF, ou inversement.

Pour faire le calcul dans le sens physique (biomasse -> carburant), il suffit de mettre la variable "sens_physique" à True
et de renseigner les biomasses d'entrée dans la variable "biomasse_entree".

Pour faire le calcul dans le sens inverse (carburant -> biomasse), il suffit de mettre la variable "sens_physique" à False
et de renseigner la quantité de e-bio-SAF produite dans la variable "kerosene_produit".
"""
from etapes import _1_biomasse as biomasse
from etapes import kerosene
from etapes import _3_FT as ft
from etapes import _4_electrolyseur as elec
from etapes import _5_gazeification as gaz
from etapes import _6_energie as energie
from etapes import _7_compression as comp
from etapes import emissions_evitees 

# TODO : ajouter des :.2f pour arrondir les affichages des flottants
# TODO : harmoniser /an

######################
# VARIABLES D'ENTRÉE #
######################

# True : calcul biomasse -> carburant, False : calcul sens inverse
sens_physique = False

# Pour le sens physique, renseigner les biomasses d'entrée dans la variable "biomasse_entree". Uniquement type bois_vert implémenté.
biomasse_entree = [
    {"type" : "bois_vert", "masse": 300000, "humidité": 0},  # 300 000 tonnes de biomasse ligneuse à 0% d'humidité
    {"type" : "bois_vert", "masse": 0, "humidité": 0.30},  # 0 tonnes de biomasse ligneuse à 30% d'humidité
]

# Pour le sens inverse, renseigner la quantité de e-bio-SAF produite dans la variable "kerosene_produit"
kerosene_produit = 97209  # en t de e-bio-SAF produites

# Si True, on ne prend pas en compte les pertes en ligne sur le réseau de distribution haute tension : on considère l'énergie consommée.
# Si False, on prend en compte ces pertes : on considère l'énergie produite.
# N'affecte que les résultats finaux, pas les consommations intermédiaires de chaque étape.
elec_conso = True

######################


def __main__():

    # Cas calcul sens physique : biomasse -> carburant
    if sens_physique == True:

        print("Calcul des émissions et consommations du processus e-bio-SAF complet, en partant de la biomasse jusqu'au carburant e-bio-SAF.")
        print("-"*60)
        print("Le calcul se base sur les hypothèses sourcées dans chaque étape du processus.\n On prend en entrée les biomasses suivantes :")
        
        # Rappel des biomasses d'entrée renseignées dans la variable "biomasse_entree"
        for b in biomasse_entree:
            print(f" - {b['masse']} t de biomasse de type {b['type']} à {b['humidité']*100}% d'humidité")
        
        # Initialisation des listes pour stocker les consommations et émissions de chaque étape du processus
        consos_energies, consos_thermiques, emissions_co2 = [], [], []
        
        print("-"*60,"\n")
        print("Étape 1 : Biomasse")
        conso_chaleur, total_emissions, masse_seche_biomasse = biomasse.Biomasse(biomasse.param_biomasse, biomasse_entree, sens_physique)
        consos_thermiques.append(conso_chaleur)
        emissions_co2.append(total_emissions)
        
        print("-"*60)
        print("Étape 2 : Gazeification")
        CO_gazif, besoin_H2_gazif, emissions_gazif, besoin_O2_gazif,dechets_gazif = gaz.gazeificationV2(masse_seche_biomasse, gaz.gaz_params, gaz.caract_syngas)
        conso_elec_gaz = gaz.conso_elec_gazeification(emissions_gazif, besoin_H2_gazif, masse_seche_biomasse, gaz.gaz_params)
        print("Consommation électrique : ", f"{conso_elec_gaz:,.2f}".replace(",", " "), " en kWh")
        print("Émissions de CO2 liées à la gazéification : ", f"{emissions_gazif:,.2f}".replace(",", " "), " en tCO2e")
        consos_energies.append(conso_elec_gaz)
        emissions_co2.append(emissions_gazif)
        
        print("-"*60)
        print("Étape 3 : Fischer-Tropsch")
        consommation_totale_FT, emissions_FT, _ = ft.Fischer_Tropsch(ft.param_FT, CO_gazif)
        emissions_co2.append(emissions_FT)
        consos_energies.append(consommation_totale_FT )
        
        print("-"*60)
        print("Étape 4 : Électrolyseur")
        conso_elec_elec = elec.consommation_electrolyseur(elec.param_electrolyseur_PEM, besoin_O2_gazif, besoin_H2_gazif)
        print("Consommation électrique électrolyseur : ", f"{conso_elec_elec:,.2f}".replace(",", " "), " en kWh")
        consos_energies.append(conso_elec_elec)
        
        print("-"*60)
        print("Étape 5 : Compression")
        masse_CO_kg = CO_gazif * 1000         # Conversion en kg
        masse_H2_kg = besoin_H2_gazif * 1000  # Conversion en kg
        masse_CO2_kg = emissions_gazif * 1000 # Conversion en kg
        masse_O2_kg = besoin_O2_gazif * 1000  # Conversion en kg
        # Calcul de la consommation électrique de compression de l'O2 entre l'électrolyseur et FT
        conso_compression_O2 = comp.conso_compression(masse_O2_kg, "O2", 0.8, 1, 20, 288.15)
        # Calcul de la consommation électrique de compression du CO2 capté sortie du réactuer BioTJet et amené à EM-Lacq
        conso_compression_CO2 = comp.conso_compression(masse_CO2_kg, "CO2", 0.8, 1, 20, 288.15)
        # Calcul de la consommation électrique de compression du syngas entre la gazéification et FT
        conso_compression_syngas = comp.conso_compression_syngaz(masse_CO2_kg, masse_H2_kg, masse_CO_kg, 0.85, 1, 1.12, 323.15) #hypothèse flux total de gaz à ventiler
        conso_elec_compression = conso_compression_O2 + conso_compression_syngas + conso_compression_CO2
        print("Consommation électrique compression : ", f"{conso_elec_compression:,.2f}".replace(",", " "), " en kWh")
        consos_energies.append(conso_elec_compression)
        
        print("-"*60)
        print("Étape 6 : Calcul des émissions totales et consommations énergétiques")
        emissions_2050, emissions_2023 = energie.emissions_energie_totale(consos_energies) # en gCO2e
        
        print("-"*60)
        print("Résultats finaux :")
        # Prise en compte des pertes en ligne sur le réseau de distribution haute tension (valeur de RTE)
        if not elec_conso : total_conso_energie *= (1/0.979)
        total_emissions_2050 = emissions_2050[-1] # le total est le dernier élément de la liste retournée par la fonction
        total_emissions_2023 = emissions_2023[-1] # le total est le dernier élément de la liste retournée par la fonction
        total_conso_energie = sum(consos_energies)
        total_conso_thermique = sum(consos_thermiques)
        print(f" - Consommation électrique totale : \t\t\t{total_conso_energie:,.2f} kWh".replace(",", " "))
        print(f" - Consommation thermique totale : \t\t\t{total_conso_thermique:,.2f} MJ".replace(",", " "))
        print(f" - Émissions totales en 2050 : \t\t\t\t{total_emissions_2050/1000000:,.2f} tCO2e".replace(",", " "))
        print(f" - Émissions totales en 2023 : \t\t\t\t{total_emissions_2023/1000000:,.2f} tCO2e".replace(",", " "))
        print(f" - Émissions totales par MJ de e-bio-SAF en 2023 : \t{total_emissions_2023 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):,.2f} gCO2e/MJ".replace(",", " "))
        print(f" - Émissions totales par MJ de e-bio-SAF en 2050 : \t{total_emissions_2050 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):,.2f} gCO2e/MJ".replace(",", " "))
        print("------------------------------FIN---------------------------------")

        # consos_energies contient les consos élec pour [gazeification, FT, électrolyseur, compression]
        # consos_thermiques contient les consos thermiques pour [biomasse]
        # emissions_co2 contient les émissions de CO2 pour [biomasse, gazeification, FT]


    # Cas calcul sens inverse : carburant -> biomasse
    else: 
        print("Calcul des émissions et consommations du processus e-bio-SAF complet, en partant du carburant e-bio-SAF produit jusqu'à la biomasse.")
        print("-"*60)
        print("Le calcul se base sur les hypothèses sourcées dans chaque étape du processus.")
        print(f"\nOn a en entrée {kerosene_produit:,.2f} t e-bio-SAF produites.\n".replace(",", " "))
        
        # Initialisation des listes pour stocker les consommations et émissions de chaque étape du processus
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
        print(f"Consommation électrique : {conso_elec_gaz:,.2f} kWh".replace(",", " "))
        consos_energies.append(conso_elec_gaz)
        emissions_co2.append(emissions_gazif)

        print("-"*60)
        print("Étape 3 : Électrolyseur")
        conso_elec_elec = elec.consommation_electrolyseur(elec.param_electrolyseur_PEM, besoin_O2_gazif, besoin_H2_gazif)
        print(f"Consommation électrique électrolyseur : {conso_elec_elec:,.2f} kWh".replace(",", " "))
        consos_energies.append(conso_elec_elec)

        print("-"*60)
        print("Étape 4 : Biomasse")
        conso_chaleur, total_emissions, _ = biomasse.Biomasse(biomasse.param_biomasse, masse_seche_biomasse, sens_physique)
        consos_thermiques.append(conso_chaleur)
        emissions_co2.append(total_emissions)

        print("-"*60)
        print("Étape 5 : Compression")
        masse_CO_kg = masseCO_sortie * 1000  # Conversion en kg
        masse_H2_kg = besoin_H2_gazif * 1000  # Conversion en kg
        masse_CO2_kg = emissions_gazif * 1000 # Conversion en kg
        masse_O2_kg = besoin_O2_gazif * 1000  # Conversion en kg
        # Calcul de la consommation électrique de compression de l'O2 entre l'électrolyseur et FT
        conso_compression_O2 = comp.conso_compression(masse_O2_kg, "O2", 0.8, 1, 20, 288.15)
        # Calcul de la consommation électrique de compression du CO2 capté sortie du réactuer BioTJet et amené à EM-Lacq
        conso_compression_CO2 = comp.conso_compression(masse_CO2_kg, "CO2", 0.8, 1, 20, 288.15)
        # Calcul de la consommation électrique de compression du syngas entre la gazéification et FT
        conso_compression_syngas = comp.conso_compression_syngaz(masse_CO2_kg, masse_H2_kg, masse_CO_kg, 0.85, 1, 1.12, 323.15) #hypothèse flux total de gaz à ventiler
        conso_elec_compression = conso_compression_O2 + conso_compression_syngas + conso_compression_CO2
        print(f"Consommation électrique compression : {conso_elec_compression:,.2f} kWh".replace(",", " "))
        consos_energies.append(conso_elec_compression)
        

        print("-"*60)
        print("Étape 6 : Calcul des émissions totales et consommations énergétiques")
        emissions_2050, emissions_2023 = energie.emissions_energie_totale(consos_energies)

        print("-"*60)
        print("Résultats finaux :")
        total_emissions_2050 = emissions_2050[-1] # le total est le dernier élément de la liste retournée par la fonction
        total_emissions_2023 = emissions_2023[-1] # le total est le dernier élément de la liste retournée par la fonction
        total_conso_energie = sum(consos_energies)
        total_conso_thermique = sum(consos_thermiques)
        # Prise en compte des pertes en ligne sur le réseau de distribution haute tension (valeur de RTE)
        if not elec_conso : total_conso_energie *= (1/0.979)

        print(f" - Consommation électrique totale : \t\t\t{total_conso_energie:,.2f} kWh".replace(",", " "))
        print(f" - Consommation thermique totale : \t\t\t{total_conso_thermique:,.2f} MJ".replace(",", " "))
        print(f" - Émissions totales en 2050 : \t\t\t\t{total_emissions_2050/1000000:,.2f} tCO2e".replace(",", " "))
        print(f" - Émissions totales en 2023 : \t\t\t\t{total_emissions_2023/1000000:,.2f} tCO2e".replace(",", " "))        
        print(f" - Émissions totales par MJ de e-bio-SAF en 2023 : \t{total_emissions_2023 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):,.4f} gCO2e/MJ".replace(",", " "))
        print(f" - Émissions totales par MJ de e-bio-SAF en 2050 : \t{total_emissions_2050 / (ft.param_FT['production_BioTJet'] * ft.param_FT['PCI_kerosene'] * 1000):,.4f} gCO2e/MJ".replace(",", " "))
        print("------------------------------FIN---------------------------------")

        # consos_energies contient les consos élec pour [FT, gazeification, électrolyseur, compression]
        # consos_thermiques contient les consos thermiques pour [biomasse]
        # emissions_co2 contient les émissions de CO2 pour [FT, gazeification, biomasse]
    
    
    
    


if __name__ == "__main__":
    __main__()
