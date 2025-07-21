import pymysql
from pymysql.constants import CLIENT
import bcrypt
import time  # Added this import

class Database:
    def __init__(self):
        try:
            self.connection = pymysql.connect(
                host='localhost',
                user='root',
                password='Abd@123',
                database='secure_auth',
                client_flag=CLIENT.MULTI_STATEMENTS
            )
            self.cursor = self.connection.cursor()
            self.create_tables()
            print("Database connection established and tables verified")
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            self.connection.commit()
            print("Users table created/verified")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
            raise

    def register_user(self, first_name, last_name, email, password):
        try:
            # Hash password with bcrypt
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            self.cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (first_name, last_name, email, password_hash))
            self.connection.commit()
            print(f"User {email} registered successfully")
            return True
        except pymysql.IntegrityError:
            print(f"Email {email} already exists")
            return False
        except Exception as e:
            print(f"Registration error: {e}")
            self.connection.rollback()
            return False

    def authenticate_user(self, email, password):
        try:
            self.cursor.execute("""
                SELECT id, password_hash FROM users WHERE email = %s
            """, (email,))
            result = self.cursor.fetchone()
            
            if result:
                user_id, password_hash = result
                # Verify password with bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
                    print(f"User {email} authenticated successfully")
                    return user_id
            print(f"Authentication failed for {email}")
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    def close(self):
        self.cursor.close()
        self.connection.close()
        print("Database connection closed")

if __name__ == "__main__":
    db = None
    try:
        db = Database()
        
        # Generate unique test email using timestamp
        test_email = f"test_{int(time.time())}@example.com"
        
        # Test registration
        print("\nTesting registration...")
        if db.register_user("Test", "User", test_email, "Test123"):
            print("✓ Registration test passed")
        else:
            print("✗ Registration test failed")
        
        # Test successful authentication
        print("\nTesting successful login...")
        user_id = db.authenticate_user(test_email, "Test123")
        if user_id:
            print(f"✓ Login test passed. User ID: {user_id}")
        else:
            print("✗ Login test failed")
        
        # Test failed authentication (wrong password)
        print("\nTesting wrong password...")
        user_id = db.authenticate_user(test_email, "WrongPassword")
        if not user_id:
            print("✓ Wrong password test passed (correctly failed)")
        
    except Exception as e:
        print(f"\n! Error during tests: {e}")
    finally:
        if db:
            db.close()