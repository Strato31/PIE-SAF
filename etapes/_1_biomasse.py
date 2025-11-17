"""
Paramètres et hypothèses sourcées pour la biomasse, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_biomasse = {
    "rendement_biomasse": 0.85,  # Rendement de conversion
    "émissions_culture": 50,     # Émissions liées à la culture (gCO2e/MJ)
    "émissions_transport": 10,    # Émissions liées au transport (gCO2e/MJ)
    "émissions_transformation": 30  # Émissions liées à la transformation (gCO2e/MJ)
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_biomasse(param_biomasse):
    # Calcul des émissions totales pour la biomasse (merci copilot)
    émissions = (param_biomasse["émissions_culture"] +
                 param_biomasse["émissions_transport"] +
                 param_biomasse["émissions_transformation"]) / param_biomasse["rendement_biomasse"]
    return émissions
