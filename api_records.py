from flask import jsonify, request, abort
from .database import db, app, Record
import base64
from .models import Record

def initialize_routes():
    app.add_url_rule("/api/v1/records/", view_func=create_record, methods=["POST"])
    app.add_url_rule("/api/v1/records/<record_id>", view_func=get_record, methods=["GET", "PUT", "DELETE"])

class CorpusAPIRecords:
    def __init__(self):
        pass

    def create_record(self):
        data = request.form
        record = Record(
            title=data.get("title"),
            description=data.get("description"),
            media_type=data.get("media_type"),
            filename=data.get("filename"),
            chunk_data=data.get("chunk_data"),
            total_chunks=int(data.get("total_chunks")),
            latitude=float(data.get("latitude")),
            longitude=float(data.get("longitude")),
            category_id=data.get("category_id"),
            user_id=data.get("user_id"),
            release_rights=data.get("release_rights"),
            language=data.get("language")
        )
        db.session.add(record)
        db.session.commit()
        return jsonify({"message": "Record created successfully", "record_id": record.id})

    def get_record(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            abort(404)
        return jsonify(record.to_dict())

    def update_record(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            abort(404)
        data = request.form
        if "title" in data:
            record.title = data["title"]
        if "description" in data:
            record.description = data["description"]
        db.session.commit()
        return jsonify({"message": "Record updated successfully"})

    def delete_record(self, record_id):
        record = Record.query.get(record_id)
        if not record:
            abort(404)
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully"})


def __initRoutes__():
    app.add_url_rule("/api/v1/records/", view_func=lambda: jsonify({"message": "Records API"}))
    app.add_url_rule("/api/v1/records/<record_id>/", view_func=lambda: jsonify({"message": "Record details"}))
    app.add_url_rule("/api/v1/records/", view_func=lambda: jsonify({"message": "List of records"}))
