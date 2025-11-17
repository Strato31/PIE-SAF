"""
Paramètres et hypothèses sourcées pour l'électrolyseur, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_electrolyseur = {
    "efficacité_electrolyseur": 0.7,   # Efficacité de l'électrolyseur
    "émissions_electricite": 100,      # Émissions liées à l'électricité utilisée (gCO2e/kWh)
    "consommation_electricite": 50     # Consommation d'électricité (kWh/kg H2)
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_electrolyseur(param_electrolyseur):
    # Calcul des émissions totales pour l'électrolyseur
    émissions = (param_electrolyseur["consommation_electricite"] * 
                 param_electrolyseur["émissions_electricite"]) / param_electrolyseur["efficacité_electrolyseur"]
    return émissions

