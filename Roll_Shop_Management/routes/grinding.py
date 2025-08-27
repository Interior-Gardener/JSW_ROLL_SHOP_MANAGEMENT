from flask import Blueprint, request, render_template, session, redirect, url_for
import os
import pandas as pd
from config import UPLOAD_FOLDER
from utils.validation import validate_excel
from utils.submission import submit_to_db

bp = Blueprint('grinding', __name__)

@bp.route('/grinding.html', methods=['GET', 'POST'])
def grinding():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    message, table_html = None, None

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith(('.xlsx', '.xls')):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            try:
                df = pd.read_excel(filepath)
                valid, result = validate_excel(df)
                if valid:
                    table_html = result.to_html(classes='table table-striped', index=False)
                    message = "✅ File validated. Ready for submission."
                else:
                    message = f"❌ Validation error: {result}"
            except Exception as e:
                message = f"❌ File processing error: {e}"
        else:
            message = "❌ Invalid file format."

    return render_template("grinding.html", message=message, table=table_html, employeeid=session['employeeid'])


@bp.route('/submit-grinding-data', methods=['POST'])
def submit_grinding_data():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    try:
        files = sorted([os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER)], key=os.path.getctime, reverse=True)
        if not files:
            return render_template("grinding.html", message="❌ No file found", employeeid=session['employeeid'])
        df = pd.read_excel(files[0])
        valid, result = validate_excel(df)
        if not valid:
            return render_template("grinding.html", message=f"❌ {result}", employeeid=session['employeeid'])

        status, msg = submit_to_db(result, table_name="VSD_ROLL_WIB")
        return render_template("grinding.html", message=msg, employeeid=session['employeeid'])
    except Exception as e:
        return render_template("grinding.html", message=f"❌ Unexpected error: {e}", employeeid=session['employeeid'])
