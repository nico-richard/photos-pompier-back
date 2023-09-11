from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
# Utilisez SQLite pour la simplicité (à remplacer par une base de données plus robuste en production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)  # Activer CORS pour permettre les requêtes depuis un frontend différent


# Modèle de données pour les photos de camions
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marque = db.Column(db.String(100), nullable=False)
    chassis = db.Column(db.String(100), nullable=False)
    annee = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Route pour créer une nouvelle photo
@app.route('/photos', methods=['POST'])
def creer_photo():
    data = request.get_json()
    nouvelle_photo = Photo(
        marque=data['marque'],
        chassis=data['chassis'],
        annee=data['annee']
    )
    db.session.add(nouvelle_photo)
    db.session.commit()
    return jsonify({'message': 'Nouvelle photo créée avec succès'}), 201


# Route pour obtenir la liste des photos
@app.route('/photos', methods=['GET'])
def obtenir_photos():
    photos = Photo.query.all()
    photos_json = [{'id': photo.id, 'marque': photo.marque, 'chassis': photo.chassis,
                    'annee': photo.annee, 'timestamp': photo.timestamp} for photo in photos]
    return jsonify(photos_json), 200


@app.route('/photos/search', methods=['GET'])
def search_photos():
    queryString = request.args.get('q')

    # Créez une requête SQLAlchemy pour rechercher les photos en fonction des critères
    query = Photo.query

    if queryString:
        query = query.filter(Photo.marque.ilike(
            f'%{queryString}%'), Photo.chassis.ilike(f'%{queryString}%'))

    # Exécutez la requête et obtenez les résultats
    results = query.all()

    # Transformez les résultats en un format JSON
    serialized_results = [
        {
            'id': photo.id,
            'marque': photo.marque,
            'chassis': photo.chassis,
            'annee': photo.annee
        }
        for photo in results
    ]

    return jsonify(serialized_results)


if __name__ == '__main__':
    app.run(debug=True)
