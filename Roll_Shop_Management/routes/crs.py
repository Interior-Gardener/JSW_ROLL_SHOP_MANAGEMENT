from flask import Blueprint, request, render_template, session, redirect, url_for
import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN

bp = Blueprint('crs', __name__)

@bp.route('/crs.html', methods=['GET', 'POST'])
def crs():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    table_html = ""
    selected_status = None
    update_msg = session.pop('update_msg', None)  # Read flash message from session

    if request.method == 'POST':
        selected_status = request.form.get('status')

        try:
            selected_status = int(selected_status)

            conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
            cursor = conn.cursor()

            sql = """
SELECT 
    w."Sr.no.",
    w."Vendor no",
    w."JSW no",
    w."Asset No",
    w."Bill Entry NO",
    w."Bill Entry Date",
    w."MRN No",
    w."MRN Date",
    m.ROLL_TYPE AS "Roll Type",
    w."Dia (min)",
    w."Dia (max)",
    w."Dia (current)",
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
    s.STATUS AS "Status",
    w."Issue slip No-Store"
FROM 
    VSD_ROLL_WIB w
JOIN 
    STATUS_MASTER s ON w."Status" = s.CODE
JOIN 
    VSD_ROLL_WIB_MASTER m ON w."Material Code" = m.MATERIAL_CODE
WHERE 
    w."Status" = :status
"""

            cursor.execute(sql, status=selected_status)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]

            if rows:
                Vendor_No_index = columns.index("Vendor no")

                table_html += "<form method='POST' action='/update_status_or_issue_slip'>"

                # 🔽 Scrollable wrapper only around the table
                table_html += """
                <div style="
                    max-height: 600px; 
                    overflow-y: auto; 
                    overflow-x: auto;  /* enable horizontal scrolling */
                    border: 1px solid #ccc; 
                    border-radius: 8px; 
                    margin-bottom: 20px;
                    width: 34.5%;       /* take full container width */
                ">
                <table border='1' style="
                    min-width: 1000px;  /* or whatever minimum width you want */
                    border-collapse: collapse;
                ">
                <thead><tr>
                """
                table_html += "<th>Select</th>"
                table_html += ''.join(f"<th>{col}</th>" for col in columns)
                table_html += "</tr></thead><tbody>"

                for row in rows:
                    Vendor_No = row[Vendor_No_index]
                    table_html += "<tr>"
                    table_html += f'<td><input type="checkbox" name="selected_rolls" value="{Vendor_No}" style="margin: 4px 0 0; line-height: normal; width: 20px; height: 20px;"></td>'
                    table_html += ''.join(f"<td>{cell}</td>" for cell in row)
                    table_html += "</tr>"

                # 🔽 End scrollable wrapper
                table_html += "</tbody></table></div>"

                # Show special dual dropdowns and buttons only for DISCARDED status (300)
                if selected_status == 300:
                    table_html += """
                    <!-- Sold Status update -->
                    <label for='issue_slip_status' style="
                        display: inline-block;
                        margin: 20px 10px 10px 0;
                        font-weight: 600;
                        font-size: large;
                        letter-spacing: 0.025em;
                        color: #dc1229;
                    ">Sold Status:</label>

                    <select name="issue_slip_status" id="issue_slip_status" style="
                        background: white;
                        border: 2px solid #e2e8f0;
                        padding: 10px 14px;
                        font-size: 16px;
                        border-radius: 8px;
                        cursor: pointer;
                        min-width: 160px;
                        margin-right: 20px;
                    ">
                        <option value="" disabled selected>-- Select Option --</option>
                        <option value="SOLD">SOLD</option>
                        <option value="NOT SOLD">NOT SOLD</option>
                    </select>

                    <button type="submit" name="update_issue_slip" style="
                        background-color: rgba(220, 18, 41, 0.1);
                        color: #dc1229;
                        padding: 12px 24px;
                        margin: 15px 10px 15px 0;
                        border: 2px solid rgba(220, 18, 41, 0.3);
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 500;
                        cursor: pointer;
                        transition: background-color 0.2s ease;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    "
                    onmouseover="this.style.backgroundColor='rgba(220, 18, 41, 0.3)';"
                    onmouseout="this.style.backgroundColor='rgba(220, 18, 41, 0.1)';"
                    >Update Issue Slip No-Store</button>

                    <!-- Normal Status update -->
                    <label for='new_status' style="
                        display: inline-block;
                        margin: 20px 0 10px auto;
                        font-weight: 600;
                        font-size: large;
                        letter-spacing: 0.025em;
                        width: 200px;
                        border-radius: 25px;
                        color: #dc1229;
                        text-align: center;
                        padding: 10px;
                        background: linear-gradient(45deg, rgba(220, 18, 41, 0.1), rgba(220, 18, 41, 0.2));
                        border: 2px solid rgba(220, 18, 41, 0.3);
                    ">New Status:</label>

                    <select name="new_status" style="
                        background: white;
                        border: 2px solid #e2e8f0;
                        padding: 12px 16px;
                        font-size: 16px;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        appearance: none;
                        background-image: url('data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e');
                        background-position: right 12px center;
                        background-repeat: no-repeat;
                        background-size: 16px;
                        padding-right: 40px;
                        min-width: 200px;
                    ">
                        <option value="" disabled selected>-- Select Status --</option>
                        <option value='100'>NEW</option>
                        <option value='201'>AVAILABLE FOR GRINDER-1</option>
                        <option value='202'>AVAILABLE FOR GRINDER-2</option>
                        <option value='203'>AVAILABLE FOR GRINDER-3</option>
                        <option value='214'>AVAILABLE FOR POMINI</option>
                        <option value='215'>AVAILABLE FOR MESTA</option>
                        <option value='204'>IN-PROCESS</option>
                        <option value='205'>GROUND</option>
                        <option value='213'>HOLD</option>
                        <option value='206'>CHOKED</option>
                        <option value='207'>IN FRONT OF MILL</option>
                        <option value='208'>AT-MILL</option>
                        <option value='209'>MILL-OUT</option>
                        <option value='210'>DECHOKED</option>
                        <option value='211'>AVAILABLE FOR GRINDING</option>
                        <option value='212'>OUT OF SERVICE</option>
                        <option value='300'>DISCARDED</option>
                    </select>

                    <button type="submit" name="update_status" style="
                        background-color: rgba(220, 18, 41, 0.1);
                        color: #dc1229;
                        padding: 12px 24px;
                        margin: 15px 0;
                        border: 2px solid rgba(220, 18, 41, 0.3);
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 500;
                        cursor: pointer;
                        transition: background-color 0.2s ease;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    "
                    onmouseover="this.style.backgroundColor='rgba(220, 18, 41, 0.3)';"
                    onmouseout="this.style.backgroundColor='rgba(220, 18, 41, 0.1)';"
                    >Update Selected Status</button>
                    """

                else:
                    # Normal status update dropdown + submit button for other statuses
                    table_html += """
                    <label for='new_status' style="
                        display: inline-block;
                        margin: 20px 0 10px auto;
                        font-weight: 600;
                        font-size: large;
                        letter-spacing: 0.025em;
                        width: 200px;
                        border-radius: 25px;
                        color: #dc1229;
                        text-align: center;
                        padding: 10px;
                        background: linear-gradient(45deg, rgba(220, 18, 41, 0.1), rgba(220, 18, 41, 0.2));
                        border: 2px solid rgba(220, 18, 41, 0.3);
                        position: relative;
                    ">New Status:</label>

                    <select name="new_status" required style="
                        background: white;
                        border: 2px solid #e2e8f0;
                        padding: 12px 16px;
                        font-size: 16px;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        appearance: none;
                        background-image: url('data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e');
                        background-position: right 12px center;
                        background-repeat: no-repeat;
                        background-size: 16px;
                        padding-right: 40px;
                        min-width: 200px;
                        position: relative;
                    ">
                        <option value="" disabled selected>-- Select Status --</option>
                        <option value='100'>NEW</option>
                        <option value='201'>AVAILABLE FOR GRINDER-1</option>
                        <option value='202'>AVAILABLE FOR GRINDER-2</option>
                        <option value='203'>AVAILABLE FOR GRINDER-3</option>
                        <option value='214'>AVAILABLE FOR POMINI</option>
                        <option value='215'>AVAILABLE FOR MESTA</option>
                        <option value='204'>IN-PROCESS</option>
                        <option value='205'>GROUND</option>
                        <option value='213'>HOLD</option>
                        <option value='206'>CHOKED</option>
                        <option value='207'>IN FRONT OF MILL</option>
                        <option value='208'>AT-MILL</option>
                        <option value='209'>MILL-OUT</option>
                        <option value='210'>DECHOKED</option>
                        <option value='211'>AVAILABLE FOR GRINDING</option>
                        <option value='212'>OUT OF SERVICE</option>
                        <option value='300'>DISCARDED</option>
                    </select>

                    <br><br>
                    <button type="submit" name="update_status" style="
                        background-color: rgba(220, 18, 41, 0.1);
                        color: #dc1229;
                        padding: 12px 24px;
                        margin: 15px 0;
                        border: 2px solid rgba(220, 18, 41, 0.3);
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 500;
                        cursor: pointer;
                        transition: background-color 0.2s ease;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                        position: relative;
                    "
                    onmouseover="this.style.backgroundColor='rgba(220, 18, 41, 0.3)';"
                    onmouseout="this.style.backgroundColor='rgba(220, 18, 41, 0.1)';"
                    >Update Selected</button>
                    """

                table_html += "</form>"

            else:
                table_html = f"<p>No records found for status <strong>{selected_status}</strong>.</p>"

        except Exception as e:
            table_html = f"<p>Error fetching data: {e}</p>"

    return render_template('crs.html', table=table_html, employeeid=session['employeeid'], update_msg=update_msg)


@bp.route('/update_status_or_issue_slip', methods=['POST'])
def update_status_or_issue_slip():
    if 'employeeid' not in session:
        return redirect(url_for('login'))

    selected_rolls = request.form.getlist('selected_rolls')
    issue_slip_status = request.form.get('issue_slip_status')
    new_status = request.form.get('new_status')

    update_issue_slip_clicked = 'update_issue_slip' in request.form
    update_status_clicked = 'update_status' in request.form

    if not selected_rolls:
        session['update_msg'] = "⚠️ Please select at least one row."
        return redirect(url_for('crs.crs'))

    try:
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        cursor = conn.cursor()

        if update_issue_slip_clicked:
            if not issue_slip_status or issue_slip_status not in ['SOLD', 'NOT SOLD']:
                session['update_msg'] = "⚠️ Please select SOLD or NOT SOLD for Issue Slip update."
                return redirect(url_for('crs.crs'))

            for vendor_no in selected_rolls:
                cursor.execute(
                    'UPDATE VSD_ROLL_WIB SET "Issue slip No-Store" = :1 WHERE "Vendor no" = :2',
                    [issue_slip_status, vendor_no]
                )
            conn.commit()
            session['update_msg'] = f"✅ Updated Issue slip No-Store to '{issue_slip_status}' for {len(selected_rolls)} record(s)."

        elif update_status_clicked:
            if not new_status:
                session['update_msg'] = "⚠️ Please select a new status."
                return redirect(url_for('crs.crs'))

            new_status_num = int(new_status)
            for vendor_no in selected_rolls:
                cursor.execute(
                    'UPDATE VSD_ROLL_WIB SET "Status" = :1 WHERE "Vendor no" = :2',
                    [new_status_num, vendor_no]
                )
            conn.commit()
            session['update_msg'] = f"✅ Updated status to {new_status_num} for {len(selected_rolls)} record(s)."

        else:
            session['update_msg'] = "⚠️ Unknown update action."

    except Exception as e:
        session['update_msg'] = f"❌ Error during update: {e}"

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('crs.crs'))
