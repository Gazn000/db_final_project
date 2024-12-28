from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import mysql.connector
import pandas as pd
import os
from datetime import datetime


# 加載環境變數
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # 使用環境變數管理秘密金鑰

# 資料庫連線設定
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'your_username')
DB_PASS = os.getenv('DB_PASS', 'your_password')
DB_NAME = os.getenv('DB_NAME', 'final_project')

# 資料庫連線函數
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )


def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 創建 account 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        );
    """)
    
     # 創建 users 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            record_id INT NOT NULL,
            account_id INT NOT NULL,
            height FLOAT NOT NULL,
            weight FLOAT NOT NULL,
            age INT NOT NULL,
            gender ENUM('Male', 'Female') NOT NULL,
            highBloodPressure BOOLEAN NOT NULL,
            highBloodSugar BOOLEAN NOT NULL,
            highCholesterol BOOLEAN NOT NULL,
            heavyAlcohol BOOLEAN NOT NULL,
            smoking BOOLEAN NOT NULL,
            stroke BOOLEAN NOT NULL,
            exercise BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES account(id) ON DELETE CASCADE
        );
    """)
    
    cursor.close()
    conn.close()

# 在應用啟動時初始化
initialize_database()


# 登入頁面
@app.route("/", methods=["GET", "POST"])
def login():
    # 如果用戶已登入，直接重定向到主頁
    if 'user_id' in session:
        return redirect(url_for('main_page'))


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
            # 登入成功，設置成功消息
            session['user_id'] = account['id']
            session['username'] = username
            flash("登入成功！", "success")
            return redirect(url_for('main_page'))
        else:
            # 登入失敗，顯示錯誤訊息
            flash("無效的用戶名或密碼。請再試一次或註冊。", "danger")
            return redirect(url_for('login'))

    # 渲染登入頁面
    return render_template("login.html")
  
@app.route("/main_page", methods=["GET"])
def main_page():
    if "user_id" not in session:
        flash("請先登入。", "warning")
        return redirect(url_for('login'))
    return render_template("main_page.html")

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
            # 註冊成功，設置成功消息
            flash("帳戶創建成功！請登入。", "success")
            return redirect(url_for('login'))  # 成功後跳轉到登入頁面
        except mysql.connector.IntegrityError:
            flash("用戶名已存在。請選擇其他用戶名。", "danger")
        finally:
            cursor.close()
            conn.close()

    # 渲染註冊頁面
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
                exercise,
                account_id,
                record_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        exercise = bool(data.get('exercise'))

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
            exercise,
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

@app.route("/view_page", methods=["GET"])
def view_page():
    if "user_id" not in session:
        return jsonify({"error": "未登入，請先登入"}), 401

    user_id = session["user_id"]

    try:
        # 初始化查詢條件
        query = "SELECT * FROM users WHERE account_id = %s"
        params = [user_id]

        filter_fields = request.args.getlist("filter_field[]")
        filter_min_values = request.args.getlist("filter_min[]")
        filter_max_values = request.args.getlist("filter_max[]")
        filter_start_dates = request.args.getlist("filter_start_date[]")
        filter_end_dates = request.args.getlist("filter_end_date[]")
        filter_values = request.args.getlist("filter_value[]")
        
        errors = []

        # 處理篩選條件
        date_i = 0
        int_i = 0
        bool_i = 0

        for field in filter_fields:  # 直接基於 filter_fields 的值迭代
            
            if field == "created_at":  # 日期篩選
                # 確保日期篩選的值存在
                start_date = filter_start_dates[date_i] if date_i < len(filter_start_dates) else None
                end_date = filter_end_dates[date_i] if date_i < len(filter_end_dates) else None
                if not start_date or not end_date:
                    errors.append("請提供完整的日期範圍")
                elif start_date > end_date:
                    errors.append("開始日期不能晚於結束日期")
                elif start_date == end_date:  # 單一天篩選
                    query += " AND DATE(created_at) = %s"
                    params.append(start_date)
                else:  # 日期範圍篩選
                    query += " AND created_at BETWEEN %s AND %s"
                    params.extend([start_date, end_date])
                date_i += 1

            elif field in ["age", "weight"]:  # 數值篩選
                # 確保數值篩選的值存在
                min_value = float(filter_min_values[int_i]) if int_i < len(filter_min_values) else None
                max_value = float(filter_max_values[int_i]) if int_i < len(filter_max_values) else None
                if min_value is None or max_value is None:
                    errors.append(f"{field} 篩選值不完整")
                elif min_value < 0 or max_value < 0:
                    errors.append(f"{field} 的篩選值不能為負數")
                elif min_value > max_value:
                    errors.append(f"{field} 的最小值不能大於最大值")
                else:
                    query += f" AND {field} BETWEEN %s AND %s"
                    params.extend([min_value, max_value])
                int_i += 1

            elif field in ["highBloodPressure", "highBloodSugar", "highCholesterol", "heavyAlcohol", "smoking", "stroke", "exercise"]:
                # 確保布林值篩選的值存在
                value = filter_values[bool_i] if bool_i < len(filter_values) else None
                if value not in ["0", "1"]:
                    errors.append(f"{field} 的值無效，請選擇是或否")
                else:
                    query += f" AND {field} = %s"
                    params.append(int(value))  # 確保布林值轉為整數
                bool_i += 1

            else:
                errors.append(f"未知的篩選條件: {field}")


                        
        # 如果有錯誤，直接返回頁面，顯示錯誤訊息
        if errors:
            return render_template("view.html", user_data=[], error="; ".join(errors))

        # 調試：列印生成的查詢和參數
        print("SQL Query:", query)
        print("Parameters:", params)

        # 查詢資料庫
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        user_data = cursor.fetchall()
        cursor.close()
        connection.close()

        if not user_data:
            return render_template("view.html", user_data=[])

        return render_template("view.html", user_data=user_data, error=None)

    except Exception as e:
        return render_template("view.html", user_data=[], error=f"發生錯誤: {str(e)}")



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
                highCholesterol, heavyAlcohol, smoking, stroke, exercise, created_at 
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
    接收 JSON 格式的資料，並更新 MySQL 資料庫的 `users` 表中的指定記錄。
    """
    if "user_id" not in session:
        return jsonify({"error": "未登入，請先登入。"}), 401

    try:
        # 從請求中獲取 JSON 資料
        data = request.get_json()
        if not data:
            return jsonify({"error": "未收到 JSON 資料"}), 400

        # 確認 `record_id` 是否提供
        record_id = data.get("record_id")
        if record_id is None:
            return jsonify({"error": "未提供記錄ID"}), 400

        # 從 session 中獲取 `user_id`
        account_id = session["user_id"]

        # 調試輸出
        print(f"Updating record_id={record_id}, account_id={account_id} with data: {data}")

        # 連接資料庫
        connection = get_db_connection()
        cursor = connection.cursor()

        # 檢查記錄是否存在且屬於當前用戶
        cursor.execute(
            "SELECT id FROM users WHERE record_id = %s AND account_id = %s",
            (record_id, account_id)
        )
        exists = cursor.fetchone()
        if not exists:
            cursor.close()
            connection.close()
            return jsonify({"error": "找不到指定的資料或您沒有權限修改。"}), 400

        # 更新 SQL，將 `updated_at` 設置為當前時間
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
                stroke = %s,
                exercise = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE record_id = %s AND account_id = %s
        """

        # 從數據中提取字段
        height = float(data.get("height"))
        weight = float(data.get("weight"))
        age = int(data.get("age"))
        gender = data.get("gender")
        highBloodPressure = bool(data.get("highBloodPressure"))
        highBloodSugar = bool(data.get("highBloodSugar"))
        highCholesterol = bool(data.get("highCholesterol"))
        heavyAlcohol = bool(data.get("heavyAlcohol"))
        smoking = bool(data.get("smoking"))
        stroke = bool(data.get("stroke"))
        exercise = bool(data.get("exercise"))

        # 執行更新操作
        cursor.execute(
            sql,
            (
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
                exercise,
                record_id,
                account_id,
            )
        )
        connection.commit()

        # 調試確認更新成功
        print(f"Record {record_id} updated successfully for user {account_id}.")

        cursor.close()
        connection.close()

        return jsonify({"message": "資料已成功更新！"}), 200

    except mysql.connector.Error as db_err:
        print(f"資料庫錯誤: {db_err}")
        return jsonify({"error": f"資料庫錯誤: {db_err}"}), 500
    except ValueError as ve:
        print(f"資料類型錯誤: {ve}")
        return jsonify({"error": f"資料類型錯誤: {ve}"}), 400
    except Exception as e:
        print(f"意外錯誤: {e}")
        return jsonify({"error": f"意外錯誤: {e}"}), 500

@app.route("/get_percentage", methods=['GET'])
def get_percentage():
    HeadInjury = request.args.get('HeadInjury')
    if HeadInjury not in ["0", "1"]:
        return jsonify({"error": "Invalid input. Please select 0 or 1."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 獲取總人數
        cursor.execute("SELECT COUNT(*) AS total_count FROM alzheimers_diagnosed")
        total_count = cursor.fetchone()['total_count']

        # 獲取符合條件的人數
        cursor.execute("SELECT COUNT(*) AS matching_count FROM alzheimers_diagnosed WHERE HeadInjury = %s", (HeadInjury,))
        matching_count = cursor.fetchone()['matching_count']

        # 計算百分比
        percentage = (matching_count / total_count) * 100 if total_count > 0 else 0

        return jsonify({
            "total_count": total_count,
            "matching_count": matching_count,
            "percentage": round(percentage, 2)
        })

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route("/get_MMSE_percentage", methods=['GET'])
def get_MMSE_percentage():
    try:
        MMSE = float(request.args.get('MMSE', 0))
        if MMSE < 0 or MMSE > 30:
            return jsonify({"error": "Invalid MMSE."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_count FROM alzheimers_diagnosed")
        total_count = cursor.fetchone()['total_count']

        cursor.execute("SELECT COUNT(*) AS matching_count FROM alzheimers_diagnosed WHERE MMSE <= %s", (MMSE,))
        matching_count = cursor.fetchone()['matching_count']

        percentage = (matching_count / total_count) * 100

        return jsonify({
            "input_MMSE": MMSE,
            "total_count": total_count,
            "matching_count": matching_count,
            "percentage": round(percentage, 2)
        })

    except ValueError:
        return jsonify({"error": "Invalid input for MMSE."}), 400

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route("/get_alcohol_percentage", methods=['GET'])
def get_alcohol_percentage():
    try:
        alcohol = float(request.args.get('alcohol', 0))
        if alcohol < 0 or alcohol > 20:
            return jsonify({"error": "Alcohol consumption must be between 0 and 20."}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_count FROM alzheimers_diagnosed")
        total_count = cursor.fetchone()['total_count']

        cursor.execute("SELECT COUNT(*) AS matching_count FROM alzheimers_diagnosed WHERE AlcoholConsumption <= %s", (alcohol,))
        matching_count = cursor.fetchone()['matching_count']

        percentage = (matching_count / total_count) * 100

        return jsonify({
            "input_alcohol": round(alcohol, 2),
            "total_count": total_count,
            "matching_count": matching_count,
            "percentage": round(percentage, 2)
        })

    except ValueError:
        return jsonify({"error": "Invalid input for alcohol consumption."}), 400

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# 刪除頁面路由
@app.route("/delete_page", methods=["GET"])
def delete_page():
    if "user_id" not in session:
        flash("請先登入。", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # 建立資料庫連線
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 獲取當前用戶的所有資料
        cursor.execute("""
            SELECT record_id, height, weight, age, gender, highBloodPressure, highBloodSugar, 
                   highCholesterol, heavyAlcohol, smoking, stroke, exercise, created_at 
            FROM users 
            WHERE account_id = %s
            ORDER BY record_id DESC
        """, (user_id,))
        user_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return render_template("delete.html", user_data=user_data)
    
    except mysql.connector.Error as db_err:
        flash(f"資料庫錯誤: {db_err}", "danger")
        return redirect(url_for('personal'))
    except Exception as e:
        flash(f"意外錯誤: {e}", "danger")
        return redirect(url_for('personal'))

# 刪除處理路由
@app.route("/delete_user/<int:record_id>", methods=["POST"])
def delete_user(record_id):
    if "user_id" not in session:
        flash("未登入，請先登入。", "warning")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 確認該記錄屬於當前用戶
        cursor.execute("SELECT id FROM users WHERE record_id = %s AND account_id = %s", (record_id, user_id))
        record = cursor.fetchone()
        
        if not record:
            flash("找不到指定的資料或您沒有權限刪除。", "danger")
            cursor.close()
            connection.close()
            return redirect(url_for('delete_page'))
        
        # 刪除該記錄
        cursor.execute("DELETE FROM users WHERE record_id = %s AND account_id = %s", (record_id, user_id))
        connection.commit()
        
        flash("資料已成功刪除。", "success")
        
        cursor.close()
        connection.close()
        
        return redirect(url_for('delete_page'))
    
    except mysql.connector.Error as db_err:
        flash(f"資料庫錯誤: {db_err}", "danger")
        return redirect(url_for('delete_page'))
    except Exception as e:
        flash(f"意外錯誤: {e}", "danger")
        return redirect(url_for('delete_page'))

'''
# 提取用戶資料
def get_user_data_from_db():
    connection = get_db_connection()
    query = """
    SELECT id, record_id, account_id, height, weight, age, 
           gender, highBloodPressure AS bp_category, 
           smoking AS smoke, heavyAlcohol AS alco, 
           highBloodSugar AS gluc, highCholesterol AS cholesterol, exercise AS active 
    FROM users;
    """
    user_data = pd.read_sql(query, connection)
    connection.close()
    return user_data
'''
# 提取訓練資料
def cardio_get_training_data():
    connection = get_db_connection()
    query = """
    SELECT age_years, gender, bmi, smoke, alco, active, 
           gluc, cholesterol, bp_category, cardio
    FROM cardiovascular;
    """
    data = pd.read_sql(query, connection)
    connection.close()
    return data

def cardio_train_and_predict(user_input):
    # 獲取訓練資料
    data = cardio_get_training_data()

    # 數據處理
    data['bp_category'] = data['bp_category'].map({
        'Normal': 0,
        'Elevated': 0,
        'Hypertension Stage 1': 1,
        'Hypertension Stage 2': 1
    })
    data = data.fillna(0)

    # 分離特徵和標籤
    X = data[['age_years', 'gender', 'bmi', 'smoke', 'alco', 'active', 
              'gluc', 'cholesterol', 'bp_category']]
    y = data['cardio']

    # 特徵標準化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 建立 Gradient Boosting 模型並訓練
    model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    # 處理用戶資料
    user_bmi = user_input['weight'] / ((user_input['height'] / 100) ** 2)
    user_data = {
        "age_years": user_input["age"],
        "gender": 0 if user_input["gender"] == "Male" else 1,
        "bmi": user_bmi,
        "smoke": int(user_input.get("smoke", 0)),  # 确保有默认值
        "alco": int(user_input.get("alco", 0)),   # 确保有默认值
        "active": int(user_input.get("active", 0)),  # 确保有默认值
        "gluc": int(user_input.get("gluc", 0)),  # 确保有默认值
        "cholesterol": int(user_input.get("cholesterol", 0)),  # 确保有默认值
        "bp_category": int(user_input.get("bp_category", 0))  # 确保有默认值
    }
    user_df = pd.DataFrame([user_data])

    # 標準化用戶資料
    user_scaled = scaler.transform(user_df)

    # 預測用戶罹病機率
    probabilities = model.predict_proba(user_scaled)
    cardio_probability = probabilities[0][1]  # 罹病的概率
    return f"{cardio_probability * 100:.1f}%"

# 提取訓練資料
def heart_get_training_data():
    connection = get_db_connection()
    query = """
    SELECT Age, Sex, BMI, Smoker, HvyAlcoholConsump, PhysActivity, 
           Diabetes, HighChol, HighBP, HeartDiseaseorAttack, Stroke
    FROM Heart;
    """
    data = pd.read_sql(query, connection)
    connection.close()
    return data

def heart_train_and_predict(user_input):
    # 獲取訓練資料
    data = heart_get_training_data()

    data = data.fillna(0)

    # 分離特徵和標籤
    X = data[['Age', 'Sex', 'BMI', 'Smoker', 'HvyAlcoholConsump', 'PhysActivity', 
              'Diabetes', 'HighChol', 'HighBP', 'Stroke']]
    y = data['HeartDiseaseorAttack']

    # 特徵標準化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 建立 Gradient Boosting 模型並訓練
    model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    # 處理用戶資料
    user_bmi = user_input['weight'] / ((user_input['height'] / 100) ** 2)
    user_data = {
        "Age": user_input["age"],
        "Sex": 0 if user_input["gender"] == "Male" else 1,
        "BMI": user_bmi,
        "Smoker": int(user_input.get("smoke", 0)),  # 确保有默认值
        "HvyAlcoholConsump": int(user_input.get("alco", 0)),   # 确保有默认值
        "PhysActivity": int(user_input.get("active", 0)),  # 确保有默认值
        "Diabetes": int(user_input.get("gluc", 0)),  # 确保有默认值
        "HighChol": int(user_input.get("cholesterol", 0)),  # 确保有默认值
        "HighBP": int(user_input.get("bp_category", 0)),  # 确保有默认值
        "Stroke": int(user_input.get("Stroke", 0))
    }
    user_df = pd.DataFrame([user_data])

    # 標準化用戶資料
    user_scaled = scaler.transform(user_df)

    # 預測用戶罹病機率
    probabilities = model.predict_proba(user_scaled)
    Heart_probability = probabilities[0][1]  # 罹病的概率
    return f"{Heart_probability * 100:.1f}%"

# 提取訓練資料
def diabetes_get_training_data():
    connection = get_db_connection()
    query = """
    SELECT Age, Sex, BMI, Smoker, HvyAlcoholConsump, PhysActivity, 
        HighChol, HighBP, Diabetes_binary, Stroke
    FROM diabetes;
    """
    data = pd.read_sql(query, connection)
    connection.close()
    return data

def diabetes_train_and_predict(user_input):
    # 獲取訓練資料
    data = diabetes_get_training_data()

    # 數據處理
    data = data.fillna(0)

    # 分離特徵和標籤
    X = data[['Age', 'Sex', 'BMI', 'Smoker', 'HvyAlcoholConsump', 'PhysActivity', 
            'HighChol', 'HighBP', 'Stroke']]
    y = data['Diabetes_binary']

    # 特徵標準化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 建立 Gradient Boosting 模型並訓練
    model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    # 處理用戶資料
    user_bmi = user_input['weight'] / ((user_input['height'] / 100) ** 2)
    user_data = {
        "Age": user_input["age"],
        "Sex": 0 if user_input["gender"] == "Male" else 1,
        "BMI": user_bmi,
        "Smoker": int(user_input.get("smoke", 0)),  # 确保有默认值
        "HvyAlcoholConsump": int(user_input.get("alco", 0)),   # 确保有默认值
        "PhysActivity": int(user_input.get("active", 0)),  # 确保有默认值
        "HighChol": int(user_input.get("cholesterol", 0)),  # 确保有默认值
        "HighBP": int(user_input.get("bp_category", 0)),  # 确保有默认值
        "Stroke": int(user_input.get("Stroke", 0))
    }
    user_df = pd.DataFrame([user_data])

    # 標準化用戶資料
    user_scaled = scaler.transform(user_df)

    # 預測用戶罹病機率
    probabilities = model.predict_proba(user_scaled)
    diabetes_probability = probabilities[0][1]  # 罹病的概率
    return f"{diabetes_probability * 100:.1f}%"


# Flask 路由
@app.route('/predict_page', methods=["GET"])
def predict_page():
    if "user_id" not in session:
        flash("請先登入。", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # 獲取用戶的最新資料
        cursor.execute("""
            SELECT * FROM users
            WHERE account_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if not user_data:
            flash("您尚未新增任何資料。", "warning")
            return redirect(url_for('personal'))
        return render_template("predict.html", user_data=user_data)
    except mysql.connector.Error as db_err:
        flash(f"資料庫錯誤: {db_err}", "danger")
        return redirect(url_for('personal'))


@app.route('/predict', methods=['POST'])
def predict():
    try:
        user_id = session.get('user_id')  # 從 session 獲取當前用戶 ID
        if not user_id:
            return jsonify({"error": "未登入，請先登入"}), 401

        # 從資料庫中查找用戶的最新數據
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 查詢當前用戶最新的數據（按 created_at 排序）
        cursor.execute("""
            SELECT * FROM users
            WHERE account_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        user_data = cursor.fetchone()
        
        cursor.close()
        connection.close()

        if not user_data:
            return jsonify({"error": f"未找到用戶 ID {user_id} 的數據"}), 404

        # 檢查字段是否齊全
        required_fields = ['smoke', 'alco', 'gluc', 'cholesterol', 'bp_category']
        for field in required_fields:
            if field not in user_data:
                user_data[field] = 0  # 填補缺失字段

        # 執行三種預測
        cardio_probability = cardio_train_and_predict(user_data)
        print("prediction input:", user_data)
        print("Cardio prediction result:", cardio_probability)
        heart_probability = heart_train_and_predict(user_data)
        print("Heart prediction result:", heart_probability)
        diabetes_probability = diabetes_train_and_predict(user_data)
        print("Cardio prediction result:", diabetes_probability)

        #heart_probability = heart_train_and_predict(user_data)
        #diabetes_probability = diabetes_train_and_predict(user_data)

        # 返回三個預測結果
        result = f"""
        心血管疾病機率: {cardio_probability}    
        心臟病機率: {heart_probability}
        糖尿病機率: {diabetes_probability}
        """
        return jsonify({"result": result})
    except mysql.connector.Error as db_err:
        return jsonify({"error": f"資料庫錯誤: {db_err}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 登出功能
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()  # 清除所有 session 資料
    flash("您已成功登出。", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    # 執行 Flask 應用程式 (預設 port=5000)
    app.run(debug=True)
