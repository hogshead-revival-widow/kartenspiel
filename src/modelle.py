import random
from sqlalchemy import text
from src.init import db
from src.tiere import alle_tiere


def zuefalliges_tier(anzahl=1):
    if anzahl > 1:
        tiere = list()
        for i in range(1, anzahl + 1):
            tiere.append(random.choice(alle_tiere))
        return ('-').join(tiere)
    return random.choice(alle_tiere)


def generiere_sitzungs_id(versuche=2):
    spiel_id = zuefalliges_tier(versuche)
    query = f'SELECT sitzung.id FROM sitzung WHERE sitzung.sitzung_id = "{spiel_id}"'
    query = db.engine.execute(text(query)).scalar()
    if query is not None:
        # id ist bereits vergeben
        versuche += 1
        generiere_sitzungs_id(versuche)
    return spiel_id




class Karte(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    kurzbeschreibung = db.Column(db.String(), nullable=False)
    bild_datei = db.Column(db.String(), nullable=False)
    ist_leitsatz = db.Column(db.Boolean(), default=False)
    eigenschaften = db.Column(db.String())

    def __repr__(self):
        return '<Karte %r>' % self.name

    def __len__(self):
        return 1


class Sitzung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sitzung_id = db.Column(db.String(), nullable=False,
                           default=generiere_sitzungs_id)
    optionen = db.Column(db.String(), default=str())
    letzter_zugriff = db.Column(
        db.DateTime(), server_default=db.func.now(),
        onupdate=db.func.now())
    ausgeteilte_karten = db.Column(db.String())

    def __repr__(self):
        return '<Sitzung %r>' % self.sitzung_id

    @classmethod
    def neu(cls, optionen):
        sitzung = cls(optionen=optionen)
        db.session.add(sitzung)
        db.session.commit()
        return sitzung

    @classmethod
    def aus_sitzung_id(cls, sitzung_id):
        return cls.query.filter_by(sitzung_id=sitzung_id).first()


ziehe_aus_stapel = {
    # x = konkrete_sitzung.ausgeteilte_karten
    'alle': lambda x: Karte.query.filter(Karte.id.notin_(x.split(', '))).order_by(db.func.random()).first(),
    # x = konkrete_sitzung.ausgeteilte_karten
    'person': lambda x: Karte.query.filter(
        Karte.ist_leitsatz == False,
        Karte.id.notin_(x.split(', '))).order_by(db.func.random()).first(),
    # x = konkrete_sitzung.ausgeteilte_karten
    'leitsatz': lambda x: Karte.query.filter(
        Karte.ist_leitsatz == True,
        Karte.id.notin_(x.split(', '))).order_by(db.func.random()).first()

}
abfragen = {
    'alle_karten': Karte.query.all,
    'ziehe_aus_stapel': ziehe_aus_stapel,
    # x = konkrete sitzung
    'ausgeteilte_karten': lambda x: [Karte.query.get(karte_id) for karte_id in x.ausgeteilte_karten.split(', ')],
    # x = liste gezogener karten
    'gezogene_karten': lambda x: Karte.query.filter(
        Karte.id.in_(x)).all(),
}
