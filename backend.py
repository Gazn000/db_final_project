from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# 資料庫連線設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'final_project'
}

@app.route("/", methods=['GET'])
def main_page():
    return render_template("main_page.html")

@app.route("/get_percentage", methods=['GET'])
def get_percentage():
    smoke = request.args.get('smoke')
    if smoke not in ["0", "1"]:
        return jsonify({"error": "Invalid input. Please select 0 or 1."}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 獲取總人數
        cursor.execute("SELECT COUNT(*) AS total_count FROM patients")
        total_count = cursor.fetchone()['total_count']

        # 獲取符合條件的人數
        cursor.execute("SELECT COUNT(*) AS matching_count FROM patients WHERE Smoking = %s", (smoke,))
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
        cursor.close()
        conn.close()

@app.route("/get_bmi_percentage", methods=['GET'])
def get_bmi_percentage():
    try:
        weight = float(request.args.get('weight', 0))
        height = float(request.args.get('height', 0))
        if weight <= 0 or height <= 0:
            return jsonify({"error": "Invalid weight or height."}), 400
        
        height_m = height / 100
        bmi = weight / (height_m ** 2)

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_count FROM patients")
        total_count = cursor.fetchone()['total_count']

        if total_count == 0:
            return jsonify({"error": "No data available in the database."}), 404

        cursor.execute("SELECT COUNT(*) AS matching_count FROM patients WHERE BMI <= %s", (bmi,))
        matching_count = cursor.fetchone()['matching_count']

        percentage = (matching_count / total_count) * 100

        return jsonify({
            "input_bmi": round(bmi, 2),
            "total_count": total_count,
            "matching_count": matching_count,
            "percentage": round(percentage, 2)
        })

    except ValueError:
        return jsonify({"error": "Invalid input for weight or height."}), 400

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
        # 獲取使用者輸入的每週酒精攝取量
        alcohol = float(request.args.get('alcohol', 0))
        if alcohol < 0 or alcohol > 20:
            return jsonify({"error": "Alcohol consumption must be between 0 and 20."}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_count FROM patients")
        total_count = cursor.fetchone()['total_count']

        if total_count == 0:
            return jsonify({"error": "No data available in the database."}), 404

        cursor.execute("SELECT COUNT(*) AS matching_count FROM patients WHERE AlcoholConsumption <= %s", (alcohol,))
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

if __name__ == '__main__':
    app.run(debug=True)
