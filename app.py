import customtkinter as ctk
import test  
# NOUVEAU : Importation de matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

fenetre = ctk.CTk()
fenetre.geometry("1100x750") 
fenetre.title("Compta PalmoDev")

tous_les_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                 "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

index_edition = None 

# --- 1. LE FORMULAIRE ---
cadre_formulaire = ctk.CTkFrame(fenetre)
cadre_formulaire.pack(pady=10, padx=20, fill="x")

combo_mois = ctk.CTkComboBox(cadre_formulaire, values=tous_les_mois, state="readonly", width=110)
combo_mois.pack(side="left", padx=5, pady=15)
combo_mois.set("Octobre") 

combo_annee = ctk.CTkComboBox(cadre_formulaire, values=["2026", "2027", "2028"], state="readonly", width=80)
combo_annee.pack(side="left", padx=5, pady=15)
combo_annee.set("2026") 

combo_type = ctk.CTkComboBox(cadre_formulaire, values=["Dépense", "Entrée"], state="readonly", width=90)
combo_type.pack(side="left", padx=5, pady=15)
combo_type.set("Dépense")

combo_contexte = ctk.CTkComboBox(cadre_formulaire, values=["Perso", "Coloc"], state="readonly", width=90)
combo_contexte.pack(side="left", padx=5, pady=15)
combo_contexte.set("Perso") 

variable_montant = ctk.StringVar()
def filtrer_montant(*args):
    texte = variable_montant.get().replace(',', '.')
    texte_propre = ""
    point_vu = False
    for caractere in texte:
        if caractere.isdigit(): texte_propre += caractere
        elif caractere == '.' and not point_vu:
            texte_propre += caractere
            point_vu = True
    if variable_montant.get() != texte_propre: variable_montant.set(texte_propre)
variable_montant.trace_add("write", filtrer_montant)

entree_montant = ctk.CTkEntry(cadre_formulaire, textvariable=variable_montant, placeholder_text="Montant (€)", width=100)
entree_montant.pack(side="left", padx=5, pady=15, expand=True, fill="x")

variable_raison = ctk.StringVar()
def limiter_texte(*args):
    if len(variable_raison.get()) > 25: variable_raison.set(variable_raison.get()[:25])
variable_raison.trace_add("write", limiter_texte)

entree_raison = ctk.CTkEntry(cadre_formulaire, textvariable=variable_raison, placeholder_text="Raison (max 25 car.)")
entree_raison.pack(side="left", padx=5, pady=15, expand=True, fill="x")

# --- 2. LOGIQUE DU BOUTON VALIDER ---
def au_clic_valider(event=None):
    global index_edition 
    if not entree_montant.get() or entree_montant.get() == ".": return
        
    try:
        montant = float(entree_montant.get())
        if index_edition is None:
            test.ajouter_transaction(combo_mois.get(), combo_annee.get(), combo_type.get(), montant, entree_raison.get(), combo_contexte.get())
        else:
            test.modifier_transaction(index_edition, combo_mois.get(), combo_annee.get(), combo_type.get(), montant, entree_raison.get(), combo_contexte.get())
            index_edition = None 
            bouton_valider.configure(text="Ajouter la transaction", fg_color="#1f538d", hover_color="#14375e") 
            
        entree_montant.delete(0, 'end')
        entree_raison.delete(0, 'end')
        actualiser_tableau()
        combo_mois.focus()
    except ValueError:
        pass

entree_montant.bind("<Return>", lambda event: entree_raison.focus())
entree_raison.bind("<Return>", au_clic_valider)
bouton_valider = ctk.CTkButton(fenetre, text="Ajouter la transaction", command=au_clic_valider)
bouton_valider.pack(pady=10)

# --- 3. LA BARRE DE FILTRES ---
cadre_filtres = ctk.CTkFrame(fenetre, fg_color="transparent") 
cadre_filtres.pack(pady=5, padx=20, fill="x")

ctk.CTkLabel(cadre_filtres, text="🔍 Filtres :", font=("Roboto", 14, "bold")).pack(side="left", padx=(10, 20))
combo_filtre_annee = ctk.CTkComboBox(cadre_filtres, values=["Toutes", "2026", "2027", "2028"], state="readonly", command=lambda c: actualiser_tableau(), width=90)
combo_filtre_annee.pack(side="left", padx=5)
combo_filtre_annee.set("Toutes")

combo_filtre_mois = ctk.CTkComboBox(cadre_filtres, values=["Tous"] + tous_les_mois, state="readonly", command=lambda c: actualiser_tableau(), width=100)
combo_filtre_mois.pack(side="left", padx=5)
combo_filtre_mois.set("Tous")

combo_filtre_contexte = ctk.CTkComboBox(cadre_filtres, values=["Tous", "Perso", "Coloc"], state="readonly", command=lambda c: actualiser_tableau(), width=100)
combo_filtre_contexte.pack(side="left", padx=5)
combo_filtre_contexte.set("Tous")

# --- NOUVEAUX BOUTONS (EXPORT ET STATS) ---
def au_clic_exporter():
    fichier = test.exporter_csv()
    # Petit retour visuel pour dire que ça a marché
    bouton_export.configure(text="✅ Export réussi !", fg_color="#2ecc71")
    # Remet le texte normal au bout de 2 secondes (2000 ms)
    fenetre.after(2000, lambda: bouton_export.configure(text="💾 Exporter CSV", fg_color="#27ae60"))

# Bouton Export
bouton_export = ctk.CTkButton(cadre_filtres, text="💾 Exporter CSV", fg_color="#27ae60", hover_color="#2ecc71", command=au_clic_exporter)
bouton_export.pack(side="right", padx=5)

# Bouton Stats
bouton_stats = ctk.CTkButton(cadre_filtres, text="📊 Graphiques", fg_color="#8e44ad", hover_color="#9b59b6", command=lambda: afficher_statistiques())
bouton_stats.pack(side="right", padx=5)


# --- 4. LE TABLEAU ---
cadre_tableau = ctk.CTkScrollableFrame(fenetre, width=950, height=200)
cadre_tableau.pack(pady=5, padx=20, fill="both", expand=True)

# --- 5. L'ESPACE DU BAS (Soldes et Coloc) ---
cadre_bas = ctk.CTkFrame(fenetre, fg_color="transparent")
cadre_bas.pack(pady=10, padx=20, fill="x")
label_solde = ctk.CTkLabel(cadre_bas, text="Solde Total : 0.00 €", font=("Roboto", 24, "bold"))
label_solde.pack(pady=5)
cadre_coloc = ctk.CTkFrame(cadre_bas)
cadre_coloc.pack(pady=10, padx=150, fill="x")
label_bilan_coloc = ctk.CTkLabel(cadre_coloc, text="Bilan Coloc : ...", font=("Roboto", 16, "bold"))
label_bilan_coloc.pack(pady=10)
cadre_saisie_coloc = ctk.CTkFrame(cadre_coloc, fg_color="transparent")
cadre_saisie_coloc.pack(pady=5)
ctk.CTkLabel(cadre_saisie_coloc, text="Total des dépenses payées par lui :").pack(side="left", padx=5)
entree_coloc_total = ctk.CTkEntry(cadre_saisie_coloc, width=80)
entree_coloc_total.pack(side="left", padx=5)
def maj_coloc(event=None):
    try:
        valeur = float(entree_coloc_total.get().replace(',', '.'))
        test.sauvegarder_total_coloc(valeur)
        actualiser_tableau() 
    except ValueError: pass
ctk.CTkButton(cadre_saisie_coloc, text="Mettre à jour", width=100, command=maj_coloc).pack(side="left", padx=10)
entree_coloc_total.bind("<Return>", maj_coloc)


# --- 6. LOGIQUE DES GRAPHIQUES ---
def afficher_statistiques():
    historique = test.charger_historique()
    if not historique:
        print("Aucune donnée à afficher.")
        return
        
    fenetre_stats = ctk.CTkToplevel(fenetre)
    fenetre_stats.title("Statistiques & Évolution")
    fenetre_stats.geometry("1000x500") 
    
    total_entrees = sum(t["montant"] for t in historique if t["type"] == "Entrée")
    total_depenses = sum(t["montant"] for t in historique if t["type"] == "Dépense")
    
    # Évolution du solde mois par mois ET par année
    evolution_solde = []
    solde_cumule = 0.0
    etiquettes_temps = []
    
    # On va extraire toutes les dates uniques (ex: ("2026", "Octobre"), ("2027", "Janvier"))
    dates_uniques = []
    for t in historique:
        date_tuple = (t.get("annee", "2026"), t["mois"])
        if date_tuple not in dates_uniques:
            dates_uniques.append(date_tuple)
            
    # Pour chaque date, on calcule le solde à ce moment-là
    for annee, mois in dates_uniques:
        transactions_periode = [t for t in historique if t.get("annee", "2026") == annee and t["mois"] == mois]
        
        for t in transactions_periode:
            if t["type"] == "Entrée": solde_cumule += t["montant"]
            else: solde_cumule -= t["montant"]
            
        evolution_solde.append(solde_cumule)
        
        # On crée une belle étiquette ex: "Oct 26"
        etiquette = f"{mois[:3]} {annee[-2:]}"
        etiquettes_temps.append(etiquette)
    
    # --- CONFIGURATION MATPLOTLIB ---
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), facecolor='#2b2b2b')
    
    # Dessin du Camembert
    if total_entrees > 0 or total_depenses > 0:
        wedges, texts, autotexts = ax1.pie(
            [total_entrees, total_depenses], 
            labels=["Entrées", "Dépenses"], 
            colors=['#2ecc71', '#e74c3c'], 
            autopct='%1.1f%%', 
            startangle=90,
            wedgeprops={'edgecolor': '#2b2b2b', 'linewidth': 2} 
        )
        ax1.set_title("Répartition Globale", color='white', pad=20, fontsize=14, fontweight='bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    else:
        ax1.text(0.5, 0.5, "Pas de données", ha='center', va='center', color='gray')
        
    # Dessin de la Courbe (Mois + Année)
    if etiquettes_temps:
        ax2.set_facecolor('#242424') 
        ax2.plot(etiquettes_temps, evolution_solde, color='#00d2d3', linewidth=3, marker='o', markersize=8)
        
        ax2.set_title("Évolution du Solde", color='white', pad=20, fontsize=14, fontweight='bold')
        ax2.grid(True, linestyle='--', alpha=0.3, color='gray') 
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_color('#888888')
        ax2.spines['left'].set_color('#888888')
        ax2.tick_params(colors='#888888')
        
        # Si on a beaucoup de dates, on incline le texte pour qu'il reste lisible
        if len(etiquettes_temps) > 5:
            ax2.tick_params(axis='x', rotation=45)
    else:
        ax2.text(0.5, 0.5, "Pas de données", ha='center', va='center', color='gray')
        
    fig.tight_layout(pad=3.0) 
    
    canvas = FigureCanvasTkAgg(fig, master=fenetre_stats)
    canvas.draw()
    widget = canvas.get_tk_widget()
    widget.configure(bg='#2b2b2b')
    widget.pack(fill="both", expand=True)
    
    # --- LA CORRECTION DU BUG DE FERMETURE EST ICI ---
    def fermer_proprement():
        plt.close(fig) # Détruit proprement la figure matplotlib
        fenetre_stats.destroy() # Ferme la fenêtre CustomTkinter
        
    # On intercepte le clic sur la croix rouge de la fenêtre pour lancer notre fonction propre
    fenetre_stats.protocol("WM_DELETE_WINDOW", fermer_proprement)
# --- 7. LOGIQUE D'AFFICHAGE (TABLEAU) ---
def au_clic_supprimer(index):
    test.supprimer_transaction(index)
    actualiser_tableau()

def preparer_edition(index, transaction):
    global index_edition
    index_edition = index
    combo_mois.set(transaction["mois"])
    combo_annee.set(transaction.get("annee", "2026"))
    combo_type.set(transaction["type"])
    
    ctx = transaction.get("contexte", "Perso")
    if ctx == "Coloc (Moi)": ctx = "Coloc"
    combo_contexte.set(ctx)
    
    entree_montant.delete(0, 'end')
    entree_montant.insert(0, str(transaction["montant"]))
    entree_raison.delete(0, 'end')
    entree_raison.insert(0, transaction["raison"])
    bouton_valider.configure(text="Enregistrer la modification", fg_color="#f39c12", hover_color="#e67e22")
    entree_montant.focus()

def actualiser_tableau():
    for widget in cadre_tableau.winfo_children(): widget.destroy()
    en_tetes = ["Année", "Mois", "Type", "Montant", "Raison", "Contexte", "Actions"]
    for colonne, texte in enumerate(en_tetes): ctk.CTkLabel(cadre_tableau, text=texte, font=("Roboto", 14, "bold")).grid(row=0, column=colonne, padx=20, pady=5)
        
    historique = test.charger_historique()
    annee_filtre = combo_filtre_annee.get()
    mois_filtre = combo_filtre_mois.get()
    contexte_filtre = combo_filtre_contexte.get()
    
    solde_affiche = 0.0
    ligne_visuelle = 1 
    
    for index, transaction in enumerate(historique):
        transaction_annee = transaction.get("annee", "2026")
        ctx = transaction.get("contexte", "Perso")
        if ctx == "Coloc (Moi)": ctx = "Coloc" 
        
        if annee_filtre != "Toutes" and transaction_annee != annee_filtre: continue
        if mois_filtre != "Tous" and transaction["mois"] != mois_filtre: continue
        if contexte_filtre != "Tous" and ctx != contexte_filtre: continue
            
        if transaction["type"] == "Entrée": solde_affiche += transaction["montant"]
        else: solde_affiche -= transaction["montant"]
            
        ctk.CTkLabel(cadre_tableau, text=transaction_annee).grid(row=ligne_visuelle, column=0, pady=5)
        ctk.CTkLabel(cadre_tableau, text=transaction["mois"]).grid(row=ligne_visuelle, column=1, pady=5)
        couleur = "#2ecc71" if transaction["type"] == "Entrée" else "#e74c3c"
        ctk.CTkLabel(cadre_tableau, text=transaction["type"], text_color=couleur).grid(row=ligne_visuelle, column=2, pady=5)
        ctk.CTkLabel(cadre_tableau, text=f'{transaction["montant"]} €').grid(row=ligne_visuelle, column=3, pady=5)
        ctk.CTkLabel(cadre_tableau, text=transaction["raison"]).grid(row=ligne_visuelle, column=4, pady=5)
        ctk.CTkLabel(cadre_tableau, text=ctx).grid(row=ligne_visuelle, column=5, pady=5)
        
        cadre_actions = ctk.CTkFrame(cadre_tableau, fg_color="transparent")
        cadre_actions.grid(row=ligne_visuelle, column=6, padx=5, pady=5)
        ctk.CTkButton(cadre_actions, text="✏️", width=30, fg_color="#f39c12", hover_color="#e67e22", command=lambda i=index, t=transaction: preparer_edition(i, t)).pack(side="left", padx=2)
        ctk.CTkButton(cadre_actions, text="❌", width=30, fg_color="#c0392b", hover_color="#e74c3c", command=lambda i=index: au_clic_supprimer(i)).pack(side="left", padx=2)
        ligne_visuelle += 1
    
    couleur_solde = "#2ecc71" if solde_affiche >= 0 else "#e74c3c"
    titre_solde = f"Solde : {solde_affiche:.2f} €"
    label_solde.configure(text=titre_solde, text_color=couleur_solde)
    
    entree_coloc_total.delete(0, 'end')
    entree_coloc_total.insert(0, str(test.lire_total_coloc()))
    
    paye_moi, paye_lui, bilan = test.calculer_dette_coloc()
    if bilan > 0: texte_coloc, couleur_coloc = f"Tu as payé {paye_moi:.2f}€ | Il a payé {paye_lui:.2f}€  ➔  IL TE DOIT {bilan:.2f}€", "#2ecc71"
    elif bilan < 0: texte_coloc, couleur_coloc = f"Tu as payé {paye_moi:.2f}€ | Il a payé {paye_lui:.2f}€  ➔  TU LUI DOIS {abs(bilan):.2f}€", "#e74c3c"
    else: texte_coloc, couleur_coloc = f"Tu as payé {paye_moi:.2f}€ | Il a payé {paye_lui:.2f}€  ➔  Vous êtes à jour !", "#3498db"
    label_bilan_coloc.configure(text=texte_coloc, text_color=couleur_coloc)

actualiser_tableau()
fenetre.mainloop()