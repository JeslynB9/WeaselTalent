# entry point
from db import engine
from models import Base

# create all tables defined on `Base`
Base.metadata.create_all(bind=engine)