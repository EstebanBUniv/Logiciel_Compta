import customtkinter as ctk
import test  

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

fenetre = ctk.CTk()
fenetre.geometry("1000x700") 
fenetre.title("Compta PalmoDev")

titre = ctk.CTkLabel(fenetre, text="Tableau de bord comptable", font=("Roboto", 24, "bold"))
titre.pack(pady=20)

tous_les_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                 "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

# --- 1. LE FORMULAIRE ---
cadre_formulaire = ctk.CTkFrame(fenetre)
cadre_formulaire.pack(pady=10, padx=20, fill="x")

combo_mois = ctk.CTkComboBox(cadre_formulaire, values=tous_les_mois, state="readonly", width=120)
combo_mois.pack(side="left", padx=5, pady=15)
combo_mois.set("Octobre") 

combo_annee = ctk.CTkComboBox(cadre_formulaire, values=["2026", "2027", "2028"], state="readonly", width=80)
combo_annee.pack(side="left", padx=5, pady=15)
combo_annee.set("2026") 

combo_type = ctk.CTkComboBox(cadre_formulaire, values=["Dépense", "Entrée"], state="readonly", width=100)
combo_type.pack(side="left", padx=5, pady=15)
combo_type.set("Dépense")

entree_montant = ctk.CTkEntry(cadre_formulaire, placeholder_text="Montant (€)", width=100)
entree_montant.pack(side="left", padx=5, pady=15, expand=True, fill="x")

variable_raison = ctk.StringVar()
def limiter_texte(*args):
    limite = 25
    if len(variable_raison.get()) > limite:
        variable_raison.set(variable_raison.get()[:limite])
variable_raison.trace_add("write", limiter_texte)

entree_raison = ctk.CTkEntry(cadre_formulaire, textvariable=variable_raison, placeholder_text="Raison (max 25 car.)")
entree_raison.pack(side="left", padx=5, pady=15, expand=True, fill="x")


# --- KEY BINDING (Raccourcis clavier) ---
def au_clic_ajouter(event=None):
    try:
        montant = float(entree_montant.get())
        test.ajouter_transaction(
            combo_mois.get(), combo_annee.get(), combo_type.get(), 
            montant, entree_raison.get()
        )
        entree_montant.delete(0, 'end')
        entree_raison.delete(0, 'end')
        actualiser_tableau()
        
        entree_montant.focus()
    except ValueError:
        print("Erreur : Le montant doit être un nombre valide.")

entree_montant.bind("<Return>", lambda event: entree_raison.focus())
entree_raison.bind("<Return>", au_clic_ajouter)


# --- 2. LE BOUTON D'AJOUT ---
ctk.CTkButton(fenetre, text="Ajouter la transaction", command=au_clic_ajouter).pack(pady=10)


# --- 3. LA BARRE DE FILTRES ---
cadre_filtres = ctk.CTkFrame(fenetre, fg_color="transparent") 
cadre_filtres.pack(pady=5, padx=20, fill="x")

ctk.CTkLabel(cadre_filtres, text="🔍 Filtrer par", font=("Roboto", 14, "bold")).pack(side="left", padx=(10, 20))

ctk.CTkLabel(cadre_filtres, text="Année :", font=("Roboto", 14)).pack(side="left", padx=5)
combo_filtre_annee = ctk.CTkComboBox(
    cadre_filtres, values=["Toutes", "2026", "2027", "2028"], state="readonly",
    command=lambda choix: actualiser_tableau()
)
combo_filtre_annee.pack(side="left", padx=5)
combo_filtre_annee.set("Toutes")

ctk.CTkLabel(cadre_filtres, text="Mois :", font=("Roboto", 14)).pack(side="left", padx=(15, 5))
combo_filtre_mois = ctk.CTkComboBox(
    cadre_filtres, values=["Tous"] + tous_les_mois, state="readonly",
    command=lambda choix: actualiser_tableau() 
)
combo_filtre_mois.pack(side="left", padx=5)
combo_filtre_mois.set("Tous")


# --- 4. LE TABLEAU ET LE SOLDE ---
cadre_tableau = ctk.CTkScrollableFrame(fenetre, width=900, height=250)
cadre_tableau.pack(pady=5, padx=20, fill="both", expand=True)

label_solde = ctk.CTkLabel(fenetre, text="Solde Total : 0.00 €", font=("Roboto", 24, "bold"))
label_solde.pack(pady=20)


# --- 5. LOGIQUE D'AFFICHAGE ---
def au_clic_supprimer(index):
    test.supprimer_transaction(index)
    actualiser_tableau()

def actualiser_tableau():
    for widget in cadre_tableau.winfo_children():
        widget.destroy()
        
    en_tetes = ["Année", "Mois", "Type", "Montant", "Raison", "Action"]
    for colonne, texte in enumerate(en_tetes):
        ctk.CTkLabel(cadre_tableau, text=texte, font=("Roboto", 14, "bold")).grid(row=0, column=colonne, padx=20, pady=5)
        
    historique = test.charger_historique()
    annee_filtre = combo_filtre_annee.get()
    mois_filtre = combo_filtre_mois.get()
    
    solde_affiche = 0.0
    ligne_visuelle = 1 
    
    for index, transaction in enumerate(historique):
        transaction_annee = transaction.get("annee", "2026")
        
        if annee_filtre != "Toutes" and transaction_annee != annee_filtre:
            continue
        if mois_filtre != "Tous" and transaction["mois"] != mois_filtre:
            continue
            
        if transaction["type"] == "Entrée":
            solde_affiche += transaction["montant"]
        else:
            solde_affiche -= transaction["montant"]
            
        ctk.CTkLabel(cadre_tableau, text=transaction_annee).grid(row=ligne_visuelle, column=0, pady=5)
        ctk.CTkLabel(cadre_tableau, text=transaction["mois"]).grid(row=ligne_visuelle, column=1, pady=5)
        
        couleur = "#2ecc71" if transaction["type"] == "Entrée" else "#e74c3c"
        ctk.CTkLabel(cadre_tableau, text=transaction["type"], text_color=couleur).grid(row=ligne_visuelle, column=2, pady=5)
        
        ctk.CTkLabel(cadre_tableau, text=f'{transaction["montant"]} €').grid(row=ligne_visuelle, column=3, pady=5)
        ctk.CTkLabel(cadre_tableau, text=transaction["raison"]).grid(row=ligne_visuelle, column=4, pady=5)
        
        ctk.CTkButton(
            cadre_tableau, text="❌", width=30, fg_color="#c0392b", hover_color="#e74c3c", 
            command=lambda i=index: au_clic_supprimer(i)
        ).grid(row=ligne_visuelle, column=5, padx=10, pady=5)
        
        ligne_visuelle += 1
    
    couleur_solde = "#2ecc71" if solde_affiche >= 0 else "#e74c3c"
    if annee_filtre == "Toutes" and mois_filtre == "Tous":
        titre_solde = f"Solde Global : {solde_affiche:.2f} €"
    else:
        titre_solde = f"Solde ({annee_filtre} - {mois_filtre}) : {solde_affiche:.2f} €"
        
    label_solde.configure(text=titre_solde, text_color=couleur_solde)

# --- 6. INITIALISATION ---
actualiser_tableau()
fenetre.mainloop()