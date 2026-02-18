"""
PARTIE : Fischer-Tropsch

Contient :
- param_FT : les paramètre liées à l'étape Fischer-Tropsch.
- Les fonctions de calcul des émissions liées à l'étape FT :
   - Fischer_Tropsch : calcule la consommation électrique totale et les émissions de CO2 liées à l'étape FT
   - Inv_Fischer_Tropsch : calcule la masse de CO nécessaire pour obtenir une certaine masse de kérosène produite, 
     ainsi que les émissions et consommation électrique associées.

"""


###############################################################
# Stockage des paramètres avec les hypothèses sourcées        #
###############################################################


param_FT = {
    
   ## PARAMETRES ELYSE/ADEME POUR EXTRAPOLATION ##
   
   # sortie e-kerosene BioTJet (t/an) (Elyse)
   "production_BioTJet": 87000,

   # PCI e-kerosene (kWh/kg) (ADEME)
   "PCI_kerosene": 11.974,

   # Besoin total en CO2 (tCO2/an) (Elyse)
   "besoin_total_CO2": 461871,

   # rendement entre Kerosene et naphta Calculé par E.Lombard à partir des données Elyse
   "rendement_kerosene_naphta": 0.79,

   # Entrée carbone par biomasse (t) (Elyse)
   "masse_carbone_initiale": 150000,

   # Masse de C dans le kerosene en sortie (t) (Elyse)
   "masse_carbone_kerosene":  78880,

   # Masse de C dans le CO2 utilisé pour EM-Lacq (t) (Elyse)
   "masse_carbone_CO2_EMLacq":  33600,

   # Masse de CO issue de la gazéification (t) (Elyse)
   "MasseCO_gazif_Elyse": 253942
}


##############################################################
# Fonctions de calcul des émissions
##############################################################

def Fischer_Tropsch(param_FT, CO_gazif): # Utilise la masse de CO issue de la gazéification
   """
   Cette fonction calcule la consommation électrique totale et les émissions de CO2 liées à l'étape FT.
   L'étape FT n'est pas modélisée, c'est une extrapolation à partir du tableau ADEME.
   On calcule d'abord un premier ratio qu'on obtient à partir des données prévisionnelles de Elyse
   puis on se sert d'une règle de trois pour obtenir les résultats pour notre cas.

   Arguments :
   -----------
       - param_FT : dictionnaire des paramètres de l'étape FT
       - CO_gazif : masse de CO issue de la gazéification (t)

   Returns :
   ----------
       - consommation_totale_FT : consommation électrique totale de l'étape FT (kWh/an)
       - emissions_rendement_carbone : émissions CO2 liées à l'étape FT (tCO2e)
       - masse_kerosene_produite : masse de kérosène produite (t)
   """


   # Calcul de consommation relative CO2 (Mt/Twh)
   conso_relative_CO2 = param_FT['besoin_total_CO2'] / (param_FT['production_BioTJet'] * param_FT['PCI_kerosene'] )  

   # Consommation électrique (Twhélec/TWh) calculée avec interpolation linéaire sur tableau de l'ADEME
   consommation_électrique = 3.3 + (conso_relative_CO2 - 0.43)*(3.2-2.4)/(0.43-0.36)

   # Consommation totale pour prod E-CHO (MWh/an)
   consommation_totale_FT = param_FT['production_BioTJet'] * param_FT['PCI_kerosene'] * (consommation_électrique)

   # Calcul des émissions liées au rendement carbone
   emissions_rendement_carbone = (param_FT['masse_carbone_initiale'] 
   - (param_FT['masse_carbone_kerosene']/ param_FT['rendement_kerosene_naphta'])
   - param_FT['masse_carbone_CO2_EMLacq'])* (44/12) # Conversion C en CO2
   # le résultat est légèrement différent du excel car la masse de naphta est calculée via le rendement et non donnée directement

   ## Calculs pour notre cas ##
   # on utilise le ratio des masses de CO par rapport à l'étude Elyse
   consommation_totale_FT = consommation_totale_FT * (CO_gazif / param_FT['MasseCO_gazif_Elyse']) * 1000    # en kWh
   emissions_rendement_carbone = emissions_rendement_carbone * (CO_gazif / param_FT['MasseCO_gazif_Elyse']) # en tCO2e
   masse_kerosene_produite = param_FT['production_BioTJet'] * (CO_gazif / param_FT['MasseCO_gazif_Elyse'])  # en t

   # affichage des résultats
   print("\n================ Résultats Fischer-Tropsch ================")
   print(f"Consommation électrique totale FT : {consommation_totale_FT:,.2f} kWh".replace(",", " "))
   print(f"Émissions liées au rendement carbone : {emissions_rendement_carbone:,.2f} tCO2e".replace(",", " "))
   print(f"Masse de kérosène produite : {masse_kerosene_produite:,.2f} t".replace(",", " "))
   print("===========================================================\n")

   return consommation_totale_FT, emissions_rendement_carbone, masse_kerosene_produite


##############################################################
# Inversion de la fonction FT pour obtenir la masse de CO nécessaire
##############################################################
def Inv_Fischer_Tropsch(param_FT, masse_kerosene_voulue):
   """
   Cette fonction calcule les émissions et la consommation électrique associée à une masse de kérosène voulue,
   ainsi que la masse de CO nécessaire à la production de kerosene voulue.

    Arguments :
       - masse de kérosène à produire (t)
    
    Sorties :
       - consommation électrique totale de l'étape FT (kWh)
       - émissions CO2 liées à l'étape FT (tCO2e)
       - masse de CO nécessaire (t)
   """
   # on se sert d'une règle de trois pour obtenir la masse de CO nécessaire
   CO_necessaire = (masse_kerosene_voulue / param_FT['production_BioTJet']) * param_FT['MasseCO_gazif_Elyse']

   # on calcule les émissions et la consommation électrique associée grace à la fonction Fischer_Tropsch()
   consommation_totale_FT, emissions_rendement_carbone, _ = Fischer_Tropsch(param_FT, CO_necessaire)

    
   return consommation_totale_FT, emissions_rendement_carbone, CO_necessaire

