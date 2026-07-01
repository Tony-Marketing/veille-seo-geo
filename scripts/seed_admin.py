"""Seed idempotent des données d'administration."""

from sqlalchemy.orm import Session

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models import AiProvider, ApplicationSetting, Permission, Role, SystemParameter

PERMISSIONS = [
    ("website.read", "Lire les sites", "website"),
    ("website.write", "Modifier les sites", "website"),
    ("website.delete", "Supprimer les sites", "website"),
    ("entity.read", "Lire les entites", "entity"),
    ("entity.write", "Modifier les entites", "entity"),
    ("entity.delete", "Supprimer les entites", "entity"),
    ("keyword.read", "Lire les mots-cles", "keyword"),
    ("keyword.write", "Modifier les mots-cles", "keyword"),
    ("keyword.delete", "Supprimer les mots-cles", "keyword"),
    ("competitor.read", "Lire les concurrents", "competitor"),
    ("competitor.write", "Modifier les concurrents", "competitor"),
    ("competitor.delete", "Supprimer les concurrents", "competitor"),
    ("url.read", "Lire les URLs", "url"),
    ("url.write", "Modifier les URLs", "url"),
    ("url.delete", "Supprimer les URLs", "url"),
    ("report.read", "Lire les rapports", "report"),
    ("report.write", "Modifier les rapports", "report"),
    ("report.delete", "Supprimer les rapports", "report"),
    ("project_task.read", "Lire les taches projet", "project_task"),
    ("project_task.write", "Modifier les taches projet", "project_task"),
    ("project_task.delete", "Supprimer les taches projet", "project_task"),
    ("user.read", "Lire les utilisateurs", "user"),
    ("user.write", "Modifier les utilisateurs", "user"),
    ("admin.read", "Lire l'administration", "admin"),
    ("admin.write", "Modifier l'administration", "admin"),
    ("ai.read", "Lire la configuration IA", "ai"),
    ("ai.write", "Modifier la configuration IA", "ai"),
    ("apikey.read", "Lire les clés API", "apikey"),
    ("apikey.write", "Modifier les clés API", "apikey"),
    ("settings.read", "Lire les paramètres", "settings"),
    ("settings.write", "Modifier les paramètres", "settings"),
    ("logs.read", "Lire les journaux", "logs"),
]

BUSINESS_MODULES = {"website", "entity", "keyword", "competitor", "url", "report", "project_task"}
ADMIN_BUSINESS_PERMISSION_CODES = {code for code, _label, module in PERMISSIONS if module in BUSINESS_MODULES}

ROLES = [
    ("Administrateur", "Accès complet à la plateforme"),
    ("SEO", "Pilotage SEO"),
    ("Marketing", "Pilotage marketing"),
    ("Développeur", "Maintenance technique"),
    ("Rédacteur", "Gestion éditoriale"),
    ("Consultation", "Accès en lecture seule"),
]

AI_PROVIDERS = ["OpenAI", "Anthropic", "Google Gemini", "Mistral", "xAI", "Perplexity", "DeepSeek", "Ollama"]


def run_seed(db: Session) -> None:
    """Insert missing administration demonstration data."""

    for code, label, module in PERMISSIONS:
        if db.query(Permission).filter(Permission.code == code).first() is None:
            db.add(Permission(code=code, label=label, module=module))

    for name, description in ROLES:
        if db.query(Role).filter(Role.name == name).first() is None:
            db.add(Role(name=name, description=description, is_system=True))

    db.flush()

    admin_role = db.query(Role).filter(Role.name == "Administrateur").first()
    if admin_role is not None:
        existing_codes = {permission.code for permission in admin_role.permissions}
        for code in sorted(ADMIN_BUSINESS_PERMISSION_CODES - existing_codes):
            permission = db.query(Permission).filter(Permission.code == code).first()
            if permission is not None:
                admin_role.permissions.append(permission)

    for name in AI_PROVIDERS:
        if db.query(AiProvider).filter(AiProvider.name == name).first() is None:
            db.add(AiProvider(name=name, description=f"Fournisseur IA {name}", is_active=True))

    default_settings = {
        "app.name": "Veille SEO-GEO Groupe A.P&Partner",
        "app.timezone": "Europe/Paris",
        "app.language": "fr",
        "app.maintenance": "false",
    }
    for key, value in default_settings.items():
        if db.query(ApplicationSetting).filter(ApplicationSetting.key == key).first() is None:
            db.add(ApplicationSetting(key=key, value=value, category="global", is_public=True))

    default_parameters = [
        ("seo", "crawler.user_agent", "VeilleSEO-GEOBot/1.0"),
        ("geo", "analysis.max_prompts", "100"),
        ("ai", "generation.temperature", "0.3"),
    ]
    for category, key, value in default_parameters:
        exists = db.query(SystemParameter).filter(
            SystemParameter.category == category,
            SystemParameter.key == key,
        )
        if exists.first() is None:
            db.add(SystemParameter(category=category, key=key, value=value))

    db.commit()


def main() -> None:
    """Run the administration seed."""

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        run_seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
