"""
Usage:  python make_admin.py <username>
Promotes a user to the 'admin' role.
"""
import sys
from database import SessionLocal
from models import User

if len(sys.argv) != 2:
    print("Usage: python make_admin.py <username>")
    sys.exit(1)

username = sys.argv[1]
db = SessionLocal()
try:
    user = db.query(User).filter_by(username=username).first()
    if not user:
        print(f"User '{username}' not found.")
        sys.exit(1)
    user.role = "admin"
    db.commit()
    print(f"'{username}' is now an admin.")
finally:
    db.close()
