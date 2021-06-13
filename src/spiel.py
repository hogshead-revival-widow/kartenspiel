from flask import session
from datetime import datetime, timedelta, timezone
from src.init import app, db
from src.modelle import Karte, Sitzung, abfragen


def neue_session(session, sitzung_id, optionen):
    ''' Erstellte neue Session (Cookie)
    '''
    session.clear()
    session['sitzung'] = {
        'id': sitzung_id,
        'gezogene_karten': list(),
        'stapel_bereits_gewechselt': False,
        'stapel_erfolgreich_gewechselt': False,
        'stapel_leer': None,
        'optionen': optionen,
        'spiel_beendet': False,
    }
    # sonst wird die session nicht geupdated, wegen mutable-objekten
    session.modified = True


def neue_sitzung(session, einstellungen, formular):
    ''' Erstellt neue Sitzung, sowohl in Datenbank als auch als Cookie.

    Parameter:
    * session (flask.session)
    * einstellungen
    * request (flask.request)

    Gibt zurück:
    * sitzung (Sitzung)
    '''
    if 'standard' in einstellungen:
        optionen = "ist_moderiert"
    else:
        optionen = list()
        for option in app.config['SPIEL_OPTIONEN']:
            if formular.get(option) is not None:
                optionen.append(option)
        optionen = (', ').join(optionen)
    sitzung = Sitzung.neu(optionen)
    neue_session(session, sitzung.sitzung_id, optionen)
    return sitzung


def loesche_verwaiste_sitzungen(session):
    ''' Löscht verwaiste Sitzungen in der Datenbank und löscht Cookie.

    Eine Sitzung ist verwaist, wenn sie älter als `app.config['SPIEL_LOESCHE_SITZUNG_NACH']` ist.

    Parameter:
    * session (flask.session)
    '''
    session.clear()
    # ist der letzte zugriff länger als app.config['SPIEL_LOESCHE_SITZUNG_NACH'] Stunden her?
    verwaiste_sitzungen = Sitzung.query.filter(
        Sitzung.letzter_zugriff <=
        # sqllite-serverzeit ist in utc
        (datetime.now(timezone.utc) -
         timedelta(hours=app.config['SPIEL_LOESCHE_SITZUNG_NACH']))
    ).all()
    if verwaiste_sitzungen is not None:
        for sitzung in verwaiste_sitzungen:
            db.session.delete(sitzung)
        db.session.commit()

def hole_sitzung(sitzung_id):
    ''' Holt existierende Sitzung.

    Parameter:
    * sitzung_id 

    Gibt zurück:
    * Sitzung
    '''
    sitzung_id = str(sitzung_id)
    sitzung = Sitzung.aus_sitzung_id(sitzung_id)
    return sitzung


def ziehe_formular_ist_valide(sitzung, formular):
    ''' Hat das Formular alle erforderlichen Felder?

    Parameter:
    * Formular (flask.request.form)
    * sitzung (Sitzung)

    Gibt zurück:
    True/False
    '''
    if formular.get('einzelkarte') is None and formular.get('doppelkarte') is None:
        return False
    if formular.get('stapel') is None and formular.get('einzelkarte') is not None:
        return False
    # einzelkarte in option und hat einen von allen möglichen stapel: app.config['SPIEL_STAPEL']['zwei_karten']
    elif formular.get('stapel') not in app.config['SPIEL_STAPEL']['zwei_karten'] and formular.get('einzelkarte') is not None:
        return False
    if formular.get('karte_zurueck') is None:
        return False
    # doppelkarte in option
    if formular.get('einzelkarte') is None and formular.get('karte_zurueck_2') is None and formular.get('karte_zurueck') != "0":
        return False
    return True


def hole_anderern_stapel(session, stapel):
    ''' Holt anderen Stapel, prüft NICHT die Spieloption.

    Parameter:
    * Session (flask.session)
    * Stapel

    Gibt zurück: 
    anderer_stapel'''

    anderer_stapel = app.config['SPIEL_STAPEL']['zwei_stapel'][0]
    if app.config['SPIEL_STAPEL']['zwei_stapel'][0] in stapel:
        anderer_stapel = app.config['SPIEL_STAPEL']['zwei_stapel'][1]
    session['sitzung']['stapel_bereits_gewechselt'] = True
    session['sitzung']['stapel_leer'] = stapel
    session.modified = True
    return anderer_stapel

def ziehe_karte(session, sitzung, stapel):
    ''' Zieht eine Karte und schreibt gezogene Karten in Cookie.

    Parameter:
    * sitzung (Sitzung)
    * stapel

    Gibt zurück:
    Karte oder None'''

    # es wird immer nur eine karte gezogen!
    # wenn ausschluss gesetzt ist, wird diese karte zusätzlich zu sitzung.ausgeteilt ignoriert
    ausgeteilte_karten = sitzung.ausgeteilte_karten
    if ausgeteilte_karten is None:
        ausgeteilte_karten = ""
    karte = abfragen['ziehe_aus_stapel'][stapel](ausgeteilte_karten)
    
    # ggf. stapel wechseln
    if karte is None:
         if app.config['SPIEL_OPTIONEN'][0] in sitzung.optionen:
             # nur stapel wechseln, wenn `zwei_stapel` gespielt wird
            if not session['sitzung'].get('stapel_bereits_gewechselt') or app.config['SPIEL_OPTIONEN'][1] in sitzung.optionen:
                # und wenn (bei einzelkarten-modus) der stapel bereits gewechselt worden ist
                anderer_stapel = hole_anderern_stapel(session, stapel)
                karte = abfragen['ziehe_aus_stapel'][anderer_stapel](ausgeteilte_karten)

    if karte is not None:
        # in cookie und sitzung die gezogene karte als ausgeteilt übertragen
        session['sitzung']['gezogene_karten'].append(str(karte.id))
        session.modified = True
        if ausgeteilte_karten != "":
            ausgeteilte_karten = ausgeteilte_karten.split(', ')
            ausgeteilte_karten.append(str(karte.id))
            ausgeteilte_karten = (', ').join(ausgeteilte_karten)
        else:
            ausgeteilte_karten = str(karte.id)
        sitzung.ausgeteilte_karten = ausgeteilte_karten
        db.session.commit()

    return karte

def lege_zurueck(session, sitzung, formular):
    ''' Legt Karte zurück.

    Parameter:
    * session (flask.session)
    * sitzung (Sitzung)
    * formular (flask.request.form)
    '''
    # spiel ist moderiert, es gibt nichts zu tun
    if  app.config['SPIEL_OPTIONEN'][2] in sitzung.optionen:
        return None

    # es ist der erste zug, gibt nix zum zurücklegen
    if formular.get('karte_zurueck') == "0":
        return None

    ausgeteilte_karten = sitzung.ausgeteilte_karten
    ausgeteilte_karten = sitzung.ausgeteilte_karten.split(', ')
    
    zurueckzulegende_karten = list()

    if 'einzelkarte' in formular:
        zurueckzulegende_karten = [formular.get('karte_zurueck')]
    if 'doppelkarte' in formular:
        if ',' in formular.get('doppelkarte'):
            # vgl. templates/karte_zwei.html, <input>
            zurueckzulegende_karten = [formular.get('doppelkarte').split(', ')[1]]
        else:
            zurueckzulegende_karten = [formular.get('karte_zurueck'), formular.get('karte_zurueck_2')]

    if len(zurueckzulegende_karten) == 0:
        return None
    for karte in zurueckzulegende_karten:
        if karte in ausgeteilte_karten and karte in session['sitzung'].get('gezogene_karten', []):
            ausgeteilte_karten.remove(karte)
    
    sitzung.ausgeteilte_karten = (', ').join(ausgeteilte_karten)
    db.session.commit()

def hole_gespielte_karten(session):
    ''' Gibt gespielte Karten der Session zurück.

    Parameter:
    * session (flask.session)

    Gibt zurück:
    * gespielte_karten (list)'''
    gespielte_karten = session['sitzung'].get('gezogene_karten')
    gespielte_karten = abfragen['gezogene_karten'](gespielte_karten)
    return gespielte_karten

def hole_karte(karten_id):
    ''' Gibt Karte zurück.

    Parameter:
    * karten_id
    
    Gibt zurück:
    * karte (Karte)
    '''
    return Karte.query.get(karten_id)

def hole_alle_karten():
    ''' Gibt alle Karten zurück.

    Gibt zurück:
    * [Karte, Karte,...]
    '''
    return abfragen['alle_karten']()