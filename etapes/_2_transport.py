"""
Paramètres et hypothèses sourcées pour le transport, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_transport = {
    "distance_moyenne": 100,      # Distance moyenne de transport (km)
    "émissions_par_km": 0.2       # Émissions par km (gCO2e/km)
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_transport(param_transport):
    # Calcul des émissions totales pour le transport
    émissions = param_transport["distance_moyenne"] * param_transport["émissions_par_km"]
    return émissions

