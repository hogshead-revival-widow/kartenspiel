#!/usr/bin/env python3
from src.init import app
from src.routen import index, neu, einladung, karte, ziehe
from src.routen import ansichtsweise_aendern, fehler_404, fehler_500, fehler_405
from src.admin import admin

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2400, debug=True)
