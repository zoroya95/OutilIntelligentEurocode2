import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from calcul_poteau import lancer_page_poteau
from calcul_poutre import calculer_poutre, betons, aciers

from export_excel import exporter_resultats


def ouvrir_poteau(fenetre):
    fenetre.destroy()
    lancer_page_poteau(lancer_application)

def ouvrir_poutre(fenetre):
    fenetre.destroy()

    page = tk.Tk()
    page.title("Dimensionnement d'une poutre en béton armé")
    page.geometry("800x800")

    frame_entree = ttk.LabelFrame(page, text="Données d'entrée")
    frame_entree.pack(fill="x", padx=10, pady=10)

    ttk.Label(frame_entree, text="Longueur L (m) :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    entry_L = ttk.Entry(frame_entree)
    entry_L.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Hauteur h (m) :").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    entry_h = ttk.Entry(frame_entree)
    entry_h.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Largeur b (m) :").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    entry_b = ttk.Entry(frame_entree)
    entry_b.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Charge permanente G (kN/m) :").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    entry_G = ttk.Entry(frame_entree)
    entry_G.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Charge d'exploitation Q (kN/m) :").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    entry_Q = ttk.Entry(frame_entree)
    entry_Q.grid(row=4, column=1, padx=5, pady=5)

    ttk.Label(frame_entree, text="Classe de béton :").grid(row=5, column=0, sticky="w", padx=5, pady=5)
    combo_beton = ttk.Combobox(frame_entree, values=list(betons.keys()), state="readonly")
    combo_beton.grid(row=5, column=1, padx=5, pady=5)
    combo_beton.current(1)

    ttk.Label(frame_entree, text="Classe d'acier :").grid(row=6, column=0, sticky="w", padx=5, pady=5)
    combo_acier = ttk.Combobox(frame_entree, values=list(aciers.keys()), state="readonly")
    combo_acier.grid(row=6, column=1, padx=5, pady=5)
    combo_acier.current(1)

    ttk.Label(frame_entree, text="Diamètre des barres HA (mm) :").grid(row=7, column=0, sticky="w", padx=5, pady=5)
    combo_diametre = ttk.Combobox(frame_entree, values=[8, 10, 12, 14, 16, 20, 25, 32], state="readonly")
    combo_diametre.grid(row=7, column=1, padx=5, pady=5)
    combo_diametre.current(2)

    frame_actions = ttk.LabelFrame(page, text="Actions")
    frame_actions.pack(fill="x", padx=10, pady=10)

    frame_resultats = ttk.LabelFrame(page, text="Résultats")
    frame_resultats.pack(fill="both", expand=True, padx=10, pady=10)

    text_resultats = tk.Text(frame_resultats, wrap="word", font=("Arial", 10), height=18)
    scrollbar = ttk.Scrollbar(frame_resultats, orient="vertical", command=text_resultats.yview)
    text_resultats.configure(yscrollcommand=scrollbar.set)

    text_resultats.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")

    dernier_resultat = {}

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

    def retour():
        page.destroy()
        lancer_application()
        
    def calculer():
        try:
            resultat = calculer_poutre(
                L=float(entry_L.get()),
                h=float(entry_h.get()),
                b=float(entry_b.get()),
                G=float(entry_G.get()),
                Q=float(entry_Q.get()),
                classe_beton=combo_beton.get(),
                classe_acier=combo_acier.get(),
                diametre=int(combo_diametre.get())
            )

            dernier_resultat.clear()
            dernier_resultat.update(resultat)

            if resultat["statut"] == "NON OK":
                texte = (
                    f"RÉSULTAT : NON OK\n\n"
                    f"{resultat['message']}\n\n"
                )
            else:
                texte = (
                    f"RÉSULTAT : OK\n\n"
                    f"Longueur L = {resultat['L']} m\n"
                    f"Hauteur h = {resultat['h']} m\n"
                    f"Largeur b = {resultat['b']} m\n\n"

                    f"q_Ed = 1.35G + 1.50Q = {resultat['q_Ed']:.2f} kN/m\n"
                    f"M_Ed = q_Ed × L² / 8 = {resultat['M_Ed']:.2f} kN.m\n\n"

                    f"d = {resultat['d']:.3f} m\n"
                    f"z = 0.9d = {resultat['z']:.3f} m\n\n"

                    f"fcd = {resultat['fcd']:.2f} MPa\n"
                    f"fyd = {resultat['fyd']:.2f} MPa\n"
                    f"fctm = {resultat['fctm']:.2f} MPa\n\n"

                    f"μ = {resultat['mu']:.4f}\n"
                    f"μmax = {resultat['mu_max']:.4f}\n\n"

                    f"As_calc = {resultat['As_calc']:.2f} mm²\n"
                    f"As_min = {resultat['As_min']:.2f} mm²\n"
                    f"As_max = {resultat['As_max']:.2f} mm²\n"
                    f"As_req = {resultat['As_req']:.2f} mm²\n\n"

                    f"Diamètre choisi : HA{resultat['diametre']}\n"
                    f"Aire d'une barre = {resultat['aire_barre']:.2f} mm²\n"
                    f"Nombre de barres = {resultat['nb_barres']}\n"
                    f"As_fournie = {resultat['As_fournie']:.2f} mm²\n\n"

                    f"{resultat['message']}"
                )

            text_resultats.delete("1.0", tk.END)
            text_resultats.insert(tk.END, texte)

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir des valeurs numériques valides.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

        

    def reinitialiser():
        entry_L.delete(0, tk.END)
        entry_h.delete(0, tk.END)
        entry_b.delete(0, tk.END)
        entry_G.delete(0, tk.END)
        entry_Q.delete(0, tk.END)
        combo_beton.current(1)
        combo_acier.current(1)
        combo_diametre.current(2)
        text_resultats.delete("1.0", tk.END)

    ttk.Button(
        frame_actions, 
        text="Calculer", 
        command=calculer
        ).pack(side="left", padx=10, pady=10)
    
    ttk.Button(
        frame_actions, 
        text="Réinitialiser", 
        command=reinitialiser
        ).pack(side="left", padx=10, pady=10)
    
    ttk.Button(
        frame_actions, 
        text="Retour accueil", 
        command=retour
        ).pack(side="left", padx=10, pady=10)
    
    ttk.Button(
        frame_actions,
        text="Exporter Excel",
        command=enregistrer_excel
        ).pack(side="left", padx=10, pady=10)
    
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
