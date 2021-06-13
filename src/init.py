from flask import Flask
from flask_basicauth import BasicAuth
import os
from flask_sqlalchemy import SQLAlchemy


# Nicht Pfad zu dieser Datei, sondern Rootverzeichnis des Spiels
basispfad = '/Pfad/Zum/Kartenspiel'
templates = os.path.join(basispfad, 'templates')
static = os.path.join(basispfad, 'static')
app = Flask(__name__, template_folder=templates, static_folder=static)

'''
// Wenn Passwortschutz gewünscht, auskommentieren und setzen
app.config['BASIC_AUTH_USERNAME'] = ''
app.config['BASIC_AUTH_PASSWORD'] = ''
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)
'''

datenbankpfad = os.path.join(basispfad, 'db/datenbank.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + datenbankpfad
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'yoursecretkey'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = os.path.join(basispfad, 'static/img')
app.config['SPIEL_LOESCHE_SITZUNG_NACH'] = 6 # in stunden
app.config['SPIEL_OPTIONEN'] = ['zwei_stapel', 'zwei_karten', 'ist_moderiert', 'ansicht_schlicht']
app.config['SPIEL_STAPEL']  = {
    'zwei_stapel': ['person', 'leitsatz'],
    'zwei_karten': ['alle', 'person', 'leitsatz'],
    'alle': 'alle'
}
