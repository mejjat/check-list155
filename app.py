from flask import Flask, render_template, request, redirect, url_for, send_file, make_response, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import pdfkit

# Configure wkhtmltopdf path
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///checklist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Add this line for flash messages
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

def init_db():
    if os.path.exists('checklist.db'):
        os.remove('checklist.db')
    with app.app_context():
        db.create_all()

init_db()

@app.route('/')
def index():
    checklists = Checklist.query.all()
    return render_template('index.html', checklists=checklists)

@app.route('/completed_checklists')
def completed_checklists():
    checklists = Checklist.query.filter_by(status='términée').all()
    return render_template('completed_checklists.html', checklists=checklists)

@app.route('/checklist/<int:id>/update_status', methods=['POST'])
def update_status(id):
    checklist = Checklist.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['encours', 'términée', 'annulée']:
        old_status = checklist.status
        checklist.status = new_status
        db.session.commit()
        flash(f'Statut mis à jour de {old_status} à {new_status}', 'success')
    else:
        flash('Statut invalide', 'error')
    return redirect(url_for('index'))

@app.route('/checklist/<int:id>')
def view_checklist(id):
    checklist = Checklist.query.get_or_404(id)
    return render_template('view_checklist.html', checklist=checklist)

@app.route('/checklist/<int:id>/edit', methods=['GET', 'POST'])
def edit_checklist(id):
    checklist = Checklist.query.get_or_404(id)
    if request.method == 'POST':
        checklist.date_controle = datetime.strptime(request.form['date_controle'], '%Y-%m-%d')
        checklist.type_checklist = request.form['type_checklist']
        checklist.responsable_electrique = request.form['responsable_electrique']
        checklist.responsable_atelier = request.form['responsable_atelier']
        checklist.inspecteur_methode = request.form['inspecteur_methode']
        checklist.categorie_engin = request.form['categorie_engin']
        checklist.numero_serie_moteur = request.form['numero_serie_moteur']
        checklist.numero_serie_ecm = request.form['numero_serie_ecm']
        checklist.hm_actuel = float(request.form['hm_actuel'])
        checklist.type_revision = request.form['type_revision']
        checklist.completed = 'completed' in request.form
        
        # Update all other fields...
        for field in request.form:
            if hasattr(checklist, field) and field not in ['date_controle', 'hm_actuel']:
                setattr(checklist, field, request.form[field])
        
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_checklist.html', checklist=checklist)

@app.route('/checklist/<int:id>/delete', methods=['POST'])
def delete_checklist(id):
    checklist = Checklist.query.get_or_404(id)
    db.session.delete(checklist)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/checklist/<int:id>/pdf')
def generate_pdf(id):
    checklist = Checklist.query.get_or_404(id)
    current_time = datetime.now()
    html = render_template('pdf_template.html', checklist=checklist, current_time=current_time)
    
    # Configure PDF options
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
    }
    
    # Generate PDF with configuration
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    
    # Create response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=checklist_{id}.pdf'
    
    return response

@app.route('/new_checklist', methods=['GET', 'POST'])
def new_checklist():
    if request.method == 'POST':
        checklist = Checklist(
            date_controle=datetime.strptime(request.form['date_controle'], '%Y-%m-%d'),
            type_checklist=request.form['type_checklist'],
            responsable_electrique=request.form['responsable_electrique'],
            responsable_atelier=request.form['responsable_atelier'],
            inspecteur_methode=request.form['inspecteur_methode'],
            categorie_engin=request.form['categorie_engin'],
            numero_serie_moteur=request.form['numero_serie_moteur'],
            numero_serie_ecm=request.form['numero_serie_ecm'],
            hm_actuel=float(request.form['hm_actuel']),
            type_revision=request.form['type_revision'],
            completed='completed' in request.form,
            
            # Capteurs
            capteur_regime_moteur=request.form.get('capteur_regime_moteur'),
            capteur_temp_liquide=request.form.get('capteur_temp_liquide'),
            switch_temp_eau=request.form.get('switch_temp_eau'),
            palpeur_debit_liquide=request.form.get('palpeur_debit_liquide'),
            capteur_pression_huile=request.form.get('capteur_pression_huile'),
            capteur_niveau_huile=request.form.get('capteur_niveau_huile'),
            capteur_pression_admission=request.form.get('capteur_pression_admission'),
            capteur_temp_admission=request.form.get('capteur_temp_admission'),
            capteur_temp_echap_droit=request.form.get('capteur_temp_echap_droit'),
            capteur_temp_echap_gauche=request.form.get('capteur_temp_echap_gauche'),
            capteur_temp_air_ambiant=request.form.get('capteur_temp_air_ambiant'),
            capteur_pression_gasoil=request.form.get('capteur_pression_gasoil'),
            switch_pression_gasoil=request.form.get('switch_pression_gasoil'),
            capteur_pression_carter=request.form.get('capteur_pression_carter'),
            switch_pression_huile=request.form.get('switch_pression_huile'),
            capteur_regime_primaire=request.form.get('capteur_regime_primaire'),
            capteur_regime_secondaire=request.form.get('capteur_regime_secondaire'),
            capteur_vitesse_convertisseur=request.form.get('capteur_vitesse_convertisseur'),
            capteur_temp_convertisseur=request.form.get('capteur_temp_convertisseur'),
            capteur_pression_atmo=request.form.get('capteur_pression_atmo'),
            
            # Circuit de démarrage
            demarreur_1=request.form.get('demarreur_1'),
            demarreur_2=request.form.get('demarreur_2'),
            alternateur_charge=request.form.get('alternateur_charge'),
            courroie_alternateur=request.form.get('courroie_alternateur'),
            tendeur_courroie=request.form.get('tendeur_courroie'),
            etat_tension_courroie=request.form.get('etat_tension_courroie'),
            
            # Contrôle branchement et câblage
            faisceau_electrique=request.form.get('faisceau_electrique'),
            branchement_electrique=request.form.get('branchement_electrique'),
            attachement_isolation=request.form.get('attachement_isolation')
        )
        db.session.add(checklist)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_checklist.html')

if __name__ == '__main__':
    app.run(debug=True)
