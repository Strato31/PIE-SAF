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

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

# On considère une électrolyse alcaline basse température (technologie de référence)

param_electrolyseur_alcalin = {
    "efficacité_electrolyseur": 0.7,            # Efficacité de l'électrolyseur (Source : ADEME)
    "consommation_electricite_stack": 56e3,     # kWh/T H2 Consommation d'électricité (kWh/kg H2) (Source : ADEME)
    
    "consommation_eau" : 1,                     # L/Nm3 
    "produit_alcalin" : 0,
    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution 
}

# On considère une électrolyse PEM (Proton Exchange Membrane)

param_electrolyseur_PEM = {
    "efficacité_electrolyseur": 0.75,           # Efficacité de l'électrolyseur PEM
    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution 

}

## à récupérer du taffe de Margaux
param_mix_elec = {
    "mix_production" : 43,   #gCO2eq/kWh => Moyenne des émissions de GES sur le territoire national pour produire toute l'électricité
    "mix_consommé" : 60      #gCO2eq/kWh => Moyenne des émissions de GES sur le territoire national prenant en compte l'électricité réellement commsommée (ajout des importations et déduction des exportation)
}

##############################################################
# Fonction de calcul de al consommation électrique stackée à partir de la référence
##############################################################

def consom_elec_stack(param_electrolyseur_ref, param_electrolyseur_cible):
    """
    Calcul de la consommation électrique stackée de l'électrolyseur cible (PEM) à partir de la référence (Alcalin)
    en ajustant (normalisation) avec les rendements respectifs.
    """
    consommation_stack_ref = param_electrolyseur_ref["consommation_electricite_stack"]
    rendement_ref = param_electrolyseur_ref["efficacité_electrolyseur"]
    rendement_cible = param_electrolyseur_cible["efficacité_electrolyseur"]
    
    consommation_stack_cible = consommation_stack_ref * (rendement_ref / rendement_cible)
    
    return consommation_stack_cible


##############################################################
# Fonction de calcul des émissions
##############################################################

"""
ENTREES : 
- Quantité de H² à produire (sortie de FT) : 
- Paramètres de l'électrolyseur (efficacité, consommation électricité, émissions électricité) : param_electrolyseur
- Mix électrique utilisé (sortie de Margaux) : mix_elec

SORTIES :
- Consommation électrique de l'électrolyseur
- Emissions associées à l'électrolyseur

"""

def emissions_electrolyseur(param_electrolyseur, mix_elec, besoin_H2):
    # Calcul de la consommation électrique stackée de l'électroyseur
    conso_elec_stack = consom_elec_stack(param_electrolyseur_alcalin, param_electrolyseur)

    # Calcul de la consommation électrique de l'électrolyseur
    consommation_electricite = besoin_H2 * conso_elec_stack  # en kWh

    # Calcul des émissions totales pour l'électrolyseur
    emissions = (consommation_electricite * mix_elec) / param_electrolyseur["efficacité_electrolyseur"]
    
    return consommation_electricite, emissions

