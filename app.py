import pymysql
from fastapi import FastAPI
from pydantic import BaseModel
import bcrypt  # 👈 Passlib hata kar sirf bcrypt import karo

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware  # Yeh file ke upar hona chahiye

# app = FastAPI() ke theek niche yeh jodo:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Browser ko permission dene ke liye
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# 📍 LOGIN API: User ko verify karne ke liye
@app.post("/login")
def login_user(user_data: UserSignup):  # Hum wahi UserSignup wala dabba use kar rahe hain
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Database mein check karo ki kya is naam ka user exist karta hai
    cursor.execute("SELECT * FROM users WHERE username = %s;", (user_data.username,))
    user = cursor.fetchone()
    conn.close()
    
    # Agar user mila hi nahi, toh seedhe mana kar do
    if not user:
        return {"error": "Galat Username ya Password! Dobara try karo."}
    
    # 2. 🔎 JAADU: Check karo ki user ka dala hua password aur database wala hash match ho rahe hain ya nahi
    # user['password_hash'] se hume database wala purana chhupa hua code mil jayega
    password_matched = bcrypt.checkpw(
        user_data.password.encode('utf-8'),      # Jo abhi user ne dala
        user['password_hash'].encode('utf-8')    # Jo database mein pehle se save hai
    )
    
    # 3. Agar password match ho gaya toh andar aane do, nahi toh error do
    if password_matched:
        return {"message": f"Welcome back, {user_data.username}! Aap successfully login ho gaye ho. 😎"}
    else:
        return {"error": "Galat Username ya Password! Dobara try karo."}