"""
Paramètres et hypothèses sourcées pour la biomasse, puis fonctions de calcul des émissions.

Facteurs importants :
- Source de la biomasse (ligneuse sèche, herbacee, résiduelle, etc.)
- PCI de la biomasse (MWh/t)
- densité
- humidité
- effets changement climatique (à différentes échelles temporelles)
- émissions liées à la culture, au transport, à la transformation


"""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_biomasse = {

    # Temporaire, à remplacer par des fonctions de calcul
    "émissions_culture": 50,     # Émissions liées à la culture (gCO2e/MJ)
    "émissions_transport": 10,    # Émissions liées au transport (gCO2e/MJ)
    "émissions_transformation": 30,  # Émissions liées à la transformation (gCO2e/MJ)


    "source_biomasse": "ligneuse_sèche",  # Source de la biomasse parmi ['ligneuse_sèche', "biomasse_vive" , "bois_secondaire", ...]

    # source : fonction à sourcer PCI = f(Humidité)
    "PCI_biomasse": 5.05, # PCI de la biomasse (MWh/t)

    "rendement_biomasse": 0.85,  # Rendement de conversion

    "procede_transformation": "gazeification",  # Procédé de transformation utilisé parmi ['pyrolyse', 'gazeification', ...]

    # capacité calorifique du cyprès selon https://www.thermoconcept-sarl.com/base-de-donnees-chaleur-specifique-ou-capacite-thermique/
    "capacite_calorifique_biomasse": 2.301,  # Capacité calorifique spécifique de la biomasse (kJ/kg.K)
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

"""Etapes de calcul des émissions liées au carbone
1. Bio-safs : cas carbone venant de la biomasse (le plus complexe) : entrée biomasse, sortie biomasse sèche
    a. Émissions liées à la culture de la biomasse
    b. Émissions liées au transport de la biomasse
    c. Émissions liées à la torréfaction de la biomasse
2. e-safs : carbone venant de ccs ou de l'air (à faire plus tard)


Hypothèses pouvant être détaillées :
- capacité calorifique propre à chaque type de biomasse / chaque espèce d'arbre éventuellement

"""



def energie_traitement_biomasse(param_biomasse, BROYAGE=True):
    """
    ARGUMENTS

    Prend en entrée une liste de types et masses de biomasse avec leur humidité associée

    SORTIE

    Retourne l'énergie totale consommée, et la quantité de chaleur récupérable (MJ)
    """
    capacite_calorifique = param_biomasse["capacite_calorifique_biomasse"]  # kJ/kg.K

    entrees_test = [
        {"type" : "ligneuse_sèche", "masse": 1.0, "humidité": 0.10},  # 1 tonne de biomasse ligneuse à 10% d'humidité
        {"type" : "agricole", "masse": 2.0, "humidité": 0.20},  # 2 tonnes de biomasse agricole à 20% d'humidité
    ]
    emissions_torrefaction = 0

    # calcul énergie nécessaire pour la torréfaction (hypothèses à vérifier/sourcer)
    for entree in entrees_test:
        masse = entree["masse"]
        humidité = entree["humidité"]

        # Hypothèse : énergie nécessaire pour évaporer l'eau + énergie pour chauffer la biomasse sèche
        energie_evaporation = masse * humidité * 2.26476  # MJ (chaleur latente de vaporisation de l'eau)

        # Hypothèse : on chauffe à 200°C depuis 25°C
        energie_chauffage = masse * capacite_calorifique * (200 - 25) / 1000  # MJ (capacité calorifique spécifique de la biomasse sèche ~1.5 kJ/kg.K)


        energie_chaleur = energie_evaporation + energie_chauffage


    energie_broyage = 0
    if BROYAGE :
        # Hypothèse : énergie de broyage TODO, quelle hypothèses faire ?
        energie_broyage = 0.1 * sum(entree["masse"] for entree in entrees_test)  # MJ

    return energie_broyage+energie_chaleur, energie_chaleur



def total_emissions_biomasse(param_biomasse):
    # Calcul des émissions totales pour la biomasse (A FAIRE)
    émissions += param_biomasse["émissions_culture"]
    émissions += param_biomasse["émissions_transport"]

    consommation = energie_traitement_biomasse(...)
    return émissions
