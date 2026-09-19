import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "shop_copilot.db")
DEFAULT_SHOP_ID = 1

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def reset_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute("DROP TABLE IF EXISTS shops;")
    cursor.execute("DROP TABLE IF EXISTS conversations;")
    cursor.execute("DROP TABLE IF EXISTS messages;")
    cursor.execute("DROP TABLE IF EXISTS memories;")
    cursor.execute("DROP TABLE IF EXISTS products;")
    cursor.execute("DROP TABLE IF EXISTS transactions;")
    cursor.execute("DROP TABLE IF EXISTS vocabulary;")
    cursor.execute("DROP TABLE IF EXISTS reorder_orders;")
    cursor.execute("DROP TABLE IF EXISTS suppliers;")
    conn.commit()
    conn.close()
    init_db()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            shop_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Shops Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    # 3. Conversations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        );
    """)

    # 4. Messages Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            intent TEXT,
            language TEXT DEFAULT 'en',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        );
    """)

    # 5. Persistent Memories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL,
            memory_type TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(shop_id, memory_type, key),
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        );
    """)

    # 6. Products Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            quantity REAL NOT NULL DEFAULT 0,
            unit TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0.0,
            purchase_price REAL NOT NULL DEFAULT 0.0,
            reorder_level REAL NOT NULL DEFAULT 10,
            avg_daily_usage REAL NOT NULL DEFAULT 1.0,
            supplier_lead_days INTEGER NOT NULL DEFAULT 2,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(shop_id, name),
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        );
    """)

    # Migration check for columns in products
    cursor.execute("PRAGMA table_info(products);")
    columns = [col['name'] for col in cursor.fetchall()]
    if 'price' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN price REAL NOT NULL DEFAULT 0.0;")
    if 'purchase_price' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN purchase_price REAL NOT NULL DEFAULT 0.0;")

    # 7. Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL DEFAULT 1,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            action TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            price REAL DEFAULT 0.0,
            raw_text TEXT,
            source TEXT DEFAULT 'voice',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
    """)

    # Migration check for price in transactions
    cursor.execute("PRAGMA table_info(transactions);")
    t_columns = [col['name'] for col in cursor.fetchall()]
    if 'price' not in t_columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN price REAL DEFAULT 0.0;")

    # 8. Vocabulary Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL DEFAULT 1,
            term TEXT NOT NULL,
            equivalent_qty REAL NOT NULL,
            equivalent_unit TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(shop_id, term),
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        );
    """)

    # 9. Reorder Orders Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reorder_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL DEFAULT 1,
            status TEXT DEFAULT 'PREPARED',
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        );
    """)

    # 10. Suppliers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER NOT NULL DEFAULT 1,
            name TEXT NOT NULL,
            products_supplied TEXT NOT NULL,
            contact_phone TEXT,
            typical_lead_days INTEGER DEFAULT 2,
            last_order_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(shop_id, name),
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM suppliers;")
    if cursor.fetchone()[0] == 0:
        seed_suppliers = [
            ('Sri Lakshmi Traders', 'Rice, Wheat Flour', '+91 98765 43210', 2, 1),
            ('Lakshmi Wholesale', 'Sugar, Dal, Salt', '+91 98765 12345', 1, 1),
            ('Universal Biscuit Co.', 'Biscuits, Tea Powder, Soap', '+91 98123 45678', 2, 1),
            ('Standard Oils & Dairy', 'Oil, Milk', '+91 98999 88877', 1, 1)
        ]
        cursor.executemany("""
            INSERT INTO suppliers (name, products_supplied, contact_phone, typical_lead_days, shop_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING;
        """, seed_suppliers)
        conn.commit()

    # Auto Seed Demo User & Shop if empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        demo_pass_hash = generate_password_hash("password123")
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, shop_name)
            VALUES ('Sahith', 'demo@shopcopilot.com', ?, 'Sah''s Store');
        """, (demo_pass_hash,))
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO shops (user_id, name)
            VALUES (?, 'Sah''s Store');
        """, (user_id,))
        shop_id = cursor.lastrowid

        # Seed initial conversation for Sah's Store
        cursor.execute("""
            INSERT INTO conversations (shop_id, title)
            VALUES (?, 'Today''s Stock & Briefing');
        """, (shop_id,))
        conv_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO messages (conversation_id, sender, message, intent, language)
            VALUES (?, 'copilot', 'Good morning! Welcome to Shop Copilot for Sah''s Store. How can I help your inventory today?', 'WELCOME', 'en');
        """, (conv_id,))

        # Seed products with purchase price & selling price
        seed_products = [
            ('Rice', 'Grains', 18.0, 'bags', 1600.0, 1450.0, 10.0, 3.0, 2, shop_id),
            ('Sugar', 'Groceries', 8.0, 'kg', 48.0, 42.0, 10.0, 2.0, 1, shop_id),
            ('Biscuits', 'Snacks', 48.0, 'packets', 12.0, 10.0, 60.0, 12.0, 2, shop_id),
            ('Oil', 'Essentials', 15.0, 'litres', 180.0, 160.0, 10.0, 1.5, 1, shop_id),
            ('Milk', 'Dairy', 20.0, 'packets', 32.0, 28.0, 10.0, 5.0, 1, shop_id),
            ('Salt', 'Groceries', 30.0, 'packets', 25.0, 20.0, 10.0, 4.0, 1, shop_id),
            ('Wheat Flour', 'Grains', 12.0, 'bags', 380.0, 340.0, 5.0, 2.0, 2, shop_id),
            ('Dal', 'Groceries', 14.0, 'kg', 140.0, 120.0, 10.0, 3.0, 2, shop_id),
            ('Tea Powder', 'Beverages', 25.0, 'packets', 75.0, 65.0, 8.0, 3.0, 1, shop_id),
            ('Soap', 'Personal Care', 40.0, 'pieces', 42.0, 35.0, 15.0, 5.0, 2, shop_id)
        ]
        cursor.executemany("""
            INSERT INTO products (name, category, quantity, unit, price, purchase_price, reorder_level, avg_daily_usage, supplier_lead_days, shop_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, seed_products)

        # Seed suppliers
        seed_suppliers = [
            ('Sri Lakshmi Traders', 'Rice, Wheat Flour', '+91 98765 43210', 2, shop_id),
            ('Lakshmi Wholesale', 'Sugar, Dal, Salt', '+91 98765 12345', 1, shop_id),
            ('Universal Biscuit Co.', 'Biscuits, Tea Powder, Soap', '+91 98123 45678', 2, shop_id),
            ('Standard Oils & Dairy', 'Oil, Milk', '+91 98999 88877', 1, shop_id)
        ]
        cursor.executemany("""
            INSERT INTO suppliers (name, products_supplied, contact_phone, typical_lead_days, shop_id)
            VALUES (?, ?, ?, ?, ?);
        """, seed_suppliers)

        # Seed custom vocabulary
        seed_vocab = [
            ('peti', 12.0, 'packets', shop_id),
            ('bora', 50.0, 'kg', shop_id),
            ('dabba', 24.0, 'pieces', shop_id)
        ]
        cursor.executemany("""
            INSERT INTO vocabulary (term, equivalent_qty, equivalent_unit, shop_id)
            VALUES (?, ?, ?, ?);
        """, seed_vocab)

        print("[DB] Seeded Demo User, Shop, 10 Products, Suppliers, and Vocabulary!")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("[DB] Multi-tenant Database initialized/updated successfully at:", DB_PATH)
