"""
Calcul des émissions liées à la compression les différents gaz impliqués dans le procédé E-CHO.
Hypothèses :
    - gaz parfaits
    - pas d'ajustement polynomiale fait -> à réflaichir utltérieurement et revoir les sources
    - compression isentropique avec rendement constant
"""

###############################################################
# Zone de données : Paramètres physico-chimiques des gaz
###############################################################
R = 8.314 # Constante des gaz parfaits en J/mol.K

carac_pysico_chimiques = { #Source ? Nasa Glem coef ?
    "CH4" : {
        "T" : 298.15,  # Température (K)
        "P" : 1,        # Pression (bar) à T=298.15 K
        "masse_molaire" : 16.0425, # Masse molaire (g/mol)
        "Cp" : 2.2316, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
        "Cv" : 1.7133, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
    },

    "H2" : {
        "T" : 298.15,  # Température (K)
        "P" : 1,        # Pression (bar) à T=298.15 K
        "PCI" : 120.39,   # Pouvoir Calorifique Inférieur (MJ/kg) à T=298.15 K
        "PCS" : 141.77,   # Pouvoir Calorifique Supérieur (MJ/kg) à T=298.15 K
        "densite" : 0.0852, # Densité (kg/m3) à 288.15 K et 1 bar 
        "masse_molaire" : 2.01588, # Masse molaire (g/mol)
        "Cp" : 14.2666, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
        "Cv" : 10.1415, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
    },

    "CO2" : {
        "densite" : 1.8714, # Densité (kg/m3) à 288.15 K et 1 bar 
        "masse_molaire" : 44.0095, # Masse molaire (g/mol)
        "Cp" : 0.8652, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
        "Cv" : 0.6763, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
    },

    "CO" : { #Source ?
    "densite" : 1.1450, # Densité (kg/m3) à 298.15 K et 1 bar 
    "masse_molaire" : 28.01, # Masse molaire (g/mol)
    "Cp" : 1.0373, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.7404, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
    },

    "O2" : { #Source ?
    "densite" : 1.3540, # Densité (kg/m3) à 288.15 K et 1 bar 
    "masse_molaire" : 31.9988, # Masse molaire (g/mol)
    "Cp" : 0.9165, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.6567, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
    "Cp1" : 0.972, # Capacité calorifique à pression contante (kJ/kg.K) à 500 K
    "Cp2" : 0.956, # Capacité calorifique à pression contante (kJ/kg.K) à 450 K
    "T1" : 500,  # Température (K)
    "T2" : 450,  # Température (K)
    },

    "vapeur_d_eau" : { #Source ?
    "chaleur_latente" : 2257, # (kJ/kg) à 373.15 K 
    "masse_molaire" : 18.015, # Masse molaire (g/mol)
    "Cp" : 2.0100, # Capacité calorifique à pression contante (kJ/kg.K) à 373.15 K
    "Cv" : 1.5777, # Capacité calorifique à volume constant (kJ/kg.K) à 373.15 K
    "T" : 373.15,  # Température (K)
    },

    "N2" : { #Source ?
    "densite" : 1.1848, # Densité (kg/m3) à 288.15 K et 1 bar 
    "masse_molaire" : 28.013, # Masse molaire (g/mol)
    "Cp" : 1.0414, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.7432, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K
    },

    "air" : {
    "densite" : 1.2263, # Densité (kg/m3) à 288.15 K et 1 bar
    "masse_molaire" : 28.976, # Masse molaire (g/mol)
    "Cp" : 1.0051, # Capacité calorifique à pression contante (kJ/kg.K) à 288.15 K
    "Cv" : 0.7181, # Capacité calorifique à volume constant (kJ/kg.K) à 288.15 K 
    },

    "eau_liquide" : { #Source ?
    "Cp_moy" : 4.196, # Capacité calorifique à pression contante (kJ/kg.K)
    },
    
}

##############################################################
# Fonctions de calcul des émissions : Calcul conso énergétique du processus
##############################################################
"""
Hypothèses :
    - Pression constante P1=1bar
    - Température initiale T1=15°C=288.15K
    - Utilisation du référentielle SHE/Turbomeca pour l'02
"""

# Fonction pour obtenir les paramètres physico-chimiques en fonction de la température
def param_temp_variable(T, gaz):
    """Renvoie les paramètres physico-chimiques, Cp et gamma en fonction de la température T (K)."""
    if gaz == "CH4":
        Cp_mol = 34.942-0.039957*T+0.00019184*T**2-0.00000015303*T**3+3.9321e-11*T**4 # source ? en J/mol.K
    elif gaz == "H2":
        Cp_mol = 33.066178-11.363417*(T/1000)+11.432816*(T/1000)**2-2.772874*(T/1000)**3-0.1585581*(T/1000)**(-2) # équation de shomate en J/mol.K /1000
    elif gaz == "CO2":
        Cp_mol =27.437+0.042315*T-0.000019555*T**2+0.0000000039968*T**3-2.9872e-12*T**4 # source ? en J/mol.K
    elif gaz == "CO":
        Cp_mol =29.556-0.0065807*T+0.00002013*T**2-0.000000012227*T**3+2.2617e-12*T**4 # source ? en J/mol.K
    elif gaz == "air":
        Cp_g = 1.93271e-13*T**4-7.9999e-10*T**3+1.1407e-6*T**2-4.489e-4*T+1.0575 # source ? en kJ/kg.K
    # A voir si besoin de coder pour N2, eau liquide et vapeur d'eau si nécessaire même modèle que l'02 ?
    elif gaz == "O2":
        Cp_g = (carac_pysico_chimiques[gaz]["Cp2"] - carac_pysico_chimiques[gaz]["Cp1"])/(carac_pysico_chimiques[gaz]["T2"] - carac_pysico_chimiques[gaz]["T1"])*(T - carac_pysico_chimiques[gaz]["T1"]) + carac_pysico_chimiques[gaz]["Cp1"] # source ? en kJ/kg.K 
    if gaz != "air" and gaz != "O2":
        Cp_g = Cp_mol / carac_pysico_chimiques[gaz]["masse_molaire"] # conversion en kJ/kg.K
    Rs = R / (carac_pysico_chimiques[gaz]["masse_molaire"]) # constante spécifique des gaz parfait en kJ/kg.K
    gamma = Cp_g / (Cp_g - Rs) # calcul de gamma
    return Cp_g, gamma, Rs

# à voir si on fait les parame temp variable pour la vapeur d'eau mais rechercher les sources

# Ces calculs ne sont utiles que dans le cas où E-CHO/BioTJet serait reconverti et fabriquerait du e-kérosène, le carbone venant de captation de CO2 : pas pris en compte pour l'instant

def calcul_echauffement_isenthropique(T0, P0 , P1, gamma):
    """Calcul de l'échauffement isenthropique pour une compression isenthropique à T0(K) de P1 à P2."""
    Tit1 = T0 * (P1 / P0)**((gamma - 1) / gamma) # itération initiale
    return Tit1

# Calcul approché de l'échauffement isentropique par itération, sur la température, jusqu'à convergence
def compression_isentropique(gaz, P1_bar, P2_bar, T0_K):
    """Renvoie la temperature de la compression isentropique pour passer 
    de la pression P1 (en bar) à la pression P2 (en bar)."""
    # Calcul de l'échauffement à l'état initial
    gamma = param_temp_variable(T0_K, gaz)[1]
    T1_K = calcul_echauffement_isenthropique(T0_K, P1_bar, P2_bar, gamma)
    Tmoy = T0_K

    while abs(Tmoy - (T0_K + T1_K) / 2) > 0.01: # calcul isenthropique de la température par itération jusqu'à convergence
        Tmoy = (T0_K + T1_K) / 2
        T1_K = calcul_echauffement_isenthropique(T0_K, P1_bar, P2_bar, param_temp_variable(Tmoy, gaz)[1])

    return T1_K

# Calcul de la consommation électrique de la compression d'un gaz
def conso_compression(masse_gaz_kg, gaz, rendement, P1_bar, P2_bar, T0_K):
    """Renvoie la consommation électrique (en MWh) pour comprimer une masse de gaz (en kg) 
    de la pression P1 (en bar) à la pression P2 (en bar) à la température initiale T0_K."""

    T1_K = compression_isentropique(gaz, P1_bar, P2_bar, T0_K)
    Tmoy = (T0_K + T1_K) / 2
    
    Cpmoy = param_temp_variable(Tmoy, gaz)[0] # en kJ/(kg.K)
    echauffement_reel = (T1_K - T0_K) / rendement
    conso_elec_MWh = echauffement_reel * Cpmoy * masse_gaz_kg / 3600 # en MWh
    return conso_elec_MWh

# Calcul de la consommation électrique de la compression du syngas (CO2, H2, CO)
def conso_compression_syngaz(masse_C02_kg, masse_H2_kg, masse_C0_kg, rendement, P1_bar, P2_bar, T0_K):
    """Renvoie la consommation électrique (en MWh) pour comprimer le syngas (en kg), calcul spécifique 
    car il prend en compte les trois gaz. procédure de calcul de l'échauffement du mélange : calcul de 
    l'échauffement de chacun des gaz, puis calcul de la T° moyenne et du Cp moyen pondéré par 
    la composition, enfin calcul de la puissance moyenne absorbée. """
    
    # Calcul de l'échauffement isentropique de chaque gaz
    T1_K_CO2 = compression_isentropique("CO2", P1_bar, P2_bar, T0_K)
    T1_K_H2 = compression_isentropique("H2", P1_bar, P2_bar, T0_K)
    T1_K_CO = compression_isentropique("CO", P1_bar, P2_bar, T0_K)

    #Calcul de l'échauffement réel pondéré par la masse de chaque gaz
    Cpmoy = (param_temp_variable((T0_K + T1_K_CO2)/2, "CO2")[0] * masse_C02_kg + 
             param_temp_variable((T0_K + T1_K_H2)/2, "H2")[0] * masse_H2_kg + 
             param_temp_variable((T0_K + T1_K_CO)/2, "CO")[0] * masse_C0_kg) /(masse_C02_kg + masse_H2_kg + masse_C0_kg)
    
    echauffement_reel = (masse_C02_kg * (T1_K_CO2 - T0_K) + 
                         masse_H2_kg * (T1_K_H2 - T0_K) + 
                         masse_C0_kg * (T1_K_CO - T0_K)) / (rendement * (masse_C02_kg + masse_H2_kg + masse_C0_kg))
    
    conso_elec_MWh = echauffement_reel * Cpmoy * (masse_C02_kg + masse_H2_kg + masse_C0_kg) / 3600 # en MWh
    return conso_elec_MWh

# Manque la Consommation d'énergie pour produire à la SOBEGI la vapeur nécessaire pour la réaction RWGS d'EM-Lacq 
# et Consommation électrique pour capter le C02 par DAC	à coder si besoin plus tardxs