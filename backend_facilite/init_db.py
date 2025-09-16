from database import Base, engine
import models  # importe tous tes modèles ici

def init_db():
    print("🚀 Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées avec succès !")

if __name__ == "__main__":
    init_db()
