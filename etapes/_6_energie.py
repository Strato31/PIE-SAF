"""
PARTIE : Energie

Paramètres et hypothèses sourcées pour le calcul des émissions liées à la consommation énergétique et thermique,
puis les fonctions de calcul de ces émissions.

Contient : 
- paramètres : 
    - facteur_emission : facteur d'émission de chaque filière énergétique en gCO2eq/kWh
    - param_mix_2050 : mix énergétique prévisionnel en 2050 
    - facteur_emission_2023 : mix énergétique actuel en 2023
- fonctions de calcul des émissions :
    - emissions_energetique_processus : calcule les émissions de CO2 (en gCO2eq) liées à une consommation énergétique donnée (en kWh),
      en utilisant un mix énergétique prévisionnel pour 2050 et le mix actuel pour 2023.
    - emissions_energie_totale : agrège les émissions de CO2 (en gCO2eq) liées à une liste de consommations énergétiques (en kWh),
      en distinguant les émissions pour 2050 et pour 2023.
    - verif_hypothèse : vérifie l'hypothèse selon laquelle la consommation thermique totale des processus est inférieure ou égale à la chaleur récupérable.

Hypothèses sur un mix énergétique pour 2050 :
    le plus pertinent est de calculer les émissions sur la base du mix électrique cible français en 2050, hypothèse nucléaire "moyenne" (14 EPR2)
    la production des pays voisins sera entièrement renouvelable. Elle aura une empreinte légèrement plus élevée car le nucléaire a l'empreinte la plus basse.
    mais on va négliger cet effet. En plus, l'empreinte carbone du solaire aura probablement baissé à cette échéance (amélioration des rendements), ce qui renforce cette simplification
    les émissions seront sous-estimées à la mise en service, mais devraient être représentatives dès 2035
    source : base ADEME V23.2 pour nucléaire, éolien, photovoltaïque et hydraulique. Site "Electricity Maps" pour biomasse.

"""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées        #
###############################################################
"""
Valeurs 2050 calculées à partir :
- Du mix prévisionnel production suite aux annonces du Président Macron en 2023 sur la construction de 14 EPR2 
(hypothèse moyenne) et du développement des parcs photovoltaïque et éolien maritime et terrestre. 
- Hypothèse réacteurs SMR non pris en compte. Calendrier de fermeture des tranches existantes sur base 
durée de vie de 60 ans. Centrales fossiles fermées. 
- Facteurs d’émission par type de production : base ADEME V23.2 pour nucléaire, éolien, photovoltaïque 
et hydraulique, site "Electricity Maps" pour biomasse
- Hypothèse que tous les pays européens auront une électricité décarbonée au même niveau que la 
France (le solaire et surtout la biomasse sont moins décarbonées. Donc pas d’effet des importations 
éventuelles. Approximation jugée acceptable pour nos besoins
"""

# Facteur d'émission de chaque filière énergétique en gCO2eq/kWh
facteur_emission = {
    "nucleaire" : 5,   # moyenne ADEME / EDF
    "eolien" : 15,
    "solaire" : 32,    # ADEME "Europe"
    "hydraulique" : 6, 
    "biomasse" : 230,  # Electricity Maps
}

# Mix énergétique prévisionnel en 2050 (part de chaque filière dans la production électrique)
param_mix_2050 = {
    "nucleaire": 0.38,      # Part du nucléaire dans le mix énergétique 
    "eolien": 0.304,        # Part de l'éolien dans le mix énergétique 
    "solaire" : 0.198,      # Part du solaire dans le mix énergétique 
    "hydraulique" : 0.082,  # Part de l'hydraulique dans le mix énergétique 
    "biomasse" : 0.03,      # Part du la biomasse dans le mix énergétique 
}

# La différence entre les deux vient de la prise en compte des importations dans le mix de consommation
facteur_emission_2023 = {
    "consommation" : 34.3, # gCO2eq/kWh pour le mix électrique français en 2023 selon RTE
    "production" : 32.4 # gCO2eq/kWh pour le mix électrique français en 2023 selon RTE
}

'''Valeur 2023 tirée du rapport « bilan électrique RTE 2023 ». Valeur un peu élevée intégrant les 
importations rendues nécessaires du fait de la faible disponibilité du parc nucléaire cette année-là'''

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_energetique_processus(conso_energie):
    """
    Calcule les émissions de CO2 (en gCO2eq) liées à une consommation énergétique donnée (en kWh),
    en utilisant un mix énergétique prévisionnel pour 2050 et le mix actuel pour 2023.

    Arguments
    ----------
        conso_energie : Consommation énergétique en kWh
    
    Returns
    -------
        emissions_2050 : Émissions de CO2 en 2050 en gCO2eq
        emissions_2023 : Émissions de CO2 en 2023 en gCO2eq
    """
    # Calcul du facteur d'émission mixte pour 2050
    emission_mix = 0 # initialisation
    for energie in facteur_emission :
        emission_mix += param_mix_2050[energie] * facteur_emission[energie] # on pondère chaque facteur d'émission par la part de cette énergie dans le mix

    # Calcul des émissions totales pour le processus de gazeification
    emissions_2050 = conso_energie * emission_mix # calcul des émissions pour 2050
    emissions_2023 = conso_energie * facteur_emission_2023['consommation'] # choix d'utiliser le mix de consommation pour 2023
    
    return emissions_2050, emissions_2023


def emissions_energie_totale(consos_energies):
    """
    Agrège les émissions de CO2 (en gCO2eq) liées à une liste de consommations énergétiques (en kWh),
    en distinguant les émissions pour 2050 et pour 2023.

    Arguments
    ----------
        consos_energies : Liste de consommations énergétiques en kWh
    
    Returns
    -------
        emissions_2050 : Liste des émissions de CO2 en 2050 en gCO2eq pour chaque consommation, et la somme totale en dernier élément
        emissions_2023 : Liste des émissions de CO2 en 2023 en gCO2eq pour chaque consommation, et la somme totale en dernier élément
    """
    # Initialisation des totaux et des listes d'émissions par processus
    emissions_totales_2050 = 0
    emissions_totales_2023 = 0
    emissions_2050 = []
    emissions_2023 = []

    # On parcourt chaque consommation énergétique pour calculer les émissions associées
    for conso in consos_energies :
        emissions_processus_2050, emissions_processus_2023 = emissions_energetique_processus (conso) # calcul des émissions pour cette consommation
        emissions_2050.append(emissions_processus_2050) # ajout à la liste d'émissions 2050
        emissions_2023.append(emissions_processus_2023) # ajout à la liste d'émissions 2023
        emissions_totales_2050 += emissions_processus_2050 # ajout au total 2050
        emissions_totales_2023 += emissions_processus_2023 # ajout au total 2023
    
    emissions_2050.append(emissions_totales_2050) # ajout du total en dernier élément de la liste 2050
    emissions_2023.append(emissions_totales_2023) # ajout du total en dernier élément de la liste 2023

    return emissions_2050, emissions_2023

'''
Hypothèse : on considère que la chaleur résiduelle générée par le procédé Fischer-Tropsch est réinjectée 
dans la phase de torréfaction et est suffisante pour l'assurer.
Source de cette chaleur : injection d'eau dans le réacteur Fischer-Tropsch pour refroidir le catalyseur et le 
conserver dans la bonne plage de température, d’où génération de vapeur d'eau (680 kt/an) dont la chaleur va 
être utilisée pour apporter des calories aux phases de torréfaction et de création de syngaz.

En pratique, on vérifie que la consommation thermique totale des processus est inférieure ou égale à la chaleur récupérable,
ce qui permet de valider cette hypothèse et d'éviter de calculer des émissions liées à une consommation thermique supplémentaire.
'''
def verif_hypothèse(consos_thermiques):
    """
    Vérifie l'hypothèse selon laquelle la consommation thermique totale des processus est inférieure ou égale à la chaleur récupérable.
    Pas utilisé car production de chaleur non encore modélisée. 
    Arguments
    ----------
        consos_thermiques : Liste de consommations thermiques en kWh (>=0 pour consommation, <0 pour production)
    
    Returns
    -------
        booléen : True si l'hypothèse est vérifiée (consommation totale <= 0), False sinon
    """
    # inititalisation de la consommation thermique totale
    conso_therm_totale = 0

    for conso_therm in consos_thermiques : # on parcourt chaque consommation thermique
        conso_therm_totale += conso_therm # on additionne les consommations thermiques
    
    # On vérifie qu'au total, la consommation thermique totale est inférieure ou égale à 0
    if conso_therm_totale <= 0:
        return True
    else:
        return False