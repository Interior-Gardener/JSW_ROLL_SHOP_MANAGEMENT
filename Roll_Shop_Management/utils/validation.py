import pandas as pd

expected_columns = [
    "Sr.no.", "Vendor no", "JSW no", "Asset No", "Bill Entry NO", "Bill Entry Date", "MRN No", "MRN Date",
    "Material Code", "Dia (min)", "Dia (max)", "Barrel Length", "Total Length", "Chrome%", "Chrome", "Supplier Name",
    "Roll's Material", "Roll Wt", "Roll Price", "Mode", "Conversion", "Roll Value in INR", "JCDB @  7.5%",
    "ZSWC@ 10% on CD", "GST@18%", "Clerance @2.5%", "Total value", "Landed Value", "UOM", "PO no",
    "Acct.ass.Cat.", "LD", "WBS Element", "EPCG Licence No", "EPCG Licence Date", "Gate entry date",
    "Receiving Date", "Status", "Issue slip No-Store", "Dia (current)"
]

required_columns = [
    "Sr.no.", "Vendor no", "JSW no", "Asset No", "Bill Entry NO", "Bill Entry Date",
    "MRN No", "MRN Date", "Material Code", "Dia (min)",  "Dia (max)", "Barrel Length",
    "Total Length", "Chrome%", "Chrome", "Supplier Name", "Roll's Material", "Roll Wt",
    "UOM", "PO no", "WBS Element", "EPCG Licence No", "EPCG Licence Date",
    "Gate entry date", "Receiving Date", "Dia (current)"
]

date_columns = [
    'Bill Entry Date', 'MRN Date', 'EPCG Licence Date', 'Gate entry date', 'Receiving Date'
]

numeric_columns = [
    'Sr.no.', 'Asset No', 'Bill Entry NO', 'MRN No', 'Material Code',
    'Dia (min)', 'Dia (max)', 'Barrel Length', 'Total Length', 'Chrome%', 'Chrome',
    'Roll Wt', 'Roll Price', 'Conversion', 'Roll Value in INR', 'JCDB @  7.5%',
    'ZSWC@ 10% on CD', 'GST@18%', 'Clerance @2.5%', 'Total value', 'Landed Value', 'PO no',
    'EPCG Licence No','Status', 'Dia (current)'
]

def validate_excel(df):
    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        return False, f"Missing columns: {', '.join(missing)}"

    nulls = [col for col in required_columns if df[col].isnull().any()]
    if nulls:
        return False, f"Nulls in required columns: {', '.join(nulls)}"

    try:
        for col in df.columns:
            if col in date_columns:
                df[col] = pd.to_datetime(df[col], dayfirst=True, errors='raise')
            elif col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='raise')
            else:
                df[col] = df[col].astype(str)
    except Exception as e:
        return False, f"Data type error: {str(e)}"

    if df["Vendor no"].duplicated().any() or df["JSW no"].duplicated().any():
        return False, "Duplicates in 'Vendor no' or 'JSW no'"

    return True, df
