import customtkinter as ctk
import test  

# --- CONFIGURATION DE LA FENÊTRE ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

fenetre = ctk.CTk()
fenetre.geometry("1000x600")
fenetre.title("Compta PalmoDev")

titre = ctk.CTkLabel(fenetre, text="Tableau de bord comptable", font=("Roboto", 24, "bold"))
titre.pack(pady=20)

# --- 1. LE FORMULAIRE ---
cadre_formulaire = ctk.CTkFrame(fenetre)
cadre_formulaire.pack(pady=10, padx=20, fill="x")

combo_annee = ctk.CTkComboBox(cadre_formulaire, values=["2026", "2027", "2028"], state="readonly")
combo_annee.pack(side="left", padx=5, pady=15)
combo_annee.set("2026") 

combo_mois = ctk.CTkComboBox(cadre_formulaire, values=["Septembre", "Octobre", "Novembre", "Décembre"], state="readonly")
combo_mois.pack(side="left", padx=5, pady=15)
combo_mois.set("Octobre") 

combo_type = ctk.CTkComboBox(cadre_formulaire, values=["Dépense", "Entrée"], state="readonly")
combo_type.pack(side="left", padx=5, pady=15)
combo_type.set("Dépense")

entree_montant = ctk.CTkEntry(cadre_formulaire, placeholder_text="Montant (€)")
entree_montant.pack(side="left", padx=5, pady=15, expand=True, fill="x")

# Limite de caractères pour la raison
variable_raison = ctk.StringVar()

def limiter_texte(*args):
    limite = 25
    texte = variable_raison.get()
    if len(texte) > limite:
        variable_raison.set(texte[:limite])

variable_raison.trace_add("write", limiter_texte)

entree_raison = ctk.CTkEntry(cadre_formulaire, textvariable=variable_raison, placeholder_text="Raison (max 25 car.)")
entree_raison.pack(side="left", padx=5, pady=15, expand=True, fill="x")


# --- 2. FONCTIONS DES BOUTONS ---
def au_clic_ajouter():
    annee = combo_annee.get()
    mois = combo_mois.get()
    type_transac = combo_type.get()
    raison = entree_raison.get()
    
    try:
        montant = float(entree_montant.get())
        
        test.ajouter_transaction(mois, annee, type_transac, montant, raison)
        
        entree_montant.delete(0, 'end')
        entree_raison.delete(0, 'end')
        actualiser_tableau()
        
    except ValueError:
        print("Erreur : Le montant doit être un nombre valide.")

def au_clic_supprimer(index):
    test.supprimer_transaction(index)
    actualiser_tableau()


# --- 3. BOUTON D'AJOUT ---
bouton_ajouter = ctk.CTkButton(fenetre, text="Ajouter la transaction", command=au_clic_ajouter)
bouton_ajouter.pack(pady=10)


# --- 4. LE TABLEAU ---
cadre_tableau = ctk.CTkScrollableFrame(fenetre, width=800, height=250)
cadre_tableau.pack(pady=10, padx=20, fill="both", expand=True)

def actualiser_tableau():
    for widget in cadre_tableau.winfo_children():
        widget.destroy()
        
    en_tetes = ["Année", "Mois", "Type", "Montant", "Raison", "Action"]
    for colonne, texte in enumerate(en_tetes):
        titre_col = ctk.CTkLabel(cadre_tableau, text=texte, font=("Roboto", 14, "bold"))
        titre_col.grid(row=0, column=colonne, padx=25, pady=5)
        
    historique = test.charger_historique()
    
    for index, transaction in enumerate(historique):
        ligne = index + 1 
        
        annee_texte = transaction.get("annee", "2026") 
        
        ctk.CTkLabel(cadre_tableau, text=annee_texte).grid(row=ligne, column=0, pady=5)
        ctk.CTkLabel(cadre_tableau, text=transaction["mois"]).grid(row=ligne, column=1, pady=5)
        
        couleur = "#2ecc71" if transaction["type"] == "Entrée" else "#e74c3c"
        ctk.CTkLabel(cadre_tableau, text=transaction["type"], text_color=couleur).grid(row=ligne, column=2, pady=5)
        
        ctk.CTkLabel(cadre_tableau, text=f'{transaction["montant"]} €').grid(row=ligne, column=3, pady=5)
        ctk.CTkLabel(cadre_tableau, text=transaction["raison"]).grid(row=ligne, column=4, pady=5)
        
        bouton_supprimer = ctk.CTkButton(
            cadre_tableau, 
            text="❌", 
            width=30, 
            fg_color="#c0392b", 
            hover_color="#e74c3c", 
            command=lambda i=index: au_clic_supprimer(i)
        )
        bouton_supprimer.grid(row=ligne, column=5, padx=10, pady=5)

actualiser_tableau()
fenetre.mainloop()