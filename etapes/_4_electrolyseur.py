"""
Paramètres et hypothèses sourcées pour l'électrolyseur, puis fonctions de calcul des émissions."""

###
# Energie en kWh
# Masse en kg
# Emissions en kgCO2eq/an
# Chaleur en MJ
###

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

# On considère une électrolyse alcaline basse température (technologie de référence)

param_electrolyseur_ref = {
    "efficacité_electrolyseur": 0.7,            # Efficacité de l'électrolyseur (Source : ADEME)
    "consommation_electricite_stack": 56,       # kWh/kgH2 Consommation d'électricité (kWh/kg H2) (Source : ADEME)
    "consommation_eau" : 1,                     # L/Nm3 
    "produit_alcalin" : 0,
    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution 
}

# On considère une électrolyse PEM (Proton Exchange Membrane)

param_electrolyseur_PEM = {
    "efficacité_electrolyseur": 0.75,           # Efficacité de l'électrolyseur PEM
    "consommation_electricite_stack": 52.3,   # kWh/kg Consommation d'électricité (kWh/kg H2)
    "pertes" : 0.979                            # Pertes en ligne : sur le réseau de distribution 

}


## à récupérer du taffe de Margaux
param_mix_elec = {
    "mix_production" : 43,   #gCO2eq/kWh => Moyenne des émissions de GES sur le territoire national pour produire toute l'électricité
    "mix_consommé" : 60      #gCO2eq/kWh => Moyenne des émissions de GES sur le territoire national prenant en compte l'électricité réellement commsommée (ajout des importations et déduction des exportation)
}

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
    # Calcul de la consommation électrique de l'électrolyseur
    consommation_electricite = besoin_H2 * param_electrolyseur["consommation_electricite_stack"] / param_electrolyseur["pertes"] # sortie en kWh

    # Calcul des émissions totales pour l'électrolyseur
    emissions = (consommation_electricite * mix_elec) / param_electrolyseur["efficacité_electrolyseur"]
    
    return consommation_electricite, emissions

