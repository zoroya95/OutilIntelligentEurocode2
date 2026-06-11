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
    "B400": {"fyk": 400},
    "B500B": {"fyk": 500}
}

def calculer_poutre(L, h, b, G, Q, classe_beton, classe_acier, diametre, enrobage=0.04):
    fck = betons[classe_beton]["fck"]
    fyk = aciers[classe_acier]["fyk"]

    # Hauteur utile
    d = h - enrobage

    # Charges
    q_Ed = 1.35 * G + 1.50 * Q

    # Moment max poutre simplement appuyée
    M_Ed = q_Ed * L**2 / 8

    # Résistances
    fcd = fck / 1.5
    fyd = fyk / 1.15

    # fctm selon séance 6
    if fck <= 50:
        fctm = 0.3 * fck ** (2 / 3)
    else:
        fctm = 2.12 * math.log(1 + fck / 10)

    # Moment réduit
    mu = M_Ed / (b * d**2 * fcd * 1000)

    mu_max = 0.45

    if mu > mu_max:
        return {
            "statut": "NON OK",
            "message": "μ > μmax : il faut augmenter les dimensions de la section ou la classe du béton.",
            "mu": mu,
            "mu_max": mu_max
        }

    # Bras de levier simplifié
    z = 0.9 * d

    # Section d'acier calculée
    As_calc = (M_Ed * 1e6) / (z * 1000 * fyd)

    # Section minimale
    As_min_1 = 0.26 * fctm / fyk * b * 1000 * d * 1000
    As_min_2 = 0.0013 * b * 1000 * d * 1000
    As_min = max(As_min_1, As_min_2)

    # Section requise
    As_req = max(As_calc, As_min)

    # Section maximale
    Ac = b * 1000 * h * 1000
    As_max = 0.04 * Ac

    if As_req > As_max:
        return {
            "statut": "NON OK",
            "message": "As > Asmax : il faut augmenter la section de béton ou la classe du béton.",
            "As_req": As_req,
            "As_max": As_max
        }

    # Choix des barres
    aire_barre = math.pi * diametre**2 / 4
    nb_barres = math.ceil(As_req / aire_barre)
    As_fournie = nb_barres * aire_barre

    return {
        "statut": "OK",
        "L": L,
        "h": h,
        "b": b,
        "d": d,
        "q_Ed": q_Ed,
        "M_Ed": M_Ed,
        "fcd": fcd,
        "fyd": fyd,
        "fctm": fctm,
        "mu": mu,
        "mu_max": mu_max,
        "z": z,
        "As_calc": As_calc,
        "As_min": As_min,
        "As_max": As_max,
        "As_req": As_req,
        "diametre": diametre,
        "aire_barre": aire_barre,
        "nb_barres": nb_barres,
        "As_fournie": As_fournie,
        "message": "La poutre est vérifiée."
    }

