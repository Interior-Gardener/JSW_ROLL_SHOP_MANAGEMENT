from flask import Blueprint, request, render_template, session, redirect, url_for
import os
import pandas as pd
from config import UPLOAD_FOLDER, DB_DSN, DB_PASSWORD, DB_USER
from utils.validation import validate_excel
from utils.submission import submit_to_db
import oracledb

bp = Blueprint('imr', __name__)

@bp.route('/imr.html')
def imr_page():
    if 'employeeid' not in session:
        return redirect(url_for('login'))
    
    try:
        # Connect to Oracle DB
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

        # Final working query with all enhancements
        query = """
            SELECT 
                w."Sr.no.",
                w."Vendor no",
                w."JSW no",
                w."Asset No",
                w."Bill Entry NO",
                w."Bill Entry Date",
                w."MRN No",
                w."MRN Date",
                m.ROLL_TYPE,
                m.LOC,
                w."Material Code",
                w."Dia (min)",
                w."Dia (current)",
                w."Dia (max)",
                w."Barrel Length",
                w."Total Length",
                w."Chrome%",
                w."Chrome",
                w."Supplier Name",
                w."Roll's Material",
                w."Roll Wt",
                w."Roll Price",
                w."Mode",
                w."Conversion",
                w."Roll Value in INR",
                w."JCDB @  7.5%",
                w."ZSWC@ 10% on CD",
                w."GST@18%",
                w."Clerance @2.5%",
                w."Total value",
                w."Landed Value",
                w."UOM",
                w."PO no",
                w."Acct.ass.Cat.",
                w."LD",
                w."WBS Element",
                w."EPCG Licence No",
                w."EPCG Licence Date",
                w."Gate entry date",
                w."Receiving Date",
                s.STATUS AS "Status Description",
                w."Issue slip No-Store"
            FROM 
                VSD_ROLL_WIB w
            JOIN 
                VSD_ROLL_WIB_MASTER m ON w."Material Code" = m.MATERIAL_CODE
            JOIN 
                STATUS_MASTER s ON w."Status" = s.CODE
            WHERE 
                m.ROLL_TYPE = 'IMR ROLL'
            ORDER BY 
                w."Receiving Date" DESC
        """

        df = pd.read_sql(query, conn)

    except Exception as e:
        print("Error fetching data:", e)
        df = pd.DataFrame()  # Fallback

    finally:
        if 'conn' in locals():
            conn.close()

    data = df.to_dict(orient='records')
    return render_template('imr.html', employeeid=session['employeeid'], table_data=data)
