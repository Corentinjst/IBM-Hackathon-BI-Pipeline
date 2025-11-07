import pymysql
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'guereak.com',
    'port': 3306,
    'user': 'votre_user',
    'password': 'votre_password',
    'database': 'help_center',
    'charset': 'utf8mb4'
}

def insert_synthetic_support_tickets():
    """Insert synthetic support ticket data into the support_tickets table"""
    
    # Synthetic support ticket data
    support_tickets_data = [
        ('marie.dubois@edu.devinci.fr', 'ESILV', 'student', 
         'Ma boîte est au Canada, comment faire pour la convention de stage ? Mon entreprise n\'a pas de SIRET et mon stage commence dans 2 semaines.',
         '2025-11-05 08:30:15'),

        ('jean.martin@edu.devinci.fr', 'EMLV', 'faculty',
         'Je souhaite encadrer un stage international cette année. Quelles sont les procédures spécifiques pour valider une convention de stage à l\'étranger ?',
         '2025-11-04 16:45:30'),

        ('sophie.chen@edu.devinci.fr', 'ESILV', 'student',
         'Quelle est la différence concrète entre faire un stage de fin d\'études et une alternance ? Quels sont les avantages et inconvénients de chaque formule ?',
         '2025-11-05 10:15:45'),

        ('lucas.petit@edu.devinci.fr', 'EMLV', 'staff',
         'Un étudiant m\'a signalé un blocage sur la plateforme de convention. Existe-t-il un manuel ou une procédure interne pour le support de première ligne ?',
         '2025-11-04 09:20:10'),

        ('thomas.rousseau@edu.devinci.fr', 'ESILV', 'student',
         'Impossible de soumettre ma demande de convention sur la plateforme. J\'ai une erreur 500 quand je clique sur "Soumettre". Mon stage commence lundi, urgent !',
         '2025-11-05 14:55:12'),

        ('camille.moreau@edu.devinci.fr', 'EMLV', 'faculty',
         'J\'ai un apprenant qui souhaite effectuer son stage dans l\'entreprise familiale. Existe-t-il des restrictions officielles ou recommandations de l\'école ?',
         '2025-11-04 11:20:45'),

        ('antoine.bernard@edu.devinci.fr', 'ESILV', 'staff',
         'Dans le cadre du support administratif, où puis-je trouver les modèles de documents pour l\'attestation d\'assurance liée aux conventions de stage ?',
         '2025-11-02 13:15:30'),

        ('julie.blanc@edu.devinci.fr', 'EXECUTIVE', 'student',
         'Je suis en contrat d\'apprentissage et je suis malade. Est-ce qu\'un certificat médical suffit ou il faut obligatoirement un arrêt de travail ?',
         '2025-11-05 13:10:55'),

        ('paul.girard@edu.devinci.fr', 'ESILV', 'faculty',
         'Je dois valider plusieurs conventions cette semaine. Est-il possible d\'avoir un accès simplifié ou une vue consolidée sur mes étudiants à suivre ?',
         '2025-11-03 17:25:40'),

        ('emma.leroy@edu.devinci.fr', 'IIM', 'staff',
         'Je gère l\'emploi du temps et un étudiant m\'a transmis un arrêt maladie. Dois-je également le transmettre au service scolarité ou est-ce automatisé ?',
         '2025-11-02 15:40:22')
    ]
    
    insert_sql = """
    INSERT INTO support_tickets 
    (user_email, user_school, user_type, question, created_at)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        # Connect to database
        print("=" * 80)
        print("Inserting Synthetic Support Ticket Data")
        print("=" * 80)
        
        print("\nConnecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        print(f"✓ Connected to {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        
        # Insert data
        print("\nInserting support ticket records...")
        inserted = 0
        errors = 0
        
        for idx, data in enumerate(support_tickets_data, 1):
            try:
                cursor.execute(insert_sql, data)
                inserted += 1
                print(f"  ✓ Ticket {idx}: {data[0]} ({data[1]}, {data[2]})")
            except Exception as e:
                errors += 1
                print(f"  ✗ Error on ticket {idx}: {str(e)}")
        
        # Commit changes
        connection.commit()
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total tickets inserted: {inserted}")
        print(f"Total errors:           {errors}")
        
        # Show breakdown by school and user type
        print("\n📊 Breakdown:")
        cursor.execute("""
            SELECT user_school, user_type, COUNT(*) as count 
            FROM support_tickets 
            GROUP BY user_school, user_type 
            ORDER BY user_school, user_type
        """)
        results = cursor.fetchall()
        for row in results:
            print(f"  • {row[0]:<10} {row[1]:<10} {row[2]} ticket(s)")
        
        print("=" * 80)
        print("✅ Synthetic support ticket data loaded successfully!")
        
        # Close connection
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    insert_synthetic_support_tickets()
