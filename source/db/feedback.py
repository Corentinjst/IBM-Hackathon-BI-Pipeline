import pymysql

import os
# Database configuration

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE_HC'),
    'charset': 'utf8mb4'
}

def create_feedback_table():
    """Create the feedback table in MariaDB"""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS feedback (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_query TEXT NOT NULL,
        matched_question_id INT,
        matched_question_title VARCHAR(500),
        similarity_score FLOAT,
        was_helpful BOOLEAN DEFAULT NULL,
        user_feedback TEXT,
        response_time_ms INT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (matched_question_id) REFERENCES questions(id),
        INDEX idx_question_id (matched_question_id),
        INDEX idx_timestamp (timestamp),
        INDEX idx_helpful (was_helpful),
        INDEX idx_similarity (similarity_score)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        # Connect to database
        print("=" * 60)
        print("Creating feedback table in MariaDB")
        print("=" * 60)
        
        print("\nConnecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print(f"✓ Connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        
        # Create table
        print("\nCreating feedback table...")
        cursor.execute(create_table_sql)
        connection.commit()
        print("✓ Table 'feedback' created successfully!")
        
        # Verify table structure
        print("\nTable Structure:")
        cursor.execute("DESCRIBE feedback")
        results = cursor.fetchall()
        
        print(f"\n{'Field':<25} {'Type':<20} {'Null':<6} {'Key':<6} {'Default':<15}")
        print("-" * 80)
        for row in results:
            field, type_, null, key, default, extra = row
            default_str = str(default) if default else ''
            print(f"{field:<25} {type_:<20} {null:<6} {key:<6} {default_str:<15}")
        
        print("\n" + "=" * 60)
        print("✅ feedback table is ready!")
        print("=" * 60)
        
        # Close connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_feedback_table()
