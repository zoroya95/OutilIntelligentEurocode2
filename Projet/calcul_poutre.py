import math

betons = {
    "C20/25": {"fck": 20},
    "C25/30": {"fck": 25},
    "C30/37": {"fck": 30},
    "C35/45": {"fck": 35},
    "C40/50": {"fck": 40},
    "C50/60": {"fck": 50},
    "C55/67": {"fck": 55},
    "C60/75": {"fck": 60}
}

aciers = {
    "B400":  {"fyk": 400},
    "B500B": {"fyk": 500}
}

PHI_ETRIER = 8
ESPACEMENTS_ETRIERS = [100, 150, 200, 250]


def calculer_poutre(L, h, b, G, Q, classe_beton, classe_acier, diametre, cnom=30):
    """
    L     : portée en m
    h, b  : dimensions section en mm
    G, Q  : charges linéiques en kN/m
    cnom  : enrobage nominal en mm
    diametre : diamètre barres longitudinales en mm
    """
    fck = betons[classe_beton]["fck"]
    fyk = aciers[classe_acier]["fyk"]

    # 1. Combinaison ELU
    qEd = 1.35 * G + 1.50 * Q          # kN/m

    # 2. Efforts internes
    MEd = qEd * L**2 / 8               # kN.m
    VEd = qEd * L / 2                  # kN

    # 3. Résistances matériaux
    fcd = fck / 1.5                    # MPa
    fyd = fyk / 1.15                   # MPa

    # 4. Hauteur utile (mm)
    d = h - cnom - PHI_ETRIER - diametre / 2
    if d <= 0:
        return {
            "statut": "NON OK",
            "message": f"Erreur : hauteur utile d = {d:.1f} mm <= 0. Augmentez h ou réduisez l'enrobage."
        }

    # 5. Bras de levier (mm)
    z = 0.9 * d

    # 6. Moment réduit (vérification résistance béton comprimé)
    mu = (MEd * 1e6) / (b * d**2 * fcd)
    mu_max = 0.45
    if mu > mu_max:
        return {
            "statut": "NON OK",
            "message": (f"mu = {mu:.4f} > mu_max = {mu_max} : "
                        f"augmentez les dimensions ou la classe de béton."),
            "mu": mu,
            "mu_max": mu_max
        }

    # 7. Section d'acier longitudinale
    # MEd * 1e6 : kN.m -> N.mm ; z en mm ; fyd en N/mm²
    As_flexion = (MEd * 1e6) / (z * fyd)

    fctm     = 0.30 * fck**(2.0 / 3.0)
    As_min_1 = 0.26 * fctm / fyk * b * d
    As_min_2 = 0.0013 * b * d
    As_min   = max(As_min_1, As_min_2)
    As_req   = max(As_flexion, As_min)

    As_max = 0.04 * b * h
    if As_req > As_max:
        return {
            "statut": "NON OK",
            "message": (f"As_req = {As_req:.0f} mm² > As_max = {As_max:.0f} mm². "
                        f"Augmentez la section ou la classe de béton.")
        }

    # 8. Choix automatique des barres
    aire_barre = math.pi * diametre**2 / 4
    nb_barres  = math.ceil(As_req / aire_barre)
    As_adoptee = nb_barres * aire_barre

    # 9. Vérification espacement entre barres dans la largeur
    b_int = b - 2 * (cnom + PHI_ETRIER)
    if nb_barres > 1:
        e_barres = (b_int - nb_barres * diametre) / (nb_barres - 1)
    else:
        e_barres = b_int - diametre
    espacement_ok = e_barres >= max(20.0, float(diametre))

    # 10. Armatures transversales HA8
    Asw    = 2 * math.pi * PHI_ETRIER**2 / 4   # mm² (2 branches)
    VEd_N  = VEd * 1000                          # kN -> N
    s_calc = (Asw * z * fyd) / VEd_N            # mm
    smax   = min(0.75 * d, 300.0)               # mm

    s_adopte = None
    for s in sorted(ESPACEMENTS_ETRIERS):
        if s <= s_calc and s <= smax:
            s_adopte = s
    if s_adopte is None:
        s_adopte = ESPACEMENTS_ETRIERS[0]

    return {
        "statut":        "OK",
        "L":             L,
        "h":             h,
        "b":             b,
        "cnom":          cnom,
        "qEd":           qEd,
        "MEd":           MEd,
        "VEd":           VEd,
        "fcd":           fcd,
        "fyd":           fyd,
        "fctm":          fctm,
        "mu":            mu,
        "mu_max":        mu_max,
        "d":             d,
        "z":             z,
        "As_flexion":    As_flexion,
        "As_min":        As_min,
        "As_max":        As_max,
        "As_req":        As_req,
        "diametre":      diametre,
        "aire_barre":    aire_barre,
        "nb_barres":     nb_barres,
        "As_adoptee":    As_adoptee,
        "b_int":         b_int,
        "e_barres":      e_barres,
        "espacement_ok": espacement_ok,
        "Asw":           Asw,
        "s_calc":        s_calc,
        "smax":          smax,
        "s_etrier":      s_adopte,
        "phi_etrier":    PHI_ETRIER,
        "message":       "La poutre est vérifiée."
    }
