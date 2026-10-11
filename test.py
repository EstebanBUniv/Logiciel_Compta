import json
import os

FICHIER_SAUVEGARDE = "data.json"

MOIS_NUM = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4, "Mai": 5, "Juin": 6,
    "Juillet": 7, "Août": 8, "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
}

def cle_tri(transaction):
    """Trie chronologiquement par Année puis par Mois."""
    annee = int(transaction.get("annee", 2026))
    mois = MOIS_NUM.get(transaction.get("mois", "Janvier"), 1)
    
    return (annee, mois)

def charger_historique():
    if os.path.exists(FICHIER_SAUVEGARDE):
        with open(FICHIER_SAUVEGARDE, "r", encoding="utf-8") as f:
            historique = json.load(f)
            if type(historique) is dict:
                historique = [historique]
            
            # Trie la liste avant de l'afficher
            return sorted(historique, key=cle_tri)
    return []

def ajouter_transaction(mois, annee, type_transaction, montant, raison):
    historique = charger_historique()
    
    nouvelle_transaction = {
        "mois": mois,
        "annee": str(annee),
        "type": type_transaction,
        "montant": montant,
        "raison": raison
    }
    
    historique.append(nouvelle_transaction)
    historique.sort(key=cle_tri) # Trie aussi à la sauvegarde
    
    with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4)

def supprimer_transaction(index):
    historique = charger_historique()
    
    if 0 <= index < len(historique):
        del historique[index] 
        with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4)

def calculer_solde():
    historique = charger_historique()
    solde_total = 0.0
    for transaction in historique:
        if transaction["type"] == "Entrée":
            solde_total += transaction["montant"]
        elif transaction["type"] == "Dépense":
            solde_total -= transaction["montant"]
    return solde_total