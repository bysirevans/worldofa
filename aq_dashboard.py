from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)
api = openaq.OpenAQ()

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(50))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f'<Time {self.datetime} --- Value {self.value}>'

@app.route('/')
def root():
    with app.app_context():
         results = Record.query.filter(Record.value >= 18).all()
    formatted_results = [f'Time {result.datetime} --- Value {result.value}' for result in results]
    return '\n'.join(formatted_results)

def get_results():
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    if status == 200:
        results = body['results']
        return [(result['date']['utc'], result['value']) for result in results]
    else:
        return []

@app.route('/refresh')
def refresh():
    with app.app_context():
        DB.drop_all()
        DB.create_all()
        results = get_results()
        records = [Record(datetime=record[0], value=record[1]) for record in results]
        DB.session.add_all(records)
        DB.session.commit()
    return 'Data refreshed!'

if __name__ == '__main__':
    with app.app_context():
        DB.create_all()
    app.run()
