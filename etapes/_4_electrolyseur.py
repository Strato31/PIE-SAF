"""
Paramètres et hypothèses sourcées pour l'électrolyseur, puis fonctions de calcul des émissions.

⚠⚠⚠⚠
La méthode appliquée permet de calculer les performances d'un électrolyseur Alcalin ou PEM 
avec des  technologies de 2020 et  supposées être disponibles en 2030.

Deux autres méthodes d'électrolyse sont en cours d'étude (SOEC = Solide Oxide Electrolysis Cell
et AEM = Anion Exchange Membrane) mais ne sont pas encore intégrées dans ce modèle.
"""

### Coordination sur les unités utilisées :
# Energie en kWh
# Masse en Tonnes
# Emissions en kgCO2eq/an
# Chaleur en MJ
###

"""
Paramètres et hypothèses sourcées pour l'électrolyseur, puis fonctions de calcul des émissions.

⚠⚠⚠⚠
La méthode appliquée permet de calculer les performances d'un électrolyseur Alcalin ou PEM 
avec des technologies de 2020 et supposées être disponibles en 2030.

Deux autres méthodes d'électrolyse sont en cours d'étude (SOEC = Solide Oxide Electrolysis Cell
et AEM = Anion Exchange Membrane) mais ne sont pas encore intégrées dans ce modèle.
"""

### Coordination sur les unités utilisées :
# Energie (électricité) en kWh
# Masse en Tonnes
# Emissions en kgCO2eq/an
# Chaleur en MJ (Conversion : 1 kWh = 3.6 MJ)
###
"""Paramètres et hypothèses sourcées pour l'électrolyseur, puis fonctions de calcul des émissions.

⚠⚠⚠⚠
La méthode appliquée permet de calculer les performances d'un électrolyseur Alcalin ou PEM 
avec des  technologies de 2020 et  supposées être disponibles en 2030.

Deux autres méthodes d'électrolyse sont en cours d'étude (SOEC = Solide Oxide Electrolysis Cell
et AEM = Anion Exchange Membrane) mais ne sont pas encore intégrées dans ce modèle.
"""

### Coordination sur les unités utilisées :
# Energie en kWh
# Masse en Tonnes
# Emissions en kgCO2eq/an
# Chaleur en MJ
###


###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

"""
Remarques sur les hypothèses : 
- L'énergie « stackée » Estack est l'énergie électrique totale en kWh / kgH2 (comprend l'électrolyse, 
    mais aussi le fonctionnement global de l'unité de production) nécessaire à la fabrication la 
    distribution de l'H2, sans prise en compte de la perte en ligne amont.
- Nous n'utiliserons que la valeur stackée de l'électrolyse alcaline car c'est la technologie choisie 
    par E-CHO

"""

# Electrolyse alcaline basse température (technologie de référence):

param_electrolyseur_alcalin = {
    "efficacité_electrolyseur": 0.7,            # Efficacité de l'électrolyseur (Source : ADEME)
    "consommation_electricite_stack": 56000,    # Consommation d'électricité stackée (kWh/tonnes H2) (Source : ADEME) 
                                                
    "consommation_eau" : 1,                     # L/Nm3 
    "produit_alcalin" : 0,
    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution 
                                                # Valeur donnée par RTE : 2.1% de pertes sur le réseau haute tension (utilisé par les industries)
}


# Electrolyse PEM (Proton Exchange Membrane):
# (cette technologie pose des problèmes de fiabilité)

param_electrolyseur_PEM = {
    "efficacité_electrolyseur": 0.75,           # Efficacité de l'électrolyseur PEM
    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution (idem alcalin)
}



##############################################################
# Fonction de calcul de la consommation électrique spécifique à partir de la technologie de référence
##############################################################

def consom_elec_stack(param_electrolyseur_ref, param_electrolyseur_cible):
    """
    Calcul de la consommation électrique stackée de l'électrolyseur cible (PEM ou autre) à partir de la 
    référence (Alcalin) en ajustant (normalisation) avec les rendements respectifs.
    """
    consommation_stack_ref = param_electrolyseur_ref["consommation_electricite_stack"]
    rendement_ref = param_electrolyseur_ref["efficacité_electrolyseur"]
    rendement_cible = param_electrolyseur_cible["efficacité_electrolyseur"]
    
    consommation_stack_cible = consommation_stack_ref * (rendement_ref / rendement_cible)
    
    return consommation_stack_cible

##############################################################
# Vérification de la cohérence de la production de H2 et 02
##############################################################
"""
La réaction d'électrolyse de l'eau est la suivante :
2 H2O(l) (+ élec) → 2 H2(g) + O2(g)
On doit alors s'assurer que la production d'oxygène est bien la moitié de la production d'hydrogène 
(environ).

"""

def coherence_electrolyse(besoin_H2, besoin_O2):
    # Calcul de la production d'oxygène théorique
    besoin_O2_theorique = besoin_H2 / 2  # en kg

    # Vérification de la cohérence
    if abs(besoin_O2 - besoin_O2_theorique) > 0.01 * besoin_O2_theorique:
        raise ValueError("Incohérence dans les besoins d'H2 et d'O2 pour l'électrolyse.")
    else:
        return True
    


##############################################################
# Fonction de calcul de la consommation électrique de l'électrolyseur
##############################################################

"""
ENTREES : 
- Quantité de H² à produire : donnée par la gazéification et Fischer-Tropsch  (en tonnes)
- Quantité de O² à produire : donnée par la gazéification (en tonnes)
- Paramètres de l'électrolyseur (efficacité, consommation électricité, émissions électricité) : param_electrolyseur

SORTIES :
- Consommation électrique de l'électrolyseur (en kWh)

"""

def consommation_electrolyseur(param_electrolyseur, besoin_H2_FT, besoin_O2_gazif, besoin_H2_gazif):
    # Calcul du besoin total en H2 de l'électrolyseur
    besoin_H2 = besoin_H2_FT + besoin_H2_gazif 

    # Vérification de la cohérence des besoins en H2 et O2
    # coherence_electrolyse(besoin_H2, besoin_O2_gazif) inutile car Maelys teste déjà

    # Calcul de la consommation électrique stackée de l'électroyseur
    conso_elec_stack = consom_elec_stack(param_electrolyseur_alcalin, param_electrolyseur)

    # Calcul de la consommation électrique de l'électrolyseur
    consommation_electricite = besoin_H2 * conso_elec_stack  # en kWh
    
    return consommation_electricite



##############
# Fonction de test
##############

# if __name__ == "__main__":
#     # Exemple d'utilisation de la fonction d'émissions pour un électrolyseur PEM
#     besoin_H2_FT = 800  # kg
#     besoin_O2_gazif = 500  # kg
#     besoin_H2_gazif = 200  # kg

    consommation_elec = consommation_electrolyseur(param_electrolyseur_PEM, besoin_H2_FT, besoin_O2_gazif, besoin_H2_gazif)
    print(f"Consommation électrique de l'électrolyseur PEM : {consommation_elec} kWh")
