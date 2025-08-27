import pandas as pd
import oracledb
from config import DB_USER, DB_PASSWORD, DB_DSN
from .validation import expected_columns, required_columns, date_columns, numeric_columns

def clean_value(col, val):
    try:
        if pd.isna(val):
            return None

        if col in date_columns:
            return pd.to_datetime(val, dayfirst=True, errors='coerce').to_pydatetime()

        elif col in numeric_columns:
            return float(val)

        else:
            val = str(val).strip()
            return val if val.lower() not in ('', 'nan', 'none') else None

    except Exception as e:
        # Optional: log or print(f"Error cleaning column {col} with value {val}: {e}")
        return None

def submit_to_db(df, table_name, backup_table_name="VSD_ROLL_WIB_BACKUP"):
    ready_to_insert, failed = 0, 0
    failed_rows = []

    # ✅ Clean Status column before loop: convert non-numeric to NaN
    if "Status" in df.columns:
        df["Status"] = pd.to_numeric(df["Status"], errors="coerce")

    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as conn:
            cursor = conn.cursor()

            for index, row in df.iterrows():
                try:
                    formatted_row = {}

                    for col in expected_columns:
                        if col in df.columns and pd.notna(row[col]):
                            cleaned = clean_value(col, row[col])

                            # ❗ Special case: Status must be numeric or skipped
                            if col == "Status":
                                if isinstance(cleaned, (int, float)):
                                    formatted_row[col] = cleaned
                                else:
                                    # Skip Status to use Oracle default
                                    continue
                            else:
                                formatted_row[col] = cleaned
                        elif col == "Status":
                            # Status not in row or NaN — omit it to trigger DEFAULT
                            continue
                        else:
                            formatted_row[col] = None

                    # ✅ Build final insert query now that row is ready
                    cols = ', '.join(f'"{col}"' for col in formatted_row.keys())
                    vals = ', '.join(f':{i+1}' for i in range(len(formatted_row)))

                    # Insert into backup table (always full insert)
                    cursor.execute(f"""
                        INSERT INTO {backup_table_name} ({cols}) VALUES ({vals})
                    """, list(formatted_row.values()))

                    # Check for duplicate in main table
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name}
                        WHERE "Vendor no" = :1 AND "JSW no" = :2
                    """, [formatted_row['Vendor no'], formatted_row['JSW no']])
                    exists = cursor.fetchone()[0]

                    if exists:
                        # Build update only for changed fields
                        update_cols = [col for col in formatted_row if col not in ['Vendor no', 'JSW no']]
                        set_clause = ', '.join(f'"{col}" = :{i+1}' for i, col in enumerate(update_cols))
                        values = [formatted_row[col] for col in update_cols]
                        values.extend([formatted_row['Vendor no'], formatted_row['JSW no']])

                        cursor.execute(f"""
                            UPDATE {table_name} SET {set_clause}
                            WHERE "Vendor no" = :{len(values)-1} AND "JSW no" = :{len(values)}
                        """, values)
                    else:
                        cursor.execute(f"""
                            INSERT INTO {table_name} ({cols}) VALUES ({vals})
                        """, list(formatted_row.values()))

                    ready_to_insert += 1

                except Exception as e:
                    failed += 1
                    failed_rows.append({
                        'row_index': index,
                        'error': str(e),
                        'row_data': row.to_dict()
                    })

            if failed > 0:
                conn.rollback()
                return False, f"❌ Submission failed. No data inserted/updated.\nFailed rows: {failed_rows}"

            conn.commit()

    except Exception as e:
        return False, f"❌ Submission Error: {e}"

    return True, f"✅ Submission complete: {ready_to_insert} inserted/updated, 0 failed."
