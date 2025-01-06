from flask import Flask, render_template, request, redirect, url_for, send_file, make_response, flash, abort, current_app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
import os
import pdfkit
import platform
import logging
from datetime import datetime

# Configure wkhtmltopdf path based on OS
if platform.system() == 'Windows':
    WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:
    WKHTMLTOPDF_PATH = 'wkhtmltopdf'

try:
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
except Exception as e:
    print(f"Warning: PDF generation may not work. Error: {e}")
    config = None

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checklist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.debug = True

db = SQLAlchemy(app)

class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_controle = db.Column(db.Date, nullable=False)
    type_checklist = db.Column(db.String(20), nullable=False)
    responsable_electrique = db.Column(db.String(100))
    responsable_atelier = db.Column(db.String(100))
    inspecteur_methode = db.Column(db.String(100))
    categorie_engin = db.Column(db.String(50))
    numero_serie_moteur = db.Column(db.String(50))
    numero_serie_ecm = db.Column(db.String(50))
    hm_actuel = db.Column(db.Float)
    type_revision = db.Column(db.String(50))
    status = db.Column(db.String(20), default='encours')
    completed = db.Column(db.Boolean, default=False)
    
    # Capteurs
    capteur_regime_moteur = db.Column(db.String(20), default='NA')
    capteur_temp_liquide = db.Column(db.String(20), default='NA')
    switch_temp_eau = db.Column(db.String(20), default='NA')
    palpeur_debit_liquide = db.Column(db.String(20), default='NA')
    capteur_pression_huile = db.Column(db.String(20), default='NA')
    capteur_niveau_huile = db.Column(db.String(20), default='NA')
    capteur_pression_admission = db.Column(db.String(20), default='NA')
    capteur_temp_admission = db.Column(db.String(20), default='NA')
    capteur_temp_echap_droit = db.Column(db.String(20), default='NA')
    capteur_temp_echap_gauche = db.Column(db.String(20), default='NA')
    capteur_temp_air_ambiant = db.Column(db.String(20), default='NA')
    capteur_pression_gasoil = db.Column(db.String(20), default='NA')
    switch_pression_gasoil = db.Column(db.String(20), default='NA')
    capteur_pression_carter = db.Column(db.String(20), default='NA')
    switch_pression_huile = db.Column(db.String(20), default='NA')
    capteur_regime_primaire = db.Column(db.String(20), default='NA')
    capteur_regime_secondaire = db.Column(db.String(20), default='NA')
    capteur_vitesse_convertisseur = db.Column(db.String(20), default='NA')
    capteur_temp_convertisseur = db.Column(db.String(20), default='NA')
    capteur_pression_atmo = db.Column(db.String(20), default='NA')
    
    # Circuit de démarrage
    demarreur_1 = db.Column(db.String(20), default='NA')
    demarreur_2 = db.Column(db.String(20), default='NA')
    alternateur_charge = db.Column(db.String(20), default='NA')
    courroie_alternateur = db.Column(db.String(20), default='NA')
    tendeur_courroie = db.Column(db.String(20), default='NA')
    etat_tension_courroie = db.Column(db.String(20), default='NA')
    
    # Contrôle branchement et câblage
    faisceau_electrique = db.Column(db.String(20), default='NA')
    branchement_electrique = db.Column(db.String(20), default='NA')
    attachement_isolation = db.Column(db.String(20), default='NA')

@app.route('/')
def index():
    try:
        checklists = Checklist.query.all()
        return render_template('index.html', checklists=checklists)
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return f"An error occurred: {str(e)}", 500

@app.route('/completed')
def completed_checklists():
    checklists = Checklist.query.filter_by(status='términée').all()
    return render_template('completed_checklists.html', checklists=checklists)

@app.route('/new_checklist', methods=['GET', 'POST'])
def new_checklist():
    if request.method == 'POST':
        try:
            checklist = Checklist(
                date_controle=datetime.strptime(request.form.get('date_controle'), '%Y-%m-%d'),
                type_checklist=request.form.get('type_checklist'),
                responsable_electrique=request.form.get('responsable_electrique'),
                responsable_atelier=request.form.get('responsable_atelier'),
                inspecteur_methode=request.form.get('inspecteur_methode'),
                categorie_engin=request.form.get('categorie_engin'),
                numero_serie_moteur=request.form.get('numero_serie_moteur'),
                numero_serie_ecm=request.form.get('numero_serie_ecm'),
                hm_actuel=float(request.form.get('hm_actuel') or 0),
                type_revision=request.form.get('type_revision'),
                
                # Capteurs
                capteur_regime_moteur=request.form.get('capteur_regime_moteur', 'NA'),
                capteur_temp_liquide=request.form.get('capteur_temp_liquide', 'NA'),
                switch_temp_eau=request.form.get('switch_temp_eau', 'NA'),
                palpeur_debit_liquide=request.form.get('palpeur_debit_liquide', 'NA'),
                capteur_pression_huile=request.form.get('capteur_pression_huile', 'NA'),
                capteur_niveau_huile=request.form.get('capteur_niveau_huile', 'NA'),
                capteur_pression_admission=request.form.get('capteur_pression_admission', 'NA'),
                capteur_temp_admission=request.form.get('capteur_temp_admission', 'NA'),
                capteur_temp_echap_droit=request.form.get('capteur_temp_echap_droit', 'NA'),
                capteur_temp_echap_gauche=request.form.get('capteur_temp_echap_gauche', 'NA'),
                capteur_temp_air_ambiant=request.form.get('capteur_temp_air_ambiant', 'NA'),
                capteur_pression_gasoil=request.form.get('capteur_pression_gasoil', 'NA'),
                switch_pression_gasoil=request.form.get('switch_pression_gasoil', 'NA'),
                capteur_pression_carter=request.form.get('capteur_pression_carter', 'NA'),
                switch_pression_huile=request.form.get('switch_pression_huile', 'NA'),
                capteur_regime_primaire=request.form.get('capteur_regime_primaire', 'NA'),
                capteur_regime_secondaire=request.form.get('capteur_regime_secondaire', 'NA'),
                capteur_vitesse_convertisseur=request.form.get('capteur_vitesse_convertisseur', 'NA'),
                capteur_temp_convertisseur=request.form.get('capteur_temp_convertisseur', 'NA'),
                capteur_pression_atmo=request.form.get('capteur_pression_atmo', 'NA'),
                
                # Circuit de démarrage
                demarreur_1=request.form.get('demarreur_1', 'NA'),
                demarreur_2=request.form.get('demarreur_2', 'NA'),
                alternateur_charge=request.form.get('alternateur_charge', 'NA'),
                courroie_alternateur=request.form.get('courroie_alternateur', 'NA'),
                tendeur_courroie=request.form.get('tendeur_courroie', 'NA'),
                etat_tension_courroie=request.form.get('etat_tension_courroie', 'NA'),
                
                # Contrôle branchement et câblage
                faisceau_electrique=request.form.get('faisceau_electrique', 'NA'),
                branchement_electrique=request.form.get('branchement_electrique', 'NA'),
                attachement_isolation=request.form.get('attachement_isolation', 'NA')
            )
            db.session.add(checklist)
            db.session.commit()
            flash('Checklist créée avec succès!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création: {str(e)}', 'error')
            return redirect(url_for('new_checklist'))
    
    return render_template('new_checklist.html')

@app.route('/edit_checklist/<int:id>', methods=['GET', 'POST'])
def edit_checklist(id):
    checklist = Checklist.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Update all fields
            for field in request.form:
                if field == 'date_controle':
                    setattr(checklist, field, datetime.strptime(request.form[field], '%Y-%m-%d'))
                elif field == 'hm_actuel':
                    setattr(checklist, field, float(request.form[field] or 0))
                else:
                    setattr(checklist, field, request.form[field])
            
            db.session.commit()
            flash('Checklist mise à jour avec succès!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la mise à jour: {str(e)}', 'error')
    return render_template('edit_checklist.html', checklist=checklist)

@app.route('/view_checklist/<int:id>')
def view_checklist(id):
    checklist = Checklist.query.get_or_404(id)
    return render_template('view_checklist.html', checklist=checklist)

@app.route('/delete_checklist/<int:id>', methods=['POST'])
def delete_checklist(id):
    checklist = Checklist.query.get_or_404(id)
    try:
        db.session.delete(checklist)
        db.session.commit()
        flash('Checklist supprimée avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    checklist = Checklist.query.get_or_404(id)
    try:
        checklist.status = request.form.get('status')
        db.session.commit()
        flash('Statut mis à jour avec succès!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la mise à jour du statut: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/generate_pdf/<int:id>')
def generate_pdf(id):
    try:
        checklist = Checklist.query.get_or_404(id)
        html = render_template('pdf_template.html', checklist=checklist, current_time=datetime.now())
        
        # Generate PDF
        pdf = pdfkit.from_string(html, False, configuration=config)
        
        # Create response
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=checklist_{id}.pdf'
        
        return response
    except Exception as e:
        app.logger.error(f"Error generating PDF: {str(e)}")
        flash(f'Erreur lors de la génération du PDF: {str(e)}', 'error')
        return redirect(url_for('view_checklist', id=id))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
    
    app.run(debug=True)
