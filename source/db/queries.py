import pymysql
import pandas as pd
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


def run_query(cursor, query, description):
    """Run a query and display results"""
    print(f"\n{'='*70}")
    print(f"📊 {description}")
    print(f"{'='*70}")
    print(f"Query: {query}\n")
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Create DataFrame for nice display
        df = pd.DataFrame(results, columns=columns)
        print(df.to_string(index=False))
        print(f"\n✓ Returned {len(results)} row(s)")
    else:
        print("No results returned")
    
    return results

def main():
    print("=" * 70)
    print("🔍 DATABASE VERIFICATION - Help Center Questions")
    print("=" * 70)
    
    try:
        # Connect to database
        print("\n⚡ Connecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print(f"✓ Connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
        
        # Query 1: Count total questions
        run_query(cursor, 
                  "SELECT COUNT(*) as total_questions FROM questions",
                  "Total Number of Questions")
        
        # Query 2: Count by Post Type
        run_query(cursor,
                  "SELECT post_type, COUNT(*) as count FROM questions GROUP BY post_type ORDER BY count DESC",
                  "Questions by Post Type")
        
        # Query 3: Count by Status
        run_query(cursor,
                  "SELECT status, COUNT(*) as count FROM questions GROUP BY status ORDER BY count DESC",
                  "Questions by Status")
        
        # Query 4: Count by Language
        run_query(cursor,
                  "SELECT langues, COUNT(*) as count FROM questions GROUP BY langues ORDER BY count DESC",
                  "Questions by Language")
        
        # Query 5: Recent questions (first 10)
        run_query(cursor,
                  "SELECT id, title, post_type, date, status FROM questions ORDER BY date DESC LIMIT 10",
                  "10 Most Recent Questions")
        
        # Query 6: Table structure
        run_query(cursor,
                  "DESCRIBE questions",
                  "Table Structure")
        
        # Query 7: Count by School
        run_query(cursor,
                  "SELECT ecoles, COUNT(*) as count FROM questions WHERE ecoles IS NOT NULL AND ecoles != '' GROUP BY ecoles ORDER BY count DESC LIMIT 10",
                  "Top 10 Schools by Question Count")
        
        # Query 8: Sample of 5 random questions
        run_query(cursor,
                  "SELECT id, title, post_type, langues, status FROM questions ORDER BY RAND() LIMIT 5",
                  "5 Random Sample Questions")
        
        # Query 9: Questions by Theme (if any)
        run_query(cursor,
                  "SELECT thematiques, COUNT(*) as count FROM questions WHERE thematiques IS NOT NULL AND thematiques != '' GROUP BY thematiques ORDER BY count DESC LIMIT 10",
                  "Top 10 Themes")
        
        # Query 10: Date range
        run_query(cursor,
                  "SELECT MIN(date) as earliest_date, MAX(date) as latest_date, COUNT(DISTINCT date) as unique_dates FROM questions WHERE date IS NOT NULL",
                  "Date Range of Questions")
        
        print("\n" + "=" * 70)
        print("✅ All queries completed successfully!")
        print("=" * 70)
        
        # Close connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
