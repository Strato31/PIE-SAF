"""
FIchiers nécessaires :
- stockages des paramètres avec les hypothèses sourcées
- fonctions de calcul des émissions pour chaque étape du cycle de vie
- main pour orchestrer le calcul de l'ACV
"""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

paramètres1 = {
    "param1": 1,
    "param2": 2
}

##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_etape_1(paramètres1):
    # Calcul des émissions pour l'étape 1
    émissions = paramètres1["param1"] * 10 + paramètres1["param2"] * 5
    return émissions



def calcul_acv(paramètres1):
    émissions_totales = 0

    # Étape 1
    émissions_totales += emissions_etape_1(paramètres1)

    return émissions_totales


def graphes_donnees():
    # Génération des graphes et des données
    pass


