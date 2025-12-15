"""
Paramètres et hypothèses sourcées pour la biomasse, puis fonctions de calcul des émissions.

Source de la biomasse (ligneuse sèche, herbacee, résiduelle, etc.)
"""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################
# --> à réorganiser/scinder pour rendre plus lisible ?
param_biomasse = {


    # TODO l'utiliser pour vérifier que les types de biomasse renseignés sont corrects
    "sources_biomasse": ["ligneuse_seche", "bois_vert", "agricole", "herbacee", "résiduelle" ,...],

    # source : https://www.bois-de-chauffage-ecologique.fr/actualite/post/32-le-pouvoir-calorifique-du-bois-de-chauffage
    "PCI_biomasse": 5050, # (kWh/t) PCI du bois de chauffage

    # capacité calorifique du cyprès selon https://www.thermoconcept-sarl.com/base-de-donnees-chaleur-specifique-ou-capacite-thermique/
    "capacite_calorifique_biomasse": 2.301,  # Capacité calorifique spécifique utilisée pour la biomasse (kJ/kg.K)

    # conso broyage/convoyage : on utilise méthode ademe méthaniseurs : 2% de l'énergie contenue dans la biomasse (PCI à 0% humidité)
    "consommation_broyage": 0.02,  # en part de l'énergie contenue dans la biomasse

    ## TRANSPORT ##
    # Ensemble articulé 40 tonnes PTRA – Grand volume (source : https://www.webfleet.com/fr_fr/webfleet/blog/emission-co2-camion-km/) 
    "emissions_transport_biomasse": 0.096,  # (kgCO2e/t.km) Émissions liées au transport de la biomasse par camion

    # Hypothèse distance moyenne de transport
    "distance_transport_biomasse": 500,  # (km) Distance moyenne de transport de la biomasse (choix arbitraire)
}


##############################################################
# Fonctions de calcul des émissions                          #
##############################################################

"""
Hypothèses pouvant être détaillées :
- capacité calorifique propre à chaque type de biomasse / chaque espèce d'arbre éventuellement
- emissions différentes selon type de biomasse (ligneuse, agricole, résiduelle, etc.)
- éventuellement : ajouter procédés e-safs et bio-safs

"""

def masse_seche_sortie(biomasse):
    """Calcule la masse totale de biomasse sèche après torréfaction.
    !! Pour l'instant, ne prend pas en compte type de biomasse."""
    biomasse_seche = 0
    for biom in biomasse:
        masse = biom['masse']
        humidite = biom['humidité']
        biomasse_seche += masse * (1 - humidite)
    return biomasse_seche



def emissions_culture_biomasse(param_biomasse, biomasse):
    """TEMPORAIRE
    Calcule émissions dues à la culture de la biomasse.
    Hypothèse : émissions fixes par MJ de biomasse entrante.

    """
    # Calcul des émissions dues au carbone relâché lors de la coupe/récolte, net à horizon 20 ans
    # masse/4 la masse de carbone (C) dans le bois (en tonnes)
    # * (44/12) le stock de CO2 émis à l'abbattage
    # * (1 + 0.5) qui prend en compte déstockage sol
    # * (1 - 0.25*(20-1)/(2*20)) moyenne pondérée sur l'horizon, hypothèse taux de substitution de 25% sur 20 ans (mélange de bois d'abattage feuillus et résineux)
    masse_bois_vert = sum(biom['masse'] for biom in biomasse if biom['type'] == "bois_vert")  # en tonnes
    emissions_recolte = masse_bois_vert / 4 * (44/12) * (1 + 0.5) * (1 - 0.25*(20-1)/(2*20))  # en tCO2e


    # à terme, y ajouter émissions pour d'autres types de biomasse (agricole, résiduelle, etc.)
    emissions_totales_culture = emissions_recolte 

    return emissions_totales_culture


def emissions_transport_biomasse(param_biomasse, biomasse):
    """Calcule émissions dues au transport de la biomasse.
    Hypothèse : émissions fixes par tonne de biomasse entrante.

    """
    emissions_transport = param_biomasse["emissions_transport_biomasse"]/1000  # tCO2e/t.km
    distance_transport = param_biomasse["distance_transport_biomasse"]  # km

    # Calcul des émissions totales liées au transport de la biomasse (en tCO2e)
    emissions_totales_transport = emissions_transport * distance_transport * sum(biom['masse'] for biom in biomasse)

    return emissions_totales_transport





def traitement_biomasse(param_biomasse, biomasse_entree, BROYAGE=True):
    """
    ARGUMENTS

    Prend en entrée une liste de types, masses (t) et humidité de biomasse, par exemple :
    
    biomasse_entree = [
        {"type" : "ligneuse", "masse": 1.0, "humidité": 0.10},  # 1 tonne de biomasse ligneuse à 10% d'humidité
        {"type" : "agricole", "masse": 2.0, "humidité": 0.20},  # 2 tonnes de biomasse agricole à 20% d'humidité
    ]

    SORTIE

    Retourne l'énergie totale consommée (kWh), la quantité de chaleur consommée (MJ), et la masse totale de biomasse sèche
    """

    capacite_calorifique = param_biomasse["capacite_calorifique_biomasse"]  # kJ/kg.K


    # 1. calcul énergie thermique nécessaire pour la torréfaction
    for entree in biomasse_entree:
        masse = entree["masse"]
        humidité = entree["humidité"]

        # Hypothèse : on chauffe à 200°C depuis 25°C
        energie_chauffage = masse * capacite_calorifique * (200 - 25) / 1000  # MJ (capacité calorifique spécifique de la biomasse sèche ~1.5 kJ/kg.K)

        # Energie nécessaire pour vaporiser l'eau de la biomasse
        energie_vaporisation = masse * humidité * 2.26476  # en MJ (on utilise la chaleur latente de vaporisation de l'eau)

        # énergie totale nécessaire au procédé de torréfaction
        energie_torrefaction = energie_vaporisation + energie_chauffage


    # 2. Calcul consommation d'énergie pour le broyage/convoyage de la biomasse
    elec_broyage = 0
    if BROYAGE :
        pci_biomasse = param_biomasse["PCI_biomasse"]
        conso_broyage = param_biomasse["consommation_broyage"]
        elec_broyage = conso_broyage * pci_biomasse * sum(entree["masse"] for entree in biomasse_entree)  # kWh


    # 3. on renvoie l'électricité consommée (broyage, kWh), l'énergie thermique consommée (torrefaction, MJ), et la masse de biomasse sèche sortie
    return elec_broyage, energie_torrefaction, masse_seche_sortie(biomasse_entree)



# fonctions test
# test traitement biomasse
biomasse_exemple = [
    {"type" : "bois_vert", "masse": 600000, "humidité": 0.10},  # 1 tonne de biomasse ligneuse à 10% d'humidité
    #{"type" : "agricole", "masse": 200000, "humidité": 0.0},  # 2 tonnes de biomasse agricole à 20% d'humidité
]
elec, chaleur, masse_seche = traitement_biomasse(param_biomasse, biomasse_exemple)
print(f"Électricité consommée pour le broyage : {elec} kWh")
print(f"Chaleur consommée pour la torréfaction : {chaleur} MJ")
print(f"Masse de biomasse sèche sortie : {masse_seche} t")
print(f"Émissions liées au transport de la biomasse : {emissions_transport_biomasse(param_biomasse, biomasse_exemple)} tCO2e")
print(f"Émissions liées à la culture de la biomasse : {emissions_culture_biomasse(param_biomasse, biomasse_exemple)} tCO2e")