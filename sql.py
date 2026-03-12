#!/usr/bin/env python
# coding: utf-8

# In[5]:


import sqlite3
import pandas as pd
print("=== Task 1: Database Creation ===")
conn = sqlite3.connect("bookstore.db")
cursor = conn.cursor()
print("Database connection established")


# In[ ]:


cursor.execute("""
CREATE TABLE IF NOT EXISTS books(
book_id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
author TEXT NOT NULL,
price REAL NOT NULL,
stock_quantity INTEGER DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers(
customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
email TEXT UNIQUE NOT NULL,
city TEXT,
join_date TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
order_id INTEGER PRIMARY KEY AUTOINCREMENT,
customer_id INTEGER,
book_id INTEGER,
quantity INTEGER NOT NULL,
order_date TEXT NOT NULL,
total_amount REAL,
FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
FOREIGN KEY(book_id) REFERENCES books(book_id)
)
""")
conn.commit()
conn.close()


# In[ ]:


print("\nSchema for books table:")
cursor.execute("PRAGMA table_info(Books)")
data = cursor.fetchall()
columns = ["cid","nmae","type","notnull","dflt_value","pk"]
df = pd.DataFrame(data,columns=columns)
print(df)
print("\nSchema for customers table:")
cursor.execute("PRAGMA table_info(Customers)")
data = cursor.fetchall()
df = pd.DataFrame(data,columns=columns)
print(df)


print("\nSchema for orders table:")
cursor.execute("PRAGMA table_info(Orders)")
data = cursor.fetchall()
df = pd.DataFrame(data,columns=columns)
print(df)


books_data = [
    ('Python Programming', 'John Smith', 599.99, 25),
    ('Data Science Handbook', 'Jane Doe', 899.50, 15),
    ('Machine Learning Basics', 'Alan Turing', 1299.00, 10),
    ('SQL Essentials', 'Edgar Codd', 499.99, 30),
    ('Web Development', 'Tim Berners', 799.00, 20)
]
cursor.executemany("""INSERT INTO Books(title,author,price,stock_quantity)
                   VALUES (?,?,?,?)""",books_data)
customers_data = [
    ('Rahul Sharma', 'rahul@email.com', 'Mumbai', '2024-01-15'),
    ('Priya Patel', 'priya@email.com', 'Delhi', '2024-01-20'),
    ('Amit Kumar', 'amit@email.com', 'Bangalore', '2024-02-01'),
    ('Sneha Reddy', 'sneha@email.com', 'Hyderabad', '2024-02-10'),
    ('Vikram Singh', 'vikram@email.com', 'Mumbai', '2024-02-15')
]
cursor.executemany("""INSERT INTO Customers(name,email,city,join_date)
                   VALUES (?,?,?,?)""",customers_data)
orders_data = [
    (1, 1, 2, '2024-03-01', 1199.00),
    (1, 2, 1, '2024-03-02', 899.50),
    (2, 1, 1, '2024-03-03', 599.99),
    (2, 3, 1, '2024-03-05', 1299.00),
    (3, 4, 3, '2024-03-07', 1499.97),
    (4, 2, 1, '2024-03-10', 899.50),
    (5, 5, 2, '2024-03-12', 1598.00)
]
cursor.executemany("""INSERT INTO Orders(customer_id,book_id,quantity,order_date,total_amount)
                   VALUES (?,?,?,?,?)""",orders_data)
conn.commit()


# In[16]:


print("Books Table")
for row in cursor.execute("SELECT * FROM Books"):
    print(row)
print("Customers Table")
for row in cursor.execute("SELECT * FROM Customers"):
    print(row)

print("Orders Table")
for rows in cursor.execute("SELECT * FROM Orders"):
    print(rows)


# In[35]:


print("Customers from Mumbai:")
cursor.execute("SELECT * FROM Customers WHERE city = 'Mumbai'")
for row in cursor.fetchall():
    print(row)


# In[36]:


print("Books priced > 800 with stock > 10:")
cursor.execute("""SELECT * FROM Books
                WHERE price > 800 and stock_quantity > 10""")
print(cursor.fetchall())


# In[39]:


cursor.execute("SELECT COUNT(*) FROM Orders")
count = cursor.fetchone()
print("Total Orders: ",count[0])


# In[32]:


cursor.execute("""SELECT customer_id,count(*) as total_orders FROM Orders
                GROUP BY customer_id
                ORDER BY total_orders DESC
                LIMIT 1""")
print(cursor.fetchall())


# In[42]:


cursor.execute("""SELECT SUM(total_amount) FROM Orders""")
sum = cursor.fetchall()
print("Total Revenue: ",sum[0])


# In[3]:


conn.close()


# In[11]:


print("=== TASK 3:Pandas Integration ===")
books_df = pd.read_sql("SELECT * FROM Books",conn)
customers_df = pd.read_sql("SELECT * FROM Customers",conn)
orders_df = pd.read_sql("SELECT * FROM Orders",conn)
print("DataFrame loaded from SQL:")
print(f"- Books: {books_df.shape[0]} rows x {books_df.shape[1]} columns")
print(f"- Customers: {customers_df.shape[0]} rows x {customers_df.shape[1]} columns")
print(f"- Orders:{orders_df.shape[0]} rows x {books_df.shape[1]} columns")


# In[19]:


report = orders_df.merge(customers_df,on = "customer_id").merge(books_df,on = "book_id")
report = report[["order_id","name","city","title","quantity","total_amount"]]
report.columns = ["order_id","customer_name","city","book_title","quantity","total_amount"]
print("\nComprehensive Order Report:")
print(report.head())


# In[22]:


avg_order = report["total_amount"].mean()
print("Ananlysis Results:")
print(f"Average Order Value: ₹{avg_order:.2f}")


# In[24]:


order_by_city = report.groupby("city")["order_id"].count()
print("\nOrders by City:")
for city,count in order_by_city.items():
    print(f"{city}: {count} orders")


# In[25]:


popular_book = report.groupby("book_title")["quantity"].sum().idxmax()
popular_count = report.groupby("book_title")["quantity"].sum().max()
print(f"\nMost Popular Book: {popular_book} ({popular_count} orders)")


# In[27]:


discount_data = {
    "book_id":[1,2,3,4,5],
    "discount_percent":[10,15,5,20,12]
}
discount_df = pd.DataFrame(discount_data)


# In[29]:


discount_df.to_sql("discounts",conn,if_exists="replace",index = False)
print("Discounts table created and saved to database")


# In[30]:


query = """
SELECT 
    b.title,
    b.price AS original_price,
    d.discount_percent,
    ROUND(b.price * (1 - d.discount_percent/100.0),2) AS discounted_price
FROM Books b
JOIN discounts d
ON b.book_id = d.book_id
"""

discounted_books = pd.read_sql(query, conn)

print("\nBooks with Discounted Prices:")
print(discounted_books)

