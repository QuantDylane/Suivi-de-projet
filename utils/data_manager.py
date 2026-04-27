import json
import os
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT_DIR, "data", "project_data.json")

DEFAULT_DATA = {
    "project": {
        "name": "Refonte du portail client",
        "description": "Modernisation complète du portail client en React et API REST.",
        "deadline": "2026-12-31",
        "created_at": "2026-01-01",
    },
    "members": [
        {"id": 1, "name": "Alice Martin", "role": "Chef de projet"},
        {"id": 2, "name": "Bob Dupont", "role": "Développeur Back-end"},
        {"id": 3, "name": "Clara Bernard", "role": "Développeuse Front-end"},
        {"id": 4, "name": "David Leroy", "role": "Designer UX/UI"},
    ],
    "tasks": [
        {
            "id": 1,
            "title": "Analyse des besoins",
            "description": "Recueil et analyse des besoins fonctionnels.",
            "assigned_to": 1,
            "status": "done",
            "priority": "high",
            "deadline": "2026-02-15",
            "created_at": "2026-01-05",
        },
        {
            "id": 2,
            "title": "Maquettes UI",
            "description": "Création des maquettes Figma pour toutes les pages.",
            "assigned_to": 4,
            "status": "done",
            "priority": "high",
            "deadline": "2026-03-01",
            "created_at": "2026-01-10",
        },
        {
            "id": 3,
            "title": "Architecture technique",
            "description": "Définition de l'architecture back-end et choix technologiques.",
            "assigned_to": 2,
            "status": "done",
            "priority": "high",
            "deadline": "2026-03-15",
            "created_at": "2026-01-15",
        },
        {
            "id": 4,
            "title": "Développement API REST",
            "description": "Implémentation des endpoints de l'API.",
            "assigned_to": 2,
            "status": "in_progress",
            "priority": "high",
            "deadline": "2026-06-30",
            "created_at": "2026-03-20",
        },
        {
            "id": 5,
            "title": "Intégration frontend",
            "description": "Développement des composants React.",
            "assigned_to": 3,
            "status": "in_progress",
            "priority": "medium",
            "deadline": "2026-07-31",
            "created_at": "2026-03-20",
        },
        {
            "id": 6,
            "title": "Tests unitaires back-end",
            "description": "Couverture de tests pour l'API.",
            "assigned_to": 2,
            "status": "todo",
            "priority": "medium",
            "deadline": "2026-09-15",
            "created_at": "2026-04-01",
        },
        {
            "id": 7,
            "title": "Tests d'intégration",
            "description": "Tests end-to-end de l'application.",
            "assigned_to": 3,
            "status": "todo",
            "priority": "medium",
            "deadline": "2026-10-01",
            "created_at": "2026-04-01",
        },
        {
            "id": 8,
            "title": "Recette utilisateur (UAT)",
            "description": "Phase de recette avec les utilisateurs finaux.",
            "assigned_to": 1,
            "status": "todo",
            "priority": "high",
            "deadline": "2026-11-15",
            "created_at": "2026-04-01",
        },
        {
            "id": 9,
            "title": "Déploiement en production",
            "description": "Mise en production et suivi post-déploiement.",
            "assigned_to": 1,
            "status": "todo",
            "priority": "high",
            "deadline": "2026-12-15",
            "created_at": "2026-04-01",
        },
    ],
}

STATUS_LABELS = {
    "todo": "À faire",
    "in_progress": "En cours",
    "done": "Terminé",
}

STATUS_COLORS = {
    "todo": "#9E9E9E",
    "in_progress": "#FF9800",
    "done": "#4CAF50",
}

PRIORITY_LABELS = {
    "low": "Faible",
    "medium": "Moyenne",
    "high": "Haute",
}

PRIORITY_COLORS = {
    "low": "#64B5F6",
    "medium": "#FFB74D",
    "high": "#E57373",
}


def load_data() -> dict:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_member_name(data: dict, member_id: int) -> str:
    for member in data.get("members", []):
        if member["id"] == member_id:
            return member["name"]
    return "Non assigné"


def get_next_id(items: list) -> int:
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def compute_progress(tasks: list) -> dict:
    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "done")
    in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
    todo = sum(1 for t in tasks if t["status"] == "todo")
    pct = round((done / total) * 100) if total > 0 else 0
    return {
        "total": total,
        "done": done,
        "in_progress": in_progress,
        "todo": todo,
        "pct": pct,
    }


def days_until(date_str: str) -> int:
    target = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (target - datetime.today().date()).days
