import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from calcul_poteau import lancer_page_poteau
from calcul_poutre import calculer_poutre, betons, aciers

from export_excel import exporter_resultats
from dessin_dxf import generer_dessin_poutre


def ouvrir_poteau(fenetre):
    fenetre.destroy()
    lancer_page_poteau(lancer_application)

def ouvrir_poutre(fenetre):
    fenetre.destroy()

    page = tk.Tk()
    page.title("Dimensionnement d'une poutre en béton armé")
    page.geometry("850x900")

    frame_entree = ttk.LabelFrame(page, text="Données d'entrée")
    frame_entree.pack(fill="x", padx=10, pady=10)

    ttk.Label(frame_entree, text="Longueur L (m) :").grid(row=0, column=0, sticky="w", padx=5, pady=4)
    entry_L = ttk.Entry(frame_entree)
    entry_L.grid(row=0, column=1, padx=5, pady=4)

    ttk.Label(frame_entree, text="Hauteur h (mm) :").grid(row=1, column=0, sticky="w", padx=5, pady=4)
    entry_h = ttk.Entry(frame_entree)
    entry_h.grid(row=1, column=1, padx=5, pady=4)

    ttk.Label(frame_entree, text="Largeur b (mm) :").grid(row=2, column=0, sticky="w", padx=5, pady=4)
    entry_b = ttk.Entry(frame_entree)
    entry_b.grid(row=2, column=1, padx=5, pady=4)

    ttk.Label(frame_entree, text="Charge permanente G (kN/m) :").grid(row=3, column=0, sticky="w", padx=5, pady=4)
    entry_G = ttk.Entry(frame_entree)
    entry_G.grid(row=3, column=1, padx=5, pady=4)

    ttk.Label(frame_entree, text="Charge d'exploitation Q (kN/m) :").grid(row=4, column=0, sticky="w", padx=5, pady=4)
    entry_Q = ttk.Entry(frame_entree)
    entry_Q.grid(row=4, column=1, padx=5, pady=4)

    ttk.Label(frame_entree, text="Enrobage nominal cnom (mm) :").grid(row=5, column=0, sticky="w", padx=5, pady=4)
    entry_cnom = ttk.Entry(frame_entree)
    entry_cnom.insert(0, "30")
    entry_cnom.grid(row=5, column=1, padx=5, pady=4)

    ttk.Label(frame_entree, text="Classe de béton :").grid(row=6, column=0, sticky="w", padx=5, pady=4)
    combo_beton = ttk.Combobox(frame_entree, values=list(betons.keys()), state="readonly")
    combo_beton.grid(row=6, column=1, padx=5, pady=4)
    combo_beton.current(1)

    ttk.Label(frame_entree, text="Classe d'acier :").grid(row=7, column=0, sticky="w", padx=5, pady=4)
    combo_acier = ttk.Combobox(frame_entree, values=list(aciers.keys()), state="readonly")
    combo_acier.grid(row=7, column=1, padx=5, pady=4)
    combo_acier.current(1)

    ttk.Label(frame_entree, text="Diamètre des barres HA (mm) :").grid(row=8, column=0, sticky="w", padx=5, pady=4)
    combo_diametre = ttk.Combobox(frame_entree, values=[10, 12, 14, 16, 20, 25], state="readonly")
    combo_diametre.grid(row=8, column=1, padx=5, pady=4)
    combo_diametre.current(3)

    ttk.Label(frame_entree, text="Numéro du groupe :").grid(row=9, column=0, sticky="w", padx=5, pady=4)
    entry_groupe = ttk.Entry(frame_entree)
    entry_groupe.insert(0, "1")
    entry_groupe.grid(row=9, column=1, padx=5, pady=4)

    frame_actions = ttk.LabelFrame(page, text="Actions")
    frame_actions.pack(fill="x", padx=10, pady=10)

    frame_resultats = ttk.LabelFrame(page, text="Résultats")
    frame_resultats.pack(fill="both", expand=True, padx=10, pady=10)

    text_resultats = tk.Text(frame_resultats, wrap="word", font=("Courier", 9), height=20)
    scrollbar = ttk.Scrollbar(frame_resultats, orient="vertical", command=text_resultats.yview)
    text_resultats.configure(yscrollcommand=scrollbar.set)
    text_resultats.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")

    dernier_resultat = {}

    # ------------------------------------------------------------------
    def calculer():
        try:
            L    = float(entry_L.get())
            h    = float(entry_h.get())
            b    = float(entry_b.get())
            G    = float(entry_G.get())
            Q    = float(entry_Q.get())
            cnom = float(entry_cnom.get())
            dia  = int(combo_diametre.get())

            if b <= 0:
                raise ValueError("Erreur : la largeur b doit être positive.")
            if h <= 0:
                raise ValueError("Erreur : la hauteur h doit être positive.")
            if L <= 0:
                raise ValueError("Erreur : la portée L doit être supérieure à 0.")
            if G < 0:
                raise ValueError("Erreur : la charge G doit être positive ou nulle.")
            if Q < 0:
                raise ValueError("Erreur : la charge Q doit être positive ou nulle.")
            if cnom <= 0:
                raise ValueError("Erreur : l'enrobage doit être positif.")

            resultat = calculer_poutre(
                L=L, h=h, b=b, G=G, Q=Q,
                classe_beton=combo_beton.get(),
                classe_acier=combo_acier.get(),
                diametre=dia,
                cnom=cnom
            )

            dernier_resultat.clear()
            dernier_resultat.update(resultat)

            if resultat["statut"] == "NON OK":
                texte = f"RÉSULTAT : NON OK\n\n{resultat['message']}\n"
            else:
                r = resultat
                ver_as   = "OK" if r["As_adoptee"] >= r["As_req"] else "NON OK"
                ver_esp  = "OK" if r["espacement_ok"] else "ATTENTION : espacement insuffisant"
                texte = (
                    "=" * 50 + "\n"
                    "   DIMENSIONNEMENT D'UNE POUTRE BA\n"
                    "=" * 50 + "\n\n"

                    "DONNÉES D'ENTRÉE\n"
                    f"  b    = {r['b']:.0f} mm\n"
                    f"  h    = {r['h']:.0f} mm\n"
                    f"  L    = {r['L']:.2f} m\n"
                    f"  G    = {G:.2f} kN/m\n"
                    f"  Q    = {Q:.2f} kN/m\n"
                    f"  cnom = {r['cnom']:.0f} mm\n\n"

                    "CHARGES\n"
                    f"  qEd = 1,35G + 1,50Q = {r['qEd']:.2f} kN/m\n\n"

                    "EFFORTS INTERNES\n"
                    f"  MEd = qEd × L² / 8 = {r['MEd']:.2f} kN.m\n"
                    f"  VEd = qEd × L / 2  = {r['VEd']:.2f} kN\n\n"

                    "MATÉRIAUX\n"
                    f"  fcd  = {r['fcd']:.2f} MPa\n"
                    f"  fyd  = {r['fyd']:.2f} MPa\n"
                    f"  fctm = {r['fctm']:.2f} MPa\n"
                    f"  μ    = {r['mu']:.4f}  (μmax = {r['mu_max']:.2f})\n\n"

                    "ARMATURES LONGITUDINALES\n"
                    f"  d            = {r['d']:.1f} mm\n"
                    f"  z            = {r['z']:.1f} mm\n"
                    f"  As,flexion   = {r['As_flexion']:.1f} mm²\n"
                    f"  As,minimum   = {r['As_min']:.1f} mm²\n"
                    f"  As,nécessaire= {r['As_req']:.1f} mm²\n"
                    f"  Solution     = {r['nb_barres']} HA{r['diametre']}\n"
                    f"  As,adoptée   = {r['As_adoptee']:.1f} mm²\n"
                    f"  Vérification : As,adoptée ≥ As,req → {ver_as}\n"
                    f"  Espacement entre barres = {r['e_barres']:.1f} mm → {ver_esp}\n\n"

                    "ARMATURES TRANSVERSALES\n"
                    f"  s calculé    = {r['s_calc']:.1f} mm\n"
                    f"  s max        = {r['smax']:.1f} mm\n"
                    f"  Étriers adoptés : HA8 / {r['s_etrier'] // 10:.0f} cm\n\n"

                    "DESSIN\n"
                    "  Cliquez sur [Générer DXF] pour créer le fichier AutoCAD.\n"
                )

            text_resultats.delete("1.0", tk.END)
            text_resultats.insert(tk.END, texte)

        except ValueError as e:
            messagebox.showerror("Erreur de saisie", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    # ------------------------------------------------------------------
    def generer_dxf():
        if not dernier_resultat or dernier_resultat.get("statut") != "OK":
            messagebox.showwarning("Attention", "Veuillez d'abord effectuer un calcul valide.")
            return

        try:
            groupe = int(entry_groupe.get())
        except ValueError:
            groupe = 1

        nom_defaut = f"poutre_BA_groupe_{groupe:02d}.dxf"
        nom_fichier = filedialog.asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("Fichier DXF", "*.dxf"), ("Tous les fichiers", "*.*")],
            initialfile=nom_defaut,
            title="Enregistrer le dessin DXF"
        )

        if not nom_fichier:
            return

        fichier, erreur = generer_dessin_poutre(dernier_resultat, groupe=groupe, nom_fichier=nom_fichier)

        if erreur:
            messagebox.showerror("Erreur DXF", erreur)
        else:
            messagebox.showinfo("Succès", f"Fichier DXF généré :\n{fichier}")

    # ------------------------------------------------------------------
    def enregistrer_excel():
        if not dernier_resultat:
            messagebox.showerror("Erreur", "Aucun résultat à exporter. Veuillez d'abord calculer.")
            return
        fichier = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Fichier Excel", "*.xlsx")],
            title="Exporter les résultats"
        )
        if fichier:
            exporter_resultats(dernier_resultat, "Résultats poutre", fichier)
            messagebox.showinfo("Succès", "Résultats exportés dans le fichier Excel.")

    # ------------------------------------------------------------------
    def reinitialiser():
        for entry in [entry_L, entry_h, entry_b, entry_G, entry_Q]:
            entry.delete(0, tk.END)
        entry_cnom.delete(0, tk.END)
        entry_cnom.insert(0, "30")
        entry_groupe.delete(0, tk.END)
        entry_groupe.insert(0, "1")
        combo_beton.current(1)
        combo_acier.current(1)
        combo_diametre.current(3)
        text_resultats.delete("1.0", tk.END)
        dernier_resultat.clear()

    def retour():
        page.destroy()
        lancer_application()

    # ------------------------------------------------------------------
    for txt, cmd in [
        ("Calculer",       calculer),
        ("Générer DXF",    generer_dxf),
        ("Exporter Excel", enregistrer_excel),
        ("Réinitialiser",  reinitialiser),
        ("Retour accueil", retour),
    ]:
        ttk.Button(frame_actions, text=txt, command=cmd).pack(side="left", padx=6, pady=10)

    page.mainloop()



def lancer_application():
    fenetre = tk.Tk()
    fenetre.title("Outil Intelligent Béton Armé")
    fenetre.geometry("500x300")

    ttk.Label(
        fenetre,
        text="Outil Intelligent Béton Armé",
        font=("Arial", 16, "bold")
    ).pack(pady=30)

    ttk.Button(
        fenetre,
        text="Dimensionner un poteau",
        command=lambda: ouvrir_poteau(fenetre)
    ).pack(pady=10)

    ttk.Button(
        fenetre,
        text="Dimensionner une poutre",
        command=lambda: ouvrir_poutre(fenetre)
    ).pack(pady=10)

    

    fenetre.mainloop()
