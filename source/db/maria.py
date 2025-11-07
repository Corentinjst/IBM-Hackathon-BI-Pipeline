import pandas as pd
import pymysql
from datetime import datetime
import re
import os

# Database configuration
DB_CONFIG = {
    'host': 'guereak.com',
    'port': 3306,
    'user': 'votre_user',
    'password': 'votre_password',
    'database': 'help_center',
    'charset': 'utf8mb4'
}

# File path - relative to this script's location
# Script is in DB/ folder, Excel file is in Data/ folder (both in same parent directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(SCRIPT_DIR, '..', 'Data', 'questions.xlsx')

def create_table(cursor):
    """Create the questions table if it doesn't exist"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS questions (
        id INT PRIMARY KEY AUTO_INCREMENT,
        title VARCHAR(500),
        content TEXT,
        date DATE,
        post_type VARCHAR(50),
        langues VARCHAR(100),
        thematiques TEXT,
        utilisateurs TEXT,
        ecoles TEXT,
        status VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_post_type (post_type),
        INDEX idx_status (status),
        INDEX idx_langues (langues)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    cursor.execute(create_table_sql)
    print("✓ Table 'questions' created/verified")

def clean_date(date_val):
    """Convert date to proper format"""
    if pd.isna(date_val):
        return None
    if isinstance(date_val, str):
        try:
            return datetime.strptime(date_val, '%Y-%m-%d').date()
        except:
            return None
    return date_val

def insert_data(cursor, df, sheet_name, allow_updates=False):
    """Insert data from dataframe into database
    
    Args:
        cursor: Database cursor
        df: DataFrame with data to insert
        sheet_name: Name of the sheet being processed
        allow_updates: If True, allows updating existing records. If False, throws error on duplicate ID
    """
    if allow_updates:
        # Original behavior: update if exists
        insert_sql = """
        INSERT INTO questions 
        (id, title, content, date, post_type, langues, thematiques, utilisateurs, ecoles, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            content = VALUES(content),
            date = VALUES(date),
            post_type = VALUES(post_type),
            langues = VALUES(langues),
            thematiques = VALUES(thematiques),
            utilisateurs = VALUES(utilisateurs),
            ecoles = VALUES(ecoles),
            status = VALUES(status)
        """
    else:
        # Safer behavior: error on duplicate (prevents overwrites)
        # If ID is NULL, auto-increment will assign it
        insert_sql = """
        INSERT INTO questions 
        (id, title, content, date, post_type, langues, thematiques, utilisateurs, ecoles, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    
    inserted = 0
    updated = 0
    errors = 0
    
    for idx, row in df.iterrows():
        try:
            # If id is not provided or is NaN, pass None to let auto-increment handle it
            row_id = int(row['id']) if pd.notna(row['id']) else None
            
            # Prepare data
            data = (
                row_id,
                str(row['Title']) if pd.notna(row['Title']) else None,
                str(row['Content']) if pd.notna(row['Content']) else None,
                clean_date(row['Date']),
                str(row['Post Type']) if pd.notna(row['Post Type']) else None,
                str(row['Langues']) if pd.notna(row['Langues']) else None,
                str(row['Thématiques']) if pd.notna(row['Thématiques']) else None,
                str(row['Utilisateurs']) if pd.notna(row['Utilisateurs']) else None,
                str(row['Écoles']) if pd.notna(row['Écoles']) else None,
                str(row['Status']) if pd.notna(row['Status']) else None
            )
            
            cursor.execute(insert_sql, data)
            
            if cursor.rowcount == 1:
                inserted += 1
            elif cursor.rowcount == 2:
                updated += 1
                
        except pymysql.err.IntegrityError as e:
            errors += 1
            if e.args[0] == 1062:  # Duplicate entry error code
                print(f"  ✗ ERROR: Row {idx} (ID: {row.get('id', 'N/A')}) - ID already exists! Cannot overwrite.")
            else:
                print(f"  ✗ Integrity Error on row {idx} (ID: {row.get('id', 'N/A')}): {str(e)}")
        except Exception as e:
            errors += 1
            print(f"  ✗ Error on row {idx} (ID: {row.get('id', 'N/A')}): {str(e)}")
    
    return inserted, updated, errors

def main():
    print("=" * 60)
    print("Loading Excel data to MariaDB - Help Center")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n1. Connecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print(f"✓ Connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        
        # Create table
        print("\n2. Creating/verifying table structure...")
        create_table(cursor)
        
        # Load Excel file
        print(f"\n3. Loading Excel file: Questions.xlsx")
        
        # Read the single sheet (no need to specify sheet_name, it will read the first/only sheet)
        print(f"\n4. Processing data...")
        df = pd.read_excel(EXCEL_FILE)
        
        print(f"  → Found {len(df)} rows")
        
        total_inserted = 0
        total_updated = 0
        total_errors = 0
        
        # Set to True if you want to allow updates of existing records
        # Set to False (recommended) to prevent accidental overwrites
        ALLOW_UPDATES = False  # Change to False for safer inserts
        
        # Insert data
        inserted, updated, errors = insert_data(cursor, df, 'All Questions', allow_updates=ALLOW_UPDATES)
        
        total_inserted += inserted
        total_updated += updated
        total_errors += errors
        
        print(f"  ✓ Inserted: {inserted} | Updated: {updated} | Errors: {errors}")
        
        # Commit changes
        connection.commit()
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total records inserted: {total_inserted}")
        print(f"Total records updated:  {total_updated}")
        print(f"Total errors:           {total_errors}")
        print("=" * 60)
        print("✓ Data successfully loaded to MariaDB!")
        
        # Close connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()