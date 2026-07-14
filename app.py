"""
糖尿病治疗方案记录 - Flask 后端（无外部模板依赖）
数据存储在 SQLite，数据文件挂载到 NAS 持久化目录
"""
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder=None, template_folder=None)

# 数据库路径 - 通过环境变量配置，默认在容器内 /app/data
DB_PATH = os.environ.get('DB_PATH', '/app/data/diabetes.db')


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表结构"""
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS diet
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  meal TEXT NOT NULL,
                  food TEXT NOT NULL,
                  calories TEXT,
                  glucose TEXT,
                  eating_order TEXT,
                  note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS exercise
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  type TEXT NOT NULL,
                  duration TEXT,
                  intensity TEXT,
                  before_glucose TEXT,
                  after_glucose TEXT,
                  sugar_carried TEXT,
                  symptom TEXT,
                  note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS glucose
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  time TEXT NOT NULL,
                  type TEXT NOT NULL,
                  value TEXT NOT NULL,
                  note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS medication
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  time_detail TEXT,
                  name TEXT NOT NULL,
                  dose TEXT,
                  time_period TEXT,
                  side_effect TEXT,
                  note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS followup
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  weight TEXT,
                  waist TEXT,
                  hba1c TEXT,
                  note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals
                 (id INTEGER PRIMARY KEY,
                  weight TEXT,
                  glucose TEXT,
                  updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_drugs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  dose TEXT NOT NULL,
                  time_period TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('INSERT OR IGNORE INTO goals (id, weight, glucose) VALUES (1, "51", "8.5")')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    """直接返回内嵌 HTML，不依赖外部模板文件"""
    return app.response_class(HTML_CONTENT, mimetype='text/html; charset=utf-8')


# ========== 饮食记录 ==========
@app.route('/api/diet', methods=['GET'])
def list_diet():
    conn = get_db()
    rows = conn.execute('SELECT * FROM diet ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/diet', methods=['POST'])
def add_diet():
    data = request.json
    conn = get_db()
    conn.execute('''INSERT INTO diet (date, meal, food, calories, glucose, eating_order, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (data.get('date'), data.get('meal'), data.get('food'),
                  data.get('calories', ''), data.get('glucose', ''),
                  data.get('order', ''), data.get('note', '')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/diet/<int:item_id>', methods=['DELETE'])
def delete_diet(item_id):
    conn = get_db()
    conn.execute('DELETE FROM diet WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ========== 运动记录 ==========
@app.route('/api/exercise', methods=['GET'])
def list_exercise():
    conn = get_db()
    rows = conn.execute('SELECT * FROM exercise ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/exercise', methods=['POST'])
def add_exercise():
    data = request.json
    conn = get_db()
    conn.execute('''INSERT INTO exercise
                    (date, type, duration, intensity, before_glucose, after_glucose, sugar_carried, symptom, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (data.get('date'), data.get('type'), data.get('duration'),
                  data.get('intensity', ''), data.get('beforeGlucose', ''),
                  data.get('afterGlucose', ''), data.get('sugar', ''),
                  data.get('symptom', ''), data.get('note', '')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/exercise/<int:item_id>', methods=['DELETE'])
def delete_exercise(item_id):
    conn = get_db()
    conn.execute('DELETE FROM exercise WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ========== 血糖记录 ==========
@app.route('/api/glucose', methods=['GET'])
def list_glucose():
    conn = get_db()
    rows = conn.execute('SELECT * FROM glucose ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/glucose', methods=['POST'])
def add_glucose():
    data = request.json
    conn = get_db()
    conn.execute('''INSERT INTO glucose (date, time, type, value, note)
                    VALUES (?, ?, ?, ?, ?)''',
                 (data.get('date'), data.get('time'), data.get('type'),
                  data.get('value'), data.get('note', '')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/glucose/<int:item_id>', methods=['DELETE'])
def delete_glucose(item_id):
    conn = get_db()
    conn.execute('DELETE FROM glucose WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ========== 用药记录 ==========
@app.route('/api/medication', methods=['GET'])
def list_medication():
    conn = get_db()
    rows = conn.execute('SELECT * FROM medication ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/medication', methods=['POST'])
def add_medication():
    data = request.json
    conn = get_db()
    conn.execute('''INSERT INTO medication
                    (date, time_detail, name, dose, time_period, side_effect, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (data.get('date'), data.get('timeDetail', ''),
                  data.get('name'), data.get('dose', ''),
                  data.get('time', ''), data.get('sideEffect', '无'),
                  data.get('note', '')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/medication/<int:item_id>', methods=['DELETE'])
def delete_medication(item_id):
    conn = get_db()
    conn.execute('DELETE FROM medication WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ========== 随访记录 ==========
@app.route('/api/followup', methods=['GET'])
def list_followup():
    conn = get_db()
    rows = conn.execute('SELECT * FROM followup ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/followup', methods=['POST'])
def add_followup():
    data = request.json
    conn = get_db()
    conn.execute('''INSERT INTO followup (date, weight, waist, hba1c, note)
                    VALUES (?, ?, ?, ?, ?)''',
                 (data.get('date'), data.get('weight', ''),
                  data.get('waist', ''), data.get('hba1c', ''),
                  data.get('note', '')))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/followup/<int:item_id>', methods=['DELETE'])
def delete_followup(item_id):
    conn = get_db()
    conn.execute('DELETE FROM followup WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ========== 目标 ==========
@app.route('/api/goals', methods=['GET'])
def get_goals():
    conn = get_db()
    row = conn.execute('SELECT * FROM goals WHERE id = 1').fetchone()
    conn.close()
    return jsonify(dict(row) if row else {'weight': '51', 'glucose': '8.5'})


@app.route('/api/goals', methods=['POST'])
def update_goals():
    data = request.json
    conn = get_db()
    w = data.get('weight') or '51'
    g = data.get('glucose') or '8.5'
    conn.execute('UPDATE goals SET weight = ?, glucose = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1', (w, g))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ========== 自定义快捷用药按钮 ==========
@app.route('/api/custom-drugs', methods=['GET'])
def list_custom_drugs():
    conn = get_db()
    rows = conn.execute('SELECT * FROM custom_drugs ORDER BY id ASC').fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/custom-drugs', methods=['POST'])
def add_custom_drug():
    data = request.json
    name = (data.get('name') or '').strip()
    dose = (data.get('dose') or '').strip()
    time_period = (data.get('time') or '早餐随餐').strip()
    if not name or not dose:
        return jsonify({'ok': False, 'error': 'name 和 dose 不能为空'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO custom_drugs (name, dose, time_period) VALUES (?, ?, ?)',
              (name, dose, time_period))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return jsonify({'ok': True, 'id': new_id})


@app.route('/api/custom-drugs/<int:item_id>', methods=['DELETE'])
def delete_custom_drug(item_id):
    conn = get_db()
    conn.execute('DELETE FROM custom_drugs WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# 应用启动时自动初始化数据库（gunicorn 和 flask run 都适用）
with app.app_context():
    init_db()

# 从外部文件加载内嵌 HTML（构建时生成，避免模板依赖）
# HTML 直接内嵌在下方，无外部文件依赖

# HTML直接内嵌 - 为避免Python字符串转义问题，HTML存储在page.html中
import os
_PAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'page.html')
if os.path.exists(_PAGE_FILE):
    with open(_PAGE_FILE, 'r', encoding='utf-8') as _f:
        HTML_CONTENT = _f.read()
else:
    # 降级：空页面（不应发生）
    HTML_CONTENT = '<html><body><h1>Error: page.html not found</h1></body></html>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
