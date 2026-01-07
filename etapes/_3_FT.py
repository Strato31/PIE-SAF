###############################################################
# Stockage des paramètres avec les hypothèses sourcées
###############################################################


param_FT = {
    # paramètres globaux
    # sortie  e-kerosene BioTJet (t/an)
    "production_BioTJet": 87000,

    # PCI e-kerosene (kWh/kg)
    "PCI_kerosene": 11.974,

    # Besoin total en CO2 (tCO2/an)
    "besoin_total_CO2": 461871,

    # rendement entre Kerosene et naphta Calculé par E.Lombard
    "rendement_kerosene_naphta": 0.79,    

    # Entrée carbone par biomasse (t)
    "masse_carbone_initiale": 150000,

    # Masse de C dans le kerosene en sortie (t)
    "masse_carbone_kerosene":  78880,

    # Masse de C dans du CO2 utilisé pour EM-Lacq
    "masse_carbone_CO2_EMLacq":  33600
}


##############################################################
# Fonctions de calcul des émissions
##############################################################

def emissions_FT(param_FT):
    # Calcul de consommatoin relative CO2 (Mt/Twh)
    conso_realtive_CO2 = param_FT['besoin_total_CO2'] / (param_FT['production_BioTJet'] * param_FT['PCI_kerosene'] )  

    # consommation électrique (Twhélec/TWh) calculée avec interpolation linéaire sur tableu de l'ADEME
    consommation_électrique = 3.3 + (conso_realtive_CO2 - 0.43)*(3.2-2.4)/(0.43-0.36)

    # Consommation totale pour prod E-CHO (GWh/an)
    consommation_totale_FT = param_FT['production_BioTJet'] * param_FT['PCI_kerosene'] * (consommation_électrique)/1000

    # Calcul des émissions liées au rendement carbone
    emmissions_rendement_carbone = (param_FT['masse_carbone_initiale'] 
    - (param_FT['masse_carbone_kerosene']/ param_FT['rendement_kerosene_naphta'])
    - param_FT['masse_carbone_CO2_EMLacq'])* (44/12) # Conversion C en CO2
    # le résultat est légèrement différent du excel car la masse de naphta est calculée via le rendement et non donnée directement

    return consommation_totale_FT, emmissions_rendement_carbone

# print(emissions_FT(param_FT))

def main_FT():
    """
    Arguments :
       - composition et quantité du syngas
    
    Sorties :
       - besoin en H2 pour FT (t)
       - émissions CO2 liées à l'étape FT (tCO2e)
       - masse de kérosène produite (t)"""
    return