from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

def get_all_menus_from_db():
    conn = sqlite3.connect('menus.db')
    cursor = conn.cursor()
    cursor.execute('SELECT restaurant, item_type, item, price FROM menus')
    rows = cursor.fetchall()
    conn.close()
    menus = {}
    for row in rows:
        restaurant = row[0]
        item_type = row[1]
        item = row[2]
        price = row[3]
        if restaurant not in menus:
            menus[restaurant] = []
        menus[restaurant].append({'type': item_type, 'item': item, 'price': price})
    return menus

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menus', methods=['GET'])
def get_menus():
    try:
        menus = get_all_menus_from_db()
        return jsonify(menus)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

