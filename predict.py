import pymysql
import pandas as pd
from flask import Flask, render_template, request, jsonify
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler

# MySQL 数据库连接配置
db_config = {
    "host": "localhost",
    "user": "gazn",
    "password": "nycu112550141",
    "database": "final_project",
    "charset": "utf8mb4"
}

app = Flask(__name__)

# 提取用户数据
def get_user_data_from_db():
    connection = pymysql.connect(**db_config)
    query = "SELECT * FROM user_data;"  # 假设用户数据存储在 `user_data` 表中
    user_data = pd.read_sql(query, connection)
    connection.close()
    return user_data

# 提取训练数据
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
        'Normal': 1,
        'Elevated': 2,
        'Hypertension Stage 1': 3,
        'Hypertension Stage 2': 4
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
        "age_years": user_input["age_years"],
        "gender": user_input["gender"],
        "bmi": user_bmi,
        "smoke": user_input["smoke"],
        "alco": user_input["alco"],
        "active": user_input["active"],
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
        user_row = user_data[user_data['ID'] == int(user_id)]

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
