from flask import Blueprint, request, session, redirect, url_for, render_template
import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN

bp = Blueprint('grinder', __name__)

@bp.route('/grinder.html', methods=['GET', 'POST'])
def grinder():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    table_html = ""
    update_msg = session.pop('update_msg', None)
    submit_label = None
    next_status = None
    submit_form = False
    show_submit_immediately = False

    if request.method == 'POST':
        selected_status = request.form.get('status') or request.form.get('next_status')   # from dropdown or form
        selected_roll = request.form.get('selected_rolls')  # radio selection
        next_status = request.form.get('next_status')

        # Inspection form fields
        current_dia = request.form.get('currentDiameter')
        osr = request.form.get('osRoughness')
        cr = request.form.get('centerRoughness')
        dsr = request.form.get('dsRoughness')
        hardness = []
        for i in range(1, 11):
            val = request.form.get(f'hardness{i}')
            hardness.append(float(val) if val else None)

        valid_hardness_values = [h for h in hardness if h is not None]
        avg_hardness = (sum(valid_hardness_values) / len(valid_hardness_values)) if valid_hardness_values else None
        eddy_current = request.form.get('eddyCurrent')
        ust = request.form.get('ust')
        remark = request.form.get('remark')

        try:
            conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
            cursor = conn.cursor()

            # CASE 1: Mark as GROUND or NOT OK (status 213)
            if selected_roll and next_status and int(next_status) == 205:
                new_status = 213 if ust == "NOTOK" else 205

                update_sql = '''UPDATE VSD_ROLL_WIB
                                SET "Status" = :status,
                                    "Dia (current)" = :dia_current
                                WHERE "Vendor no" = :vendor_no'''
                cursor.execute(update_sql, status=new_status, dia_current=float(current_dia), vendor_no=selected_roll)

                cursor.execute('SELECT "JSW no" FROM VSD_ROLL_WIB WHERE "Vendor no" = :vendor_no', vendor_no=selected_roll)
                jsw_no_row = cursor.fetchone()
                jsw_no = jsw_no_row[0] if jsw_no_row else None

                insert_sql = '''
                    INSERT INTO HARDNESS (
                        VENDOR_NO, JSW_NO, DIA_CURRENT, OSR, CR, DSR,
                        HARDNESS_1, HARDNESS_2, HARDNESS_3, HARDNESS_4, HARDNESS_5,
                        HARDNESS_6, HARDNESS_7, HARDNESS_8, HARDNESS_9, HARDNESS_10,
                        AVG_HARDNESS, EDDY_CURRENT, UST, REMARK
                    ) VALUES (
                        :vendor_no, :jsw_no, :dia_current, :osr, :cr, :dsr,
                        :h1, :h2, :h3, :h4, :h5,
                        :h6, :h7, :h8, :h9, :h10,
                        :avg_hardness, :eddy_current, :ust, :remark
                    )
                '''
                cursor.execute(insert_sql,
                               vendor_no=selected_roll,
                               jsw_no=jsw_no,
                               dia_current=float(current_dia),
                               osr=float(osr) if osr else None,
                               cr=float(cr) if cr else None,
                               dsr=float(dsr) if dsr else None,
                               h1=hardness[0], h2=hardness[1], h3=hardness[2], h4=hardness[3], h5=hardness[4],
                               h6=hardness[5], h7=hardness[6], h8=hardness[7], h9=hardness[8], h10=hardness[9],
                               avg_hardness=avg_hardness,
                               eddy_current=float(eddy_current) if eddy_current else None,
                               ust=ust,
                               remark=remark)

                conn.commit()
                session['update_msg'] = f"Roll {selected_roll} marked as {'NOT OK - status 213' if ust == 'NOTOK' else 'GROUND - status 205'} and inspection saved."
                return redirect(url_for('grinder.grinder'))

            # CASE 2: Mark as IN-PROCESS
            elif selected_roll and next_status and int(next_status) == 204:
                update_sql = '''UPDATE VSD_ROLL_WIB
                                SET "Status" = :status
                                WHERE "Vendor no" = :vendor_no'''
                cursor.execute(update_sql, status=204, vendor_no=selected_roll)
                conn.commit()
                session['update_msg'] = f"Roll {selected_roll} marked as IN-PROCESS."
                return redirect(url_for('grinder.grinder'))

            # Determine dropdown state
            if not selected_status:
                raise ValueError("No status provided.")

            status_code = int(selected_status)
            if status_code in [201, 202, 203, 214, 215, 213]:
                submit_form = False
                submit_label = "Mark Selected as IN-PROCESS"
                next_status = 204
                show_submit_immediately = True
            elif status_code == 204:
                submit_form = True
                submit_label = "Mark Selected as GROUND"
                next_status = 205
                show_submit_immediately = False
            else:
                submit_form = False
                submit_label = None
                next_status = None
                show_submit_immediately = False

            # Query matching rolls
            sql = '''
                SELECT
                    r."Sr.no.",
                    r."Vendor no",
                    r."JSW no",
                    m."ROLL_TYPE" AS "Roll Type",
                    m."LOC" AS "Location",
                    r."Dia (current)",
                    r."Barrel Length",
                    r."Total Length",
                    r."Supplier Name",
                    r."Mode",
                    sm."STATUS" AS "Status"
                FROM VSD_ROLL_WIB r
                LEFT JOIN STATUS_MASTER sm ON r."Status" = sm."CODE"
                LEFT JOIN VSD_ROLL_WIB_MASTER m ON r."Material Code" = m.MATERIAL_CODE
                WHERE r."Status" = :status
                ORDER BY r."Sr.no."
            '''
            cursor.execute(sql, status=status_code)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            if rows:
                vendor_index = columns.index("Vendor no")
                table_html = "<table border='1'><thead><tr><th>Select</th>"
                table_html += ''.join(f"<th>{col}</th>" for col in columns)
                table_html += "</tr></thead><tbody>"

                for row in rows:
                    vendor_no = row[vendor_index]
                    table_html += "<tr>"
                    table_html += (
                        f'<td><input type="radio" name="selected_rolls" value="{vendor_no}" '
                        f'style="margin: 4px 0 0; line-height: normal; width: 20px; height: 20px;"></td>'
                    )
                    table_html += ''.join(f"<td>{cell}</td>" for cell in row)
                    table_html += "</tr>"

                table_html += "</tbody></table>"
            else:
                table_html = "<p>No records found.</p>"

        except Exception as e:
            if "int() argument must be a string" in str(e):
                table_html = "<p style='color: red; font-size:25px'>Please select at least one roll.</p>"
            else:
                table_html = f"<p>Error: {e}</p>"

    return render_template(
        'grinder.html',
        table=table_html,
        update_msg=update_msg,
        employeeid=session['employeeid'],
        submit_label=submit_label,
        next_status=next_status,
        submit_form=submit_form,
        show_submit_immediately=show_submit_immediately
    )
