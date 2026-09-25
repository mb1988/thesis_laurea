# -*- coding: utf-8 -*-
"""Create the local SQLite database and the users ``manage.py setup`` made.

Original credentials (from 2014 manage.py): admin/password, guest/password.
"""

import bootstrap  # noqa: F401  (env defaults + shims)

from app import app, dbsqla
from app.user.models import User

USERS = (
    ("admin", "admin@gmail.com", True),
    ("guest", "guest@gmail.com", False),
)


def main():
    with app.app_context():
        dbsqla.create_all()
        created = []
        for username, email, is_admin in USERS:
            exists = dbsqla.session.query(User).filter_by(username=username).first()
            if exists:
                continue
            dbsqla.session.add(
                User(username=username, email=email, password="password", admin=is_admin)
            )
            created.append(username)
        dbsqla.session.commit()

    print("tables ready in %s" % app.config["SQLALCHEMY_DATABASE_URI"])
    print("users created: %s" % (", ".join(created) if created else "none (already present)"))


if __name__ == "__main__":
    main()
