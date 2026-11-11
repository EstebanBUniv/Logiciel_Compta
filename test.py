import json
import os
import csv

FICHIER_SAUVEGARDE = "data.json"
FICHIER_COLOC = "coloc.json" # Nouveau mini-fichier pour sauvegarder son total à lui

MOIS_NUM = {
    "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4, "Mai": 5, "Juin": 6,
    "Juillet": 7, "Août": 8, "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
}

def cle_tri(transaction):
    annee = int(transaction.get("annee", 2026))
    mois = MOIS_NUM.get(transaction.get("mois", "Janvier"), 1)
    return (annee, mois)

def charger_historique():
    if os.path.exists(FICHIER_SAUVEGARDE):
        with open(FICHIER_SAUVEGARDE, "r", encoding="utf-8") as f:
            historique = json.load(f)
            if type(historique) is dict: historique = [historique]
            return sorted(historique, key=cle_tri)
    return []

def ajouter_transaction(mois, annee, type_transaction, montant, raison, contexte):
    historique = charger_historique()
    historique.append({
        "mois": mois, "annee": str(annee), "type": type_transaction,
        "montant": montant, "raison": raison, "contexte": contexte
    })
    historique.sort(key=cle_tri) 
    with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4)

def modifier_transaction(index, mois, annee, type_transaction, montant, raison, contexte):
    historique = charger_historique()
    if 0 <= index < len(historique):
        historique[index] = {
            "mois": mois, "annee": str(annee), "type": type_transaction,
            "montant": montant, "raison": raison, "contexte": contexte
        }
        historique.sort(key=cle_tri)
        with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4)

def supprimer_transaction(index):
    historique = charger_historique()
    if 0 <= index < len(historique):
        del historique[index] 
        with open(FICHIER_SAUVEGARDE, "w", encoding="utf-8") as f:
            json.dump(historique, f, indent=4)

# --- GESTION DU COLOCATAIRE ---
def lire_total_coloc():
    """Lit la somme totale payée par le colocataire."""
    if os.path.exists(FICHIER_COLOC):
        with open(FICHIER_COLOC, "r", encoding="utf-8") as f:
            return json.load(f).get("total_coloc", 0.0)
    return 0.0

def sauvegarder_total_coloc(montant):
    """Sauvegarde la somme totale payée par le colocataire."""
    with open(FICHIER_COLOC, "w", encoding="utf-8") as f:
        json.dump({"total_coloc": montant}, f)

def calculer_dette_coloc():
    """Formule : (Mes dépenses coloc - Ses dépenses coloc) / 2"""
    historique = charger_historique()
    mes_depenses_coloc = 0.0
    
    for t in historique:
        # Rétrocompatibilité au cas où tu aurais enregistré un "Coloc (Moi)" tout à l'heure
        ctx = t.get("contexte", "Perso")
        if t["type"] == "Dépense" and ctx in ["Coloc", "Coloc (Moi)"]:
            mes_depenses_coloc += t["montant"]
            
    ses_depenses_coloc = lire_total_coloc()
    
    bilan = (mes_depenses_coloc - ses_depenses_coloc) / 2
    return mes_depenses_coloc, ses_depenses_coloc, bilan

def exporter_csv():
    """Génère un fichier CSV lisible par Excel avec tout l'historique."""
    historique = charger_historique()
    nom_fichier = "export_compta.csv"
    
    with open(nom_fichier, mode="w", newline="", encoding="utf-8-sig") as fichier_csv:
        
        # --- LA SOLUTION EST ICI : quoting=csv.QUOTE_ALL ---
        # Ça force les guillemets autour de toutes les valeurs
        writer = csv.writer(fichier_csv, delimiter=";", quoting=csv.QUOTE_ALL)
        
        writer.writerow(["Année", "Mois", "Type", "Montant", "Raison", "Contexte"])
        
        for t in historique:
            # On force 2 chiffres après la virgule (ex: 456,00)
            montant_formate = f"{float(t['montant']):.2f}".replace(".", ",")
            
            writer.writerow([
                t.get("annee", "2026"),
                t["mois"],
                t["type"],
                montant_formate,
                t["raison"],
                t.get("contexte", "Perso")
            ])
            
    return nom_fichier