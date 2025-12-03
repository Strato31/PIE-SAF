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

    # capacité calorifique du cyprès selon https://www.thermoconcept-sarl.com/base-de-donnees-chaleur-specifique-ou-capacite-thermique/
    "capacite_calorifique_biomasse": 2.301,  # Capacité calorifique spécifique utilisée pour la biomasse (kJ/kg.K)

    # référence broyeur trouvée en ligne : https://www.biopelletmachine.com/french/produit/machine-a-fabriquer-de-la-sciure-de-bois/broyeur-de-bois-electrique-html
    "consommation_broyage": 0.162,  # Consommation énergétique pour le broyage (MJ/kg) 45kWh/t --> 0.162 MJ/kg
}


##############################################################
# Fonctions de calcul des émissions
##############################################################

"""Etapes de calcul des émissions liées au carbone
1. Bio-safs : cas carbone venant de la biomasse (le plus complexe) : entrée biomasse, sortie biomasse sèche
    a. Émissions liées à la culture de la biomasse
    b. Émissions liées au transport de la biomasse
    c. Émissions liées à la torréfaction de la biomasse
2. e-safs : carbone venant de ccs ou dac (à faire plus tard)


Hypothèses pouvant être détaillées :
- capacité calorifique propre à chaque type de biomasse / chaque espèce d'arbre éventuellement

"""

def masse_seche_sortie(biomasse):
    """Calcul de la masse sèche sortie de la biomasse après torréfaction"""
    for biom in biomasse:
        masse = biom['masse']
        humidite = biom['humidité']
        biomasse_seche += masse * (1 - humidite)
    return biomasse_seche



def energie_traitement_biomasse(param_biomasse, biomasse_entree, BROYAGE=True):
    """
    ARGUMENTS

    Prend en entrée une liste de types, masses (t) et humidité de biomasse avec leur humidité associée

    SORTIE

    Retourne l'énergie totale consommée (MJ), et la quantité de chaleur récupérable (MJ)
    """

    capacite_calorifique = param_biomasse["capacite_calorifique_biomasse"]  # kJ/kg.K

    # exemple = [
    #     {"type" : "ligneuse_sèche", "masse": 1.0, "humidité": 0.10},  # 1 tonne de biomasse ligneuse à 10% d'humidité
    #     {"type" : "agricole", "masse": 2.0, "humidité": 0.20},  # 2 tonnes de biomasse agricole à 20% d'humidité
    # ]

    # calcul énergie thermique nécessaire pour la torréfaction
    for entree in biomasse_entree:
        masse = entree["masse"]
        humidité = entree["humidité"]

        # Hypothèse : on chauffe à 200°C depuis 25°C
        energie_chauffage = masse * capacite_calorifique * (200 - 25) / 1000  # MJ (capacité calorifique spécifique de la biomasse sèche ~1.5 kJ/kg.K)

        # Energie nécessaire pour vaporiser l'eau de la biomasse
        energie_vaporisation = masse * humidité * 2.26476  # en MJ (on utilise la chaleur latente de vaporisation de l'eau)

        # énergie totale nécessaire au procédé de torréfaction
        energie_torrefaction = energie_vaporisation + energie_chauffage


    # Calcul consommation d'énergie pour le broyage de la biomasse
    energie_broyage = 0
    if BROYAGE :
        conso_broyage = param_biomasse["consommation_broyage"]
        energie_broyage = conso_broyage * sum(entree["masse"] for entree in biomasse_entree)  # MJ

    # on renvoie l'électricité consommée (broyage), l'énergie thermique consommée (torrefaction), et la masse de biomasse sèche sortie
    return energie_broyage, energie_torrefaction, masse_seche_sortie(biomasse_entree)



