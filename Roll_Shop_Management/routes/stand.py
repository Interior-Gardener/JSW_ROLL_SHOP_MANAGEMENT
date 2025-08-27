from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
import oracledb
import pandas as pd
from config import DB_DSN, DB_PASSWORD, DB_USER

bp = Blueprint('stand', __name__)

@bp.route('/stand.html')
def stand():
    if 'employeeid' not in session:
        return redirect(url_for('login'))
    return render_template('stand.html', employeeid=session['employeeid'])

@bp.route('/get_assembled_rolls_for_stand')
def get_assembled_rolls_for_stand():
    if 'employeeid' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        df = pd.read_sql("""
            SELECT ROLL_TYPE,
VENDOR_NO,
DIA_MIN,
DIA_MAX,
FRONT_CHOCK,
BACK_CHOCK,
DIA_CURRENT,
POSITION FROM VSD_ROLL_ASBL WHERE STAND_NO IS NULL
        """, conn)

        data = df.to_dict(orient='records')
        return jsonify(data)

    except Exception as e:
        print("Error fetching assembled rolls:", e)
        return jsonify([])

    finally:
        if 'conn' in locals():
            conn.close()

@bp.route('/get_free_stand_nos')
def get_free_stand_nos():
    if 'employeeid' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        df = pd.read_sql("""
            SELECT STAND_NO FROM STAND_MASTER WHERE STAND_STATUS = 'FREE'
        """, conn)

        stand_nos = df['STAND_NO'].dropna().tolist()
        return jsonify(stand_nos)

    except Exception as e:
        print("Error fetching free stand numbers:", e)
        return jsonify([])

    finally:
        if 'conn' in locals():
            conn.close()

@bp.route('/submit_roll', methods=['POST'])
def submit_roll():
    if 'employeeid' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    data = request.get_json()

    rollType1 = data.get('rollType1')
    vendorNo1 = data.get('vendorNo1')
    diaCurrent1 = data.get('diaCurrent1')
    standPosition1 = data.get('standPosition1')

    rollType2 = data.get('rollType2')
    vendorNo2 = data.get('vendorNo2')
    diaCurrent2 = data.get('diaCurrent2')
    standPosition2 = data.get('standPosition2')

    standNo = data.get('standNo')

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cur = conn.cursor()

        # Fetch existing roll types and stand positions in this stand
        df = pd.read_sql("""
            SELECT a.STAND_POSITION, a.VENDOR_NO, b.ROLL_TYPE
            FROM STAND_ASBL a
            JOIN VSD_ROLL_ASBL b ON a.VENDOR_NO = b.VENDOR_NO
            WHERE a.STAND_NO = :standno
        """, conn, params={"standno": standNo})

        # Append incoming data to validate all together
        new_entries = pd.DataFrame([
            {'STAND_POSITION': standPosition1, 'VENDOR_NO': vendorNo1, 'ROLL_TYPE': rollType1},
            {'STAND_POSITION': standPosition2, 'VENDOR_NO': vendorNo2, 'ROLL_TYPE': rollType2}
        ])
        combined = pd.concat([df, new_entries], ignore_index=True)

        # Constraint 1: Max 6 rolls
        if combined.shape[0] > 6:
            return jsonify({'success': False, 'message': 'Cannot exceed 6 rolls per stand.'})

        # Constraint 2: Max 2 rolls per roll type
        type_counts = combined['ROLL_TYPE'].value_counts()
        if any(type_counts > 2):
            return jsonify({'success': False, 'message': 'Cannot have more than 2 rolls of the same type in one stand.'})

        # Constraint 3: If roll type appears more than once, STAND_POSITION must differ
        duplicates = combined.groupby('ROLL_TYPE')['STAND_POSITION'].nunique()
        if any((type_counts > 1) & (duplicates < 2)):
            return jsonify({'success': False, 'message': 'Duplicate roll types must have different stand positions (TOP/BOTTOM).'})

        # Validated — continue with inserts and updates
        cur.execute("""
            UPDATE VSD_ROLL_WIB SET "Status" = 208 WHERE "Vendor no" = :1
        """, (vendorNo1,))

        cur.execute("""
            UPDATE VSD_ROLL_WIB SET "Status" = 208 WHERE "Vendor no" = :1
        """, (vendorNo2,))

        cur.execute("""
            INSERT INTO STAND_ASBL (VENDOR_NO, STAND_POSITION, STAND_NO, DIA_CURRENT)
            VALUES (:1, :2, :3, :4)
        """, (vendorNo1, standPosition1, standNo, diaCurrent1))

        cur.execute("""
            INSERT INTO STAND_ASBL (VENDOR_NO, STAND_POSITION, STAND_NO, DIA_CURRENT)
            VALUES (:1, :2, :3, :4)
        """, (vendorNo2, standPosition2, standNo, diaCurrent2))

        cur.execute("""
            UPDATE VSD_ROLL_ASBL SET STAND_NO = :1 WHERE VENDOR_NO = :2
        """, (standNo, vendorNo1))

        cur.execute("""
            UPDATE VSD_ROLL_ASBL SET STAND_NO = :1 WHERE VENDOR_NO = :2
        """, (standNo, vendorNo2))

        cur.execute("""
            SELECT COUNT(*) FROM STAND_ASBL WHERE STAND_NO = :1
        """, (standNo,))
        count = cur.fetchone()[0]

        if count == 6:
            cur.execute("""
                UPDATE STAND_MASTER SET STAND_STATUS = 'ENGAGED' WHERE STAND_NO = :1 AND STAND_STATUS = 'FREE'
            """, (standNo,))

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        print("Error in roll submission:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if 'conn' in locals():
            conn.close()

@bp.route('/get_status_asbl')
def get_status_asbl():
    if 'employeeid' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        df = pd.read_sql("""
    SELECT 
        sa.STAND_NO,
        sa.VENDOR_NO,
        sa.STAND_POSITION,
        sa.DIA_CURRENT,
        rm.ROLL_TYPE
    FROM 
        STAND_ASBL sa
    JOIN 
        VSD_ROLL_WIB rw ON sa.VENDOR_NO = rw."Vendor no"
    JOIN 
        VSD_ROLL_WIB_MASTER rm ON rw."Material Code" = rm.MATERIAL_CODE
    ORDER BY 
        sa.STAND_NO
""", conn)

        data = df.to_dict(orient='records')
        return jsonify(data)

    except Exception as e:
        print("Error fetching stand_asbl data:", e)
        return jsonify([])

    finally:
        if 'conn' in locals():
            conn.close()

@bp.route('/stand_out_action', methods=['POST'])
def stand_out_action():
    if 'employeeid' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    selected_rows = request.get_json()
    if not selected_rows or not isinstance(selected_rows, list):
        return jsonify({'success': False, 'message': 'Invalid input'}), 400

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cur = conn.cursor()

        for row in selected_rows:
            stand_no = row.get('STAND_NO')
            vendor_no = row.get('VENDOR_NO')

            cur.execute("""
                DELETE FROM STAND_ASBL 
                WHERE STAND_NO = :1 AND VENDOR_NO = :2
            """, (stand_no, vendor_no))

            cur.execute("""
                UPDATE STAND_MASTER 
                SET STAND_STATUS = 'FREE' 
                WHERE STAND_NO = :1
            """, (stand_no,))

            cur.execute("""
                UPDATE VSD_ROLL_ASBL 
                SET STAND_NO = NULL 
                WHERE VENDOR_NO = :1
            """, (vendor_no,))
            
            cur.execute("""
                UPDATE VSD_ROLL_WIB SET "Status" = 209 WHERE "Vendor no" = :1
            """, (vendor_no,))

        conn.commit()
        return jsonify({'success': True})

    except Exception as e:
        print("Error in stand_out_action:", e)
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        if 'conn' in locals():
            conn.close()