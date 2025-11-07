import pymysql
from datetime import datetime
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


def insert_synthetic_feedback():
    """Insert synthetic feedback data into the feedback table"""
    
    # Synthetic feedback data
    feedback_data = [
        # High confidence, helpful
        ('Comment créer une convention de stage ?', 2650, 'Comment créer une convention de stage', 0.95, True, 'Très clair, merci !', 245, '2025-11-05 09:15:23'),
        
        # High confidence, helpful
        ('Certificat médical absence', 2133, 'Un certificat médical peut-il excuser une absence?', 0.88, True, None, 198, '2025-11-05 10:22:45'),
        
        # Medium confidence, not helpful
        ('Ma boîte est au Canada, comment faire ?', 2650, 'Comment créer une convention de stage', 0.62, False, 'Ne répond pas à ma question sur les entreprises étrangères', 312, '2025-11-05 11:05:12'),
        
        # High confidence, no feedback yet
        ('Procédure convention stage', 2650, 'Comment créer une convention de stage', 0.91, None, None, 223, '2025-11-05 11:30:08'),
        
        # Low confidence, not helpful
        ('Stage non rémunéré est-ce légal ?', 2650, 'Comment créer une convention de stage', 0.54, False, 'Pas du tout ce que je cherchais', 289, '2025-11-05 12:15:33'),
        
        # Medium confidence, helpful (surprising!)
        ('Différence entre stage et alternance', 2133, 'Un certificat médical peut-il excuser une absence?', 0.67, True, 'Indirectement utile', 267, '2025-11-05 13:42:19'),
        
        # High confidence, helpful
        ('Vidéo bienvenue EMLV', 2528, 'Bienvenue à l\'EMLV !', 0.93, True, 'Super vidéo !', 178, '2025-11-05 14:20:55'),
        
        # Low confidence, no feedback yet
        ('Combien d\'absences autorisées ?', 2133, 'Un certificat médical peut-il excuser une absence?', 0.58, None, None, 301, '2025-11-05 15:10:41'),
        
        # High confidence, not helpful
        ('Convention de stage documents', 2650, 'Comment créer une convention de stage', 0.87, False, 'Trop long, je voulais juste la liste des docs', 234, '2025-11-05 16:05:27'),
        
        # Medium confidence, helpful
        ('Excuser une absence maladie', 2133, 'Un certificat médical peut-il excuser une absence?', 0.73, True, None, 256, '2025-11-05 16:45:18')
    ]
    
    insert_sql = """
    INSERT INTO feedback 
    (user_query, matched_question_id, matched_question_title, similarity_score, was_helpful, user_feedback, response_time_ms, timestamp) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        # Connect to database
        print("=" * 60)
        print("Inserting Synthetic Feedback Data")
        print("=" * 60)
        
        print("\nConnecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print(f"✓ Connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        
        # Insert data
        print("\nInserting feedback records...")
        inserted = 0
        errors = 0
        
        for idx, data in enumerate(feedback_data, 1):
            try:
                cursor.execute(insert_sql, data)
                inserted += 1
                print(f"  ✓ Record {idx}: '{data[0][:50]}...'")
            except Exception as e:
                errors += 1
                print(f"  ✗ Error on record {idx}: {str(e)}")
        
        # Commit changes
        connection.commit()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total records inserted: {inserted}")
        print(f"Total errors:           {errors}")
        print("=" * 60)
        print("✅ Synthetic feedback data loaded successfully!")
        
        # Close connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    insert_synthetic_feedback()
