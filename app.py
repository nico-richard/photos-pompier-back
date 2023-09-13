from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
import base64


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

CORS(app)

# Modèle de données pour les photos de camions


class Photo(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marque: Mapped[str] = mapped_column(String(100), nullable=False)
    chassis: Mapped[str] = mapped_column(String(100), nullable=False)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    image: Mapped[LargeBinary] = mapped_column(LargeBinary, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)


# Route pour créer une nouvelle photo
@app.route('/photos', methods=['POST'])
def creer_photo():
    data = request.get_json()
    nouvelle_photo = Photo(
        marque=data['marque'],
        chassis=data['chassis'],
        annee=data['annee'],
        image=base64.b64decode(data['image'].split(',')[1])
    )
    db.session.add(nouvelle_photo)
    db.session.commit()
    return jsonify({'message': 'Nouvelle photo créée avec succès'}), 201


# Route pour obtenir la liste des photos
@app.route('/photos', methods=['GET'])
def obtenir_photos():
    photos = Photo.query.all()
    photos_json = [{'id': photo.id, 'marque': photo.marque, 'chassis': photo.chassis,
                    'annee': photo.annee, 'timestamp': photo.timestamp, 'image': base64.b64encode(photo.image).decode('utf-8')} for photo in photos]
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
