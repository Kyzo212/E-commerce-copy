from database import engine, Base
import models  # registers Product on Base.metadata

Base.metadata.create_all(engine)
print("Database tables created.")
