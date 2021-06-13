
from flask import url_for
from flask_admin import Admin, form
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.event import listens_for
from jinja2 import Markup
from wtforms import validators, TextAreaField, TextField
from werkzeug.utils import secure_filename
import os
from src.init import app, db
from src.modelle import Karte, Sitzung


file_path = os.path.join(app.config['UPLOAD_FOLDER'])


@listens_for(Karte, 'after_delete')
def del_image(mapper, connection, target):
    if target.bild_datei:
        # Lösche Bild
        try:
            os.remove(os.path.join(file_path, target.bild_datei))
        except OSError:
            pass

        # Lösche Thumbnail
        try:
            os.remove(os.path.join(file_path,
                                   form.thumbgen_filename(target.bild_datei)))
        except OSError:
            pass


class KarteView(ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.bild_datei:
            return ''

        return Markup('<img src="%s">' % url_for('static',
                                                 filename='img/'+form.thumbgen_filename(model.bild_datei)))

    column_formatters = {
        'bild_datei': _list_thumbnail
    }

    form_extra_fields = {
        'eigenschaften': TextField('Eigenschaften (HTML erlaubt)'),
        'bild_datei': form.ImageUploadField('Bild',
                                            [validators.DataRequired()],
                                            base_path=file_path,
                                            thumbnail_size=(100, 100, True)),
        'kurzbeschreibung': TextAreaField('Beschreibung (HTML erlaubt)', [validators.DataRequired()])}
    column_labels = dict(ist_leitsatz='Leitsatz?', bild_datei='Bild')
    column_searchable_list = ['eigenschaften', 'kurzbeschreibung', 'name']
    column_editable_list = ['name', 'eigenschaften', 'kurzbeschreibung',
                            'ist_leitsatz']
    create_modal = True
    edit_modal = True
    can_export = True


class SitzungView(ModelView):
    column_searchable_list = ['sitzung_id', 'optionen']
    column_labels = dict(sitzung_id='Spielcode', bild_datei='Bild')
    create_modal = True
    edit_modal = True
    can_export = True


admin = Admin(app, name='Verwaltung', template_mode='bootstrap4')
admin.add_view(KarteView(Karte, db.session))
admin.add_view(SitzungView(Sitzung, db.session))
