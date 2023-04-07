import io
from flask import Flask, request, render_template, session
from data import read_json_file, data_manipulation, plot_graphs

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('upload.html')
    elif request.method == 'POST':
        if 'file' in request.files:
            json_file = request.files.get('file')
            if not json_file:
                return 'No file uploaded.', 400
            session['json_file'] = json_file.read()
            df, dates, agent_ids, fields = read_json_file(io.BytesIO(session['json_file']))
            if not fields:
                return 'No fields found in the uploaded file.', 400
        if 'field' in request.form and 'date' in request.form:
            if 'json_file' not in session:
                return 'No file uploaded.', 400
            df, dates, agent_ids, fields = read_json_file(io.BytesIO(session['json_file']))
            field = request.form['field']
            date = request.form['date']
            if not field or not date:
                return 'Field and Date are required.', 400
            df_filtered = data_manipulation(df, dates, agent_ids, fields, field.lower(), date)
            if df_filtered.empty:
                return 'No data found for the selected field and date.', 400
            plot = plot_graphs(df_filtered)
            return render_template('graph.html', image=plot)
        else:
            return render_template('dropdown.html', fields=fields, dates=dates)


if __name__ == '__main__':
    app.run()