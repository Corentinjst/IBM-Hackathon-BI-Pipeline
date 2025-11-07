import pymysql

# Database configuration
DB_CONFIG = {
    'host': 'guereak.com',
    'port': 3306,
    'user': 'votre_user',
    'password': 'votre_password',
    'database': 'help_center',
    'charset': 'utf8mb4'
}

def create_support_tickets_table():
    """Create the support_tickets table in MariaDB"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS support_tickets (
        id INT PRIMARY KEY AUTO_INCREMENT,
        
        -- User Information (minimal)
        user_email VARCHAR(255) NOT NULL,
        user_school ENUM('EMLV', 'ESILV', 'IIM', 'EXECUTIVE') NOT NULL,
        user_type ENUM('student', 'faculty', 'staff') DEFAULT 'student',
        
        -- Question
        question TEXT NOT NULL,
        
        -- Metadata
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Indexes
        INDEX idx_school (user_school),
        INDEX idx_created (created_at),
        INDEX idx_email (user_email)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        # Connect to database
        print("=" * 60)
        print("Creating support_tickets table in MariaDB")
        print("=" * 60)
        
        print("\nConnecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print(f"✓ Connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        
        # Create table
        print("\nCreating support_tickets table...")
        cursor.execute(create_table_sql)
        connection.commit()
        print("✓ Table 'support_tickets' created successfully!")
        
        # Verify table structure
        print("\nTable Structure:")
        cursor.execute("DESCRIBE support_tickets")
        results = cursor.fetchall()
        
        print(f"\n{'Field':<25} {'Type':<30} {'Null':<6} {'Key':<6} {'Default':<15}")
        print("-" * 90)
        for row in results:
            field, type_, null, key, default, extra = row
            default_str = str(default) if default else ''
            print(f"{field:<25} {type_:<30} {null:<6} {key:<6} {default_str:<15}")
        
        print("\n" + "=" * 60)
        print("✅ support_tickets table is ready!")
        print("=" * 60)
        
        # Close connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_support_tickets_table()
