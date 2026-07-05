from fastapi import FastAPI
import pymysql

app = FastAPI()

# 📍 1. MySQL se connect karne ka simple tareeqa
def get_db_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="8619247084", # Apna MySQL password dalo
        database="fastapi_db",
        cursorclass=pymysql.cursors.DictCursor # Isse data dict {} ke roop mein aata hai
    )
    return connection


# 📍 2. GET API: MySQL se data nikalna (SELECT Query)
@app.get("/products")
def get_all_products():
    conn = get_db_connection() # Database khola
    cursor = conn.cursor()
    
    # 👇 Aapki jaani-pechani simple SQL query!
    cursor.execute("SELECT * FROM products;")
    
    data = cursor.fetchall() # Saara data nikal liya
    conn.close() # Database band kiya
    
    return {"all_products": data}


# 📍 3. POST API: MySQL mein naya data dalna (INSERT Query)
@app.post("/add-product")
def add_product(product_name: str, product_price: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 👇 Wahi simple INSERT query jo aapko aati hai
    query = "INSERT INTO products (name, price) VALUES (%s, %s);"
    
    # Query ko chalaya aur usme naam aur price bhej diya
    cursor.execute(query, (product_name, product_price))
    
    conn.commit() # Database mein save pakka kiya
    conn.close()
    
    return {"message": "Product successfully add ho gaya!"}


# data delete karne ke liye DELETE request
@app.delete("/delete-product/{product_id}")
def delete_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 👇 Wahi simple DELETE query jo aapko aati hai
    query = "DELETE FROM products WHERE id = %s;"
    
    # Query ko chalaya aur usme product_id bhej diya
    cursor.execute(query, (product_id,))
    
    conn.commit() # Database mein save pakka kiya
    conn.close()
    
    return {"message": f"Product successfully delete ho gaya!"}



# Data update karne ke liye PUT request
@app.put("/update-product/{product_id}")
def update_product(product_id: int, new_name: str, new_price: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 👇 Aapki simple SQL Update query!
    query = "UPDATE products SET name = %s, price = %s WHERE id = %s;"
    
    # Query chalayi aur usme naya naam, nayi price aur product ki id bhej di
    cursor.execute(query, (new_name, new_price, product_id))
    
    conn.commit() # Badlaav ko save kiya
    conn.close()
    
    return {"message": f"Product ID {product_id} successfully update ho gaya!"}