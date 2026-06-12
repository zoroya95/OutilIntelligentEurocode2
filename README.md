========================================================
  OUTIL INTELLIGENT EUROCODE 2 - NOTICE D'UTILISATION
  Projet ING1 - CY Cergy Paris Universite - 2025-2026
========================================================


--------------------------------------------------------
1. COMMENT INSTALLER LES BIBLIOTHEQUES NECESSAIRES
--------------------------------------------------------

Avant de lancer le programme, installez les bibliotheques
Python suivantes via la commande pip dans un terminal :

    pip install ezdxf
    pip install openpyxl

Verification : Python 3.8 ou superieur est requis.
Pour verifier votre version Python :

    python --version

Si pip n'est pas reconnu, essayez :

    python -m pip install ezdxf openpyxl


--------------------------------------------------------
2. COMMENT LANCER LE PROGRAMME
--------------------------------------------------------

1. Ouvrez un terminal (invite de commandes ou PowerShell)
   dans le dossier du projet.

2. Lancez le programme principal :

       python main.py

3. La fenetre d'accueil s'ouvre avec deux options :
   - "Dimensionner un poteau"
   - "Dimensionner une poutre"

   Cliquez sur le bouton correspondant a votre calcul.


--------------------------------------------------------
3. QUELLES DONNEES SAISIR
--------------------------------------------------------

--- POUTRE EN BETON ARME ---

Champ                    | Unite  | Exemple
-------------------------|--------|--------
Longueur L               | m      | 5
Hauteur h                | mm     | 500
Largeur b                | mm     | 300
Charge permanente G      | kN/m   | 18
Charge exploitation Q    | kN/m   | 12
Enrobage nominal cnom    | mm     | 30
Classe de beton          | -      | C25/30
Classe d'acier           | -      | B500B
Diametre des barres HA   | mm     | 16
Numero du groupe         | -      | 1

Apres saisie, cliquez sur "Calculer" pour obtenir :
  - qEd, MEd, VEd
  - fcd, fyd
  - d, z
  - As flexion, As min, As necessaire
  - Choix automatique des armatures longitudinales
  - Espacement des etrierss
  - Verification As adoptee >= As necessaire

--- POTEAU EN BETON ARME ---

Champ                      | Unite  | Exemple
---------------------------|--------|--------
Type de section            | -      | Rectangulaire
Largeur b / diametre a     | m      | 0.30
Hauteur h                  | m      | 0.30
Hauteur du poteau H        | m      | 3.2
Charge permanente NG       | kN     | 350
Charge exploitation NQ     | kN     | 600
Classe de beton            | -      | C25/30
Classe d'acier             | -      | B500B
Diametre des barres HA     | mm     | 10

Apres saisie, cliquez sur "Calculer" pour obtenir :
  - NEd, fcd, fyd
  - Ac, elancement lambda
  - As calc, As min, As req
  - Choix des barres
  - Espacement cadres scl,max
  - Verification N_Rd >= N_Ed


--------------------------------------------------------
4. OU TROUVER LE FICHIER DXF GENERE
--------------------------------------------------------

Apres avoir clique sur "Generer DXF" :

1. Une boite de dialogue s'ouvre pour choisir
   l'emplacement de sauvegarde.

2. Le nom de fichier propose par defaut est :
   - Poutre : poutre_BA_groupe_XX.dxf
   - Poteau : poteau_BA_groupe_XX.dxf
   (XX = numero du groupe)

3. Choisissez le dossier de destination et confirmez.

4. Un message "Succes" confirme la creation du fichier.

IMPORTANT : cliquez d'abord sur "Calculer" avant
de cliquer sur "Generer DXF", sinon le bouton
DXF affichera un avertissement.


--------------------------------------------------------
5. COMMENT OUVRIR LE FICHIER DXF
--------------------------------------------------------

Option A - AutoCAD :
  1. Lancez AutoCAD.
  2. Fichier > Ouvrir > selectionnez le fichier .dxf
  3. Les calques disponibles sont :
       BETON, ACIER_LONG, ETRIERS,
       COTATIONS, TEXTES, AXES
  4. Utilisez "ZOOM > Etendue" (touche Z puis E)
     pour voir tout le dessin.

Option B - Lecteur DXF gratuit :
  - DWG TrueView (Autodesk, gratuit) :
    https://www.autodesk.com/products/dwg
  - LibreCAD (open source, gratuit)
  - Ouvrez le fichier .dxf avec l'un de ces logiciels.

Le dessin contient deux vues :
  - Vue longitudinale (elevation)
  - Coupe transversale


--------------------------------------------------------
6. QUELLES SONT LES LIMITES DU PROGRAMME
--------------------------------------------------------

Ce programme est un OUTIL PEDAGOGIQUE SIMPLIFIE.
Il ne remplace pas une note de calcul professionnelle.

Limites techniques :
  - Calcul simplifie a l'ELU uniquement
    (pas de verification ELS, ni fleche)
  - Poutre simplement appuyee avec charge uniformement
    repartie uniquement (pas de charge ponctuelle)
  - Section rectangulaire uniquement (pas de T, L, I)
  - Pas de gestion automatique de 2 lits d'armatures
  - Pas de verification de l'effort tranchant detaille
    selon Eurocode 2 (approche simplifiee)
  - Les cadres du poteau sont estimes (scl,max)
    sans calcul detaille de l'effort tranchant
  - Le poids propre de la poutre doit etre inclus
    manuellement dans la charge G
  - Poteau : calcul simplifie sans effets du second
    ordre (pas de prise en compte de la flambement
    detaillee selon EN 1992-1-1)

Limites du dessin DXF :
  - Le dessin est genere a l'echelle 1:1 en mm
  - Les armatures sont representees de facon
    schematique (pas de crochets ni de facades reels)



--------------------------------------------------------
FICHIERS DU PROJET
--------------------------------------------------------

main.py          -> Programme principal (lancement)
calcul_poutre.py -> Calculs Eurocode 2 pour la poutre
calcul_poteau.py -> Calculs Eurocode 2 pour le poteau
dessin_dxf.py    -> Generation automatique DXF
interface.py     -> Interface graphique (tkinter)
export_excel.py  -> Export des resultats en Excel
README.txt       -> Ce fichier


--------------------------------------------------------
DONNEES D'EXEMPLE OBLIGATOIRES (sujet)
--------------------------------------------------------

  b = 300 mm, h = 500 mm, L = 5 m
  G = 18 kN/m, Q = 12 kN/m
  fck = 25 MPa (C25/30), fyk = 500 MPa (B500B)
  cnom = 30 mm

Resultats attendus :
  qEd = 42.30 kN/m
  MEd = 132.19 kN.m
  VEd = 105.75 kN
  d = 454 mm, z = 409 mm
  As necessaire ~ 741 mm2
  Solution : 4 HA16 (As = 804 mm2)
  Etrierss : HA8 / 15 cm


========================================================
  Enseignants : Mme Rana AL ALI / M. Abdenour KHEZZANE
  Annee universitaire : 2025-2026
========================================================
