import pymysql
from fastapi import FastAPI
from pydantic import BaseModel
import bcrypt  # 👈 Passlib hata kar sirf bcrypt import karo

app = FastAPI()

# 2. Users ke data ka structure (Dabba)
class UserSignup(BaseModel):
    username: str
    password: str

# 3. Database Connection
def get_db_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="8619247084",  # Aapka password
        database="fastapi_db",
        cursorclass=pymysql.cursors.DictCursor  # Data {} format mein aane ke liye
    )
    return connection

# 📍 GET API: Products dekhna
@app.get("/products")
def get_all_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products;")
    data = cursor.fetchall()
    conn.close()
    return {"all_products": data}

# 📍 POST API: Product add karna
@app.post("/add-product")
def add_product(product_name: str, product_price: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO products (name, price) VALUES (%s, %s);"
    cursor.execute(query, (product_name, product_price))
    conn.commit()
    conn.close()
    return {"message": "Product successfully add ho gaya!"}

# 📍 DELETE API: Product hatana
@app.delete("/delete-product/{product_id}")
def delete_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM products WHERE id = %s;"
    cursor.execute(query, (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Product successfully delete ho gaya!"}

# 📍 PUT API: Product badalna
@app.put("/update-product/{product_id}")
def update_product(product_id: int, new_name: str, new_price: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE products SET name = %s, price = %s WHERE id = %s;"
    cursor.execute(query, (new_name, new_price, product_id))
    conn.commit()
    conn.close()
    return {"message": f"Product ID {product_id} successfully update ho gaya!"}


# 📍 NEW SIGNUP API: Naya User Banane Ke Liye
@app.post("/signup")
def signup_user(user_data: UserSignup):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Check karo ki username pehle se hai ya nahi
    cursor.execute("SELECT * FROM users WHERE username = %s;", (user_data.username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return {"error": "Yeh username pehle se kisi ne le rakha hai!"}
    
    # 2. 🤫 Direct bcrypt se secure hash karo (Yeh 3.14 par makhhan chalega)
    password_bytes = user_data.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    # 3. Database mein bilkul sahi columns mein data dalo
    query = "INSERT INTO users (username, password_hash) VALUES (%s, %s);"
    cursor.execute(query, (user_data.username, hashed_password))
    
    conn.commit()
    conn.close()
    
    return {"message": f"User '{user_data.username}' ka account successfully ban gaya!"}