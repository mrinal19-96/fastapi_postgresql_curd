from auth_db import engine, Base
import models

Base.metadata.create_all(bind=engine)