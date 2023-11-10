from zipfile import ZipFile
import shutil
from flask import Flask, abort, request, render_template, flash, redirect, send_from_directory, url_for, session
import os
from analyzer import main

app = Flask(__name__)
app.secret_key = '309dc7534117b76a761287ce'

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'db'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_zip_archive():
    source_folder = 'static/exported_data'
    output_filename = 'static/exported_data.zip'

    try:
        with ZipFile(output_filename, 'w') as zipf:
            for foldername, subfolders, filenames in os.walk(source_folder):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    # Create a relative path inside the ZIP archive
                    zipf.write(filepath, os.path.relpath(
                        filepath, source_folder))
    except Exception as e:
        print(f"Error creating zip archive: {str(e)}")


@app.route('/download_zip', methods=['GET'])
def download_zip():
    create_zip_archive()
    return send_from_directory(directory='static', path='exported_data.zip', as_attachment=True)


@app.errorhandler(404)
def page_not_found(error):
    user_mode = request.args.get("mode")
    return render_template('error.html', mode=user_mode)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    user_mode = request.args.get("mode")

    if request.method != 'POST':
        return render_template('error.html', mode=user_mode)

    if request.method == 'POST':

        file = request.files['fileInput']

        if file.filename == '':
            return "No selected file", 405

        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'database.db'))
            flash('File uploaded and renamed to "database.db"')
            results_dict = main('sqlite:///data/database.db')

            print(results_dict['tables_with_duplicate_records'])

            execution_time = results_dict['execution_time']

            if not results_dict['tables_with_missing_cells']:
                missing_cells_info = "No missing cells found."
            else:
                missing_cells_info = "<br>".join(
                    [f"Table '{table}' has {count} missing cells." for table, count in results_dict['tables_with_missing_cells'].items()])

            if not results_dict['tables_with_duplicate_records']:
                duplicate_records_info = "No duplicate records found."
            else:
                duplicate_records_info = "<br>".join(
                    [f"Table '{table}' has the following duplicate records:\n{records}" for table, records in results_dict['tables_with_duplicate_records'].items()])
            user_mode = request.args.get("mode")
            return render_template('index.html', execution_time=execution_time, missing_cells_info=missing_cells_info, duplicate_records_info=duplicate_records_info, user_mode=user_mode)

        else:
            flash('Invalid file format')
            return "File is not uploaded", 405


if __name__ == '__main__':
    app.run(debug=True)
