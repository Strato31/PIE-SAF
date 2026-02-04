# PIE-SAF
<img width="1088" height="698" alt="image" src="https://github.com/user-attachments/assets/28f3b4d7-7b81-400b-ac4c-fe46b5fc0a16" />
___________________________

Diagramme présentant les données d'entrée et de sortie pour chaque module "étape" du code. En plus de ces données, les modules étape prendront également en entrée une série de variables et d'hypothèses qu'on ne détaille pas ici. Attention : ce ne sont pas les entrées et sorties physiques de ces étapes, mais bien les arguments et retours des fonctions qui composent chaque module. 
Par exemple, l'hydrogène est une sortie pour FT car l'algorithme calcule la quantité d'hydrogène nécessaire à produire par l'électrolyseur.

Les entrées/sorties peuvent être résumées comme suit :

**BIOMASSE**
- Entrées : type/masse/humidité des biomasses utilisées
- Sorties : élec, chaleur, masse_biomasse_seche

**GASIFICATION**
- Entrées : masse_biomasse_seche, oxygene
- Sorties : élec, chaleur, CO2, quantités CO et H2 dans le syngas, déchets

**FT**
Cette étape n'est pas réellement modélisée, elle utilise une interpolation des données de l'ADEME pour d'autres procédés. Les prévisions d'ELYSE de production de kerosène et de demande en bois sont utilisées pour faire une règle de trois avec les scénari modélisés.
Sens Physique :
- Entrées : quantités CO dans le syngas
- Sorties :  connso élec, émissions CO2, kérosène produit
Sens inverse :
- Entrées : quantité de kérosène produit
- Sorties :Masse de CO, Consommation élec, conso élec

**ELECTROLYSE**
- Entrées : eau, quantité H2 à produire
- Sorties : élec

**ENERGIES**
- Entrées : consommations chaleur et élec
- Sortie : émissions

**COMPRESSION**
- Entrées : masse CO2, quantités CO et H2 dans le syngas, masse 02
- Sorties : élec
________________________________________

UNITES : 
- emissions carbone : tCO2e
- masse : en tonnes
- électricité : kWh
- énergie : MJ (positive si consommée, négative si produite)
- --> Conversion : 1 kWh = 3.6 MJ


## Structure du projet 

```
PIE-SAF/
│├── README.md
│├── etapes/                      # Dossier principal du code
││   ├── _1_biomasse.py          
││   ├── _3_FT.py
││   ├── _4_electrolyseur.py
││   ├── _5_gazefication.py
││   ├── _6_energies.py
││   ├── _7_compression.py
││   ├── contexte.py
││   ├── emissions_evites.py
││   └── kerosene.py  
│├── tests/   
│├── init.py
│└── main.py
```

### Description des étapes : 

- **Biomasse**

- **Fischer-Tropsch**

- **Electrolyseur**

La partie `_4_electrolyseur.py` a pour but de donner la consommation électrique de la partie électrolyse.

Cette étape n’a pas besoin d’être réversible. Peu importe si on part de la masse de kérosène à produire et on cherche la quantité de biomasse nécessaire, ou à l’inverse si on part de la quantité de biomasse qu’on a et on cherche combien de kérosène on peut produire, l’électrolyse n’est concernée que par les quantités de H<sub>2</sub> et O<sub>2</sub> à produire pour la gazéification et ses fonctions sont utilisables dans les deux sens du code. 

Le paramètre principal de l’étape électrolyseur est la valeur de l’énergie Estack pour la technologique considérée. Cette énergie “stackée” est l’énergie électrique totale nécessaire à la fabrication et à la distribution d’un kilogramme d’H<sub>2</sub> (valeur en kWh/kgH2). Cette énergie comprend l’électrolyse et le fonctionnement global de l’unité de production mais pas la perte en ligne amont qu’on devra ajouter. 

Pour prendre en main le code rapidement : 
1. Si vous utilisez la technologie alcaline basse température : mettez à jour le dictionnaire des paramètres déjà existant si les valeurs ne sont plus correctes.
2. Si vous utilisez une technologie d’électrolyse différente : copiez un dictionnaire déjà existant d’une autre technologie, adaptez le nom, mettez à jour les valeurs. Si la consommation électrique stackée n’est pas connue, laissez juste `None`. Une fonction `consom_elec_stack` a été créée pour fournir une valeur en normalisant à partir de la valeur de consommation stackée de la technologie de référence et des rendements respectifs.
- La fonction `coherence_electrolyse` permet de vérifier que les valeurs de masse de O<sub>2</sub> et de H<sub>2</sub> demandées en entrée sont cohérentes avec les proportion voulues par la réaction d’électrolyse. Pour le moment, la gazéification s’occupe de cette étape de vérification. Par la suite, si on est amené à considérer d’autres procédés qui n’utilisent pas forcément la gazéification, cette fonction pourra être utile, il faudra alors juste dé-commenter la ligne correspondante dans la fonction centrale.

- **Gazéification**

- **Energies**

La partie `_6_energie.py` a pour but de calculer les émissions de CO2 lié à la consommation électrique en fonction du mix énergétique. Cette partie est organisé en deux sous-partie : 

1. ***Paramètres du mix énergétique**  
2. ***Calcul des émissions**

***Partie données***
*facteur emission* : dictionnaire regroupant les facteurs d'émission de chaque filiaire de production d'énergie.

*param_mix_2050* : répartition de la production de l'énergie en fonction des différentes filiaires de production pour 2050, cette répartition a été estimés par les shifters à partir des annonces du Président Macron en 2023 sur la construction de 14 EPR2 (hypothèse moyenne) et du développement des parcs photovoltaïque et éolien maritime et terrestre. 
Cette répartition peut être adapté en fonction des scénarios prospectif pour 2050.

*param_mix_2023* : facteur d'émission lié à la production et à la consommation d'électricité en France en 2023 d'après le rapport « bilan électrique RTE 2023 ».

***Partie calcul***
*emissions_energetique_processus* : Calcule les émissions de CO2 (en gCO2eq) liées à une consommation énergétique donnée pour un processus (en kWh), en utilisant un mix énergétique prévisionnel pour 2050 et le mix actuel pour 2023.

*emissions_energie_totale* : Agrège les émissions de CO2 (en gCO2eq) liées à une liste de consommations énergétiques (en kWh),en distinguant les émissions pour 2050 et pour 2023.
    
*verif_hypothèse* : Vérifie l'hypothèse selon laquelle la consommation thermique totale des processus est inférieure ou égale à la chaleur récupérable.

- **Compression**

La partie `_7_compression.py` est organisé en deux sous-parties principales :

1. ***Gestion des données physico-chimiques**  
2. ***Calcul de la consommation énergétique**

Cette partie contient des fonctions permettant de calculer l'énergie nécessaire à la compression de gaz, elle ne nécessite pas d'adaption particulière pour pouvoir être réversible. Elle a été codée à partir de l'excel des shifters mais de manière à pouvoir calculer l'énergie nécessaire à la compression du CO2, du CO, de l'O2 et du syngas, ainsi s'il faut faire des calculs de compression avec d'autres gaz il y aura certainement des ajustements à faire.

***Partie données***

Les propriétés physico-chimiques des gaz sont regroupées dans une structure de type dictionnaire :

*carac_physico_chimiques* : Ce dictionnaire contient l’ensemble des caractéristiques physico-chimiques associées à chaque gaz.

Les valeurs utilisées proviennent du fichier Excel des Shifters, en considérant :

- un comportement de gaz parfait,
- des conditions de référence de **288,15 K** et **1 bar**.

***Partie calcul***

Plusieurs fonctions permettent de réaliser les calculs thermodynamiques et d’estimer la consommation énergétique liée à la compression.

*param_temp_variable* : Calcule les caractéristiques physico-chimiques des gaz en fonction de la température. Cette fonction implémente les équations des capacités calorifiques propres à chaque gaz. Elle calcule également : le coefficient adiabatique γ (gamma), la constante spécifique du gaz Rs, car ces paramètres dépendent de Cp et sont nécessaires aux calculs ultérieurs.

*calcul_echauffement_isentropique* : Calcule l’échauffement isentropique lors d’une compression allant de la pression P1 à la pression P2, à partir d’une température initiale T0 (K). Cette fonction s’appuie sur l’application de la **loi de Laplace** pour les gaz parfaits.

*compression_isentropique* : Renvoie la température finale obtenue après une compression isentropique permettant de passer de la pression P1 (bar) à la pression P2 (bar). Le calcul est réalisé de manière itérative afin de déterminer précisément l’échauffement lié à la compression du gaz.

*conso_compression* : Calcule la consommation électrique (en **MWh**) nécessaire pour comprimer une masse de gaz donnée (en **kg**) de la pression P1 (bar) à la pression P2 (bar) à partir d’une température initiale T0_K. La consommation électrique est estimée à partir de l’échauffement réel. Les équations détaillées utilisées pour ce calcul sont documentées dans le fichier Excel de référence.

*conso_compression_syngaz* : Calcule la consommation électrique (en **MWh**) nécessaire à la compression du syngaz. renvoie la consommation électrique (en MWh) nécessaire pour comprimer du syngaz (en kg). Il s’agit d’un calcul spécifique prenant en compte les trois gaz constituant le mélange. La procédure de calcul est la suivante : calcul de l’échauffement pour chacun des gaz, détermination de la température moyenne du mélange, calcul d’un Cp moyen pondéré par la composition et calcul de la puissance moyenne absorbée.

Le processus de calcul suit les étapes détaillées dans le document technique associé.
La consommation finale d’énergie liée à la compression d’un gaz est obtenue via la fonction conso_compression. Pour le cas particulier du syngaz, il est nécessaire d’utiliser la fonction conso_compression_syngaz, car ce dernier étant composé de plusieurs gaz, il faut pondérer les échauffements de chacun d’eux par leur proportion massique.
________________________________________

Etapes a inclure :
- convoyage et broyage du bois
- mix électrique (hypothèses)
- origine du bois
- données E-CHO
- consommation énergétique production
- oxygène
- chaleur (pour l'instant ignorée)
- consommation électrique fonctionnement
- transport du bois
- CO2
- raffinage
    - rendement carbone
    - fonctionnement pompes à eau
        - transfert de vapeur vers l'extérieur
- electrolyseur (très long oscour) (H2)



LA SUITE :
- permettre de faire les calculs dans l'autre sens (biomasse->kérosène et kérosène->biomasse)
- créer format dictionnaire de données par projet
- rendre globales les variables qui le sont
- faire un main fonctionnel
