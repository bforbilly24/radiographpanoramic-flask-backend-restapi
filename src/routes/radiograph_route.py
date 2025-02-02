# src/routes/radiograph_route.py
from flask import Blueprint
from flask_jwt_extended import jwt_required
from src.controllers.radiograph_controller import predict_radiograph, filter_radiographs

radiograph_route = Blueprint("radiograph_route", __name__, url_prefix='/api/radiograph')

@radiograph_route.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    return predict_radiograph()

@radiograph_route.route("/filter", methods=["POST"])
@jwt_required()
def filter():
    return filter_radiographs()
