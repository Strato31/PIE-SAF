"""
Paramètres et hypothèses sourcées pour la gazeification, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées : Calcul de la quantité de syngas en sortie 
###############################################################


gaz_params = {

    #Le taux carbone du bois sec est autour de 50% de C et est assez indépendant de l'essence de l'arbre (source : https://www-woodworks-org.translate.goog/resources/calculating-the-carbon-stored-in-wood-products/?_x_tr_sl=en&_x_tr_tl=fr&_x_tr_hl=fr&_x_tr_pto=rq)
    "taux_carbone": 0.50,       #Taux carbone du bois sec (% de masse)

    #Autre moyen de calculer taux carbone :     PCI_sec = PCI_humide / (1 - Humidité) => taux_carbone = PCI_sec / 34.5

    #Source "t'inquiète"
    "fractionH2" : 0.75, # Fraction de H2 injectée dans le syngaz 

    #Source : galtié 
    "fractionCO2perdue_syngas" : ..., # Fraction de CO2 perdue dans le syngas

    #Masses moalires utiles pour la partie gazeification
    "masseMolaireC" : 12 , 
    "masseMolaire0" : 16 ,
    "masseMolaireH" : 1 ,

    # Conditions standards pour le syngas
    "P" : 101325 , # Pression du syngas en Pa = 1atm
    "T" : 273, # Température du syngas en K (0°C)??

    "R" : 8.314  # constante des gaz parfait J/mol·K 

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
    "C20":  {"fraction": 0.001,  "nC": 20, "nH": 0, "nO": 0,  "M": 54.0},
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
    print(volume_molaire)
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

def gazeificationV2(biomasseEntree,masseEntree_O2, masseEntree_H2, gaz_params, caract_syngas):

    """
    Bilan des masses du procédé de gazéification
    
    :param biomasseEntree_kg: Valeur de sortie par l'étape Biomasse
    :param masseEntree_O2: Valeur de sortie par l'étape Electrolyse
    :param masseEntree_H2: Valeur de sortie par l'étape Electrolyse
    :param gaz_params: Paramètres de la gazéification
    :param pourcentages_syngas: Pourcentages en masse des différents composants du syngas (ESTIMÉS !)


    Réaction non équilibrée de la gazéification :
    C + O2 + H2  → CO + H2 + CO2 + (CH4 + C2H2 + C3H6 + C2O) 
    NB: les déchets entre parenthèses sont des pertes carbones à prendre compiler à al fin du processus total)

    """

    #Pramètres d'entrée
    masse_C = biomasseEntree * gaz_params["taux_carbone"]
    masseEntree_H2reelle = masseEntree_H2*gaz_params["fractionH2"]

    masse_tot_entree = masse_C + masseEntree_O2 + masseEntree_H2reelle

    #Gazéification

    # Normalisation des fractions 
    total_fraction = sum(gas["fraction"] for gas in caract_syngas.values())

    caract_syngas_normalized = {
        gas_name: {
            **gas_data,
            "fraction": gas_data["fraction"] / total_fraction
        }
        for gas_name, gas_data in caract_syngas.items()
    }


    masses_vol_ponderees = [conversionMasseMolaire(caract_syngas[k]["M"], gaz_params) *caract_syngas_normalized[k]["fraction"] for k in caract_syngas]
    
    pourcentages_massiques = [0 for _ in range(len(masses_vol_ponderees))]
    for h in range(len(masses_vol_ponderees)):
        pourcentages_massiques [h]= masses_vol_ponderees[h]/sum(masses_vol_ponderees)

        
    # Séparer gaz carbonés et H2 
    carbon_gases = [k for k, v in caract_syngas_normalized.items() if v["nC"] > 0]



    # Calcul des moles des gaz carbonés 
    for k in carbon_gases:
        caract_syngas[k]["moles"] = (masse_C * caract_syngas[k]["fraction"] * caract_syngas[k]["nC"]) / (factor * gaz_params["masseMolaireC"])

    # Masse des gaz carbonés
    for k in carbon_gases:
        caract_syngas[k]["mass"] = caract_syngas[k]["moles"] * caract_syngas[k]["M"]

    # Calcul de H2 
    x_total_carbon = sum(caract_syngas[k]["fraction"] for k in carbon_gases)
    n_total = sum(caract_syngas[k]["moles"] for k in carbon_gases) / x_total_carbon

    caract_syngas["H2"]["moles"] = n_total * caract_syngas["H2"]["fraction"]
    caract_syngas["H2"]["mass"] = caract_syngas["H2"]["moles"] * caract_syngas["H2"]["M"]

    print(f"{'Gaz':<6} {'Fraction':<10} {'Moles':<12} {'Masse (t/an)':<12}")
    for k, v in caract_syngas.items():
        print(f"{k:<6} {v['fraction']:<10.4f} {v['moles']:<12.4f} {v['mass']:<12.2f}")
    
    return caract_syngas

gazeificationV2(biomasseEntree=300000, masseEntree_O2=180000, masseEntree_H2=32130,
                     gaz_params=gaz_params, caract_syngas=caract_syngas)


def gazeificationV3(biomasseEntree, masseEntree_O2, masseEntree_H2, gaz_params, caract_syngas):

    """
    Bilan complet de masse et de moles pour la gazeification avec bilans atomiques C, H, O
    """

    print("\n========== GAZÉIFICATION BtJ – BILAN COMPLET ==========")

    # ----------- CONSTANTES ------------ #
    M_C = gaz_params["masseMolaireC"]
    M_O = gaz_params["masseMolaire0"]
    M_H = gaz_params["masseMolaireH"]

    # ----------- ENTRÉES ------------ #
    masse_C = biomasseEntree * gaz_params["taux_carbone"]
    masse_H2 = masseEntree_H2 * gaz_params["fractionH2"]
    masse_O2 = masseEntree_O2

    nC_entree = masse_C / M_C
    nH2_entree = masse_H2 / (2 * M_H)
    nO2_entree = masse_O2 / (2 * M_O)

    print(f"Masse carbone biomasse : {masse_C:.2f} t/an")
    print(f"Masse H2 injectée      : {masse_H2:.2f} t/an")
    print(f"Masse O2 injectée      : {masse_O2:.2f} t/an")

    # ------------ NORMALISATION DES FRACTIONS ------------ #
    #total_fraction = sum(g["fraction"] for g in caract_syngas.values())
    #for g in caract_syngas.values():
    #    g["fraction"] /= total_fraction

    # ------------ GAZ CARBONÉS ------------ #
    carbon_gases = [k for k, v in caract_syngas.items() if v["nC"] > 0]

    # ------------ DISTRIBUTION DU CARBONE ------------ #
    total_C_units = sum(caract_syngas[k]["fraction"] * caract_syngas[k]["nC"] for k in carbon_gases)

    for k in carbon_gases:
        frac = caract_syngas[k]["fraction"]
        nC = caract_syngas[k]["nC"]

        # moles gaz imposés par bilan C
        caract_syngas[k]["moles"] = nC_entree * frac * nC / total_C_units
        caract_syngas[k]["mass"] = caract_syngas[k]["moles"] * caract_syngas[k]["M"]

    # ------------ CALCUL DU H2 SELON LES FRACTIONS ------------ #
    xC = sum(caract_syngas[k]["fraction"] for k in carbon_gases)
    n_total_syngas = sum(caract_syngas[k]["moles"] for k in carbon_gases) / xC

    caract_syngas["H2"]["moles"] = n_total_syngas * caract_syngas["H2"]["fraction"]
    caract_syngas["H2"]["mass"] = caract_syngas["H2"]["moles"] * caract_syngas["H2"]["M"]

    # ------------ BILANS ATOMIQUES ------------ #
    C_out = sum(v["moles"] * v["nC"] for v in caract_syngas.values() if v["nC"] > 0)
    H_out = (
        caract_syngas["H2"]["moles"] * 2
        + caract_syngas["CH4"]["moles"] * 4
        + caract_syngas["C2H2"]["moles"] * 2
        + caract_syngas["C3H6"]["moles"] * 6
    )

    O_out = (
        caract_syngas["CO"]["moles"] * 1
        + caract_syngas["CO2"]["moles"] * 2
    )

    print("\n====== BILANS ATOMIQUES ======")
    print(f"Carbone  IN = {nC_entree:.2f} mol | OUT = {C_out:.2f} mol")
    print(f"Hydrogène IN = {nH2_entree*2:.2f} mol | OUT = {H_out:.2f} mol")
    print(f"Oxygène   IN = {nO2_entree*2:.2f} mol | OUT = {O_out:.2f} mol")

    # ------------ REACTIFS LIMITANTS ------------ #

    print("\n====== RÉACTIF LIMITANT ======")

    # Besoin théorique en O et H pour former le syngaz
    O_needed = (
        caract_syngas["CO"]["moles"] * 1 +
        caract_syngas["CO2"]["moles"] * 2
    )

    H_needed = (
        caract_syngas["H2"]["moles"] * 2 +
        caract_syngas["CH4"]["moles"] * 4 +
        caract_syngas["C2H2"]["moles"] * 2 +
        caract_syngas["C3H6"]["moles"] * 6
    )

    # Disponibilités réelles
    O_available = nO2_entree * 2
    H_available = nH2_entree * 2

    ratio_O = O_available / O_needed if O_needed > 0 else 999
    ratio_H = H_available / H_needed if H_needed > 0 else 999

    print(f"O nécessaire = {O_needed:.2f} mol | O disponible = {O_available:.2f} mol")
    print(f"H nécessaire = {H_needed:.2f} mol | H disponible = {H_available:.2f} mol")

    scaling = min(1.0, ratio_O, ratio_H)

    # Application du facteur limitant
    for k in caract_syngas:
        caract_syngas[k]["moles"] *= scaling
        caract_syngas[k]["mass"] *= scaling

    if scaling < 1:
        print(f"⚠️ Syngaz limité par réactif : facteur = {scaling:.3f}")
    else:
        print("✅ Aucun réactif limitant : conditions satisfaites")


    # ------------ TABLEAU DE SORTIE ------------ #

    print("\n========= COMPOSITION SYNGAS =========")
    print(f"{'Gaz':<6} {'Frac':<8} {'Moles':<12} {'Masse (t/an)':<12}")
    for k, v in caract_syngas.items():
        print(f"{k:<6} {v['fraction']:<8.4f} {v['moles']:<12.2f} {v['mass']:<12.2f}")

    return caract_syngas


#gazeificationV3(biomasseEntree=300000, masseEntree_O2=180000, masseEntree_H2=32130,gaz_params=gaz_params, caract_syngas=caract_syngas)

def bilan_chaleur_gazeification():

    chaleur = 0

    return chaleur


def conso_elec_gazeification():

    energie_gazeification = 0

    return energie_gazeification



def emissions_gazeification(param_gazeification):
    # Calcul des émissions totales pour le processus de gazeification
    émissions = 0
    return émissions

<<<<<<< HEAD


###############################################################
# Stockage des paramètres avec les hypothèses sourcées : Calcul conso énergétique du processus
###############################################################
cara_pysico_chimique_methane = { #Source ?
    T : 298.15,  # Température (K)
    P : 1,        # Pression (bar)
    PCI : 803.3,   # Pouvoir Calorifique Inférieur (kJ/mol)
    PCS : 890.8,   # Pouvoir Calorifique Supérieur (kJ/mol)
    # PCI : 50.07,   # Pouvoir Calorifique Inférieur (MJ/kg)
    # PCS : 55.53,   # Pouvoir Calorifique Supérieur (MJ/kg)
    # densite : , # Densité (kg/m3) à 298.15 K et 1 bar source ?
    densite : 0.6709, # Densité (kg/m3) à 288.15 K et 1 bar 
}

##############################################################
# Fonctions de calcul des émissions : Calcul conso énergétique du processus
##############################################################
=======
>>>>>>> 11174a8 (compression)
