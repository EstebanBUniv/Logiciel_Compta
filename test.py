import json
import os

FICHIER_SAUVEGARDE = "data.json"

def charger_historique():
    """Lit le fichier JSON et retourne la liste des transactions."""
    if os.path.exists(FICHIER_SAUVEGARDE):
        with open(FICHIER_SAUVEGARDE, "r", encoding="utf-8") as f:
            historique = json.load(f)
            if type(historique) is dict:
                return [historique]
            return historique
    return []

def ajouter_transaction(mois, annee, type_transaction, montant, raison):
    """Ajoute une transaction et sauvegarde le fichier."""
    historique = charger_historique()
    
    nouvelle_transaction = {
        "mois": mois,
        "annee": annee,
        "type": type_transaction,
        "montant": montant,
        "raison": raison
    }
    
    historique.append(nouvelle_transaction)
    
    with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4)

def supprimer_transaction(index):
    """Supprime une transaction à l'index donné et sauvegarde le fichier."""
    historique = charger_historique()
    
    if 0 <= index < len(historique):
        del historique[index] 
        
        with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4)