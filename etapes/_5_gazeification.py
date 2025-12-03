"""
Paramètres et hypothèses sourcées pour la gazeification, puis fonctions de calcul des émissions."""

###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################

param_gazeification = {
    "rendement_gazeification": ...,    # Efficacité du processus de gazeification
    #"émissions_gazeification": 60,      # Émissions liées à la gazeification (gCO2e/MJ)
    #"consommation_biomasse": 0.1,        # Consommation de biomasse (MJ/MJ de gaz produit)

    "masse_oxygène" : ... 
}


gaz_params = {

    # Le taux carbone du bois sec est autour de 50% de C et est assez indépendant de l'essence de l'arbre (source : https://www-woodworks-org.translate.goog/resources/calculating-the-carbon-stored-in-wood-products/?_x_tr_sl=en&_x_tr_tl=fr&_x_tr_hl=fr&_x_tr_pto=rq)
    "taux_carbone": 0.50,       #Taux carbone du bois sec (% de masse)

    #Autre moyen de calculer taux carbone :     PCI_sec = PCI_humide / (1 - Humidité) => taux_carbone = PCI_sec / 34.5


    "rendement": 0.85,
    "pertes_c": 0.05,
    "part_co2": 0.40,
    "elec_kwh_t": 120,
    "chaleur_kwh_t": 300
    }


##############################################################
# Fonctions de calcul des émissions
##############################################################
def gazeification(biomasse_kg,params):

    C_total = biomasse_kg * params["taux_carbone"]

    C_utilisable = C_total * params["rendement_gazeification"]
    C_pertes = C_utilisable * params["pertes_c"]
    C_syngaz = C_utilisable - C_pertes
    C_CO2 = C_syngaz * params["part_co2"]

    CO2 = C_CO2 * (44/12)

    return

def bilan_chaleur_gazeification():

    chaleur = 0

    return chaleur


def conso_elec_gazeification():

    energie_gazeification = 0

    return energie_gazeification



def emissions_gazeification(param_gazeification):
    # Calcul des émissions totales pour le processus de gazeification
    émissions = 0
    return émissions