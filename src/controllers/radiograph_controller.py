# src/controllers/radiograph_controller.py
from flask import jsonify, request
import os
from werkzeug.utils import secure_filename
from ..models.radiograph_model import Radiograph 
from src.app import db

def predict_radiograph():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    original_filename = secure_filename(file.filename)

    original_file_path = os.path.join('uploads', 'original', original_filename)

    os.makedirs('uploads/original', exist_ok=True)

    file.save(original_file_path)

    try:
        from src.services.radiograph_service import load_model, predict_image

        model = load_model('model/unet_gigi_100.h5')

        encoded_image, predicted_file_path = predict_image(model, original_file_path)

        new_radiograph = Radiograph.create_and_generate_task(
            patient_name="1086.ARCHI,NY.34TH",
            original=original_file_path, 
            status_detection="in progress"
        )

        new_radiograph.predicted = predicted_file_path
        db.session.commit() 

        return jsonify({
            'message': 'Prediction successful',
            'original_file': original_file_path,  
            'predicted_file': predicted_file_path, 
            'image': encoded_image,
            'task_id': new_radiograph.tasks 
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        if os.path.exists(original_file_path):
            os.remove(original_file_path)


def get_filtered_radiograph():
    try:
        data = request.get_json()
        filters = data.get('filters', [])
        
        if not filters:
            return jsonify({'error': 'No filters provided'}), 400

        image_id = data.get('image_id')
        if not image_id:
            return jsonify({'error': 'No image ID provided'}), 400

        radiograph = Radiograph.query.get(image_id)
        if not radiograph:
            return jsonify({'error': 'Radiograph not found'}), 404
            
        if not radiograph.predicted:
            return jsonify({'error': 'No predicted image available for this radiograph'}), 404

        predicted_path = radiograph.predicted
        if not os.path.exists(predicted_path):
            return jsonify({'error': 'Predicted image file not found'}), 404

        from src.services.radiograph_service import apply_filters
        filtered_image, filtered_path = apply_filters(predicted_path, filters)

        return jsonify({
            'message': 'Filters applied successfully',
            'filtered_image': filtered_image,
            'conditions': filters,
            'original_path': radiograph.predicted,
            'filtered_path': filtered_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500