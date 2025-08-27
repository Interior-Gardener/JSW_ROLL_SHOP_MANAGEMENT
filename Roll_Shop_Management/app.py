from flask import Flask, render_template, session, redirect, url_for, request, send_from_directory
from config import SECRET_KEY, UPLOAD_FOLDER, DB_USER, DB_PASSWORD, DB_DSN
from routes import grinding, wr, imr, br, job_work_details, level_2_data, sap_purchase_details, inventoryform, assembler, allrd, crs, update_status, grinder, update_grinder_status, brg, stand
import oracledb

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Register Blueprints from capitalized module files
app.register_blueprint(grinding.bp)
app.register_blueprint(wr.bp)
app.register_blueprint(imr.bp)
app.register_blueprint(br.bp)
app.register_blueprint(job_work_details.bp)
app.register_blueprint(level_2_data.bp)
app.register_blueprint(sap_purchase_details.bp)
app.register_blueprint(inventoryform.bp)
app.register_blueprint(allrd.bp)
app.register_blueprint(crs.bp)
app.register_blueprint(update_status.bp)
app.register_blueprint(grinder.bp)
app.register_blueprint(update_grinder_status.bp)
app.register_blueprint(assembler.bp)
app.register_blueprint(brg.bp)
app.register_blueprint(stand.bp)

@app.route('/', methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        employeeid = request.form.get("employeeid")
        password = request.form.get("password")
        try:
            with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT employeeid, role FROM users
                    WHERE employeeid = :1 AND password = :2
                """, [employeeid, password])
                user = cursor.fetchone()
                if user:
                    session["employeeid"] = user[0]
                    session["role"] = user[1]
                    return redirect(url_for("home"))
                else:
                    error = "Invalid employee ID or password"
        except Exception as e:
            error = f"Database error: {e}"
    return render_template("login.html", error=error)


@app.route('/logout')
def logout():
    session.pop("employeeid", None)
    return redirect(url_for("login"))

@app.route('/homepage.html')
def home():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    user = {
        'employeeid': session['employeeid'],
        'role': session.get('role')
    }

    slides = [
        'slides/logo.png',
        'slides/image1.jpeg',
        'slides/image2.avif'
    ]

    return render_template('homepage.html', user=user, slides=slides)


@app.route('/download/<filename>')
def download_file(filename):
    if 'employeeid' not in session:
        return redirect(url_for('login'))
    allowed = ['Basic_template.xlsx']
    if filename not in allowed:
        return "Unauthorized", 403
    return send_from_directory('static', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)