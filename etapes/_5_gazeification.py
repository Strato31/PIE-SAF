from etapes import _1_biomasse as biomasse
from etapes import _7_compression as comp

"""
Paramètres et hypothèses sourcées pour la gazeification, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées : Calcul de la quantité de syngas en sortie 
###############################################################


gaz_params = {


    #Le taux carbone du bois sec est autour de 50% de C et est assez indépendant de l'essence de l'arbre (source : https://www-woodworks-org.translate.goog/resources/calculating-the-carbon-stored-in-wood-products/?_x_tr_sl=en&_x_tr_tl=fr&_x_tr_hl=fr&_x_tr_pto=rq)
    "taux_carbone": 0.50,       #Taux carbone du bois sec (% de masse)

    #Source : https://www.appa.asso.fr/wp-content/uploads/2020/02/Rogaume_2009.pdf 
    "fractionO" : 0.43, # Pourcentage massique d'oxygène contenu dans la biomasse sèche 

    #Source "t'inquiète"
    "fractionH2" : 0.75, # Fraction de H2 injectée dans le syngaz, nécessaire que pour la V1

    #Masses moalires utiles pour la partie gazeification
    "masseMolaireC" : 12 , 
    "masseMolaireO" : 16 ,
    "masseMolaireH" : 1 ,

    # Conditions standards pour le syngas
    "P" : 101325 , # Pression du syngas en Pa = 1atm
    "T" : 273, # Température du syngas en K (0°C)??

    "R" : 8.314,  # constante des gaz parfait J/mol·K 

    "filtres_amine" : 4, # Quantité unitaire élec. pour chauffage et désorption filtres amine GJ/t

    "fondtionnement_interne" : 2 # Pourcentage de l'énergie des entrants utilisé pour le fonctionnement interne de la gazéification (%)
    }


caract_syngas = {
    
    # Caractéristiques des différents composants du syngas (source : Galtié)
        
    # Il faut que "CO + H2> 80%" pour que le syngas soit utilisable en synthèse Fischer-Tropsch (source : ?)

    #Pour chaque composé : fraction en masse (%), nombre d'atomes de C, H, O, masse molaire (g/mol)

    "CO":   {"fraction": 0.70, "nC": 1,  "nH": 0, "nO": 1,  "M": 28.0},
    "CO2":  {"fraction": 0.15, "nC": 1,  "nH": 0, "nO": 2,  "M": 44.0},
    "CH4":  {"fraction": 0.01,  "nC": 1,  "nH": 4, "nO": 0,  "M": 16.0},
    "C2H2": {"fraction": 0.005,  "nC": 2,  "nH": 2, "nO": 0,  "M": 26.0},
    "C3H6": {"fraction": 0.005,  "nC": 3,  "nH": 6, "nO": 0,  "M": 42.0},
    "C20":  {"fraction": 0.001,  "nC": 1, "nH": 42, "nO": 0,  "M": 54.0}, #bizarre, résultats à pas prendre en compte : déchet 
    "H2":   {"fraction": 0.13, "nC": 0,  "nH": 2, "nO": 0,  "M": 2.0}
}


##############################################################
# Fonctions de calcul des émissions : Calcul de la quantité de syngas en sortie 
##############################################################

#Fonction de conversion en masse de CO2 en Carbone
def conversionMasseCO2_masseC(masse_CO2,gaz_params):

    #Rapport de la masse molaire du carbone sur celle du CO2
    masse_C = masse_CO2 * (gaz_params["masseMolaireC"]/(gaz_params["masseMolaireC"]+2*gaz_params["masseMolaireO"])) # masse_CO2 * (12/44)
    return masse_C

#Fonction de conversion en masse de Carbone en CO2
def conversionMasseC_masseC02(masse_C):

    #Rapport de la masse molaire du CO2 sur celle du carbone
    masse_CO2 = masse_C * ((gaz_params["masseMolaireC"]+2*gaz_params["masseMolaireO"])/gaz_params["masseMolaireC"]) # masse_C * (44/12)
    return masse_CO2

def conversionMasseMolaire(Mcomposé,gaz_params):
    """
    Conversion de la masse molaire(g/mol) d'un composé gazeux en masse volumique (kg/m3)  (1kg/m3 = 1 g/L)
    :param Mcomposé: Masse molaire du composé (g/mol)
    :param gaz_params: Paramètres physiques du gaz
    :return: Masse volumique du composé (kg/m3)

    NB = 22.4 L/mol à 0°C et 1 atm dans l'excel (volume molaire d'un gaz parfait)

    """
    R = gaz_params["R"]
    T = gaz_params["T"]
    P = gaz_params["P"]
    volume_molaire = 1000*(R * T) / P  # en m3/mol  
    masse_molaire = Mcomposé / volume_molaire # en kg/m3
    
    return masse_molaire


def gazeificationV1(biomasseEntree,masseEntree_O2, masseEntree_H2, gaz_params):

    """
    Bilan des masses du procédé de gazéification
    
    :param biomasseEntree: Valeur de sortie par l'étape Biomasse
    :param masseEntree_O2: Valeur de sortie par l'étape Electrolyse
    :param masseEntree_H2: Valeur de sortie par l'étape Electrolyse
    :param gaz_params: Paramètres de la gazéification

    Réactions principales :
    Eau/Gaz 				C+H2O →CO+H2	 
    Boudouard				C + CO2 → 2CO 
    Changement eau-gaz 		CO + H2O → CO2 + H2       
    Méthanation (réaction de Sabatier)	CO + 3H2→ CH4 + H2O

    Réaction non équilibrée de la gazéification :
    C + O2 + H2  → CO + H2 + CO2

    """

    #Paramètres d'entrée
    masse_C = biomasseEntree * gaz_params["taux_carbone"]
    masseEntree_H2reelle = masseEntree_H2*gaz_params["fractionH2"]

    masse_tot_entree = masse_C + masseEntree_O2 + masseEntree_H2reelle

    #Gazéification

    masseC_perdue =  167200 # tonnes de C perdue par an à remplacer par un calcul plus précis dans V2 (masseCarboneEntrée_ - masseCarboneSortie)(masseCarboneSortie = masseCdanskérosène_sortie + masseCO2_sortie * (12/44) + masseC_dans_Naphta_sortie) )
    masseCO2captee = 123200 # tonnes de CO2 par an à remplacer par un calcul plus précis dans V2 (d'après revendications Elyse)

    #Paramètres de sortie
    
    massseCO2perdue_recuperee = conversionMasseC_masseC02(masseC_perdue)*gaz_params["fractionCO2perdue_syngas"]

    masseCO2_sortie= masseCO2captee + massseCO2perdue_recuperee
    
    #hyp? 
    masseH2_sortie = masseEntree_H2reelle

    # masses entrées = masses sorties (= masseCO + massseH2 + masseCO2 + masseDechets) (masseDechets (~2%)<<les autres masses)
    masseCO_sortie = masse_tot_entree - masseH2_sortie - masseCO2_sortie

    return masseCO_sortie, masseH2_sortie, masseCO2_sortie

def gazeificationV2(biomasseEntree, gaz_params, caract_syngas):

    """
    Bilan complet de masse et de moles pour la gazeification avec bilans atomiques C, H, O
    :param biomasseEntree: Valeur de sortie par l'étape Biomasse
    :param gaz_params: Paramètres de la gazéification
    :param caract_syngas: Caractéristiques du syngas
    :return: masseCO_sortie, masseH2_necessaire, masseCO2_sortie, masseO2_necessaire

    NB : La somme des fractions volumiques des gaz doit être égale à 1
    80% de CO + H2 dans le syngas pour être conforme (source : ?) :

    """

    # ------------------------------
    # Paramètres d'entrée
    # ------------------------------

    masse_C = biomasseEntree * gaz_params["taux_carbone"]

    # Normalisation des fractions 
    total_fraction = sum(gas["fraction"] for gas in caract_syngas.values())

    caract_syngas_normalized = {
        gas_name: {
            **gas_data,
            "fraction": gas_data["fraction"] / total_fraction
        }
        for gas_name, gas_data in caract_syngas.items()
    }

    # Vérification de la condition CO + H2 > 80 % (fraction volumique)
    if caract_syngas_normalized["CO"]["fraction"] + caract_syngas_normalized["H2"]["fraction"] < 0.80:
        raise ValueError("Syngas non conforme : fraction volumique CO + H2 < 80 %")

    # ------------------------------
    # Conversion fractions volumiques -> massiques
    # ------------------------------

    masses_vol_ponderees = {
        gas: conversionMasseMolaire(caract_syngas[gas]["M"], gaz_params) *
             caract_syngas_normalized[gas]["fraction"]
        for gas in caract_syngas
    }    

    somme_masses_vol = sum(masses_vol_ponderees.values())
    pourcentages_massiques = {
        gas: masses_vol_ponderees[gas] / somme_masses_vol
        for gas in caract_syngas
    }

    # ------------------------------
    # Séparation gaz carbonés
    # ------------------------------

    carbon_gases = [k for k, v in caract_syngas_normalized.items() if v["nC"] > 0]

    # Masses de carbone et hors carbone
    masses_carbone = {}
    masses_hors_carbone = {}
    masses_totales_composes = {}

    #Version de l'excel qui parait fausse 
    # for i, compo in enumerate(carbon_gases):
    #      masses_carbone[compo] = pourcentages_massiques[compo] * masse_C
    #      if caract_syngas[compo]["nO"] == 0:
    #          masses_hors_carbone[compo] = masses_carbone[compo] * gaz_params["masseMolaireH"] / gaz_params["masseMolaireC"]
    #      else:
    #          masses_hors_carbone[compo] = masses_carbone[compo] * gaz_params["masseMolaireO"] / gaz_params["masseMolaireC"]
    #      masses_totales_composes[compo] = masses_carbone[compo] + masses_hors_carbone[compo]

    
    # Calcul des masses hors carbone et masses totales de chaque composé
    for compo in carbon_gases:
         
         masses_carbone[compo] = pourcentages_massiques[compo] * masse_C
         # Masse hors carbone = masseC * (nH*MH + nO*MO) / (nC*MC)
         masses_hors_carbone[compo] = masses_carbone[compo] * (
             caract_syngas[compo]["nH"] * gaz_params["masseMolaireH"] +
             caract_syngas[compo]["nO"] * gaz_params["masseMolaireO"]
         ) / (caract_syngas[compo]["nC"] * gaz_params["masseMolaireC"])

         # Masse totale du composé = masse de carbone + masse hors carbone
         masses_totales_composes[compo] = masses_carbone[compo] + masses_hors_carbone[compo]
    
    vol_composes = {}

    for compo in carbon_gases:
        #Calcul des volumes des composés en Nm3
        vol_composes[compo] = masses_totales_composes.get(compo,0) *1000/conversionMasseMolaire(caract_syngas[compo]["M"], gaz_params)

    # ------------------------------
    # Calcul H2 à injecter et nécessaire
    # ------------------------------

    #Calcul de H2 faux dans l'excel
    #masseH2_syngaz = masse_C - sum(masses_carbone.values()) # H2 à injecter dans le syngaz
    #masseH2_necessaire = masseH2_syngaz / gaz_params["fractionH2"] #H2 à produire pour le syngaz (seulement 75% de H2 injecté dans le syngaz)

    # Calcul de la masse de H2 dans le syngaz version corrigée
    masseH2_syngaz = 0
    for compo in carbon_gases:
        nH = caract_syngas[compo]["nH"]
        if nH > 0:
            masseH2_syngaz += masses_totales_composes[compo] * (nH * gaz_params["masseMolaireH"] / caract_syngas[compo]["M"])
    

    volH2total = 2*vol_composes["CO"]  # Pour entrer dans la synthèse FT, il faut un ratio H2/CO de 2
    masseH2_totale = volH2total*conversionMasseMolaire(caract_syngas["H2"]["M"], gaz_params) /1000 # Pasage du volume en tonnes
    masseH2_necessaire = masseH2_totale - masseH2_syngaz # Du H2 est contenu dans le syngaz, on ne le compte pas dans le H2 à produire

    #Le code précédent remplace la version simplifiée si dessous avec une fraction H2 non sourcée de 75%
    #masseH2_necessaire = masseH2_syngaz / gaz_params["fractionH2"] 

    # ------------------------------
    # Calcul O2 nécessaire     ##### A VERIFIER 
    # ------------------------------
    masseO_dans_syngaz = 0
    for compo in carbon_gases:
        nO = caract_syngas[compo]["nO"]
        if nO > 0:
            masseO_dans_syngaz += masses_totales_composes[compo] * (nO * gaz_params["masseMolaireO"] / caract_syngas[compo]["M"])

    masseO_biomasse = biomasseEntree * gaz_params["fractionO"] # O contenu dans la biomasse sèche

    # Calcul de l'O nécessaire à ajouter en entrée de la gazéification pour la combustion
    masseO_necessaire = masseO_dans_syngaz - masseO_biomasse

    masseO2_necessaire = max(0, masseO_necessaire) * 2


    # ------------------------------
    # Récupération CO et CO2
    # ------------------------------
    masseCO_sortie = masses_totales_composes.get("CO", 0)
    masseCO2_sortie = masses_totales_composes.get("CO2", 0)

    # ------------------------------
    # Récupération masses déchets (méthane, autres hydrocarbures)
    # ------------------------------

    masse_dechets = masses_totales_composes.get("CH4", 0) + masses_totales_composes.get("C2H2", 0) + masses_totales_composes.get("C3H6", 0) + masses_totales_composes.get("C20", 0)
    
    print("\n========== RÉSULTATS GAZÉIFICATION V2 ==========")
    print(f"Biomasse sèche en entrée      : {biomasseEntree} tonnes/an")
    print(f"Carbone dans la biomasse      : {masse_C} tonnes/an")
    print("------------------------------------------------")
    print(f"CO produit                    : {masseCO_sortie} tonnes/an")
    print(f"CO₂ produit                   : {masseCO2_sortie} tonnes/an")
    print(f"H₂ dans syngaz                : {masseH2_syngaz} tonnes/an")
    print(f"H₂ à ajouter                  : {masseH2_necessaire} tonnes/an")
    print(f"O₂ nécessaire                 : {masseO2_necessaire} tonnes/an")
    print(f"Masse déchets estimée         : {masse_dechets} tonnes/an")
    print("================================================\n")

    return masseCO_sortie, masseH2_necessaire, masseCO2_sortie, masseO2_necessaire,masse_dechets

#gazeificationV2(biomasseEntree=300000, gaz_params=gaz_params, caract_syngas=caract_syngas)


def bilan_chaleur_gazeification():

    chaleur = 0

    return chaleur


def conso_elec_gazeification(masse_CO2, masse_H2, masse_seche_biomasse, gaz_params):
    """
    Calcul de la consommation électrique de gazéification.
    Consommation liée aux entrants de la gazéification : biomasse et H2.
    Consommation liée au chauffage et à la désorption des filtres amines pour le captage du CO2.
    """
    energie_entrants_H2 = masse_H2 * comp.carac_pysico_chimiques["H2"]["PCI"] / 3600 * 10e6# en kWh
    energie_entrants_bois = masse_seche_biomasse * biomasse.param_biomasse['PCI_biomasse'] # en kWh
    energie_entrants = (energie_entrants_H2 + energie_entrants_bois)*gaz_params['fondtionnement_interne']/100 # en kWh
    energie_desorption_filtres_amines = masse_CO2 * gaz_params["filtres_amine"] / 3600 * 10e6 # en kWh
    energie_gazeification = energie_desorption_filtres_amines + energie_entrants # en kWh
    return energie_gazeification

################################################################
#Inversion du code pour retrouver la biomasse nécessaire à une quantité de syngas donnée
################################################################

#def Inv_gazeificationV2(masseCO_sortie,masseCO2_sortie,masse_dechets, gaz_params, caract_syngas):
def Inv_gazeificationV2(masseCO_sortie,masseCO2_sortie, gaz_params, caract_syngas):

    # Normalisation des fractions 
    total_fraction = sum(gas["fraction"] for gas in caract_syngas.values())

    caract_syngas_normalized = {
        gas_name: {
            **gas_data,
            "fraction": gas_data["fraction"] / total_fraction
        }
        for gas_name, gas_data in caract_syngas.items()
    }

    # Vérification de la condition CO + H2 > 80 % (fraction volumique)
    if caract_syngas_normalized["CO"]["fraction"] + caract_syngas_normalized["H2"]["fraction"] < 0.80:
        raise ValueError("Syngas non conforme : fraction volumique CO + H2 < 80 %")

    # ------------------------------
    # Conversion fractions volumiques -> massiques
    # ------------------------------

    masses_vol_ponderees = {
        gas: conversionMasseMolaire(caract_syngas[gas]["M"], gaz_params) *
             caract_syngas_normalized[gas]["fraction"]
        for gas in caract_syngas
    }    

    somme_masses_vol = sum(masses_vol_ponderees.values())
    pourcentages_massiques = {
        gas: masses_vol_ponderees[gas] / somme_masses_vol
        for gas in caract_syngas
    }

    #masses_totales_composes = {"CO": masseCO_sortie, "CO2": masseCO2_sortie, "dechets": masse_dechets}
    masses_totales_composes = {"CO": masseCO_sortie, "CO2": masseCO2_sortie}


    for gas in caract_syngas:
        if gas not in masses_totales_composes:
            masses_totales_composes[gas] = (pourcentages_massiques[gas] / (pourcentages_massiques["CO"] + pourcentages_massiques["CO2"])) * (masseCO_sortie + masseCO2_sortie)
            #La masse des autres composés est estimée proportionnellement à leur pourcentage massique par rapport à la somme CO + CO2
    # ------------------------------
    # Séparation gaz carbonés
    # ------------------------------

    carbon_gases = [k for k, v in caract_syngas_normalized.items() if v["nC"] > 0]

        
    # ------------------------------
    # Calcul C issu de la biomasse nécessaire   
    # ------------------------------

    masse_C_total = 0
    for compo in carbon_gases:
        nC = caract_syngas[compo]["nC"]
        if nC > 0:
            masse_C_total += masses_totales_composes[compo] * (nC * gaz_params["masseMolaireC"] / caract_syngas[compo]["M"])

    #estimation de la biomasse sèche nécessaire
    biomasseEntree = masse_C_total / gaz_params["taux_carbone"]


    # ------------------------------
    # Calcul O2 nécessaire     ##### A VERIFIER 
    # ------------------------------


    masseO_dans_syngaz = 0
    for compo in carbon_gases:
        nO = caract_syngas[compo]["nO"]
        if nO > 0:
            masseO_dans_syngaz += masses_totales_composes[compo] * (nO * gaz_params["masseMolaireO"] / caract_syngas[compo]["M"])

    masseO_biomasse = biomasseEntree * gaz_params["fractionO"] # O contenu dans la biomasse sèche

    # Calcul de l'O nécessaire à ajouter en entrée de la gazéification pour la combustion
    masseO_necessaire = masseO_dans_syngaz - masseO_biomasse

    masseO2_necessaire = max(0, masseO_necessaire) * 2

    # ------------------------------
    # Calcul H2 à injecter et nécessaire        
    # ------------------------------

    masseH2_syngaz = 0
    for compo in carbon_gases:
        nH = caract_syngas[compo]["nH"]
        if nH > 0:
            masseH2_syngaz += masses_totales_composes[compo] * (nH * gaz_params["masseMolaireH"] / caract_syngas[compo]["M"])
    
    volume_CO = masses_totales_composes["CO"] *1000/conversionMasseMolaire(caract_syngas["CO"]["M"], gaz_params)

    volH2total = 2*volume_CO # Pour entrer dans la synthèse FT, il faut un ratio H2/CO de 2
    masseH2_totale = volH2total*conversionMasseMolaire(caract_syngas["H2"]["M"], gaz_params) /1000 # Pasage du volume en tonnes
    masseH2_necessaire = masseH2_totale - masseH2_syngaz # Du H2 est contenu dans le syngaz, on ne le compte pas dans le H2 à produire

    #Estimation masse déchets (méthane, autres hydrocarbures)
    masse_dechets = masses_totales_composes.get("CH4", 0) + masses_totales_composes.get("C2H2", 0) + masses_totales_composes.get("C3H6", 0) + masses_totales_composes.get("C20", 0)

    print("\n========== RÉSULTATS GAZÉIFICATION INVERSE V2 ==========")
    print(f"CO FT                         : {masseCO_sortie} tonnes/an")
    print(f"CO₂ FT                        : {masseCO2_sortie} tonnes/an")
    print("------------------------------------------------")
    print(f"Biomasse sèche en entrée      : {biomasseEntree} tonnes/an")
    print(f"O₂ nécessaire                 : {masseO2_necessaire} tonnes/an")
    print(f"H₂ dans syngaz                : {masseH2_syngaz} tonnes/an")
    print(f"H₂ à ajouter                  : {masseH2_necessaire} tonnes/an")
    print(f"Masse estimée déchets         : {masse_dechets} tonnes/an")
    print("------------------------------------------------")

    return biomasseEntree, masseH2_necessaire, masseO2_necessaire

#Inv_gazeificationV2(253942.40023691423,134374.76863848377, gaz_params, caract_syngas)
