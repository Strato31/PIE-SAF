"""
Calcul des émissions liées à la compression les différents gaz impliqués dans le procédé E-CHO.
Hypothèses :
    - gaz parfaits
    - pas d'ajustement polynomiale fait -> à réflaichir utltérieurement et revoir les sources

"""

###############################################################
# Zone de données : Paramètres physico-chimiques des gaz
###############################################################
R = 8.314 # Constante des gaz parfaits en J/mol.K

carac_pysico_chimique_methane = { #Source ?
    "T" : 298.15,  # Température (K)
    "P" : 1,        # Pression (bar) à T=298.15 K
    "PCI" : 803.3,   # Pouvoir Calorifique Inférieur (kJ/mol) à T=298.15 K
    "PCS" : 890.8,   # Pouvoir Calorifique Supérieur (kJ/mol) à T=298.15 K
    # PCI : 50.07,   # Pouvoir Calorifique Inférieur (MJ/kg) à T=298.15 K
    # PCS : 55.53,   # Pouvoir Calorifique Supérieur (MJ/kg) à T=298.15 K
    # densite : , # Densité (kg/m3) à 298.15 K et 1 bar source ?
    "densite" : 0.6709, # Densité (kg/m3) à 288.15 K et 1 bar 
    "masse_molaire" : 16.0425, # Masse molaire (g/mol)
    "Cp" : 2.2316, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 1.7133, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
}

def param_temp_variable(T):
    """Renvoie les paramètres physico-chimiques, Cp et gamma, du méthane en fonction de la température T (K)."""
    Cp_mol = 34.942-0.039957*T+0.00019184*T**2-0.00000015303*T**3+3,9321E-11*T**4 # source ? en J/mol.K
    Cp_g = Cp_mol / carac_pysico_chimique_methane["masse_molaire"] # conversion en kJ/kg.K
    Rs = R / (carac_pysico_chimique_methane["masse_molaire"]) # constante spécifique des gaz parfait en kJ/kg.K
    gamma = Cp_g / (Cp_g - Rs) # calcul de gamma
    return Cp_g, gamma

carac_pysico_chimique_CO2 = { #Source ?
    "densite" : 1.8714, # Densité (kg/m3) à 288.15 K et 1 bar 
    "masse_molaire" : 44.0095, # Masse molaire (g/mol)
    "Cp" : 0.8652, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.6763, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
}

def param_temp_variable_CO2(T):
    """Renvoie les paramètres physico-chimiques, Cp et gamma, du CO2 en fonction de la température T (K)."""
    Cp_mol =27.437+0.042315*T-0.000019555*T**2+0.0000000039968*T**3-2,9872E-12*T**4 # source ? en J/mol.K
    Cp_g = Cp_mol / carac_pysico_chimique_CO2["masse_molaire"] # conversion en kJ/kg.K
    Rs = R / (carac_pysico_chimique_CO2["masse_molaire"]) # constante spécifique des gaz parfait en kJ/kg.K
    gamma = Cp_g / (Cp_g - Rs) # calcul de gamma
    return Cp_g, gamma

carac_pysico_chimique_CO = { #Source ?
    "densite" : 1.1450, # Densité (kg/m3) à 298.15 K et 1 bar 
    "masse_molaire" : 28.01, # Masse molaire (g/mol)
    "Cp" : 1.0373, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.7404, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
    "PCI" : 283.0,   # Pouvoir Calorifique Inférieur (kJ/mol) à T=298.15 K
    "PCS" : 283.4,   # Pouvoir Calorifique Supérieur (kJ/mol) à T=298.15 K
    # "PCI" : 10.10,   # Pouvoir Calorifique Inférieur (MJ/kg) à T=298.15 K
    # "PCS" : 10.12,   # Pouvoir Calorifique Supérieur (MJ/kg) à T=298.15 K
}

def param_temp_variable_CO(T):
    """Renvoie les paramètres physico-chimiques, Cp et gamma, du CO en fonction de la température T (K)."""
    Cp_mol =29.556-0.0065807*T+0.00002013*T**2-0.000000012227*T**3+2,2617E-12*T # source ? en J/mol.K
    Cp_g = Cp_mol / carac_pysico_chimique_CO["masse_molaire"] # conversion en kJ/kg.K
    Rs = R / (carac_pysico_chimique_CO["masse_molaire"]) # constante spécifique des gaz parfait en kJ/kg.K
    gamma = Cp_g / (Cp_g - Rs) # calcul de gamma
    return Cp_g, gamma

carac_pysico_chimique_O2 = { #Source ?
    "densite" : 1.3540, # Densité (kg/m3) à 288.15 K et 1 bar 
    "masse_molaire" : 31.9988, # Masse molaire (g/mol)
    "Cp" : 0.9165, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.6567, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
}

# def param_temp_variable_O2(T):
#     """Renvoie les paramètres physico-chimiques, Cp et gamma, de l'O2 en fonction de la température T (K)."""
#     #Cp_mol = # source ? en J/mol.K
#     Cp_g = Cp_mol / carac_pysico_chimique_O2["masse_molaire"] # conversion en kJ/kg.K
#     Rs = R / (carac_pysico_chimique_O2["masse_molaire"]) # constante spécifique des gaz parfait en kJ/kg.K
#     gamma = Cp_g / (Cp_g - Rs) # calcul de gamma
#     return Cp_g, gamma

carac_pysico_chimique_vepeur_d_eau = { #Source ?
    "chaleur_latente" : 2257, # (kJ/kg) à 373.15 K 
    "masse_molaire" : 18.015, # Masse molaire (g/mol)
    "Cp" : 2.0100, # Capacité calorifique à pression contante (kJ/kg.K) à 373.15 K
    "Cv" : 1.5777, # Capacité calorifique à volume constant (kJ/kg.K) à 373.15 K
    "T" : 373.15,  # Température (K)
}

# à voir si on fait les parame temp variable pour la vapeur d'eau mais rechercher les sources

carac_pysico_chimique_eau_liquide = { #Source ?
    "Cp_moy" : 4.196, # Capacité calorifique à pression contante (kJ/kg.K)
}

carac_pysico_chimique_N2 = { #Source ?
    "densite" : 1.1848, # Densité (kg/m3) à 288.15 K et 1 bar 
    "masse_molaire" : 28.013, # Masse molaire (g/mol)
    "Cp" : 1.0414, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.7432, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
}

# à voir si besoin de gamma

carac_pysico_chimique_air = {
    "densite" : 1.2263, # Densité (kg/m3) à 288.15 K et 1 bar
    "masse_molaire" : 28.976, # Masse molaire (g/mol)
    "Cp" : 1.0051, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.7181, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K 
}

def param_temp_variable_air(T):
    """Renvoie les paramètres physico-chimiques, Cp et gamma, de l'air en fonction de la température T (K)."""
    Cp_g = 1.93271*10**(-13)*T**4-7.9999*10**(-10)*T**3+1.1407*10**(-6)*T**2-4.489*10**(-4)*T**1+1.0575 # source ? en kJ/kg.K
    Rs = R / (carac_pysico_chimique_air["masse_molaire"]) # constante spécifique des gaz parfait en kJ/kg.K
    gamma = Cp_g / (Cp_g - Rs) # calcul de gamma
    return Cp_g, gamma

##############################################################
# Fonctions de calcul des émissions : Calcul conso énergétique du processus
##############################################################
"""
Hypothèses :
    - Pression constante P1=1bar
    - Température initiale T1=15°C=288.15K
    - Utilisation du référentielle SHE/Turbomeca 

"""
# Calcul de la consomation électrique (en MWh) pour comprimer le CO2 capté en sortie de réacteur syngas BioTJet 
def calcul_echauffement_isenthropique(T0, P0 , P1, gamma):
    """Renvoie la température finale (en K) d'un gaz comprimé de manière isentropique 
    de la pression P0 (en bar) à la pression P1 (en bar) à la température T (en K)."""
    Tit1 = T0 * (P1 / P0)**((gamma - 1) / gamma)
    Tit2 = (Tit1+T0)/2 * (P1 / P0)**((gamma - 1) / gamma)
    while ((T0+Tit2)/2-(T0+Tit1)/2) < 0.01 :
        Tit1 = Tit2
        Tit2 = (Tit1+T0)/2 * (P1 / P0)**((gamma - 1) / gamma)
    return Tit2

def conso_compression_CO2(masse_CO2_kg, P1_bar, P2_bar, T1_K):
    """Renvoie la consommation électrique (en MWh) pour comprimer une masse de CO2 (en kg) 
    de la pression P1 (en bar) à la pression P2 (en bar) à la température T1 (en K)."""
    
    Cp_CO2, gamma_CO2 = param_temp_variable_CO2(T1_K)
    R_CO2 = R / carac_pysico_chimique_CO2["masse_molaire"] # constante spécifique des gaz parfait en kJ/kg.K

    # Calcul du travail de compression isentropique (en kJ)
    travail_isentropique_kJ = (Cp_CO2 * T1_K) * ((P2_bar / P1_bar)**((gamma_CO2 - 1) / gamma_CO2) - 1)

    # Consommation électrique en kJ
    conso_elec_kJ = masse_CO2_kg * travail_isentropique_kJ

    # Conversion en MWh
    conso_elec_MWh = conso_elec_kJ / 3.6e6

    return conso_elec_MWh