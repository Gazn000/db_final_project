from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# 加載環境變數
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # 使用環境變數管理秘密金鑰

# 資料庫連線設定
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'xinya')
DB_PASS = os.getenv('DB_PASS', '123')
DB_NAME = os.getenv('DB_NAME', 'fp')

# 資料庫連線函數
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

# 登入頁面
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']  # 原始密碼

        # 資料庫連線
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, password FROM account WHERE username = %s", (username,))
        account = cursor.fetchone()
        cursor.close()
        conn.close()

        if account and check_password_hash(account['password'], password):
            # 登入成功，將用戶的 id 和 username 存入 session
            session['user_id'] = account['id']
            session['username'] = username
            flash("登入成功！", "success")
            return redirect(url_for('personal'))
        else:
            # 登入失敗，顯示錯誤訊息
            flash("無效的用戶名或密碼。請再試一次或註冊。", "danger")
            return redirect(url_for('login'))

    return render_template("login.html")

# 註冊頁面
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # 使用 werkzeug.security 來雜湊密碼
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO account (username, password) VALUES (%s, %s)", (username, password_hash))
            conn.commit()
            flash("帳戶創建成功！請登入。", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("用戶名已存在。請選擇其他用戶名。", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")

# 個人資料頁面
@app.route("/personal", methods=["GET"])
def personal():
    if "user_id" not in session:
        flash("請先登入。", "warning")
        return redirect(url_for('login'))
    return render_template("personal.html", username=session["username"])

# 建立資料頁面
@app.route("/create_page", methods=["GET"])
def create_page():
    if "user_id" not in session:
        flash("請先登入。", "warning")
        return redirect(url_for('login'))
    return render_template("create.html")

# 處理資料創建
@app.route("/create", methods=["POST"])
def create_data():
    """
    從前端接收 JSON 格式的資料 (height, weight, age...等)，
    並寫入 MySQL 資料庫的 users 表。
    """
    if "user_id" not in session:
        return jsonify({"error": "未登入，請先登入。"}), 401

    try:
        # 1. 從 request 中取得 JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "未收到 JSON 資料"}), 400

        # 2. 從 session 中取得 user_id
        account_id = session['user_id']

        # 3. 建立資料庫連線
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 4. 查詢當前用戶的最大 record_id
        cursor.execute("SELECT MAX(record_id) AS max_record FROM users WHERE account_id = %s", (account_id,))
        result = cursor.fetchone()
        max_record = result['max_record'] if result['max_record'] is not None else 0
        new_record_id = max_record + 1

        # 5. 準備 SQL 指令，包含 account_id 和 record_id
        sql = """
            INSERT INTO users (
                height,
                weight,
                age,
                gender,
                highBloodPressure,
                highBloodSugar,
                highCholesterol,
                heavyAlcohol,
                smoking,
                stroke,
                account_id,
                record_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 6. 從 data 中取得欄位，這些 key 要和前端送過來的 JSON 一致
        height = float(data.get('height'))
        weight = float(data.get('weight'))
        age = int(data.get('age'))
        gender = data.get('gender')
        highBloodPressure = bool(data.get('highBloodPressure'))
        highBloodSugar = bool(data.get('highBloodSugar'))
        highCholesterol = bool(data.get('highCholesterol'))
        heavyAlcohol = bool(data.get('heavyAlcohol'))
        smoking = bool(data.get('smoking'))
        stroke = bool(data.get('stroke'))

        # 7. 執行 SQL
        cursor.execute(sql, (
            height,
            weight,
            age,
            gender,
            highBloodPressure,
            highBloodSugar,
            highCholesterol,
            heavyAlcohol,
            smoking,
            stroke,
            account_id,
            new_record_id  # 添加 record_id
        ))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "資料成功插入！"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"資料庫錯誤: {db_err}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"資料類型錯誤: {ve}"}), 400
    except Exception as e:
        return jsonify({"error": f"意外錯誤: {e}"}), 500

# 新增：修改資料頁面
@app.route("/modify_page", methods=["GET"])
def modify_page():
    if "user_id" not in session:
        flash("請先登入。", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # 建立資料庫連線
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 獲取所有使用者的資料
        cursor.execute("""
            SELECT record_id, height, weight, age, gender, highBloodPressure, highBloodSugar, 
                   highCholesterol, heavyAlcohol, smoking, stroke, created_at 
            FROM users 
            WHERE account_id = %s
            ORDER BY record_id DESC
        """, (user_id,))
        user_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template("modify.html", user_data=user_data)
    
    except mysql.connector.Error as db_err:
        flash(f"資料庫錯誤: {db_err}", "danger")
        return redirect(url_for('personal'))
    except Exception as e:
        flash(f"意外錯誤: {e}", "danger")
        return redirect(url_for('personal'))

# 修改：更新資料頁面，接受 record_id
@app.route("/update_page/<int:record_id>", methods=["GET"])
def update_page(record_id):
    if "user_id" not in session:
        flash("請先登入。", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # 建立資料庫連線
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 獲取指定的 users 記錄
        cursor.execute("""
            SELECT * FROM users 
            WHERE record_id = %s AND account_id = %s
        """, (record_id, user_id))
        user_data = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not user_data:
            flash("找不到指定的資料或您沒有權限修改。", "danger")
            return redirect(url_for('modify_page'))
        
        return render_template("update.html", user_data=user_data)
    
    except mysql.connector.Error as db_err:
        flash(f"資料庫錯誤: {db_err}", "danger")
        return redirect(url_for('personal'))
    except Exception as e:
        flash(f"意外錯誤: {e}", "danger")
        return redirect(url_for('personal'))

# 修改：處理資料更新
@app.route("/update", methods=["POST"])
def update_data():
    """
    從前端接收 JSON 格式的資料 (record_id, height, weight, age...等)，
    並更新 MySQL 資料庫的 users 表中的指定記錄。
    """
    if "user_id" not in session:
        return jsonify({"error": "未登入，請先登入。"}), 401

    try:
        # 1. 從 request 中取得 JSON
        data = request.get_json()
        if not data:
            return jsonify({"error": "未收到 JSON 資料"}), 400

        # 2. 從 JSON 中取得 record_id
        record_id = data.get('record_id')
        if record_id is None:
            return jsonify({"error": "未提供記錄ID"}), 400

        # 3. 從 session 中取得 user_id
        account_id = session['user_id']

        # 4. 建立資料庫連線
        connection = get_db_connection()
        cursor = connection.cursor()

        # 5. 確認該記錄屬於當前用戶
        cursor.execute("""
            SELECT id FROM users 
            WHERE record_id = %s AND account_id = %s
        """, (record_id, account_id))
        exists = cursor.fetchone()
        if not exists:
            cursor.close()
            connection.close()
            return jsonify({"error": "找不到指定的資料或您沒有權限修改。"}), 400

        # 6. 準備 SQL 指令，更新指定的記錄
        sql = """
            UPDATE users SET
                height = %s,
                weight = %s,
                age = %s,
                gender = %s,
                highBloodPressure = %s,
                highBloodSugar = %s,
                highCholesterol = %s,
                heavyAlcohol = %s,
                smoking = %s,
                stroke = %s
            WHERE record_id = %s AND account_id = %s
        """

        # 7. 從 data 中取得欄位，這些 key 要和前端送過來的 JSON 一致
        height = float(data.get('height'))
        weight = float(data.get('weight'))
        age = int(data.get('age'))
        gender = data.get('gender')
        highBloodPressure = bool(data.get('highBloodPressure'))
        highBloodSugar = bool(data.get('highBloodSugar'))
        highCholesterol = bool(data.get('highCholesterol'))
        heavyAlcohol = bool(data.get('heavyAlcohol'))
        smoking = bool(data.get('smoking'))
        stroke = bool(data.get('stroke'))

        # 8. 執行 SQL
        cursor.execute(sql, (
            height,
            weight,
            age,
            gender,
            highBloodPressure,
            highBloodSugar,
            highCholesterol,
            heavyAlcohol,
            smoking,
            stroke,
            record_id,  # 指定要更新的記錄 record_id
            account_id  # 確保是當前用戶
        ))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "資料成功更新！"}), 200

    except mysql.connector.Error as db_err:
        return jsonify({"error": f"資料庫錯誤: {db_err}"}), 500
    except ValueError as ve:
        return jsonify({"error": f"資料類型錯誤: {ve}"}), 400
    except Exception as e:
        return jsonify({"error": f"意外錯誤: {e}"}), 500

# 登出功能
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("已登出。", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    # 執行 Flask 應用程式 (預設 port=5000)
    app.run(debug=True)
