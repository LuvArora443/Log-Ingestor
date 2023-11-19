import mysql.connector
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='templates')

def create_database():
    # Connect to MySQL server without specifying a database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password@123'
    )
    cursor = conn.cursor()

    # Create a new database if it doesn't exist
    cursor.execute('CREATE DATABASE IF NOT EXISTS Logs')

    cursor.close()
    conn.close()

# Create the database if it doesn't exist
create_database()

# Initialize MySQL database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='password@123',
    database='Logs'
)

cursor = conn.cursor()

# Create the 'logs' table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        level VARCHAR(255),
        message TEXT,
        resourceId VARCHAR(255),
        timestamp VARCHAR(255),
        traceId VARCHAR(255),
        spanId VARCHAR(255),
        commit VARCHAR(255),
        parentResourceId VARCHAR(255)
    )
''')

conn.commit()
cursor.close()
conn.close()

# Root route - Show the query form
@app.route('/')
def query_form():
    return render_template('query_form.html')

# Log Ingestor
@app.route('/logs', methods=['POST'])
def ingest_log():
    log_data = request.json
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password@123',
        database='Logs'
    )
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (level, message, resourceId, timestamp, traceId, spanId, commit, parentResourceId)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        log_data.get('level'),
        log_data.get('message'),
        log_data.get('resourceId'),
        log_data.get('timestamp'),
        log_data.get('traceId'),
        log_data.get('spanId'),
        log_data.get('commit'),
        log_data.get('metadata', {}).get('parentResourceId')
    ))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'}), 201

# Query Interface - Process the form submission
@app.route('/query', methods=['POST'])
def query_logs():
    query_params = request.form.to_dict()
    page = int(request.args.get('page', 1))  # Get the requested page from the query parameters
    per_page = 10  # Set the number of results per page

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='password@123',
        database='Logs'
    )
    cursor = conn.cursor(dictionary=True)

    # Build SQL query based on filters
    sql_query = 'SELECT * FROM logs WHERE 1=1'
    values = []
    for key, value in query_params.items():
        if value:
            sql_query += f' AND {key} = %s'
            values.append(value)

    # Add pagination to the query
    sql_query += ' LIMIT %s OFFSET %s'
    values.extend([per_page, (page - 1) * per_page])

    # Execute the query
    cursor.execute(sql_query, values)
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('query_result.html', logs=result)

if __name__ == '__main__':
    app.run(port=3000, debug=True)

