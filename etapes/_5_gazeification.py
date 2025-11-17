"""
Paramètres et hypothèses sourcées pour la gazeification, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_gazeification = {
    "efficacité_gazeification": 0.8,    # Efficacité du processus de gazeification
    "émissions_gazeification": 60,      # Émissions liées à la gazeification (gCO2e/MJ)
    "consommation_biomasse": 0.1        # Consommation de biomasse (MJ/MJ de gaz produit)
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_gazeification(param_gazeification):
    # Calcul des émissions totales pour le processus de gazeification
    émissions = (param_gazeification["émissions_gazeification"] + 
                 param_gazeification["consommation_biomasse"] * 50) / param_gazeification["efficacité_gazeification"]
    return émissions