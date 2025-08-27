from flask import Blueprint, request, session, redirect, url_for , flash
import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN

bp = Blueprint('update_status', __name__)

@bp.route('/update_status', methods=['POST'])
def update_status_route():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    selected_rolls = request.form.getlist('selected_rolls')
    new_status = request.form.get('new_status')

    if not selected_rolls or not new_status:
        session['update_msg'] = "⚠️ Please select at least one row and choose a new status."
        return redirect(url_for('crs.crs'))

    try:
        # Convert new_status to integer for numeric DB column
        new_status_num = int(new_status)

        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        for roll_no in selected_rolls:
            cursor.execute(
                'UPDATE VSD_ROLL_WIB SET "Status" = :1 WHERE "Vendor no" = :2',
                [new_status_num, roll_no]
            )
        conn.commit()

        session['update_msg'] = f"✅ Updated {len(selected_rolls)} record(s) to status <strong>{new_status_num}</strong>."

    except ValueError:
        session['update_msg'] = "❌ Invalid status value. Must be numeric."

    except Exception as e:
        session['update_msg'] = f"❌ Error during update: {e}"

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('crs.crs'))
