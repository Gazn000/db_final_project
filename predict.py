from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import mysql.connector
import pymysql
import pandas as pd
import os

# MySQL 数据库连接配置
db_config = {
    "host": "localhost",
    "user": "gazn",
    "password": "nycu112550141",
    "database": "final_project",
    "charset": "utf8mb4"
}

app = Flask(__name__)

# 提取用戶資料
def get_user_data_from_db():
    connection = pymysql.connect(**db_config)
    query = """
    SELECT id, record_id, account_id, height, weight, age, 
           gender, highBloodPressure AS bp_category, 
           smoking AS smoke, heavyAlcohol AS alco, 
           highBloodSugar AS gluc, highCholesterol AS cholesterol 
    FROM users;
    """  # 提取符合新表結構的資料
    user_data = pd.read_sql(query, connection)
    connection.close()
    return user_data

# 提取訓練資料
def get_training_data():
    connection = pymysql.connect(**db_config)
    query = """
    SELECT age_years, gender, bmi, smoke, alco, active, 
           gluc, cholesterol, bp_category, cardio
    FROM cardiovascular;
    """
    data = pd.read_sql(query, connection)
    connection.close()
    return data

# 预测函数
def train_and_predict(user_input):
    # 获取训练数据
    data = get_training_data()
    
    # 数据处理
    data['bp_category'] = data['bp_category'].map({
        'Normal': 0,
        'Elevated': 0,
        'Hypertension Stage 1': 1,
        'Hypertension Stage 2': 1
    })
    data = data.fillna(0)
    
    # 分离特征和标签
    X = data[['age_years', 'gender', 'bmi', 'smoke', 'alco', 'active', 
              'gluc', 'cholesterol', 'bp_category']]
    y = data['cardio']
    
    # 特征标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 建立 Gradient Boosting 模型并训练
    model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    # 用户数据处理
    user_bmi = user_input['weight'] / ((user_input['height'] / 100) ** 2)
    user_data = {
        "age_years": user_input["age"],
        "gender": 0 if user_input["gender"] == "Male" else 1,
        "bmi": user_bmi,
        "smoke": user_input["smoke"],
        "alco": user_input["alco"],
        "active": 1,  # 假設用戶活躍狀態爲固定值
        "gluc": user_input["gluc"],
        "cholesterol": user_input["cholesterol"],
        "bp_category": user_input["bp_category"]
    }
    user_df = pd.DataFrame([user_data])
    
    # 确保用户数据与训练数据格式一致
    user_scaled = scaler.transform(user_df)
    
    # 预测用户罹病概率
    probabilities = model.predict_proba(user_scaled)
    cardio_probability = probabilities[0][1]  # 罹病的概率
    return f"根據資料庫數據統計預測，罹病機率為 {cardio_probability * 100:.1f}%"

@app.route('/')
def index():
    # 提取用户数据并显示在页面上
    user_data = get_user_data_from_db()
    return render_template('predict.html', user_data=user_data.to_dict(orient='records'))

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 获取用户输入的 ID
        user_id = request.json.get('user_id')

        # 提取数据库中的用户数据
        user_data = get_user_data_from_db()
        user_row = user_data[user_data['id'] == int(user_id)]  # id 替换原 ID

        # 检查是否找到对应的用户数据
        if user_row.empty:
            return jsonify({"error": f"User ID {user_id} not found"}), 404

        # 转换为字典格式
        user_input = user_row.iloc[0].to_dict()

        # 调用预测函数
        probabilities = train_and_predict(user_input)
        return jsonify({"result": probabilities})  # 返回格式化的结果文本
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
