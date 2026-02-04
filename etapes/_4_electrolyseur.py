"""
PARTIE : Électrolyseur

Contient :
 - Paramètres sourcés pour l'électrolyseur :
    - param_electrolyseur_alcalin : paramètres pour l'électrolyseur alcalin
    - param_electrolyseur_PEM : paramètres pour l'électrolyseur PEM
 - Fonctions de calcul :
    - consom_elec_stack : calcule la consommation électrique stackée pour une technologie cible à partir de la technologie de référence
    - coherence_electrolyse : vérifie la cohérence entre la production d'H2 et d'O2
    - consommation_electrolyseur : calcule la consommation électrique totale de l'électrolyseur


⚠⚠⚠⚠
La méthode appliquée permet de calculer les performances d'un électrolyseur Alcalin  
avec des  technologies de 2020 et supposées être disponibles en 2030. 

Deux autres méthodes d'électrolyse sont en cours d'étude (SOEC = Solide Oxide Electrolysis Cell
et AEM = Anion Exchange Membrane) mais ne sont pas encore intégrées dans ce modèle.
"""

### Coordination sur les unités utilisées :
# Energie (électricité) en kWh
# Masse en t
# Emissions en kgCO2eq/an
# Chaleur en MJ (Conversion : 1 kWh = 3.6 MJ)
###


###############################################################
# Stockage des paramètres avec les hypothèses sourcées        #
###############################################################

"""
Remarques : 
- L'énergie « stackée » Estack est l'énergie électrique totale en kWh / tH2 nécessaire à la fabrication et la 
    distribution de l'H2, sans prise en compte de la perte en ligne amont (comprend l'électrolyse, 
    mais aussi le fonctionnement global de l'unité de production).
- Nous n'utilisons actuellement que la valeur stackée de l'électrolyse alcaline car c'est la technologie 
    choisie par E-CHO

"""

# Electrolyse alcaline basse température (technologie de référence):
param_electrolyseur_alcalin = {
    "efficacite_electrolyseur": 0.7,            # Efficacité de l'électrolyseur (Source : ADEME)
    "consommation_electricite_stack": 56000,    # Consommation d'électricité stackée (kWh/tonnes H2) (Source : ADEME) 
                                                
    "consommation_eau" : 1,                     # L/Nm3 
    "produit_alcalin" : 0,
    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution 
                                                # Valeur donnée par RTE : 2.1% de pertes sur le réseau haute tension (utilisé par les industries)
}


# Electrolyse PEM (Proton Exchange Membrane):
# (cette technologie pose des problèmes de fiabilité pour le moment)
param_electrolyseur_PEM = {
    "efficacite_electrolyseur": 0.75,           # Efficacité de l'électrolyseur PEM
    "consommation_electricite_stack": None,     # Consommation d'électricité stackée (kWh/tonnes H2) (pas de valeur fiable connue)

    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution (idem alcalin)
}

# Pour ajouter une nouvelle technologie d'électrolyseur, il suffit de créer un nouveau dictionnaire
# avec les paramètres correspondants (faire une copie des précédents, changer les valeurs et adapter 
# le nom) et de l'utiliser dans les fonctions ci-dessous.



###################################################################
# Fonction de calcul de la consommation électrique electrolyseur  #
###################################################################

"""
Pour les technologies encore trop peu matures ou utilisées, on n'a pas de valeur de la consommation 
électrique stackée. Si on veut quand même utiliser ce modèle pour ces technologies, on peut estimer la
consommation électrique stackée en ajustant la valeur de la technologie de référence (électrolyse 
alcaline) avec les rendements respectifs et un processus de normalisation.

"""
def consom_elec_stack(param_electrolyseur_ref, param_electrolyseur_cible):
    """
    Calcul de la consommation électrique stackée de l'électrolyseur cible (PEM ou autre) à partir de la 
    référence (Alcalin) en ajustant (normalisation) avec les rendements respectifs.

    Arguments :
    -----------
        - param_electrolyseur_ref : dictionnaire des paramètres de l'électrolyseur de référence (Alcalin)
        - param_electrolyseur_cible : dictionnaire des paramètres de l'électrolyseur cible (PEM ou autre)

    Returns :
    ----------
        - consommation_stack_cible : consommation électrique stackée de l'électrolyseur cible (kWh/tonnes H2)
    """
    # Extraction des valeurs nécessaires
    consommation_stack_ref = param_electrolyseur_ref["consommation_electricite_stack"]
    rendement_ref = param_electrolyseur_ref["efficacite_electrolyseur"]
    rendement_cible = param_electrolyseur_cible["efficacite_electrolyseur"]
    
    # Calcul de la consommation électrique stackée pour la technologie cible
    consommation_stack_cible = consommation_stack_ref * (rendement_ref / rendement_cible)
    
    # Mise à jour du dictionnaire de paramètres de l'électrolyseur cible
    param_electrolyseur_cible["consommation_electricite_stack"] = consommation_stack_cible

    return consommation_stack_cible



##############################################################
# Vérification de la cohérence de la production de H2 et 02
##############################################################

"""
La réaction d'électrolyse de l'eau est la suivante :
2 H2O(l) (+ élec) → 2 H2(g) + O2(g)
On doit alors s'assurer que la production d'oxygène est bien la moitié de la production d'hydrogène (environ).
Selon les masses molaires : 
M_H2 = 2 g/mol et M_O2 = 32 g/mol)
La production d'un kg de H2 génère systématiquement environ 8 kg d'O2.

Cette étape est finalement effectuée dans la partie gazéification. On conserve la fonction au cas où l'étude
d'autres procédés sans la gazéification demande cette vérification.

"""

def coherence_electrolyse(besoin_H2, besoin_O2):
    """
    Vérifie la cohérence entre la production d'H2 et d'O2.
    
    Arguments :
    -----------
        - besoin_H2 : quantité d'H2 à produire (t)
        - besoin_O2 : quantité d'O2 à produire (t)
    Returns :
    ----------
        - True si cohérent, sinon lève une erreur.
    """
    # Calcul de la production d'oxygène théorique
    besoin_O2_theorique = besoin_H2 * 8  # en t

    # Vérification de la cohérence
    if abs(besoin_O2 - besoin_O2_theorique) > 0.01 * besoin_O2_theorique:
        raise ValueError("Incohérence dans les besoins d'H2 et d'O2 pour l'électrolyse.")
    else:
        return True




##############################################################
# Calcul de la consommation électrique de l'électrolyseur    #
##############################################################



def consommation_electrolyseur(param_electrolyseur, besoin_O2_gazif, besoin_H2_gazif):
    """
    Arguments :
    ----------- 
    - Quantité de H² à produire : donnée par la gazéification et Fischer-Tropsch  (t)
    - Quantité de O² à produire : donnée par la gazéification (t)
    - Paramètres de l'électrolyseur (efficacité, consommation électricité, émissions électricité) : 
        param_electrolyseur

    Returns :
    ----------
    - Consommation électrique de l'électrolyseur (en kWh)

    """

    # Vérification de la cohérence des besoins en H2 et O2
    # coherence_electrolyse(besoin_H2, besoin_O2_gazif) inutile car déjà testé dans la gazéification.

    # Calcul de la consommation électrique stackée de l'électroyseur
    if param_electrolyseur["consommation_electricite_stack"] is None:
        conso_elec_stack = consom_elec_stack(param_electrolyseur_alcalin, param_electrolyseur)
    else:
        conso_elec_stack = param_electrolyseur["consommation_electricite_stack"]

    # Calcul de la consommation électrique de l'électrolyseur
    consommation_electricite = besoin_H2_gazif * conso_elec_stack  # en kWh
    
    return consommation_electricite


