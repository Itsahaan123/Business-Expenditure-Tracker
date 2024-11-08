from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import csv
### from io import StringIO  # Add this import
from datetime import datetime
from io import StringIO, BytesIO  # Import both StringIO and BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://youruser:yourpassword@localhost/business_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Expenditure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Expenditure {self.date} - {self.description}>'



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.json
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    description = data['description']
    transaction_type = data['transaction_type']
    amount = float(data['amount'])

    new_record = Expenditure(date=date, description=description, transaction_type=transaction_type, amount=amount)
    db.session.add(new_record)
    db.session.commit()
    return jsonify({"message": "Record added successfully!"})

@app.route('/update_record/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    data = request.json
    record = Expenditure.query.get(record_id)
    if record:
        record.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        record.description = data['description']
        record.transaction_type = data['transaction_type']
        record.amount = float(data['amount'])
        db.session.commit()
        return jsonify({"message": "Record updated successfully!"})
    return jsonify({"message": "Record not found!"}), 404

@app.route('/delete_record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    record = Expenditure.query.get(record_id)
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Record deleted successfully!"})
    return jsonify({"message": "Record not found!"}), 404

@app.route('/get_records', methods=['GET'])
def get_records():
    records = Expenditure.query.all()
    result = [{
        "id": r.id,
        "date": r.date.strftime('%Y-%m-%d'),
        "description": r.description,
        "transaction_type": r.transaction_type,
        "amount": r.amount
    } for r in records]

    total_balance = sum(r.amount if r.transaction_type == 'credited' else -r.amount for r in records)
    return jsonify({"records": result, "total_balance": total_balance})


@app.route('/export_csv', methods=['GET'])
def export_csv():
    records = Expenditure.query.all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Description', 'Transaction Type', 'Amount'])  # Column headers
    for record in records:
        writer.writerow([record.date, record.description, record.transaction_type, record.amount])

    # Convert StringIO content to bytes
    output.seek(0)
    byte_output = BytesIO()
    byte_output.write(output.getvalue().encode('utf-8'))
    byte_output.seek(0)

    return send_file(byte_output, mimetype='text/csv', download_name='expenditure_records.csv', as_attachment=True)
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)