"""
Paramètres et hypothèses sourcées pour FT, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_FT = {
    "efficacité_FT": 0.9,            # Efficacité du processus FT
    "émissions_FT": 40,              # Émissions liées au processus FT (gCO2e/MJ)
    "consommation_hydrogène": 0.05  # Consommation d'hydrogène (MJ/MJ de carburant)
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_FT(param_FT):
    # Calcul des émissions totales pour le processus FT
    émissions = (param_FT["émissions_FT"] + 
                 param_FT["consommation_hydrogène"] * 10) / param_FT["efficacité_FT"]
    return émissions

