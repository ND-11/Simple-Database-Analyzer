DatabaseAnalyzer

DatabaseAnalyzer is a web-based project designed to analyze SQLite databases. It uses Flask for HTTP handling and SQLAlchemy for database analysis. This project is primarily for personal practice, and contributions and suggestions are welcome.

Project Overview
The project includes two HTML pages:
1. **index.html**: This page provides a project description and allows users to upload an SQLite database. After uploading, users can execute a random query, find duplicate records, identify missing cells, and download a zip file containing CSV versions of each table.
2. **error.html**: A custom error page for HTTP 404 errors.

Demo avalible until February 2024 here: http://dbanalyzer.online/

Folder Structure:
repository/
|-- data/
|   `-- database.db
|-- static/
|   `-- exported_data/
|   `-- css/
|       `-- style.css
|   `-- img/
|       `-- [website icon]
|   `-- Instrument_Sans/
|       `-- [font files]
|-- templates/
|   `-- index.html
|   `-- 404.html
|-- app.py
|-- analyzer.py
|-- README.md
|-- requirements.txt

Requirements
mainly you will need the following requirements
Python 3.10.7
Flask 2.2.3
SQLAlchemy 1.4.46

Usage
1. Clone the repository.
2. Install the required Python packages: pip install -r requirements.txt
3. Run the Flask application: python app.py
4. Visit http://localhost:5000 in your web browser.

Important Notes
The SQLite database will be renamed to database.db and stored in the data folder.
CSV files will be stored in static/exported_data.
Do not delete the data and static/exported_data folders; otherwise, update paths in the code accordingly.

Sample SQLite Database
For testing purposes, you can use the SQLite sample database here https://www.sqlitetutorial.net/sqlite-sample-database/.

Contributions
This project is open for contributions. Feel free to fork and submit pull requests.

Feedback
Any suggestions or recommendations are appreciated. Open an issue or contact me on X (_ND_ND) for further discussion.