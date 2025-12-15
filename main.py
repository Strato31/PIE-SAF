from etapes import _1_biomasse as biomasse
from etapes import kerosene as transport
from etapes import _3_FT as ft
from etapes import _4_electrolyseur as elec
from etapes import _5_gazeification as gaz
from etapes import _6_energie as energie

def __main__():
    
    emissions_totales = 0

    elec_biomasse, chaleur_biomasse, biomasse_seche = biomasse.traitement_biomasse()
    elec_gaz, chaleur_gaz = gaz.emissions_gazeification(biomasse_seche)
    elec = [elec_biomasse, elec_gaz, ...]
    print(f"Émissions totales du processus PIE-SAF : {emissions_totales} gCO2e/MJ")
    print('Emissions détaillées par étapes :')
    print(f" - Biomasse : {biomasse.total_emissions_biomasse(biomasse.param_biomasse)} gCO2e/MJ")
    print(f" - Transport : {transport.emissions_transport(transport.param_transport)} gCO2e/MJ")
    print(f" - Fischer-Tropsch : {ft.emissions_FT(ft.param_FT)} gCO 2e/MJ")
    print(f" - Électrolyseur : {elec.emissions_electrolyseur(elec.param_electrolyseur)} gCO2e/MJ")
    print(f" - Gazeification : {gaz.emissions_gazeification(gaz.param_gazeification)} gCO2e/MJ")




if __name__ == "__main__":
    __main__()
