"""
PARTIE : Biomasse

Contient : 
 - param_biomasse : les paramètres liés à la biomasse
 - Les fonctions de calcul des émissions et consommations liées à la biomasse :
    - masse_seche_sortie : calcule la masse de biomasse sèche selon taux d'humidité initial
    - masse_humide_sortie : calcule les masses équivalentes de biomasses humides pour obtenir une masse sèche donnée
    - culture_biomasse : calcule les émissions liées à la culture de la biomasse 
    - transport_biomasse : calcule les émissions liées au transport de la biomasse
    - traitement_biomasse : calcule les consommations énergétiques liées à la torréfaction
    - main_biomasse : calcule et print les émissions totales et consommations énergétiques liées à la biomasse
    

Pistes d'amélioration / évolutions futures :
- capacité calorifique propre à chaque type de biomasse voire chaque espèce d'arbre
- différencier calcul d'émissions selon le type de biomasse (bois vert, agricole, résiduelle, etc.)
- ajouter procédés e-safs et bio-safs


"""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées        #
###############################################################

param_biomasse = {

    # Pour de futures évolutions du code : pour l'instant, seul "bois_vert" est utilisé
    "sources_biomasse": ["bois_vert", "taillis", "agricole", "herbacee", "résiduelle" ,...],

    # >> Sert à l'estimation de la consommation énergétique pour le broyage/convoyage dans la partie gazeification
    # source : https://www.bois-de-chauffage-ecologique.fr/actualite/post/32-le-pouvoir-calorifique-du-bois-de-chauffage
    "PCI_biomasse": 5050, # (kWh/t) PCI du bois de chauffage
    # >> à faire dans gazeification : conso broyage/convoyage : on utilise méthode Ademe méthaniseurs : 2% de l'énergie contenue dans la biomasse (PCI à 0% humidité)
    "consommation_broyage": 0.02,  # en part de l'énergie contenue dans la biomasse seche
    
    ## TORRÉFACTION ##
    # capacité calorifique du cyprès selon https://www.thermoconcept-sarl.com/base-de-donnees-chaleur-specifique-ou-capacite-thermique/
    "capacite_calorifique_biomasse": 2.301,  # Capacité calorifique spécifique utilisée pour la biomasse (kJ/kg.K)

    
    ## TRANSPORT ##
    # Ensemble articulé 40 tonnes PTRA – Grand volume (source : https://www.webfleet.com/fr_fr/webfleet/blog/emission-co2-camion-km/) 
    "emissions_transport_biomasse": 0.096,  # (kgCO2e/t.km) facteur d'émissions liées au transport de la biomasse par camion
    # Hypothèse distance moyenne de transport
    "distance_biomasse-torrefaction": 500,  # (km) Distance moyenne de transport de la biomasse (ici, choix arbitraire)
    "distance_torrefaction-gazeification": 50,  # (km) Distance moyenne de transport de la biomasse torréfiée jusqu'au site de gazéification (ici, choix arbitraire)
}   


##############################################################
# Fonctions de calcul des émissions                          #
##############################################################



def masse_seche_sortie(biomasse):
    """Calcule la masse totale de biomasse sèche après torréfaction en fonction de l'humidité.
    
    Arguments
    ----------
        biomasse : liste de dictionnaires avec 'type', 'masse' (t) et 'humidité' (fraction) pour chaque élément de biomasse
        
    Returns
    -------
        biomasse_seche : masse totale de biomasse sèche (t)
    """

    biomasse_seche = 0 # initialisation
    for b in biomasse: # on parcourt chaque type de biomasse
        masse = b['masse']
        humidite = b['humidité']
        biomasse_seche += masse * (1 - humidite)
    
    return biomasse_seche


def masse_humide_sortie(biomasse_seche, humidites=[0.25, 0.40, 0.50, 0.60], verbose=True):
    """Calcule la quantité nécessaire de biomasses selon différents taux d'humidité pour obtenir 
    la masse sèche demandée après torréfaction.

    Arguments
    ----------
        biomasse_seche : masse de biomasse sèche à fournir (t)
        humidites : liste des taux d'humidité (fractions) des biomasses simulées, par défaut [0.25, 0.40, 0.50, 0.60]
        verbose : booléen pour print ou non les résultats, par défaut True
    
    Returns
    -------
        masse_humide : la masse humide nécessaire pour un taux d'humidité de 25% (t)
    
    """

    masse_eq_bois_vert = [] #initialisation
    for h in humidites: #on parcourt humidites
        masse_eq_bois_vert.append(biomasse_seche / (1 - h))

    if verbose: # si verbose, on print les résultats
        print("Pour obtenir", biomasse_seche, "t de biomasse sèche, il faut :")
        for i, h in enumerate(humidites):
            print(f" - {masse_eq_bois_vert[i]:.0f} t de biomasse de type bois vert à {h*100:.0f}% d'humidité")
    masse_humide = biomasse_seche/(1-0.25)
    return masse_humide # on renvoie la masse humide pour un taux d'humidité de 25% (hypothèse par défaut)


def culture_biomasse(param_biomasse, biomasse):
    """
    Calcule les émissions dues à la culture de la biomasse.
    Pour l'instant, on ne calcule que les émissions liées à la coupe/récolte du bois vert.
    
    Hypothèse : émissions fixes par MJ de biomasse entrante.

    Arguments
    ----------
        param_biomasse : dictionnaire des paramètres liés à la biomasse
        biomasse : liste de dictionnaires avec 'type', 'masse' (t) et 'humidité' (fraction)
    
    Returns
    -------
        emissions_totales_culture : émissions totales liées à la culture de la biomasse (tCO2e)

    """
    # Calcul des émissions dues au carbone relâché lors de la coupe/récolte, net à horizon 20 ans
    # masse/4 la masse de carbone (C) dans le bois (en tonnes)
    # * (44/12) le stock de CO2 émis à l'abbattage
    # * (1 + 0.5) qui prend en compte déstockage sol
    # * (1 - 0.25*(20-1)/(2*20)) moyenne pondérée sur l'horizon, hypothèse taux de substitution de 25% sur 20 ans (correspond à un mélange de bois d'abattage feuillus et résineux)
    masse_bois_vert = sum(biom['masse'] for biom in biomasse if biom['type'] == "bois_vert")  # en tonnes
    emissions_recolte_bois_vert = masse_bois_vert / 4 * (44/12) * (1 + 0.5) * (1 - 0.25*(20-1)/(2*20))  # en tCO2e


    # à terme, y ajouter émissions pour d'autres types de biomasse (agricole, résiduelle, etc.)
    emissions_totales_culture = emissions_recolte_bois_vert 

    return emissions_totales_culture


def transport_biomasse(param_biomasse, biomasse):
    """Calcule les émissions dues au transport de la biomasse, du lieu de culture jusqu'au site de torrefaction,
    puis de la biomasse torréfiée (sèche) jusqu'au site de gazéification.
    Hypothèse : émissions fixes par tonne de biomasse entrante. Transport camion aller-retour.
    
    Arguments
    ----------
        param_biomasse : dictionnaire des paramètres liés à la biomasse
        biomasse : liste de dictionnaires avec 'type', 'masse' (t) et 'humidité' (fraction)
    Sorties
    -------
        emissions_totales_transport : émissions totales liées au transport de la biomasse (tCO2e)
    """

    biomasse_seche = masse_seche_sortie(biomasse)  # t
    emissions_transport_biomasse = param_biomasse["emissions_transport_biomasse"]/1000  # tCO2e/t.km
    distance_biomasse_torrefaction = param_biomasse["distance_biomasse-torrefaction"]  # km
    distance_torrefaction_gazeification = param_biomasse["distance_torrefaction-gazeification"]  # km
    
    emissions_totales_transport = 0  # initialisation
    # 1. Calcul des émissions totales liées au transport de la biomasse jusqu'au lieu de torréfaction (en tCO2e)
    emissions_totales_transport += emissions_transport_biomasse * distance_biomasse_torrefaction * 2 * sum(biom['masse'] for biom in biomasse)
    # 2. On ajoute les émissions liées au transport de la biomasse torréfiée jusqu'au site de gazéification
    emissions_totales_transport += emissions_transport_biomasse * distance_torrefaction_gazeification * 2 * biomasse_seche
    
    return emissions_totales_transport


def traitement_biomasse(param_biomasse, biomasse_entree):
    """Calcule les consommations énergétiques liées au traitement de la biomasse 
    (Pour l'instant, torréfaction du bois vert)
    
    Arguments
    ----------
        param_biomasse : dictionnaire des paramètres liés à la biomasse
        biomasse_entree : liste de dictionnaires avec 'type', 'masse' (t) et 'humidité' (fraction)
    
    Returns
    -------
        energie_torrefaction : consommation d'énergie thermique pour la torréfaction (MJ)
        masse_seche_sortie : masse totale de biomasse sèche après torréfaction (t)

    """
    # on récupère la capacité calorifique dans le dictionnaire des paramètres dans une variable plus lisible
    capacite_calorifique = param_biomasse["capacite_calorifique_biomasse"]  # kJ/kg.K

    # initialisation
    energie_chauffage = 0  # énergie pour chauffer la biomasse (MJ)
    energie_vaporisation = 0  # énergie pour vaporiser l'eau de la biom

    # Calcul de l'énergie thermique nécessaire pour la torréfaction
    for entree in biomasse_entree: # on parcourt chaque biomasse d'entrée
        masse = entree["masse"]
        humidité = entree["humidité"]

        # 1. Hypothèse : on chauffe à 200°C depuis 25°C
        energie_chauffage += masse * capacite_calorifique * (200 - 25) / 1000  # MJ 

        # 2. Energie nécessaire pour vaporiser l'eau de la biomasse
        energie_vaporisation += masse * humidité * 2.26476  # en MJ (on utilise la chaleur latente de vaporisation de l'eau)

    # énergie totale nécessaire au procédé de torréfaction
    energie_torrefaction = energie_vaporisation + energie_chauffage

    # On renvoie l'énergie thermique consommée (torrefaction, en MJ), et la masse de biomasse sèche sortie (t)
    return energie_torrefaction, masse_seche_sortie(biomasse_entree)


def main_biomasse(param_biomasse, biomasse, sens_physique=True):
    """Calcule les émissions totales liées à la biomasse, ainsi que les consommations énergétiques.
    Affiche les émissions et consommations plus en détail.
    
    Arguments
    ----------
        param_biomasse : dictionnaire des paramètres liés à la biomasse
        biomasse : liste de dictionnaires avec 'type', 'masse' (t) et 'humidité' (fraction) ou masse sèche (t) selon valeur de sens_physique
        sens_physique : booléen pour indiquer le sens du calcul effectué : biomasse -> carburant (True) ou inverse (False)
        
    Returns
    -------
        conso_chaleur : consommation thermique liée à la biomasse (MJ)
        total_emissions : émissions totales liées à la biomasse (tCO2e)
        masse_seche_biomasse : masse totale de biomasse sèche après torréfaction (t)
    """
    if sens_physique:
        print("Calcul des émissions et consommations liées à la biomasse en entrée du processus e-bio-SAF.\n")
        emissions_culture = culture_biomasse(param_biomasse, biomasse)
        emissions_transport = transport_biomasse(param_biomasse, biomasse)
        conso_chaleur, masse_seche_biomasse = traitement_biomasse(param_biomasse, biomasse)
        total_emissions_biomasse = emissions_culture + emissions_transport
    
    else:
        print("Calcul des émissions et consommations liées à la biomasse en sortie du processus e-bio-SAF.\n")
        masse_humide = masse_humide_sortie(biomasse) # où biomasse est la masse sèche souhaitée
        
        print("On suppose une biomasse humide de type bois vert à 25% d'humidité")
        biomasse_humide = [{"type": "bois_vert", "masse": masse_humide, "humidité": 0.25}]
        
        # On reprend les calculs d'émissions dans le sens physique avec la biomasse humide supposée.
        emissions_culture = culture_biomasse(param_biomasse, biomasse_humide)
        emissions_transport = transport_biomasse(param_biomasse, biomasse_humide)
        conso_chaleur, masse_seche_biomasse = traitement_biomasse(param_biomasse, biomasse_humide)
        total_emissions_biomasse = emissions_culture + emissions_transport

    print(f"\n - Masse de biomasse sèche : {masse_seche_biomasse} t")
    print(f" - Émissions liées à la culture de la biomasse : {emissions_culture:.2f} tCO2e")
    print(f" - Émissions liées au transport de la biomasse : {emissions_transport:.2f} tCO2e")
    print(f" - Consommation thermique pour la torréfaction : {conso_chaleur:.2f} MJ")
    print(f" - Émissions totales liées à la biomasse : {total_emissions_biomasse:.2f} tCO2e\n")

    return conso_chaleur, total_emissions_biomasse, masse_seche_biomasse




