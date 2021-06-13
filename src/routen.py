from flask import session, abort, redirect, render_template, request, url_for, send_from_directory, jsonify
from src.init import app
from src.spiel import hole_sitzung, hole_alle_karten, hole_gespielte_karten, hole_karte
from src.spiel import neue_sitzung, neue_session, loesche_verwaiste_sitzungen
from src.spiel import ziehe_karte, lege_zurueck, ziehe_formular_ist_valide

@app.route('/ansichtsweise_aendern')
def ansichtsweise_aendern():
    ''' Setzt das Session-Cookie neu mit jeweils anderer Karten-Ansicht als der aktuellen.

    Routen:
    * /ansichtsweise_aendern
    '''
    try:
        optionen = session['sitzung']['optionen'].split(', ')
        if 'ansicht_schlicht' in optionen:
            optionen.remove('ansicht_schlicht')
        else:
            optionen.append('ansicht_schlicht')
        session['sitzung']['optionen'] = (', ').join(optionen)
        session.modified = True
        return jsonify(success=True)
    except:
        return jsonify(success=False)

# Fehlermeldungen


@ app.errorhandler(404)
def fehler_404(error):
    ''' Fehler (404)'''
    return render_template('fehler_404.html'), 404


@ app.errorhandler(500)
def fehler_500(error):
    ''' Fehler (500)'''
    return render_template('fehler_500.html'), 500


@ app.errorhandler(405)
def fehler_405(error):
    ''' Fehler (405)'''
    return render_template('fehler_404.html'), 405


# Eigentliches Spiel

@app.route('/')
def index():
    ''' Löscht verwaiste Sitzungen und gibt Index aus.

    Routen:
    * /
    '''
    loesche_verwaiste_sitzungen(session)
    return render_template('index.html')


@app.route('/neu', methods=['POST'])
@app.route('/neu/<string:einstellungen>', methods=['GET'])
def neu(einstellungen=[None]):
    ''' Konfigurationsmöglichkeiten übernehmen und neue Sitzung anlegen.

    Routen:
    * /neu
    '''
    if not ('standard' in einstellungen or request.method == 'POST'):
        abort(404)
    sitzung = neue_sitzung(session, einstellungen, request.form)
    return redirect(url_for('einladung', sitzung_id=sitzung.sitzung_id))


@ app.route('/einladung/<string:sitzung_id>')
def einladung(sitzung_id):
    ''' Spiel beginnen / Spiel beitreten.

    Parameter:
    * sitzung_id: str

    Routen:
    * /einladung/<string:sitzung_id>
    '''
    sitzung = hole_sitzung(sitzung_id)
    if sitzung is None:
        abort(404)
    # ggf. passende session anlegen
    if session.get('sitzung') is None:
        neue_session(session, sitzung.sitzung_id, sitzung.optionen)
    else:
        if session['sitzung']['id'] != sitzung_id:
            neue_session(session, sitzung.sitzung_id, sitzung.optionen)
    return render_template('spiel_einladung.html', sitzung=sitzung, stapel=app.config['SPIEL_STAPEL'])


@app.route('/ziehe', methods=['POST'])
def ziehe(stapel=app.config['SPIEL_STAPEL']['alle']):
    ''' Zieht eine oder zwei Karten. 

    Parameter:
    * stapel

    Routen:
    * /ziehe
    '''
    if session.get('sitzung') is None:
        abort(404)
    else:
        sitzung = hole_sitzung(session['sitzung'].get('id'))
        if sitzung is None:
            abort(404)
        if not ziehe_formular_ist_valide(sitzung, request.form):
            abort(404)
        stapel = request.form.get('stapel')
        if stapel is None:
            if ', ' in request.form.get('doppelkarte'):
                # es wird nur eine karte zurückgeben, nicht neu gezogen, und nur die eine behalten
                behalte = request.form.get('doppelkarte').split(', ')[0]
                lege_zurueck(session, sitzung, request.form)
                return redirect(url_for('karte', karten_id=behalte))
            stapel = request.form.get('doppelkarte')
        # valider ziehe-zug
        if app.config['SPIEL_OPTIONEN'][1] in sitzung.optionen:
            # es sollen zwei karten gezogen werden
            karten = list()
            karten.append(ziehe_karte(session, sitzung, stapel))
            karten.append(ziehe_karte(session, sitzung, stapel))
            # lege_zurueck legt abhängig von formular auch zwei karten zurück
            lege_zurueck(session, sitzung, request.form)
            if None in karten:
                session['sitzung']['spiel_beendet'] = True
                session.modified = True
                if karten[0] is None and karten[1] is None:
                    return redirect(url_for('karte', karten_id='leer'))
                else:
                    karte = karten[0]
                    if karte is None:
                        karte = karten[1]
                    session['sitzung']['spiel_beendet'] = True
                    session.modified = True
                    return redirect(url_for('karte', karten_id='leer', andere_karten_id=karte.id))
            return redirect(url_for('karte', karten_id=karten[0].id, andere_karten_id=karten[1].id))
        else:
            # es soll nur eine karte gezogen werden
            karte = ziehe_karte(session, sitzung, stapel)
            lege_zurueck(session, sitzung, request.form)
            if karte is None:
                session['sitzung']['spiel_beendet'] = True
                session.modified = True
                return redirect(url_for('karte', karten_id='leer'))
            return redirect(url_for('karte', karten_id=karte.id))


@ app.route('/karte/<string:karten_id>')
@ app.route('/karte/<string:karten_id>/karte/<string:andere_karten_id>')
def karte(karten_id, andere_karten_id=None):
    ''' Karte anzeigen.

    Parameter:
    * karten_id: str
    * andere_karten_id: str = None

    Routen:
    * /karte/<string:karten_id>
    * /karte/<string:karten_id>/karte/<string:andere_karten_id>
    '''
    # Sonderfälle
    if 'alle' in karten_id:
        # alle karten anzeigen
        karten = hole_alle_karten()
        return render_template('karte_alle.html', karten=karten)
    if 'leer' in karten_id:
        # das deck ist leer
        if session.get('sitzung') is None:
            abort(404)
        if not session['sitzung']['spiel_beendet']:
            abort(404)
        gespielte_karten = hole_gespielte_karten(session)
        optionen = dict()
        optionen['gespielte_karten'] = gespielte_karten
        if andere_karten_id is not None:
            # restkarte holen
            karte = hole_karte(andere_karten_id)
            if karte is None:
                abort(404)
            optionen['letzte_karte'] = karte
        return render_template('spiel_deck_leer.html', **optionen)

    # Regulär
    template = 'karte.html'
    karte = hole_karte(karten_id)
    if karte is None:
        abort(404)

    if andere_karten_id is not None:
        # zweite karte holen
        andere_karte = hole_karte(andere_karten_id)
        karte = [karte, andere_karte]
        if andere_karte is None:
            abort(404)
        template = 'karte_zwei.html'

    if session.get('sitzung') is None:
        return render_template(template, karte=karte, nur_anzeige=True)
    if karten_id not in session['sitzung'].get('gezogene_karten') or session['sitzung']['spiel_beendet']:
        return render_template(template, karte=karte, nur_anzeige=True)

    sitzung = hole_sitzung(session['sitzung'].get('id'))

    if sitzung is None:
        return render_template(template, karte=karte, nur_anzeige=True)
    if karten_id not in sitzung.ausgeteilte_karten.split(', ') and session['sitzung']['gezogene_karten']:
        return render_template(template, karte=karte, nur_anzeige=True)

    stapel_gewechselt = False
    if session['sitzung'].get('stapel_bereits_gewechselt') and not session['sitzung'].get('stapel_erfolgreich_gewechselt'):
        # der andere stapel ist leer
        session['sitzung']['stapel_erfolgreich_gewechselt'] = True
        stapel_gewechselt = True
        session.modified = True
    return render_template(template, karte=karte, sitzung=sitzung,
                           nur_anzeige=False, stapel=app.config['SPIEL_STAPEL'],
                           stapel_gewechselt=stapel_gewechselt,
                           stapel_leer=session['sitzung'].get('stapel_leer'))
