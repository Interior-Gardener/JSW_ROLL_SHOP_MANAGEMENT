from flask import Blueprint, request, session, redirect, url_for, render_template
import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN

bp = Blueprint('level_2_data', __name__)

@bp.route('/level_2_data.html', methods=['GET', 'POST'])
def level_2_data():
    if 'employeeid' not in session:
        return redirect(url_for('login')) 
    
    table_html = ""
    error_msg = None
    update_msg = session.pop('update_msg', None)

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        sql = 'SELECT * FROM VSD_ROLL_L2'
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        if rows:
            vendor_index = columns.index("Vendor no") if "Vendor no" in columns else None

            table_html = "<table border='1'><thead><tr>"
            if vendor_index is not None:
                table_html += "<th>Select</th>"

            table_html += ''.join(f"<th>{col}</th>" for col in columns)
            table_html += "</tr></thead><tbody>"

            for row in rows:
                table_html += "<tr>"
                if vendor_index is not None:
                    vendor_no = row[vendor_index]
                    table_html += f'<td><input type="checkbox" name="selected_rolls" value="{vendor_no}"></td>'

                table_html += ''.join(f"<td>{cell}</td>" for cell in row)
                table_html += "</tr>"

            table_html += "</tbody></table>"
        else:
            table_html = "<p>No records found.</p>"

    except Exception as e:
        error_msg = f"Error: {e}"

    return render_template('level_2_data.html',table=table_html,update_msg=update_msg,error_msg=error_msg,employeeid=session['employeeid'])
