#!/usr/bin/env python3
from src.modelle import db

if __name__ == '__main__':
    db.create_all()
    db.session.commit()

