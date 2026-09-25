# Alerte solde bancaire négatif — Pennylane

Automatisation d'une alerte quotidienne destinée à un cabinet comptable : détecter et notifier, par collaborateur, les clients dont le solde bancaire est passé en négatif.

⚠️ **Dépôt de démonstration** : ce projet reproduit l'architecture réelle mise en place pour un cabinet comptable, mais avec des données entièrement fictives (`clients.csv`) et sans secrets valides. Il ne s'exécute pas réellement.

## Contexte

Un cabinet comptable gérant plusieurs dizaines de dossiers clients sur Pennylane avait besoin d'une détection automatique des clients en tension de trésorerie, répartie entre plusieurs collaborateurs selon leur portefeuille.

## Architecture

clients.csv (correspondance client → collaborateur)
│
▼
GitHub Actions (déclenchement programmé, lundi 10h Europe/Paris)
│
│
▼
script.py
  ├─ lire_clients()          → lit le CSV
  ├─ recuperer_comptes()     → appelle l'API Pennylane (par dossier client)
  ├─ filtrer_et_regrouper()  → ne garde que les soldes négatifs, regroupe par collaborateur
  └─ envoyer_email()         → un email par collaborateur, via SMTP Gmail
\`\`\`

## Défis techniques rencontrés

- **L'API Pennylane impose un appel par dossier client** (header `X-Company-Id`), pas d'endpoint global — la boucle et le volume d'appels ont dû être pensés en conséquence.
- **Limite de débit de l'API** (5 requêtes/seconde) : une pause (`time.sleep`) a été ajoutée entre chaque appel pour éviter les erreurs `429`.
- **GitHub Actions ne programme qu'en UTC** : pour un déclenchement fiable toute l'année malgré le changement d'heure été/hiver, deux horaires cron sont déclarés, et le script vérifie lui-même l'heure réelle à Paris (`zoneinfo`) avant d'agir.
- **Un client peut avoir plusieurs comptes bancaires** : décision métier de déclencher l'alerte dès qu'un seul compte est négatif, plutôt que de raisonner sur un solde total.

## Stack

Python · API REST · GitHub Actions · SMTP

## Ce que ce dépôt ne montre pas

Le vrai dépôt opérationnel (données clients réelles, vrais secrets) reste privé, pour des raisons évidentes de confidentialité vis-à-vis du cabinet comptable.
