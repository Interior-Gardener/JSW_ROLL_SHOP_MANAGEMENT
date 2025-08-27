from flask import Blueprint, request, session, redirect, url_for
import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN

bp = Blueprint('update_grinder_status', __name__)

@bp.route('/update_grinder_status', methods=['POST'])
def update_grinder_status():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    selected_rolls = request.form.getlist('selected_rolls')
    status_code = 205  # Fixed GROUND status

    if not selected_rolls:
        session['update_msg'] = "⚠️ No rows selected."
        return redirect(url_for('grinder.grinder'))

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        for roll_no in selected_rolls:
            cursor.execute(
                'UPDATE VSD_ROLL_WIB SET "Status" = :1 WHERE "Vendor no" = :2',
                [status_code, roll_no]
            )
        conn.commit()
        session['update_msg'] = f"✅ Updated {len(selected_rolls)} rows to GROUND."

    except Exception as e:
        session['update_msg'] = f"❌ Update error: {e}"

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('grinder.grinder'))
