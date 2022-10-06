from unicodedata import name
from oleorcarl.database.models import db, Student

print(db.get_tables())

Student(    
    name="Alistair Pattison",
    email="pattisona@carleton.edu",
    school="carleton",
    image="Alistair Pattison",
)