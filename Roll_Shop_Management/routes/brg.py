from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
import oracledb
import pandas as pd
from config import DB_DSN, DB_USER, DB_PASSWORD
import numpy as np

bp = Blueprint('brg', __name__)

@bp.route('/brg.html')
def brg():
    if 'employeeid' not in session:
        return redirect(url_for('login'))
    return render_template('brg.html', employeeid=session['employeeid'])

@bp.route('/brg/get_chock_data')
def get_chock_data():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        query = """
            SELECT * FROM chock
            WHERE brg_no IS NOT NULL
              AND chock_status = 'FREE'
        """
        df = pd.read_sql(query, conn)
        # Replace NaN/NaT with None (valid JSON)
        df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        print("Error fetching CHOCK data:", e)
        return jsonify([])
    finally:
        if 'conn' in locals(): conn.close()


@bp.route('/brg/get_brg_data')
def get_brg_data():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        df = pd.read_sql("SELECT * FROM brg WHERE brg_status = 'FREE'", conn)

        # Convert NaN/NaT to None for safe JSON serialization
        df = df.fillna(value=None)

        return jsonify(df.to_dict(orient='records'))

    except Exception as e:
        print("Error fetching BRG data:", e)
        return jsonify([])

    finally:
        if 'conn' in locals():
            conn.close()


# New route for BEARING ASSEMBLE chock+brg data
@bp.route('/brg/get_assemble_data')
def get_assemble_data():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

        # Get CHOCK data where brg_no is NULL
        chock_query = """
            SELECT chock_no, position, side 
            FROM chock
            WHERE brg_no IS NULL
        """
        df_chock = pd.read_sql(chock_query, conn)
        df_chock = df_chock.replace({np.nan: None})  # Fix NaN

        # Get BRG data where chock_no is NULL and status is FREE
        brg_query = """
            SELECT brg_no, brg_type, km 
            FROM brg
            WHERE chock_no IS NULL AND brg_status = 'FREE'
        """
        df_brg = pd.read_sql(brg_query, conn)
        df_brg = df_brg.replace({np.nan: None})  # Fix NaN

        return jsonify({
            'chock': df_chock.to_dict(orient='records'),
            'brg': df_brg.to_dict(orient='records')
        })
    except Exception as e:
        print("Error fetching assemble data:", e)
        return jsonify({'chock': [], 'brg': []})
    finally:
        if 'conn' in locals():
            conn.close()


@bp.route('/brg/update_chock', methods=['POST'])
def update_chock():
    try:
        data = request.get_json()
        print("Received data for update_chock:", data)  # Debug log
        selected_id = data.get('id')
        if not selected_id:
            return jsonify({"success": False, "error": "No CHOCK ID provided"})

        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cur = conn.cursor()

        cur.execute("SELECT brg_no, chock_no FROM chock WHERE chock_no = :id", {'id': selected_id})
        result = cur.fetchone()
        if not result:
            print(f"CHOCK row with chock_no={selected_id} not found.")  # Debug log
            return jsonify({"success": False, "error": "CHOCK row not found"})

        brg_no, chock_no = result

        cur.execute("""
            UPDATE brg SET chock_no = NULL, brg_status = 'FREE'
            WHERE brg_no = :brg_no
        """, {'brg_no': brg_no})

        cur.execute("""
            UPDATE chock SET brg_no = NULL, brg_type = NULL
            WHERE chock_no = :chock_no
        """, {'chock_no': chock_no})

        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        print("Error in update_chock:", e)
        return jsonify({"success": False, "error": str(e)})
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@bp.route('/brg/update_brg', methods=['POST'])
def update_brg():
    try:
        data = request.get_json()
        selected_id = data.get('id')
        if not selected_id:
            return jsonify({"success": False, "error": "No BRG ID provided"})

        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cur = conn.cursor()

        cur.execute("SELECT brg_no FROM brg WHERE brg_no = :id", {'id': selected_id})
        result = cur.fetchone()
        if not result:
            return jsonify({"success": False, "error": "BRG row not found"})

        cur.execute("""
            UPDATE brg SET brg_status = 'SERVICE'
            WHERE brg_no = :brg_no
        """, {'brg_no': selected_id})

        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        print("Error in update_brg:", e)
        return jsonify({"success": False, "error": str(e)})
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


@bp.route('/brg/submit_assembly', methods=['POST'])
def submit_assembly():
    try:
        data = request.get_json()
        chock_no = data.get('chock_no')
        brg_no = data.get('brg_no')

        if not chock_no or not brg_no:
            return jsonify({"success": False, "error": "Missing CHOCK or BRG selection"})

        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cur = conn.cursor()

        # Step 1: Update BRG table: set BRG_STATUS = 'ENGAGED'
        cur.execute("""
            UPDATE brg
            SET brg_status = 'ENGAGED'
            WHERE brg_no = :brg_no
        """, {'brg_no': brg_no})

        # Step 2: Update BRG table: set CHOCK_NO = :chock_no
        cur.execute("""
            UPDATE brg
            SET chock_no = :chock_no
            WHERE brg_no = :brg_no
        """, {'chock_no': chock_no, 'brg_no': brg_no})

        # Step 3: Update CHOCK table: set BRG_NO = :brg_no
        cur.execute("""
            UPDATE chock
            SET brg_no = :brg_no
            WHERE chock_no = :chock_no
        """, {'brg_no': brg_no, 'chock_no': chock_no})

        # Step 4: Get BRG_TYPE from BRG table using brg_no
        cur.execute("""
            SELECT brg_type FROM brg WHERE brg_no = :brg_no
        """, {'brg_no': brg_no})
        row = cur.fetchone()
        brg_type = row[0] if row else None

        # Update CHOCK table with brg_type
        if brg_type:
            cur.execute("""
                UPDATE chock
                SET brg_type = :brg_type
                WHERE chock_no = :chock_no
            """, {'brg_type': brg_type, 'chock_no': chock_no})

        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        print("Error during assembly update:", e)
        return jsonify({"success": False, "error": str(e)})

    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@bp.route('/brg/get_service_brg')
def get_service_brg():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT BRG_NO, BRG_TYPE, KM, BRG_STATUS
            FROM BRG
            WHERE BRG_STATUS = 'SERVICE'
        """)

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        print("Fetched SERVICE BRGs:", data)  # ✅ Debug log

        return jsonify(data)

    except Exception as e:
        print("Error in get_service_brg:", e)
        return jsonify([])
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@bp.route('/brg/update_brg_to_free', methods=['POST'])
def update_brg_to_free():
    try:
        data = request.get_json()
        brg_no = data.get('brg_no')

        if not brg_no:
            return jsonify({"success": False, "error": "Missing BRG_NO"})

        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE BRG
            SET BRG_STATUS = 'FREE'
            WHERE BRG_NO = :brg_no
        """, {'brg_no': brg_no})

        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        print("Error updating BRG to FREE:", e)
        return jsonify({"success": False, "error": str(e)})
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@bp.route('/brg/get_free_brg')
def get_free_brg():
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT BRG_NO, BRG_TYPE, KM, BRG_STATUS
            FROM BRG
            WHERE BRG_STATUS = 'FREE'
        """)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]
        return jsonify(data)
    except Exception as e:
        print("Error in get_free_brg:", e)
        return jsonify([])
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@bp.route('/brg/update_brg_status', methods=['POST'])
def update_brg_status():
    try:
        data = request.get_json()
        brg_no = data.get('brg_no')
        target_status = data.get('target_status')

        if not brg_no or not target_status:
            return jsonify({"success": False, "error": "Missing brg_no or target_status"})

        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cur = conn.cursor()

        cur.execute("""
            UPDATE brg
            SET brg_status = :target_status
            WHERE brg_no = :brg_no
        """, {'target_status': target_status, 'brg_no': brg_no})

        conn.commit()
        return jsonify({"success": True})

    except Exception as e:
        print("Error updating BRG status:", e)
        return jsonify({"success": False, "error": str(e)})

    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()