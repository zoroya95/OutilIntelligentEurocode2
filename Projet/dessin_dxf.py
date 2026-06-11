import math

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
    EZDXF_OK = True
except ImportError:
    EZDXF_OK = False


# ---------------------------------------------------------------------------
# Helpers cotations
# ---------------------------------------------------------------------------

def _cotation_h(msp, x1, x2, y_ref, y_dim, texte, th, layer="COTATIONS"):
    """Cotation horizontale entre x1 et x2, ligne de cote à y_dim."""
    tick = th * 0.5
    msp.add_line((x1, y_ref), (x1, y_dim - tick), dxfattribs={"layer": layer})
    msp.add_line((x2, y_ref), (x2, y_dim - tick), dxfattribs={"layer": layer})
    msp.add_line((x1, y_dim), (x2, y_dim), dxfattribs={"layer": layer})
    # Flèches
    for xf, sens in [(x1, +1), (x2, -1)]:
        msp.add_line((xf, y_dim), (xf + sens * tick * 2, y_dim + tick), dxfattribs={"layer": layer})
        msp.add_line((xf, y_dim), (xf + sens * tick * 2, y_dim - tick), dxfattribs={"layer": layer})
    t = msp.add_text(texte, dxfattribs={"height": th, "layer": layer})
    t.set_placement(((x1 + x2) / 2, y_dim - th * 1.8), align=TextEntityAlignment.MIDDLE_CENTER)


def _cotation_v(msp, y1, y2, x_ref, x_dim, texte, th, layer="COTATIONS"):
    """Cotation verticale entre y1 et y2, ligne de cote à x_dim."""
    tick = th * 0.5
    msp.add_line((x_ref, y1), (x_dim + tick, y1), dxfattribs={"layer": layer})
    msp.add_line((x_ref, y2), (x_dim + tick, y2), dxfattribs={"layer": layer})
    msp.add_line((x_dim, y1), (x_dim, y2), dxfattribs={"layer": layer})
    for yf, sens in [(y1, +1), (y2, -1)]:
        msp.add_line((x_dim, yf), (x_dim + tick, yf + sens * tick * 2), dxfattribs={"layer": layer})
        msp.add_line((x_dim, yf), (x_dim - tick, yf + sens * tick * 2), dxfattribs={"layer": layer})
    t = msp.add_text(texte, dxfattribs={"height": th, "layer": layer, "rotation": 90})
    t.set_placement((x_dim + th * 1.8, (y1 + y2) / 2), align=TextEntityAlignment.MIDDLE_CENTER)


def _texte(msp, contenu, x, y, th, layer="TEXTES", rotation=0, align="MIDDLE_CENTER"):
    t = msp.add_text(contenu, dxfattribs={"height": th, "layer": layer, "rotation": rotation})
    t.set_placement((x, y), align=getattr(TextEntityAlignment, align))


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------

def generer_dessin_poutre(resultats, groupe=1, nom_fichier=None):
    """
    Génère le fichier DXF d'une poutre BA.
    Retourne (nom_fichier, None) en cas de succès, (None, message_erreur) sinon.
    """
    if not EZDXF_OK:
        return None, "ezdxf n'est pas installé. Lancez : pip install ezdxf"

    if resultats.get("statut") != "OK":
        return None, "Calcul invalide — effectuez d'abord un calcul correct."

    # -- Données --
    b        = resultats["b"]           # mm
    h        = resultats["h"]           # mm
    L        = resultats["L"]           # m
    L_mm     = L * 1000                 # mm
    cnom     = resultats.get("cnom", 30)
    nb       = resultats["nb_barres"]
    dia      = resultats["diametre"]    # mm
    As_ad    = resultats["As_adoptee"]
    s_et     = resultats["s_etrier"]    # mm
    phi_et   = 8                        # HA8
    phi_sup  = 10                       # HA10 constructif
    MEd      = resultats["MEd"]
    VEd      = resultats["VEd"]
    d_mm     = resultats["d"]
    z_mm     = resultats["z"]
    As_req   = resultats["As_req"]

    if nom_fichier is None:
        nom_fichier = f"poutre_BA_groupe_{groupe:02d}.dxf"

    # -- Tailles textes et marges --
    th_t = max(100.0, h * 0.14)     # texte titre
    th_c = max(75.0,  h * 0.10)     # texte corps
    off  = max(300.0, h * 0.55)     # offset cotations
    sup  = max(150.0, h * 0.25)     # hauteur triangle appui
    gap  = max(1500.0, b * 2.5)     # espacement entre vues

    # -- Document --
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4     # mm

    # Calques
    for nom, col, lw in [
        ("BETON",      7, 50),
        ("ACIER_LONG", 1, 35),
        ("ETRIERS",    3, 25),
        ("COTATIONS",  2, 18),
        ("TEXTES",     4, 18),
        ("AXES",       5, 13),
    ]:
        doc.layers.add(nom, color=col, lineweight=lw)

    msp = doc.modelspace()

    # ================================================================
    # VUE LONGITUDINALE  — origine (0, 0)
    # ================================================================
    x0, y0 = 0.0, 0.0

    # Contour béton
    msp.add_lwpolyline(
        [(x0, y0), (x0 + L_mm, y0), (x0 + L_mm, y0 + h), (x0, y0 + h)],
        close=True, dxfattribs={"layer": "BETON"}
    )

    # Armatures inférieures (ligne unique en élévation)
    y_inf   = y0 + cnom + phi_et + dia / 2
    x_debut = x0 + cnom + phi_et
    x_fin   = x0 + L_mm - cnom - phi_et
    msp.add_line((x_debut, y_inf), (x_fin, y_inf), dxfattribs={"layer": "ACIER_LONG"})

    # Armatures supérieures constructives
    y_sup = y0 + h - cnom - phi_et - phi_sup / 2
    msp.add_line((x_debut, y_sup), (x_fin, y_sup), dxfattribs={"layer": "ACIER_LONG"})

    # Étriers
    y_et_bas = y0 + cnom
    y_et_haut = y0 + h - cnom
    x_et = x_debut
    while x_et <= x_fin + 1:
        msp.add_line((x_et, y_et_bas), (x_et, y_et_haut), dxfattribs={"layer": "ETRIERS"})
        x_et += s_et
    # dernier étrier exactement à x_fin
    if x_et - s_et < x_fin - 1:
        msp.add_line((x_fin, y_et_bas), (x_fin, y_et_haut), dxfattribs={"layer": "ETRIERS"})

    # Appuis
    sw = sup * 0.6   # demi-largeur triangle
    # Rotule (gauche)
    msp.add_lwpolyline(
        [(x0, y0), (x0 - sw, y0 - sup), (x0 + sw, y0 - sup)],
        close=True, dxfattribs={"layer": "BETON"}
    )
    msp.add_line((x0 - sw * 1.6, y0 - sup), (x0 + sw * 1.6, y0 - sup),
                 dxfattribs={"layer": "BETON"})
    # Rouleau (droite)
    msp.add_lwpolyline(
        [(x0 + L_mm, y0), (x0 + L_mm - sw, y0 - sup), (x0 + L_mm + sw, y0 - sup)],
        close=True, dxfattribs={"layer": "BETON"}
    )
    msp.add_circle(
        (x0 + L_mm, y0 - sup - sw * 0.7), radius=sw * 0.35,
        dxfattribs={"layer": "BETON"}
    )
    msp.add_line((x0 + L_mm - sw * 1.6, y0 - sup), (x0 + L_mm + sw * 1.6, y0 - sup),
                 dxfattribs={"layer": "BETON"})

    # Cotation portée L
    y_cote_L = y0 - sup - off
    _cotation_h(msp, x0, x0 + L_mm, y0, y_cote_L,
                f"L = {L:.2f} m  ({L_mm:.0f} mm)", th_c)

    # Ligne de coupe A-A
    x_coupe = x0 + L_mm / 2
    msp.add_line((x_coupe, y0 - 200), (x_coupe, y0 + h + 200),
                 dxfattribs={"layer": "AXES"})
    _texte(msp, "A", x_coupe, y0 + h + 300, th_t, "AXES")
    _texte(msp, "A", x_coupe, y0 - 300,      th_t, "AXES")

    # Textes en-tête vue longitudinale
    y_hdr = y0 + h + off + th_t
    _texte(msp, f"Poutre BA - Groupe {groupe}",
           x0 + L_mm / 2, y_hdr + th_t * 1.5, th_t)
    _texte(msp, f"b = {b:.0f} mm  |  h = {h:.0f} mm  |  L = {L:.2f} m",
           x0 + L_mm / 2, y_hdr, th_c)
    _texte(msp,
           f"Arm. inf. : {nb} HA{dia}  |  Arm. sup. : 2 HA10  |  Etriers : HA8 / {s_et // 10:.0f} cm",
           x0 + L_mm / 2, y_hdr - th_c * 2.2, th_c)

    # ================================================================
    # COUPE TRANSVERSALE  — origine (x0 + L_mm + gap, 0)
    # ================================================================
    xc, yc = x0 + L_mm + gap, y0

    # Contour béton
    msp.add_lwpolyline(
        [(xc, yc), (xc + b, yc), (xc + b, yc + h), (xc, yc + h)],
        close=True, dxfattribs={"layer": "BETON"}
    )

    # Étrier fermé (rectangle intérieur)
    ex0, ey0 = xc + cnom, yc + cnom
    ex1, ey1 = xc + b - cnom, yc + h - cnom
    msp.add_lwpolyline(
        [(ex0, ey0), (ex1, ey0), (ex1, ey1), (ex0, ey1)],
        close=True, dxfattribs={"layer": "ETRIERS"}
    )

    # Armatures inférieures (cercles)
    y_bi = yc + cnom + phi_et + dia / 2
    x_g  = xc + cnom + phi_et + dia / 2
    x_d  = xc + b - cnom - phi_et - dia / 2

    if nb == 1:
        bar_xs = [xc + b / 2]
    else:
        bar_xs = [x_g + i * (x_d - x_g) / (nb - 1) for i in range(nb)]

    for bx in bar_xs:
        msp.add_circle((bx, y_bi), radius=dia / 2, dxfattribs={"layer": "ACIER_LONG"})

    # Armatures supérieures constructives
    y_bs  = yc + h - cnom - phi_et - phi_sup / 2
    sup_xg = xc + cnom + phi_et + phi_sup / 2
    sup_xd = xc + b - cnom - phi_et - phi_sup / 2
    msp.add_circle((sup_xg, y_bs), radius=phi_sup / 2, dxfattribs={"layer": "ACIER_LONG"})
    msp.add_circle((sup_xd, y_bs), radius=phi_sup / 2, dxfattribs={"layer": "ACIER_LONG"})

    # Cotation b
    _cotation_h(msp, xc, xc + b, yc, yc - off, f"b = {b:.0f} mm", th_c)

    # Cotation h
    _cotation_v(msp, yc, yc + h, xc + b, xc + b + off, f"h = {h:.0f} mm", th_c)

    # Textes en-tête coupe
    y_hdr_c = yc + h + off + th_t
    _texte(msp, "Coupe A-A", xc + b / 2, y_hdr_c + th_t * 1.5, th_t)
    _texte(msp,
           f"b = {b:.0f} mm  |  h = {h:.0f} mm  |  cnom = {cnom:.0f} mm",
           xc + b / 2, y_hdr_c, th_c)
    _texte(msp,
           f"Arm. inf. : {nb} HA{dia}  |  Arm. sup. : 2 HA10  |  Etrier : HA8",
           xc + b / 2, y_hdr_c - th_c * 2.2, th_c)

    # ================================================================
    # RÉSUMÉ DES CALCULS (sous la coupe)
    # ================================================================
    y_res = yc - off - th_c * 3
    lignes = [
        f"MEd = {MEd:.2f} kN.m     VEd = {VEd:.2f} kN",
        f"d = {d_mm:.1f} mm     z = {z_mm:.1f} mm",
        f"As,req = {As_req:.1f} mm2     As,adoptee = {As_ad:.1f} mm2  ({nb} HA{dia})",
        f"Etriers : HA8 / {s_et // 10:.0f} cm",
    ]
    for i, ligne in enumerate(lignes):
        _texte(msp, ligne, xc + b / 2, y_res - i * th_c * 2.0, th_c)

    # ================================================================
    # Sauvegarde
    # ================================================================
    try:
        doc.saveas(nom_fichier)
        return nom_fichier, None
    except Exception as exc:
        return None, str(exc)


# ---------------------------------------------------------------------------
# Helpers barre poteau
# ---------------------------------------------------------------------------

def _bars_rect_perimeter(xc, yc, b_mm, h_mm, cnom, phi_e, phi_l, nb):
    """Distribue nb barres uniformément sur le périmètre intérieur d'un poteau rect."""
    x0 = xc + cnom + phi_e + phi_l / 2
    x1 = xc + b_mm - cnom - phi_e - phi_l / 2
    y0 = yc + cnom + phi_e + phi_l / 2
    y1 = yc + h_mm - cnom - phi_e - phi_l / 2
    dx = max(x1 - x0, 1.0)
    dy = max(y1 - y0, 1.0)
    perim = 2 * (dx + dy)
    pts = []
    for i in range(nb):
        s = i * perim / nb
        if s <= dx:
            pts.append((x0 + s, y0))
        elif s <= dx + dy:
            pts.append((x1, y0 + (s - dx)))
        elif s <= 2 * dx + dy:
            pts.append((x1 - (s - dx - dy), y1))
        else:
            pts.append((x0, y1 - (s - 2 * dx - dy)))
    return pts


# ---------------------------------------------------------------------------
# Dessin DXF — POTEAU
# ---------------------------------------------------------------------------

def generer_dessin_poteau(resultats, groupe=1, nom_fichier=None, cnom=30):
    """
    Génère le fichier DXF d'un poteau BA.
    Retourne (nom_fichier, None) ou (None, message_erreur).
    """
    if not EZDXF_OK:
        return None, "ezdxf n'est pas installé. Lancez : pip install ezdxf"
    if resultats.get("statut") != "OK":
        return None, "Calcul invalide."

    # -- Données --
    type_sec  = resultats["type_section"]
    b_mm      = resultats["b_mm"]
    h_mm      = resultats["h_mm"]
    H         = resultats["H"]                 # m
    H_mm      = H * 1000                       # mm
    nb        = resultats["nb_barres"]
    dia       = resultats["diametre"]          # mm
    As_ad     = resultats["As_fournie"]
    As_req    = resultats["As_req"]
    scl       = resultats["scl_max"]           # mm
    phi_e     = max(6, int(resultats.get("diametre_transversal_min", 6)))
    NEd       = resultats["NEd"]
    NRd       = resultats.get("NRd", 0)

    if nom_fichier is None:
        nom_fichier = f"poteau_BA_groupe_{groupe:02d}.dxf"

    # -- Échelles --
    ref  = max(b_mm, 200.0)
    th_t = max(80.0,  ref * 0.14)
    th_c = max(60.0,  ref * 0.10)
    off  = max(300.0, ref * 0.60)
    gap  = max(1200.0, ref * 2.5)

    # -- Document --
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    for nom_l, col, lw in [
        ("BETON",      7, 50),
        ("ACIER_LONG", 1, 35),
        ("ETRIERS",    3, 25),
        ("COTATIONS",  2, 18),
        ("TEXTES",     4, 18),
        ("AXES",       5, 13),
    ]:
        doc.layers.add(nom_l, color=col, lineweight=lw)

    msp = doc.modelspace()

    # ================================================================
    # COUPE TRANSVERSALE  — origine (0, 0)
    # ================================================================
    xc, yc = 0.0, 0.0
    phi_l = float(dia)

    if type_sec == "Circulaire":
        a_mm = b_mm
        cx, cy = xc + a_mm / 2, yc + a_mm / 2
        # Béton
        msp.add_circle((cx, cy), radius=a_mm / 2, dxfattribs={"layer": "BETON"})
        # Cadre (cercle intérieur)
        msp.add_circle((cx, cy), radius=a_mm / 2 - cnom, dxfattribs={"layer": "ETRIERS"})
        # Barres
        r_b = a_mm / 2 - cnom - phi_e - phi_l / 2
        for i in range(nb):
            ang = 2 * math.pi * i / nb - math.pi / 2
            bx = cx + r_b * math.cos(ang)
            by = cy + r_b * math.sin(ang)
            msp.add_circle((bx, by), radius=phi_l / 2, dxfattribs={"layer": "ACIER_LONG"})
        # Cotation diamètre
        _cotation_h(msp, xc, xc + a_mm, yc, yc - off, f"d = {a_mm:.0f} mm", th_c)
        sec_w, sec_h = a_mm, a_mm
    else:
        # Béton
        msp.add_lwpolyline(
            [(xc, yc), (xc + b_mm, yc), (xc + b_mm, yc + h_mm), (xc, yc + h_mm)],
            close=True, dxfattribs={"layer": "BETON"}
        )
        # Cadre (rect. intérieur)
        ex0, ey0 = xc + cnom, yc + cnom
        ex1, ey1 = xc + b_mm - cnom, yc + h_mm - cnom
        msp.add_lwpolyline(
            [(ex0, ey0), (ex1, ey0), (ex1, ey1), (ex0, ey1)],
            close=True, dxfattribs={"layer": "ETRIERS"}
        )
        # Barres
        for bx, by in _bars_rect_perimeter(xc, yc, b_mm, h_mm, cnom, phi_e, phi_l, nb):
            msp.add_circle((bx, by), radius=phi_l / 2, dxfattribs={"layer": "ACIER_LONG"})
        # Cotations
        _cotation_h(msp, xc, xc + b_mm, yc, yc - off, f"b = {b_mm:.0f} mm", th_c)
        _cotation_v(msp, yc, yc + h_mm, xc + b_mm, xc + b_mm + off, f"h = {h_mm:.0f} mm", th_c)
        sec_w, sec_h = b_mm, h_mm

    # Titre coupe
    y_hdr_c = yc + sec_h + off + th_t
    _texte(msp, "Coupe transversale", xc + sec_w / 2, y_hdr_c + th_t * 1.5, th_t)
    _texte(msp,
           (f"d = {b_mm:.0f} mm" if type_sec == "Circulaire"
            else f"b = {b_mm:.0f} mm  |  h = {h_mm:.0f} mm"),
           xc + sec_w / 2, y_hdr_c, th_c)
    _texte(msp,
           f"Arm. long. : {nb} HA{dia}  |  Cadres : HA{phi_e:.0f} / {scl:.0f} mm",
           xc + sec_w / 2, y_hdr_c - th_c * 2.2, th_c)

    # ================================================================
    # VUE EN ÉLÉVATION  — décalée à droite
    # ================================================================
    xe, ye = xc + sec_w + gap, 0.0
    marg = cnom + phi_e + phi_l / 2     # marge interne pour les barres

    # Contour béton
    msp.add_lwpolyline(
        [(xe, ye), (xe + b_mm, ye), (xe + b_mm, ye + H_mm), (xe, ye + H_mm)],
        close=True, dxfattribs={"layer": "BETON"}
    )

    # Barres longitudinales (lignes, 2 côtés visibles)
    for bx in [xe + marg, xe + b_mm - marg]:
        msp.add_line((bx, ye + marg), (bx, ye + H_mm - marg),
                     dxfattribs={"layer": "ACIER_LONG"})

    # Cadres (lignes horizontales)
    y_cad = ye + marg
    while y_cad <= ye + H_mm - marg + 1:
        msp.add_line((xe + cnom, y_cad), (xe + b_mm - cnom, y_cad),
                     dxfattribs={"layer": "ETRIERS"})
        y_cad += scl
    # Dernier cadre en haut
    if y_cad - scl < ye + H_mm - marg - 1:
        msp.add_line((xe + cnom, ye + H_mm - marg),
                     (xe + b_mm - cnom, ye + H_mm - marg),
                     dxfattribs={"layer": "ETRIERS"})

    # Cotation H (à droite)
    _cotation_v(msp, ye, ye + H_mm, xe + b_mm, xe + b_mm + off,
                f"H = {H:.2f} m", th_c)

    # Cotation b (en bas)
    _cotation_h(msp, xe, xe + b_mm, ye, ye - off,
                f"b = {b_mm:.0f} mm", th_c)

    # Titre et résumé élévation
    y_hdr_e = ye + H_mm + off + th_t * 2
    _texte(msp, f"Poteau BA - Groupe {groupe}",
           xe + b_mm / 2, y_hdr_e + th_t * 1.5, th_t)
    _texte(msp,
           (f"d = {b_mm:.0f} mm  |  H = {H:.2f} m" if type_sec == "Circulaire"
            else f"b = {b_mm:.0f} mm  |  h = {h_mm:.0f} mm  |  H = {H:.2f} m"),
           xe + b_mm / 2, y_hdr_e, th_c)
    _texte(msp,
           f"Arm. long. : {nb} HA{dia}  |  Cadres : HA{phi_e:.0f} / {scl:.0f} mm",
           xe + b_mm / 2, y_hdr_e - th_c * 2.2, th_c)
    _texte(msp,
           f"NEd = {NEd:.1f} kN  |  As,req = {As_req:.0f} mm2  |  As,adoptee = {As_ad:.0f} mm2",
           xe + b_mm / 2, y_hdr_e - th_c * 4.4, th_c)

    # ================================================================
    # Sauvegarde
    # ================================================================
    try:
        doc.saveas(nom_fichier)
        return nom_fichier, None
    except Exception as exc:
        return None, str(exc)
