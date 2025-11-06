import pandas as pd
import pymysql
from datetime import datetime
import re
from dotenv import load_dotenv
import os

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE_HC'),
    'charset': 'utf8mb4'
}

# File path - relative to this script's location
# Script is in DB/ folder, Excel file is in Data/ folder (both in same parent directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(SCRIPT_DIR, '..', 'data', 'questions.xlsx')

def create_table(cursor):
    """Create the questions table if it doesn't exist"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS questions (
        id INT PRIMARY KEY,
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

def insert_data(cursor, df, sheet_name):
    """Insert data from dataframe into database"""
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
    
    inserted = 0
    updated = 0
    errors = 0
    
    for idx, row in df.iterrows():
        try:
            # Prepare data
            data = (
                int(row['id']) if pd.notna(row['id']) else None,
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
        
        # Read all sheets
        sheet_names = ['Questions-Export-2025-October-2', 'Video Export', 'Tutoriel Export']
        
        total_inserted = 0
        total_updated = 0
        total_errors = 0
        
        for sheet_name in sheet_names:
            try:
                print(f"\n4. Processing sheet: '{sheet_name}'")
                df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
                
                print(f"  → Found {len(df)} rows")
                
                # Insert data
                inserted, updated, errors = insert_data(cursor, df, sheet_name)
                
                total_inserted += inserted
                total_updated += updated
                total_errors += errors
                
                print(f"  ✓ Inserted: {inserted} | Updated: {updated} | Errors: {errors}")
                
            except Exception as e:
                print(f"  ✗ Error reading sheet '{sheet_name}': {str(e)}")
        
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