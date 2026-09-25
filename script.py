import requests
import time
import os
import csv
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo

def lire_clients():
  with open("clients.csv", newline="", encoding="utf-8") as f:
    clients = list(csv.DictReader(f))
  return clients

def recuperer_comptes(company_id):
  token = os.environ["PENNYLANE_TOKEN"]
  headers = {
    "accept": "application/json",
    "authorization": "Bearer " + token,
    "X-Company-Id": company_id
  }
  reponse = requests.get("https://app.pennylane.com/api/external/v2/bank_accounts", headers=headers)
  time.sleep(0.3)

  return reponse.json()["items"]

def filtrer_et_regrouper(clients):
  alertes = {}
  for client in clients:
    comptes = recuperer_comptes(client["company_id"])
    for compte in comptes:
      solde = float(compte["balance"])
      if solde < 0:
        email = client["collaborateur-email"]
        if email not in alertes:
          alertes[email] = []
        alertes[email].append(client["company_name"] + " : " + str(solde) + " €")
  return alertes

def envoyer_email(destinataire, liste_clients):
  expediteur = os.environ["GMAIL_ADDRESS"]
  mot_de_passe = os.environ["GMAIL_APP_PASSWORD"]
  if len(liste_clients) == 1:
    sujet = "Solde négatif chez " + liste_clients[0].split(" : ")[0]
  else:
    sujet = str(len(liste_clients)) + " clients en solde négatif aujourd'hui"
  texte = "\n".join(liste_clients)
  message = MIMEText(texte)
  message["Subject"] = sujet
  message["From"] = expediteur
  message["To"] = destinataire

  serveur = smtplib.SMTP("smtp.gmail.com", 587)
  serveur.starttls()
  serveur.login(expediteur, mot_de_passe)
  serveur.send_message(message)
  serveur.quit()

def est_lundi_10h():
  maintenant = datetime.now(ZoneInfo("Europe/Paris"))
  return maintenant.weekday() == 0 and maintenant.hour == 10

if __name__ == "__main__":
  if est_lundi_10h():
    clients = lire_clients()
    alertes = filtrer_et_regrouper(clients)
    for destinataire in alertes:
      envoyer_email(destinataire, alertes[destinataire])
