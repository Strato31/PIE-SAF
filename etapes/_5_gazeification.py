"""
PARTIE : Gazeification

Contient : 
- paramètres sourcés pour la gazeification :
    - gaz_params : dictionnaire des paramètres de la gazéification
    - caract_syngas : dictionnaire des caractéristiques du syngas produit
- fonctions de conversion utiles pour la gazéification
- fonctions de bilan de masse pour la gazéification :
    - gazeificationV1 : première version simplifiée de la gazéification
    - gazeificationV2 : version complète avec bilans atomiques C, H, O
- fonction de calcul de la consommation électrique de la gazéification
- fonction d'inversion de la gazéification pour retrouver la biomasse nécessaire à une quantité de syngas donnée
Paramètres et hypothèses sourcées pour la gazeification, puis fonctions de calcul des émissions.
"""

from etapes import _1_biomasse as biomasse
from etapes import _7_compression as comp


###############################################################
# Stockage des paramètres de la gazeification
###############################################################


gaz_params = {

    #Le taux carbone du bois sec est autour de 50% de C et est assez indépendant de l'essence de l'arbre (source : https://www-woodworks-org.translate.goog/resources/calculating-the-carbon-stored-in-wood-products/?_x_tr_sl=en&_x_tr_tl=fr&_x_tr_hl=fr&_x_tr_pto=rq)
    "taux_carbone": 0.50,       #Taux carbone du bois sec (% de masse)

    #Source : https://www.appa.asso.fr/wp-content/uploads/2020/02/Rogaume_2009.pdf 
    "fractionO" : 0.43, # Pourcentage massique d'oxygène contenu dans la biomasse sèche 

    #Source "t'inquiète"
    "fractionH2" : 0.75, # Fraction de H2 injectée dans le syngaz, nécessaire que pour la fonction gazeificationV1

    #Masses molaires utiles pour la partie gazéification
    "masseMolaireC" : 12 ,  #g/mol
    "masseMolaireO" : 16 ,  #g/mol
    "masseMolaireH" : 1 ,   #g/mol

    # Conditions standards pour le syngas
    "P" : 101325 ,  # Pression du syngas en Pa = 1atm
    "T" : 273,      # Température du syngas en K (0°C)
    "R" : 8.314,    # constante des gaz parfait J/mol·K 

    # Quantité unitaire élec. pour chauffage et désorption filtres amine GJ/t
    "filtres_amine" : 4, 
    
    # Pourcentage de l'énergie des entrants utilisé pour le fonctionnement interne de la gazéification (%)
    "fonctionnement_interne" : 2 
    }


caract_syngas = {
    
    # Caractéristiques des différents composants du syngas (source : pourcentages viennent de Bernard Galtié)
    # Il faut que "CO + H2> 80%vol" pour que le syngas soit utilisable en synthèse Fischer-Tropsch 
    # (source : https://d2zo35mdb530wx.cloudfront.net/_binary/UCPthyssenkruppUhde/5e5b1ace-c7c7-4b69-a542-ef2dbad0cfee/link-TK_20_0770_uhde_Gasification_Broschuere_SCREEN.pdf )

    #Pour chaque composé : fraction en masse (%), nombre d'atomes de C, H, O, masse molaire (g/mol)

    "CO":   {"fraction": 0.78, "nC": 1,  "nH": 0, "nO": 1,  "M": 28.0},
    "CO2":  {"fraction": 0.1, "nC": 1,  "nH": 0, "nO": 2,  "M": 44.0},
    "CH4":  {"fraction": 0.01,  "nC": 1,  "nH": 4, "nO": 0,  "M": 16.0},
    "C2H2": {"fraction": 0.005,  "nC": 2,  "nH": 2, "nO": 0,  "M": 26.0},
    "C3H6": {"fraction": 0.005,  "nC": 3,  "nH": 6, "nO": 0,  "M": 42.0},
    "C20":  {"fraction": 0.000,  "nC": 1, "nH": 42, "nO": 0,  "M": 54.0},  
    "H2":   {"fraction": 0.1, "nC": 0,  "nH": 2, "nO": 0,  "M": 2.0}
}


############################
# Fonctions de conversions #
############################

def conversionMasseMolaire(Mcomposé,gaz_params):
    """
    Conversion de la masse molaire(g/mol) d'un composé gazeux en masse volumique (kg/m3)  (1kg/m3 = 1 g/L)

    Arguments :
    ----------
        Mcomposé:     Masse molaire du composé (g/mol)
        gaz_params:   Paramètres physiques du gaz

    Returns :
    ----------
        masse_molaire : Masse volumique du composé (kg/m3)
    
    NB = 22.4 L/mol à 0°C et 1 atm dans l'excel (volume molaire d'un gaz parfait)

    """
    R = gaz_params["R"]
    T = gaz_params["T"]
    P = gaz_params["P"]
    volume_molaire = 1000*(R * T) / P  # en m3/mol  
    masse_molaire = Mcomposé / volume_molaire # en kg/m3
    
    return masse_molaire

####################################################
# Fonctions de bilan de masses de la Gazéification #
####################################################

#Première version de la gazéification (simplifiée) : adaptée de la partie gazéification de l'excel PIE-SAF/ plutôt qualitative que quantitative
def gazeificationV1(biomasseEntree,masseEntree_O2, masseEntree_H2, gaz_params):
    """
    Fait le bilan des masses du procédé de gazéification.
    N'est pas utilisée dans le code principal, mais conservée pour référence.

    Arguments :
    -----------
        biomasseEntree : Masse de biomasse sèche en entrée (tonnes)
        masseEntree_O2 : Masse d'O2 en sortie de l'étape d'électrolyse (tonnes)
        masseEntree_H2 : Masse d'H2 en sortie de l'étape d'électrolyse (tonnes)
        gaz_params :     Paramètres de la gazéification
    
    Returns :
    -----------
        masseCO_sortie :  Masse de CO en sortie de gazeification (tonnes)
        masseH2_sortie :  Masse de H2 en sortie de gazeification (tonnes)
        masseCO2_sortie : Masse de CO2 en sortie de gazeification (tonnes)
    
    Réactions principales :
    Eau/Gaz 				C+H2O →CO+H2	 
    Boudouard				C + CO2 → 2CO 
    Changement eau-gaz 		CO + H2O → CO2 + H2       
    Méthanation (réaction de Sabatier)	CO + 3H2→ CH4 + H2O

    Réaction non équilibrée de la gazéification :
    C + O2 + H2  → CO + H2 + CO2
    """

    #Paramètres d'entrée : masse de C + masse de O + masse de H2
    masse_C = biomasseEntree * gaz_params["taux_carbone"]
    masseEntree_H2reelle = masseEntree_H2*gaz_params["fractionH2"]

    # Masse totale en entrée
    masse_tot_entree = masse_C + masseEntree_O2 + masseEntree_H2reelle

    #Gazéification
    masseC_perdue =  167200 # tonnes de C perdue par an à remplacer par un calcul plus précis dans V2 (d'après revendications Elyse)
    masseCO2captee = 123200 # tonnes de CO2 par an à remplacer par un calcul plus précis dans V2 (d'après revendications Elyse)

    massseCO2perdue_recuperee = masseC_perdue*(44/12)*gaz_params["fractionCO2perdue_syngas"] # conversion masse C perdue en CO2 perdue et récupérée
    
    #Paramètres de sortie
    masseCO2_sortie= masseCO2captee + massseCO2perdue_recuperee
    
    #Omission volontaire du H2 contenu dans le bois sec libéré lors de la gazéification
    masseH2_sortie = masseEntree_H2reelle

    #masses entrées = masses sorties (= masseCO + massseH2 + masseCO2 + masseDechets) (masseDechets (~2%)<<les autres masses)
    masseCO_sortie = masse_tot_entree - masseH2_sortie - masseCO2_sortie

    return masseCO_sortie, masseH2_sortie, masseCO2_sortie



def gazeificationV2(biomasseEntree, gaz_params, caract_syngas):
    """
    Deuxième version de la gazéification (plus complète) :
    Bilan complet de masse et de moles pour la gazeification avec bilans atomiques C, H, O.

    Arguments :
    -----------
        biomasseEntree :  Masse de biomasse sèche en entrée (tonnes)
        gaz_params :      Paramètres de la gazéification
        caract_syngas :   Caractéristiques du syngas produit (fractions massiques, nombres d'atomes, masses molaires)

    Returns :
    -----------
        masseCO_sortie :      Masse de CO en sortie de gazeification (tonnes)
        masseH2_necessaire :  Masse de H2 nécessaire à injecter dans la gazéification (tonnes)
        masseCO2_sortie :     Masse de CO2 en sortie de gazeification (tonnes)
        masseO2_necessaire :  Masse d'O2 nécessaire à injecter dans la gazéification (tonnes)
        masse_dechets :       Masse des autres composés en sortie de la gazéification (tonnes)
    """

    # --------------------
    # Paramètres d'entrée
    # --------------------

    # Masse de carbone dans la biomasse sèche
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

    # Vérification de la condition CO + H2 > 80 %vol (fraction volumique)
    if caract_syngas_normalized["CO"]["fraction"] + caract_syngas_normalized["H2"]["fraction"] < 0.80:
        raise ValueError("Syngas non conforme : fraction volumique CO + H2 < 80 %")

    # ---------------------------------------------
    # Conversion fractions volumiques -> massiques
    # ---------------------------------------------

    # Calcul des masses volumiques pondérées par les fractions volumiques g/m3
    masses_vol_ponderees = {
        gas: conversionMasseMolaire(caract_syngas[gas]["M"], gaz_params) *
             caract_syngas_normalized[gas]["fraction"]
        for gas in caract_syngas
    }    

    # Calcul des pourcentages massiques à partir des masses volumiques pondérées
    somme_masses_vol = sum(masses_vol_ponderees.values())
    pourcentages_massiques = {
        gas: masses_vol_ponderees[gas] / somme_masses_vol
        for gas in caract_syngas
    }

    # ------------------------
    # Séparation gaz carbonés
    # ------------------------

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

    
    # Calcul des masses hors carbone et masses totales de chaque composé t/an
    for compo in carbon_gases:
         
         # Masse de carbone calculée à partir du pourcentage massique en carbone et de la masse totale de carbone
         masses_carbone[compo] = pourcentages_massiques[compo] * masse_C

         # Masse hors carbone = masseC * (nH*MH + nO*MO) / (nC*MC)
         masses_hors_carbone[compo] = masses_carbone[compo] * (
             caract_syngas[compo]["nH"] * gaz_params["masseMolaireH"] +
             caract_syngas[compo]["nO"] * gaz_params["masseMolaireO"]
         ) / (caract_syngas[compo]["nC"] * gaz_params["masseMolaireC"])

         # Masse totale du composé = masse de carbone + masse hors carbone
         masses_totales_composes[compo] = masses_carbone[compo] + masses_hors_carbone[compo]
    
    vol_composes = {} # initialisation dictionnaire volumes composés

    #Calcul des volumes des composés en Nm3
    for compo in carbon_gases:
        vol_composes[compo] = masses_totales_composes.get(compo,0) *1000/conversionMasseMolaire(caract_syngas[compo]["M"], gaz_params)

    # -----------------------------------
    # Calcul H2 à injecter et nécessaire
    # -----------------------------------

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
    masseH2_totale = volH2total*conversionMasseMolaire(caract_syngas["H2"]["M"], gaz_params) /1000 # Passage du volume en tonnes
    masseH2_necessaire = masseH2_totale - masseH2_syngaz # Du H2 est contenu dans le syngaz, on ne le compte pas dans le H2 à produire

    # ------------------------------
    # Calcul O2 nécessaire    
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

    return masseCO_sortie, masseH2_necessaire, masseCO2_sortie, masseO2_necessaire, masse_dechets




def conso_elec_gazeification(masse_CO2 : float, masse_H2 : float, masse_seche_biomasse : float, gaz_params : dict) -> float:
    """
    Calcul de la consommation électrique de gazéification : 
        - consommation liée aux entrants de la gazéification : biomasse et H2.
        - consommation liée au chauffage et à la désorption des filtres amines pour le captage du CO2.

    Arguments
    ----------
        masse_CO2 :             Masse de CO2 en sortie de la gazéification, captée pour EM-Lacq (tonnes)
        masse_H2 :              Masse de H2 utilisée par la gazéification (tonnes)
        masse_seche_biomasse :  Masse de biomasse sèche utilisée par la gazéification (tonnes)
        gaz_params :            Paramètres de la gazéification
    
    Returns
    -------
        energie_gazeification : consommation électrique totale de la gazéification sans 
        prendre en compte la compression du syngaz (cf étape 7 compression) (kWh)
    """
    energie_entrants_H2 = masse_H2 * comp.carac_pysico_chimiques["H2"]["PCI"] / 3600 * 10e6                   # en kWh
    energie_entrants_bois = masse_seche_biomasse * biomasse.param_biomasse['PCI_biomasse']                    # en kWh
    energie_entrants = (energie_entrants_H2 + energie_entrants_bois)*gaz_params['fonctionnement_interne']/100 # en kWh
    energie_desorption_filtres_amines = masse_CO2 * gaz_params["filtres_amine"] / 3600 * 10e6                 # en kWh
    energie_gazeification = energie_desorption_filtres_amines + energie_entrants                              # en kWh
    
    return energie_gazeification

################################################################
#Inversion du code pour retrouver la biomasse nécessaire à une quantité de syngas donnée
################################################################

def Inv_gazeificationV1(masseCO_sortie, gaz_params, caract_syngas):
    """Fonction d'inversion de la gazéification pour retrouver la biomasse nécessaire à une quantité de syngas donnée.
    
    Arguments :
    -----------
        masseCO_sortie :  Masse de CO en sortie de gazeification (tonnes)
        gaz_params :      Paramètres de la gazéification
        caract_syngas :   Caractéristiques du syngas produit (fractions massiques, nombres d'atomes, masses molaires)
        
    Returns :
    -----------
        biomasse_entree :     Masse de biomasse sèche en entrée (tonnes)
        masseH2_necessaire :  Masse de H2 nécessaire à injecter dans la gazéification (tonnes)
        masseO2_necessaire :  Masse d'O2 nécessaire à injecter dans la gazéification (tonnes)
        masseCO2_sortie :     Masse de CO2 en sortie de gazeification (tonnes)
    """

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

    # Calcul des masses volumiques pondérées par les fractions volumiques g/m3
    masses_vol_ponderees = {
        gas: conversionMasseMolaire(caract_syngas[gas]["M"], gaz_params) *
             caract_syngas_normalized[gas]["fraction"]
        for gas in caract_syngas
    }    

    # Calcul des pourcentages massiques à partir des masses volumiques pondérées
    somme_masses_vol = sum(masses_vol_ponderees.values())
    pourcentages_massiques = {
        gas: masses_vol_ponderees[gas] / somme_masses_vol
        for gas in caract_syngas
    }

    # ------------------------------
    # Récupération CO2
    # ------------------------------
    masseCO2_sortie = masseCO_sortie*pourcentages_massiques["CO2"]  * caract_syngas["CO2"]["M"] / (pourcentages_massiques["CO"]  * caract_syngas["CO"]["M"])

    # ------------------------------
    # Calcul des masses totales de chaque composé
    # ------------------------------
    masses_totales_composes = {"CO": masseCO_sortie, "CO2": masseCO2_sortie}

    for gas in caract_syngas:
        if gas not in masses_totales_composes:
            masses_totales_composes[gas] = masseCO_sortie*pourcentages_massiques[gas]  * caract_syngas[gas]["M"] / (pourcentages_massiques["CO"]  * caract_syngas["CO"]["M"])
            #La masse des autres composés est estimée proportionnellement à leur pourcentage massique par rapport à la masse de CO 
    
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
    biomasse_entree = masse_C_total / gaz_params["taux_carbone"]


    # ------------------------------
    # Calcul O2 nécessaire     
    # ------------------------------

    masseO_dans_syngaz = 0
    for compo in carbon_gases:
        nO = caract_syngas[compo]["nO"]
        if nO > 0:
            masseO_dans_syngaz += masses_totales_composes[compo] * (nO * gaz_params["masseMolaireO"] / caract_syngas[compo]["M"])

    masseO_biomasse = biomasse_entree * gaz_params["fractionO"] # O contenu dans la biomasse sèche

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

    print("\n========== RÉSULTATS GAZÉIFICATION INVERSE V1 ==========")
    print(f"CO FT                         : {masseCO_sortie} tonnes/an")
    print("------------------------------------------------")
    print(f"CO₂ émis                      : {masseCO2_sortie} tonnes/an")
    print(f"Biomasse sèche en entrée      : {biomasse_entree} tonnes/an")
    print(f"O₂ nécessaire                 : {masseO2_necessaire} tonnes/an")
    print(f"H₂ dans syngaz                : {masseH2_syngaz} tonnes/an")
    print(f"H₂ à ajouter                  : {masseH2_necessaire} tonnes/an")
    print(f"Masse estimée déchets         : {masse_dechets} tonnes/an")
    print("------------------------------------------------")

    return biomasse_entree, masseH2_necessaire, masseO2_necessaire, masseCO2_sortie

