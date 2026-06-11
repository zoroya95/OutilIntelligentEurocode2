import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from export_excel import exporter_resultats
import math


# -----------------------------
# Données matériaux
# -----------------------------

betons = {
    "C20/25": {"fck": 20},
    "C25/30": {"fck": 25},
    "C30/37": {"fck": 30},
    "C35/45": {"fck": 35},
    "C40/50": {"fck": 40},
    "C45/55": {"fck": 45},
    "C50/60": {"fck": 50},
    "C55/67": {"fck": 55},
    "C60/75": {"fck": 60},
    "C70/85": {"fck": 70},
    "C80/95": {"fck": 80},
    "C90/105": {"fck": 90}
}

aciers = {
    "B400": {"fyk": 400},
    "B500B": {"fyk": 500}
}

diametres = [8, 10, 12, 14, 16, 20, 25, 32]


def lancer_page_poteau(retour_accueil=None):

    dernier_resultat = {}

    def calculer():
        type_section = combo_section.get()
        try:
            # Récupération des valeurs numériques
            b = float(entry_b.get())
            h = float(entry_h.get())
            H = float(entry_H.get())
            NG = float(entry_NG.get())
            NQ = float(entry_NQ.get())

        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Veuillez saisir des valeurs numériques valides pour b, h, H, NG et NQ."
            )
            return

        # Récupération des listes déroulantes
        classe_beton = combo_beton.get()
        classe_acier = combo_acier.get()
        diametre_texte = combo_diametre.get()

        # Vérification des listes déroulantes
        if classe_beton == "":
            messagebox.showerror("Erreur", "Veuillez choisir une classe de béton.")
            return

        if classe_acier == "":
            messagebox.showerror("Erreur", "Veuillez choisir une classe d'acier.")
            return

        if diametre_texte == "":
            messagebox.showerror("Erreur", "Veuillez choisir un diamètre de barre.")
            return

        try:
            diametre = int(diametre_texte)
        except ValueError:
            messagebox.showerror("Erreur", "Le diamètre choisi n'est pas valide.")
            return

        # Vérification des valeurs
        if b <= 0 or h <= 0 or H <= 0:
            messagebox.showerror(
                "Erreur",
                "Les dimensions b, h et H doivent être strictement positives."
            )
            return

        if NG < 0 or NQ < 0:
            messagebox.showerror(
                "Erreur",
                "Les charges NG et NQ ne doivent pas être négatives."
            )
            return
        
            # Vérification géométrique du poteau
        grand_cote = max(b, h)
        petit_cote = min(b, h)

        if petit_cote < grand_cote / 4 or H < 3 * grand_cote:
            messagebox.showerror(
                "Erreur",
                "Les dimensions ne permettent pas de considérer l'élément comme un poteau.\n"
                "Il faut vérifier : b ≥ h/4 et H ≥ 3h."
            )
            return

        # -----------------------------
        # Calculs
        # -----------------------------

        fck = betons[classe_beton]["fck"]
        fyk = aciers[classe_acier]["fyk"]

        if type_section == "Rectangulaire":
            b_mm = b * 1000
            h_mm = h * 1000
            Ac = b_mm * h_mm

            grand_cote = max(b, h)
            petit_cote = min(b, h)

            if petit_cote < grand_cote / 4 or H < 3 * grand_cote:
                messagebox.showerror(
                    "Erreur",
                    "Les dimensions ne permettent pas de considérer l'élément comme un poteau rectangulaire."
                )
                return

            i_min = petit_cote / math.sqrt(12)

        else:
            a = b
            a_mm = a * 1000

            Ac = math.pi * a_mm**2 / 4
            i_min = a / 4

            b_mm = a_mm
            h_mm = a_mm

            petit_cote = a
            grand_cote = a

        # Étape 4 : élancement
        lambd = H / i_min

        # Étape 5 : effort normal de calcul
        NEd = 1.35 * NG + 1.50 * NQ

        # Étape 6 : résistance béton
        fcd = fck / 1.50

        # Étape 7 : résistance acier
        fyd = fyk / 1.15

        # Étape 8 : résistance béton seul
        # Coefficient eta
        if fck <= 50:
            eta = 1.0
        else:
            eta = 1.0 - ((fck - 50) / 200)

        # Coefficient lambda
        if fck <= 50:
            lambda_beton = 0.8
        else:
            lambda_beton = 0.8 - ((fck - 50) / 400)

        # Résistance béton avec eta et lambda
        NcRd = eta * lambda_beton * fcd * Ac / 1000

        # Étape 9 : section d'acier calculée
        if NEd > NcRd:
            As_calc = (NEd - NcRd) * 1000 / fyd
        else:
            As_calc = 0

        # Étape 10 : section minimale
        As_min = 0.0034 * Ac

        # Étape 11 : section requise
        As_req = max(As_calc, As_min)

        # Section maximale d'acier
        As_max = 0.04 * Ac

        if As_req > As_max:
            messagebox.showerror(
                "Erreur",
                "La section d'acier requise dépasse As_max = 0.04 × Ac.\n"
                "Il faut augmenter les dimensions du poteau ou la classe de béton."
            )
            return

        # Étape 12 : choix des barres
        aire_barre = math.pi * diametre**2 / 4
        nb_barres = math.ceil(As_req / aire_barre)
        As_fournie = nb_barres * aire_barre

            # Armatures transversales
        phi_long_max = diametre
        phi_long_min = diametre

        diametre_transversal_min = max(6, phi_long_max / 4)

        b_mm_petit = petit_cote * 1000
        scl_max = min(20 * phi_long_min, b_mm_petit, 400)


        # Étape 13 : vérification finale
        NRd = (0.85 * fcd * Ac + As_fournie * fyd) / 1000

        if NRd >= NEd:
            verification = "OK : N_Rd ≥ N_Ed, le poteau est vérifié."
        else:
            verification = "NON OK : N_Rd < N_Ed, le poteau n'est pas vérifié."

        # Affichage des résultats
        if type_section == "Rectangulaire":
            texte_i = f"i_min = dimension_min / √12 = {i_min:.3f} m"
        else:
            texte_i = f"i = a / 4 = {i_min:.3f} m"

        texte = (
            f"ÉTAPE 1 : Conversion des dimensions\n"
            f"b = {b_mm:.0f} mm\n"
            f"h = {h_mm:.0f} mm\n\n"

            f"ÉTAPE 2 : Aire de béton\n"
            f"Ac = b × h = {Ac:.0f} mm²\n\n"

            f"ÉTAPE 3 : Rayon de giration minimal\n"
            f"{texte_i}\n\n"

            f"ÉTAPE 4 : Élancement\n"
            f"λ = H / i_min = {lambd:.1f}\n\n"

            f"ÉTAPE 5 : Effort normal de calcul\n"
            f"N_Ed = 1.35 NG + 1.50 NQ = {NEd:.2f} kN\n\n"

            f"ÉTAPE 6 : Résistance de calcul du béton\n"
            f"fcd = fck / 1.50 = {fcd:.2f} N/mm²\n\n"

            f"ÉTAPE 7 : Résistance de calcul de l'acier\n"
            f"fyd = fyk / 1.15 = {fyd:.2f} N/mm²\n\n"

            f"ÉTAPE 8 : Résistance du béton seul\n"
            f"η = {eta:.3f}\n"
            f"λ béton = {lambda_beton:.3f}\n"
            f"Nc,Rd = η × λ × fcd × Ac = {NcRd:.2f} kN\n\n"

            f"ÉTAPE 9 : Section d'acier calculée\n"
            f"As_calc = {As_calc:.2f} mm²\n\n"

            f"ÉTAPE 10 : Section minimale/maximale\n"
            f"As_min = {As_min:.2f} mm²\n\n"
            f"As_max = 0.04 × Ac = {As_max:.2f} mm²\n\n"

            f"ÉTAPE 11 : Section requise\n"
            f"As_req = max(As_calc ; As_min) = {As_req:.2f} mm²\n\n"

            f"ARMATURES TRANSVERSALES\n"
            f"Diamètre minimal des cadres = max(6 ; φlong/4) = {diametre_transversal_min:.2f} mm\n"
            f"Espacement maximal scl,max = min(20φlong ; b ; 400) = {scl_max:.2f} mm\n\n"

            f"ÉTAPE 12 : Choix des barres\n"
            f"Diamètre choisi : HA{diametre}\n"
            f"Aire d'une barre = {aire_barre:.2f} mm²\n"
            f"Nombre de barres = {nb_barres}\n"
            f"As_fournie = {As_fournie:.2f} mm²\n\n"

            f"ÉTAPE 13 : Vérification finale\n"
            f"N_Rd = {NRd:.2f} kN\n"
            f"N_Ed = {NEd:.2f} kN\n"
            f"{verification}"
        )

        dernier_resultat.clear()
        dernier_resultat.update({
            "statut":                 "OK",
            "type_section":           type_section,
            "b_mm":                   b_mm,
            "h_mm":                   h_mm,
            "H":                      H,
            "NEd":                    NEd,
            "fcd":                    fcd,
            "fyd":                    fyd,
            "Ac":                     Ac,
            "nb_barres":              nb_barres,
            "diametre":               diametre,
            "As_fournie":             As_fournie,
            "As_req":                 As_req,
            "As_min":                 As_min,
            "As_max":                 As_max,
            "NRd":                    NRd,
            "diametre_transversal_min": diametre_transversal_min,
            "scl_max":                scl_max,
        })

        text_resultats.delete(1.0, tk.END)
        text_resultats.insert(tk.END, texte)




    # -----------------------------
    # Fonction réinitialiser
    # -----------------------------

    def enregistrer_excel():

        if not dernier_resultat:
            messagebox.showerror(
                "Erreur",
                "Aucun résultat à exporter. Veuillez d'abord effectuer un calcul."
            )
            return

        fichier = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Fichier Excel", "*.xlsx")],
            title="Exporter les résultats"
        )

        if fichier:
            exporter_resultats(
                dernier_resultat,
                "Résultats poteau",
                fichier
            )

            messagebox.showinfo(
                "Succès",
                "Résultats exportés dans le fichier Excel."
            )

    def reinitialiser():
        entry_b.delete(0, tk.END)
        entry_h.delete(0, tk.END)
        entry_H.delete(0, tk.END)
        entry_NG.delete(0, tk.END)
        entry_NQ.delete(0, tk.END)

        combo_beton.current(1)      # C25/30
        combo_acier.current(1)      # B500B
        combo_diametre.current(1)   # HA10

        text_resultats.delete("1.0", tk.END)
        # -----------------------------
    # Fenêtre principale
    # -----------------------------

    fenetre = tk.Tk()
    fenetre.title("Dimensionnement d'un poteau en béton armé")
    fenetre.geometry("800x800")


    # -----------------------------
    # Bloc données d'entrée
    # -----------------------------

    frame_entree = ttk.LabelFrame(fenetre, text="Données d'entrée")
    frame_entree.pack(fill="x", padx=10, pady=10)


    # -----------------------------
    # Zone géométrie
    # -----------------------------

    ttk.Label(frame_entree, text="Type de section :").grid(row=1, column=0, sticky="w", padx=5, pady=5)

    combo_section = ttk.Combobox(
        frame_entree,
        values=["Rectangulaire", "Circulaire"],
        state="readonly"
    )
    combo_section.grid(row=1, column=1, padx=5, pady=5)
    combo_section.current(0)

    ttk.Label(frame_entree, text="Largeur b / diametre a (m) :").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_b = ttk.Entry(frame_entree)
    entry_b.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Hauteur h (m) :").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_h = ttk.Entry(frame_entree)
    entry_h.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Hauteur du poteau H (m) :").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    entry_H = ttk.Entry(frame_entree)
    entry_H.grid(row=4, column=1, padx=5, pady=5)


    # -----------------------------
    # Zone matériaux
    # -----------------------------

    ttk.Label(
        frame_entree,
        text="Matériaux",
        font=("Arial", 10, "bold")
    ).grid(row=5, column=0, columnspan=2, pady=5)

    ttk.Label(frame_entree, text="Classe de béton :").grid(row=6, column=0, sticky="w", padx=5, pady=5)
    combo_beton = ttk.Combobox(frame_entree, values=list(betons.keys()), state="readonly")
    combo_beton.grid(row=6, column=1, padx=5, pady=5)
    combo_beton.current(1)

    ttk.Label(frame_entree, text="Classe d'acier :").grid(row=7, column=0, sticky="w", padx=5, pady=5)
    combo_acier = ttk.Combobox(frame_entree, values=list(aciers.keys()), state="readonly")
    combo_acier.grid(row=7, column=1, padx=5, pady=5)
    combo_acier.current(1)


    # -----------------------------
    # Zone chargements
    # -----------------------------

    ttk.Label(
        frame_entree,
        text="Chargements",
        font=("Arial", 10, "bold")
    ).grid(row=8, column=0, columnspan=2, pady=5)

    ttk.Label(frame_entree, text="Charge permanente NG (kN) :").grid(row=9, column=0, sticky="w", padx=5, pady=5)
    entry_NG = ttk.Entry(frame_entree)
    entry_NG.grid(row=9, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Charge d'exploitation NQ (kN) :").grid(row=10, column=0, sticky="w", padx=5, pady=5)
    entry_NQ = ttk.Entry(frame_entree)
    entry_NQ.grid(row=10, column=1, padx=5, pady=5)


    # -----------------------------
    # Zone choix des barres
    # -----------------------------

    ttk.Label(frame_entree, text="Diamètre des barres HA (mm) :").grid(row=11, column=0, sticky="w", padx=5, pady=5)

    combo_diametre = ttk.Combobox(frame_entree, values=diametres, state="readonly")
    combo_diametre.grid(row=11, column=1, padx=5, pady=5)
    combo_diametre.current(1)


    # -----------------------------
    # Bloc actions
    # -----------------------------

    frame_actions = ttk.LabelFrame(fenetre, text="Actions")
    frame_actions.pack(fill="x", padx=10, pady=10)

    btn_calculer = ttk.Button(frame_actions, text="Calculer", command=calculer)
    btn_calculer.pack(side="left", padx=10, pady=10)

    btn_reset = ttk.Button(frame_actions, text="Réinitialiser", command=reinitialiser)
    btn_reset.pack(side="left", padx=10, pady=10)

    btn_export = ttk.Button(
    frame_actions,
    text="Exporter Excel",
    command=enregistrer_excel
    )

    btn_export.pack(side="left", padx=10, pady=10)


    # -----------------------------
    # Bloc résultats
    # -----------------------------

    frame_resultats = ttk.LabelFrame(fenetre, text="Résultats")
    frame_resultats.pack(fill="both", expand=True, padx=10, pady=10)

    text_resultats = tk.Text(
        frame_resultats,
        wrap="word",
        font=("Arial", 10),
        height=18
    )

    scrollbar = ttk.Scrollbar(
        frame_resultats,
        orient="vertical",
        command=text_resultats.yview
    )

    text_resultats.configure(yscrollcommand=scrollbar.set)

    text_resultats.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    def generer_dxf():
        if not dernier_resultat or dernier_resultat.get("statut") != "OK":
            messagebox.showwarning("Attention", "Veuillez d'abord effectuer un calcul valide.")
            return

        from tkinter import simpledialog
        groupe = simpledialog.askinteger(
            "Numéro du groupe", "Entrez le numéro du groupe :",
            initialvalue=1, minvalue=1, maxvalue=99
        )
        if groupe is None:
            return

        nom_defaut = f"poteau_BA_groupe_{groupe:02d}.dxf"
        nom_fichier = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("Fichier DXF", "*.dxf"), ("Tous les fichiers", "*.*")],
            initialfile=nom_defaut,
            title="Enregistrer le dessin DXF"
        )
        if not nom_fichier:
            return

        from dessin_dxf import generer_dessin_poteau
        fichier, erreur = generer_dessin_poteau(dernier_resultat, groupe=groupe, nom_fichier=nom_fichier)

        if erreur:
            messagebox.showerror("Erreur DXF", erreur)
        else:
            messagebox.showinfo("Succès", f"Fichier DXF généré :\n{fichier}")

    def retour():
        fenetre.destroy()

        if retour_accueil:
            retour_accueil()

    btn_generer_dxf = ttk.Button(
        frame_actions,
        text="Générer DXF",
        command=generer_dxf
    )
    btn_generer_dxf.pack(side="left", padx=10, pady=10)

    btn_retour = ttk.Button(
        frame_actions,
        text="Retour accueil",
        command=retour
    )

    btn_retour.pack(side="left", padx=10, pady=10)
    fenetre.mainloop()
