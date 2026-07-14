"""
糖尿病治疗方案记录 - Flask 后端 v2
数据存储在 SQLite，数据文件挂载到 NAS 持久化目录
新增：个人信息(profile)、记录编辑(PUT)、数据备份(backup/restore)、DB连接安全
"""
from flask import Flask, request, jsonify
import sqlite3
import os
import json

app = Flask(__name__, static_folder=None, template_folder=None)

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
                  date TEXT NOT NULL, meal TEXT NOT NULL, food TEXT NOT NULL,
                  calories TEXT, glucose TEXT, eating_order TEXT, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS exercise
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL, type TEXT NOT NULL, duration TEXT, intensity TEXT,
                  before_glucose TEXT, after_glucose TEXT, sugar_carried TEXT,
                  symptom TEXT, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS glucose
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL, time TEXT NOT NULL, type TEXT NOT NULL,
                  value TEXT NOT NULL, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS medication
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL, time_detail TEXT, name TEXT NOT NULL,
                  dose TEXT, time_period TEXT, side_effect TEXT, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS followup
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL, weight TEXT, waist TEXT, hba1c TEXT, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS goals
                 (id INTEGER PRIMARY KEY,
                  weight TEXT, glucose TEXT,
                  updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS custom_drugs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL, dose TEXT NOT NULL, time_period TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS profile
                 (id INTEGER PRIMARY KEY,
                  height TEXT, weight TEXT, age TEXT, gender TEXT,
                  glucose_fasting_target TEXT, glucose_post_target TEXT,
                  weight_target TEXT,
                  updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('INSERT OR IGNORE INTO goals (id, weight, glucose) VALUES (1, "56", "7.8")')
    c.execute('''INSERT OR IGNORE INTO profile (id, height, weight, age, gender,
                  glucose_fasting_target, glucose_post_target, weight_target)
                  VALUES (1, "175", "51", "35", "男", "5.6", "7.8", "56")''')

    conn.commit()
    conn.close()


@app.route('/')
def index():
    return app.response_class(HTML_CONTENT, mimetype='text/html; charset=utf-8')


# ===== 通用 helper =====
def _db_op(query, params=(), fetch=False, fetchone=False, commit=True):
    """安全数据库操作，自动 close"""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        result = None
        if fetchone:
            result = cur.fetchone()
        elif fetch:
            result = cur.fetchall()
        if commit:
            conn.commit()
        return result, conn, cur
    except Exception:
        conn.rollback()
        raise


# ========== 个人信息 (profile) ==========
@app.route('/api/profile', methods=['GET'])
def get_profile():
    row, conn, _ = _db_op('SELECT * FROM profile WHERE id=1', fetchone=True)
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({
        'height': '175', 'weight': '51', 'age': '35', 'gender': '男',
        'glucose_fasting_target': '5.6', 'glucose_post_target': '7.8',
        'weight_target': '56'
    })


@app.route('/api/profile', methods=['POST'])
def update_profile():
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE profile SET height=?, weight=?, age=?, gender=?,
           glucose_fasting_target=?, glucose_post_target=?, weight_target=?,
           updated_at=CURRENT_TIMESTAMP WHERE id=1''',
        (data.get('height', '175'), data.get('weight', '51'),
         data.get('age', '35'), data.get('gender', '男'),
         data.get('glucose_fasting_target', '5.6'),
         data.get('glucose_post_target', '7.8'),
         data.get('weight_target', '56')),
        commit=True)
    conn.close()
    return jsonify({'ok': True})


# ========== 饮食记录 ==========
@app.route('/api/diet', methods=['GET'])
def list_diet():
    rows, conn, _ = _db_op('SELECT * FROM diet ORDER BY id DESC', fetch=True)
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/diet', methods=['POST'])
def add_diet():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO diet (date, meal, food, calories, glucose, eating_order, note)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (data.get('date'), data.get('meal'), data.get('food'),
         data.get('calories', ''), data.get('glucose', ''),
         data.get('order', ''), data.get('note', '')))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/diet/<int:item_id>', methods=['PUT'])
def update_diet(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE diet SET date=?, meal=?, food=?, calories=?, glucose=?,
           eating_order=?, note=? WHERE id=?''',
        (data.get('date'), data.get('meal'), data.get('food'),
         data.get('calories', ''), data.get('glucose', ''),
         data.get('order', ''), data.get('note', ''), item_id))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/diet/<int:item_id>', methods=['DELETE'])
def delete_diet(item_id):
    _, conn, _ = _db_op('DELETE FROM diet WHERE id=?', (item_id,))
    conn.close()
    return jsonify({'ok': True})


# ========== 运动记录 ==========
@app.route('/api/exercise', methods=['GET'])
def list_exercise():
    rows, conn, _ = _db_op('SELECT * FROM exercise ORDER BY id DESC', fetch=True)
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/exercise', methods=['POST'])
def add_exercise():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO exercise
           (date, type, duration, intensity, before_glucose, after_glucose,
            sugar_carried, symptom, note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (data.get('date'), data.get('type'), data.get('duration'),
         data.get('intensity', ''), data.get('beforeGlucose', ''),
         data.get('afterGlucose', ''), data.get('sugar', ''),
         data.get('symptom', ''), data.get('note', '')))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/exercise/<int:item_id>', methods=['PUT'])
def update_exercise(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE exercise SET date=?, type=?, duration=?, intensity=?,
           before_glucose=?, after_glucose=?, sugar_carried=?, symptom=?,
           note=? WHERE id=?''',
        (data.get('date'), data.get('type'), data.get('duration'),
         data.get('intensity', ''), data.get('beforeGlucose', ''),
         data.get('afterGlucose', ''), data.get('sugar', ''),
         data.get('symptom', ''), data.get('note', ''), item_id))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/exercise/<int:item_id>', methods=['DELETE'])
def delete_exercise(item_id):
    _, conn, _ = _db_op('DELETE FROM exercise WHERE id=?', (item_id,))
    conn.close()
    return jsonify({'ok': True})


# ========== 血糖记录 ==========
@app.route('/api/glucose', methods=['GET'])
def list_glucose():
    rows, conn, _ = _db_op('SELECT * FROM glucose ORDER BY id DESC', fetch=True)
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/glucose', methods=['POST'])
def add_glucose():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO glucose (date, time, type, value, note)
           VALUES (?, ?, ?, ?, ?)''',
        (data.get('date'), data.get('time'), data.get('type'),
         data.get('value'), data.get('note', '')))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/glucose/<int:item_id>', methods=['PUT'])
def update_glucose(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE glucose SET date=?, time=?, type=?, value=?, note=? WHERE id=?''',
        (data.get('date'), data.get('time'), data.get('type'),
         data.get('value'), data.get('note', ''), item_id))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/glucose/<int:item_id>', methods=['DELETE'])
def delete_glucose(item_id):
    _, conn, _ = _db_op('DELETE FROM glucose WHERE id=?', (item_id,))
    conn.close()
    return jsonify({'ok': True})


# ========== 用药记录 ==========
@app.route('/api/medication', methods=['GET'])
def list_medication():
    rows, conn, _ = _db_op('SELECT * FROM medication ORDER BY id DESC', fetch=True)
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/medication', methods=['POST'])
def add_medication():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO medication
           (date, time_detail, name, dose, time_period, side_effect, note)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (data.get('date'), data.get('timeDetail', ''),
         data.get('name'), data.get('dose', ''),
         data.get('time', ''), data.get('sideEffect', '无'),
         data.get('note', '')))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/medication/<int:item_id>', methods=['PUT'])
def update_medication(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE medication SET date=?, time_detail=?, name=?, dose=?,
           time_period=?, side_effect=?, note=? WHERE id=?''',
        (data.get('date'), data.get('timeDetail', ''),
         data.get('name'), data.get('dose', ''),
         data.get('time', ''), data.get('sideEffect', '无'),
         data.get('note', ''), item_id))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/medication/<int:item_id>', methods=['DELETE'])
def delete_medication(item_id):
    _, conn, _ = _db_op('DELETE FROM medication WHERE id=?', (item_id,))
    conn.close()
    return jsonify({'ok': True})


# ========== 随访记录 ==========
@app.route('/api/followup', methods=['GET'])
def list_followup():
    rows, conn, _ = _db_op('SELECT * FROM followup ORDER BY id DESC', fetch=True)
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/api/followup', methods=['POST'])
def add_followup():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO followup (date, weight, waist, hba1c, note)
           VALUES (?, ?, ?, ?, ?)''',
        (data.get('date'), data.get('weight', ''),
         data.get('waist', ''), data.get('hba1c', ''),
         data.get('note', '')))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/followup/<int:item_id>', methods=['PUT'])
def update_followup(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE followup SET date=?, weight=?, waist=?, hba1c=?, note=? WHERE id=?''',
        (data.get('date'), data.get('weight', ''),
         data.get('waist', ''), data.get('hba1c', ''),
         data.get('note', ''), item_id))
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/followup/<int:item_id>', methods=['DELETE'])
def delete_followup(item_id):
    _, conn, _ = _db_op('DELETE FROM followup WHERE id=?', (item_id,))
    conn.close()
    return jsonify({'ok': True})


# ========== 目标 (goals) ==========
@app.route('/api/goals', methods=['GET'])
def get_goals():
    row, conn, _ = _db_op('SELECT * FROM goals WHERE id=1', fetchone=True)
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'weight': '56', 'glucose': '7.8'})


@app.route('/api/goals', methods=['POST'])
def update_goals():
    data = request.json
    w = data.get('weight') or '56'
    g = data.get('glucose') or '7.8'
    _, conn, _ = _db_op(
        'UPDATE goals SET weight=?, glucose=?, updated_at=CURRENT_TIMESTAMP WHERE id=1',
        (w, g))
    conn.close()
    return jsonify({'ok': True})


# ========== 自定义快捷用药按钮 ==========
@app.route('/api/custom-drugs', methods=['GET'])
def list_custom_drugs():
    rows, conn, _ = _db_op('SELECT * FROM custom_drugs ORDER BY id ASC', fetch=True)
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
    _, conn, cur = _db_op(
        'INSERT INTO custom_drugs (name, dose, time_period) VALUES (?, ?, ?)',
        (name, dose, time_period))
    new_id = cur.lastrowid
    conn.close()
    return jsonify({'ok': True, 'id': new_id})


@app.route('/api/custom-drugs/<int:item_id>', methods=['DELETE'])
def delete_custom_drug(item_id):
    _, conn, _ = _db_op('DELETE FROM custom_drugs WHERE id=?', (item_id,))
    conn.close()
    return jsonify({'ok': True})


# ========== 数据备份与恢复 ==========
@app.route('/api/backup', methods=['GET'])
def backup_data():
    """导出所有数据为 JSON"""
    tables = ['profile', 'goals', 'custom_drugs', 'diet', 'exercise',
              'glucose', 'medication', 'followup']
    backup = {}
    conn = get_db()
    try:
        for t in tables:
            rows = conn.execute(f'SELECT * FROM {t}').fetchall()
            backup[t] = [dict(r) for r in rows]
        conn.close()
    except Exception:
        conn.rollback()
        conn.close()
        raise
    return jsonify(backup)


@app.route('/api/restore', methods=['POST'])
def restore_data():
    """从 JSON 恢复所有数据（覆盖现有数据）"""
    data = request.json
    conn = get_db()
    try:
        # 清空所有表
        for t in ['diet', 'exercise', 'glucose', 'medication', 'followup', 'custom_drugs']:
            conn.execute(f'DELETE FROM {t}')
        # 恢复数据
        for t, rows in data.items():
            if t in ('profile', 'goals'):
                # 单行表，用 UPDATE
                if t == 'profile' and rows:
                    r = rows[0]
                    conn.execute(
                        '''UPDATE profile SET height=?, weight=?, age=?, gender=?,
                           glucose_fasting_target=?, glucose_post_target=?,
                           weight_target=?, updated_at=CURRENT_TIMESTAMP WHERE id=1''',
                        (r.get('height', '175'), r.get('weight', '51'),
                         r.get('age', '35'), r.get('gender', '男'),
                         r.get('glucose_fasting_target', '5.6'),
                         r.get('glucose_post_target', '7.8'),
                         r.get('weight_target', '56')))
                elif t == 'goals' and rows:
                    r = rows[0]
                    conn.execute(
                        'UPDATE goals SET weight=?, glucose=?, updated_at=CURRENT_TIMESTAMP WHERE id=1',
                        (r.get('weight', '56'), r.get('glucose', '7.8')))
            elif t == 'custom_drugs':
                for r in rows:
                    conn.execute(
                        'INSERT INTO custom_drugs (name, dose, time_period) VALUES (?, ?, ?)',
                        (r.get('name'), r.get('dose'), r.get('time_period')))
            elif t == 'diet':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO diet (date, meal, food, calories, glucose, eating_order, note)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (r.get('date'), r.get('meal'), r.get('food'),
                         r.get('calories', ''), r.get('glucose', ''),
                         r.get('eating_order', ''), r.get('note', '')))
            elif t == 'exercise':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO exercise
                           (date, type, duration, intensity, before_glucose, after_glucose,
                            sugar_carried, symptom, note)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (r.get('date'), r.get('type'), r.get('duration'),
                         r.get('intensity', ''), r.get('before_glucose', ''),
                         r.get('after_glucose', ''), r.get('sugar_carried', ''),
                         r.get('symptom', ''), r.get('note', '')))
            elif t == 'glucose':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO glucose (date, time, type, value, note)
                           VALUES (?, ?, ?, ?, ?)''',
                        (r.get('date'), r.get('time'), r.get('type'),
                         r.get('value'), r.get('note', '')))
            elif t == 'medication':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO medication
                           (date, time_detail, name, dose, time_period, side_effect, note)
                           VALUES (?, ?, ?, ?, ?, ?, ?)''',
                        (r.get('date'), r.get('time_detail', ''),
                         r.get('name'), r.get('dose', ''),
                         r.get('time_period', ''), r.get('side_effect', '无'),
                         r.get('note', '')))
            elif t == 'followup':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO followup (date, weight, waist, hba1c, note)
                           VALUES (?, ?, ?, ?, ?)''',
                        (r.get('date'), r.get('weight', ''),
                         r.get('waist', ''), r.get('hba1c', ''),
                         r.get('note', '')))
        conn.commit()
        conn.close()
        return jsonify({'ok': True})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'ok': False, 'error': str(e)}), 500


# 应用启动时自动初始化数据库
with app.app_context():
    init_db()

# 从外部文件加载 HTML
_PAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'page.html')
if os.path.exists(_PAGE_FILE):
    with open(_PAGE_FILE, 'r', encoding='utf-8') as _f:
        HTML_CONTENT = _f.read()
else:
    HTML_CONTENT = '<html><body><h1>Error: page.html not found</h1></body></html>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
