from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
import oracledb
import pandas as pd
from config import DB_DSN, DB_PASSWORD, DB_USER

bp = Blueprint('assembler', __name__)

@bp.route('/assembler.html')
def assembler():
    if 'employeeid' not in session:
        return redirect(url_for('login'))
    return render_template('assembler.html', employeeid=session['employeeid'])

@bp.route('/get_roll_data')
def get_roll_data():
    if 'employeeid' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    roll_type = request.args.get('roll_type')

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

        if not roll_type or roll_type.upper() == "ALL":
            query = """
                SELECT 
                    w."Vendor no", 
                    w."Dia (min)",
                    w."Dia (current)",
                    w."Dia (max)", 
                    m.ROLL_TYPE
                FROM VSD_ROLL_WIB w
                JOIN VSD_ROLL_WIB_MASTER m ON w."Material Code" = m.MATERIAL_CODE
                WHERE w."Status" = 205 ORDER BY w."Dia (current)" asc
            """
            df = pd.read_sql(query, conn)
        else:
            query = """
                SELECT 
                    w."Vendor no", 
                    w."Dia (min)",
                    w."Dia (current)",
                    w."Dia (max)", 
                    m.ROLL_TYPE
                FROM VSD_ROLL_WIB w
                JOIN VSD_ROLL_WIB_MASTER m ON w."Material Code" = m.MATERIAL_CODE
                WHERE m.ROLL_TYPE = :roll_type
                AND w."Status" = 205 ORDER BY w."Dia (current)" asc
            """
            df = pd.read_sql(query, conn, params={"roll_type": roll_type})

        df.rename(columns={
            'Vendor no': 'vendor_no',
            'Dia (min)': 'dia_min',
            'Dia (current)': 'dia_current',
            'Dia (max)': 'dia_max',
            'ROLL_TYPE': 'roll_type'
        }, inplace=True)

        data = df.to_dict(orient='records')

    except Exception as e:
        print("Error fetching data:", e)
        data = []

    finally:
        if 'conn' in locals():
            conn.close()

    return jsonify(data)


@bp.route('/get_chocks')
def get_chocks():
    pos = request.args.get('position', '').upper()    # TOP or BOTTOM
    side = request.args.get('side', '').upper()       # FRONT or BACK

    if not pos or not side:
        return jsonify([])

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        df = pd.read_sql(
            """
            SELECT CHOCK_NO
            FROM CHOCK
            WHERE CHOCK_STATUS = 'FREE' AND POSITION = :pos AND SIDE = :side and brg_no is not null
            """,
            conn,
            params={'pos': pos, 'side': side}
        )
        return jsonify(df['CHOCK_NO'].dropna().tolist())
    except Exception as e:
        print("Error fetching chocks:", e)
        return jsonify([])
    finally:
        if 'conn' in locals():
            conn.close()


@bp.route('/assemble_roll', methods=['POST'])
def assemble_roll():
    if 'employeeid' not in session:
        return jsonify({"status": "unauthorized"}), 401

    data = request.json

    vendor_no = data.get('vendorNo')
    dia_min = data.get('diaMin')
    dia_current=data.get('diaCurrent')
    dia_max = data.get('diaMax')
    roll_type = data.get('rollType')
    position = data.get('position')
    front_chock = data.get('frontChock')
    back_chock = data.get('backChock')

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        insert_sql = """
            INSERT INTO VSD_ROLL_ASBL (ROLL_TYPE, VENDOR_NO, DIA_MIN, DIA_CURRENT, DIA_MAX, POSITION, FRONT_CHOCK, BACK_CHOCK)
            VALUES (:roll_type, :vendor_no, :dia_min, :dia_current, :dia_max, :position, :front_chock, :back_chock)
        """
        cursor.execute(insert_sql, {
            'roll_type': roll_type,
            'vendor_no': vendor_no,
            'dia_min': dia_min,
            'dia_current':dia_current,
            'dia_max': dia_max,
            'position': position,
            'front_chock': front_chock,
            'back_chock': back_chock
        })

        update_wib_sql = """
            UPDATE VSD_ROLL_WIB
            SET "Status" = 206
            WHERE "Vendor no" = :vendor_no
        """
        cursor.execute(update_wib_sql, {'vendor_no': vendor_no})

        if front_chock:
            cursor.execute("""
                UPDATE CHOCK
                SET VENDOR_NO = :vendor_no,
                    ROLL_TYPE = :roll_type,
                    CHOCK_STATUS = 'ENGAGED'
                WHERE CHOCK_NO = :chock_no
            """, {'vendor_no': vendor_no, 'roll_type': roll_type, 'chock_no': front_chock})

        if back_chock:
            cursor.execute("""
                UPDATE CHOCK
                SET VENDOR_NO = :vendor_no,
                    ROLL_TYPE = :roll_type,
                    CHOCK_STATUS = 'ENGAGED'
                WHERE CHOCK_NO = :chock_no
            """, {'vendor_no': vendor_no, 'roll_type': roll_type, 'chock_no': back_chock})

        conn.commit()
        return jsonify({"status": "success"})

    except Exception as e:
        print("Assembly Error:", e)
        if 'conn' in locals():
            conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@bp.route('/get_assembled_rolls')
def get_assembled_rolls():
    if 'employeeid' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        df = pd.read_sql("""
            SELECT * 
            FROM VSD_ROLL_ASBL WHERE STAND_NO IS NULL
        """, conn)

        data = df.to_dict(orient='records')
        return jsonify(data)

    except Exception as e:
        print("Error fetching assembled rolls:", e)
        return jsonify([])

    finally:
        if 'conn' in locals():
            conn.close()

@bp.route('/dechoke_roll', methods=['POST'])
def dechoke_roll():
    try:
        data = request.json
        vendor_no = data.get('vendor_no')
        front_chock = data.get('front_chock')
        back_chock = data.get('back_chock')

        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        # 1st Step: Update VSD_ROLL_WIB Status to 211 for this Vendor No
        update_wib_sql = """
            UPDATE VSD_ROLL_WIB
            SET "Status" = 211
            WHERE "Vendor no" = :vendor_no
        """
        cursor.execute(update_wib_sql, vendor_no=vendor_no)

        # 2nd Step: Free both Chocks in CHOCK table
        free_chock_sql = """
            UPDATE CHOCK
            SET CHOCK_STATUS = 'FREE',
                VENDOR_NO = NULL,
                ROLL_TYPE = NULL
            WHERE CHOCK_NO = :front_chock OR CHOCK_NO = :back_chock
        """
        cursor.execute(free_chock_sql, front_chock=front_chock, back_chock=back_chock)

        # 3rd Step: Delete the selected row from VSD_ROLL_ASBL
        delete_asbl_sql = """
            DELETE FROM VSD_ROLL_ASBL
            WHERE VENDOR_NO = :vendor_no
        """
        cursor.execute(delete_asbl_sql, vendor_no=vendor_no)

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'De-Assemble operations completed.'})

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        return jsonify({'status': 'error', 'message': str(e)})