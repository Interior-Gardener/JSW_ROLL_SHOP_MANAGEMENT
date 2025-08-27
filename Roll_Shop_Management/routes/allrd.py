from flask import Blueprint, request, render_template, session, redirect, url_for
import pandas as pd
import oracledb
from config import DB_DSN, DB_PASSWORD, DB_USER

bp = Blueprint('allrd', __name__)

@bp.route('/allrd.html')
def allrd():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    error_msg = None
    data = []
    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)

        query = """
SELECT
    r."Sr.no.",
    r."Vendor no",
    r."JSW no",
    r."Asset No",
    r."Bill Entry NO",
    r."Bill Entry Date",
    r."MRN No",
    r."MRN Date",
    m."ROLL_TYPE" AS "Roll Type",
    r."Dia (min)",
    r."Dia (current)",
    r."Dia (max)",
    r."Barrel Length",
    r."Total Length",
    r."Chrome%",
    r."Chrome",
    r."Supplier Name",
    r."Roll's Material",
    r."Roll Wt",
    r."Roll Price",
    r."Mode",
    r."Conversion",
    r."Roll Value in INR",
    r."JCDB @  7.5%",
    r."ZSWC@ 10% on CD",
    r."GST@18%",
    r."Clerance @2.5%",
    r."Total value",
    r."Landed Value",
    r."UOM",
    r."PO no",
    r."Acct.ass.Cat.",
    r."LD",
    r."WBS Element",
    r."EPCG Licence No",
    r."EPCG Licence Date",
    r."Gate entry date",
    r."Receiving Date",
    sm."STATUS" as "Status",
    r."Issue slip No-Store"
FROM VSD_ROLL_WIB r
LEFT JOIN STATUS_MASTER sm ON r."Status" = sm."CODE"
LEFT JOIN vsd_roll_wib_master m ON r."Material Code" = m.MATERIAL_CODE ORDER BY r."Receiving Date" DESC

"""


        df = pd.read_sql(query, conn)
        data = df.to_dict(orient='records')

    except Exception as e:
        error_msg = str(e)

    finally:
        if 'conn' in locals():
            conn.close()

    return render_template('allrd.html', employeeid=session['employeeid'], table_data=data, error_msg=error_msg)
