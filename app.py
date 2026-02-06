from flask import Flask, request, redirect, render_template
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    conn = get_db_connection()
    products = conn.execute(
        "SELECT * FROM products ORDER BY id DESC LIMIT 3"
    ).fetchall()
    conn.close()
    return render_template("home.html", products=products)
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return f"Total products in database: {len(products)}"

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        stock_status = request.form["stock_status"]

        image = request.files["image"]
        image_name = image.filename
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO products (name, price, description, stock_status, image) VALUES (?, ?, ?, ?, ?)",
            (name, price, description, stock_status, image_name)
        )
        conn.commit()
        conn.close()

        return redirect("/admin")

    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    html = ""
    html += "<h2>Admin Panel - Add Product</h2>"

    html += """
    <form method="post" enctype="multipart/form-data">
        <input name="name" placeholder="Product name" required><br><br>
        <input name="price" type="number" step="0.01" placeholder="Price" required><br><br>
        <textarea name="description" placeholder="Description"></textarea><br><br>
        <select name="stock_status">
            <option value="In Stock">In Stock</option>
            <option value="Out of Stock">Out of Stock</option>
        </select><br><br>
        <input type="file" name="image" required><br><br>
        <button type="submit">Add Product</button>
    </form>
    <hr>
    <h3>Existing Products</h3>
    """

    for p in products:
        html += f"""
        <div style="border:1px solid #ccc; padding:10px; margin:10px;">
            <strong>{p['name']}</strong> - Rs. {p['price']}
            <a href="/edit/{p['id']}" style="margin-left:10px;">Edit</a>
<a href="/delete/{p['id']}" style="color:red; margin-left:10px;">Delete</a>

        </div>
        """

    return html
        


@app.route("/shop")
def shop():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()

    output = "<h2>Shop</h2>"

    for p in products:
        output += f"""
        <div style='border:1px solid #ccc; padding:10px; margin:10px;'>
            <img src="/static/uploads/{p['image']}" width="200"><br><br>
            <h3>{p['name']}</h3>
            <p>Price: Rs. {p['price']}</p>
<p>Status: {p['stock_status']}</p>

<a href="https://wa.me/918089796998?text=I%20want%20to%20order%20{p['name']}%20for%20Rs.%20{p['price']}"
   target="_blank"
   style="display:inline-block; margin-top:10px; padding:8px 15px; background:#25D366; color:white; border-radius:20px;">
   Order on WhatsApp
</a>

            <p>{p['description']}</p>
        </div>
        """


    return output
@app.route("/delete/<int:id>")
def delete_product(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]
        description = request.form["description"]
        stock_status = request.form["stock_status"]

        conn.execute(
            "UPDATE products SET name=?, price=?, description=?, stock_status=? WHERE id=?",
            (name, price, description, stock_status, id)
        )
        conn.commit()
        conn.close()
        return redirect("/admin")

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    return f"""
    <h2>Edit Product</h2>
    <form method="post">
        <input name="name" value="{product['name']}" required><br><br>
        <input name="price" type="number" step="0.01" value="{product['price']}" required><br><br>
        <textarea name="description">{product['description']}</textarea><br><br>
        <select name="stock_status">
            <option value="In Stock" {"selected" if product['stock_status']=="In Stock" else ""}>In Stock</option>
            <option value="Out of Stock" {"selected" if product['stock_status']=="Out of Stock" else ""}>Out of Stock</option>
        </select><br><br>
        <button type="submit">Update Product</button>
    </form>
    <br>
    <a href="/admin">Back</a>
    """

if __name__ == "__main__":
    app.run(debug=True)

