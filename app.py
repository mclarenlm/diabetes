"""
糖尿病治疗方案记录 - Flask 后端 v2
数据存储在 SQLite，数据文件挂载到 NAS 持久化目录
新增：个人信息(profile)、记录编辑(PUT)、数据备份(backup/restore)、DB连接安全
"""
from flask import Flask, request, jsonify, session, g
import sqlite3
import os
import json

app = Flask(__name__, static_folder=None, template_folder=None)

DB_PATH = os.environ.get('DB_PATH', '/app/data/diabetes.db')

# ========== 访问安全（Phase 1：单密码 gate） ==========
# 设置环境变量 ACCESS_PASSWORD 即开启密码保护；留空则保持开放（向后兼容）
ACCESS_PASSWORD = (os.environ.get('ACCESS_PASSWORD', '') or '').strip()
AUTH_ENABLED = bool(ACCESS_PASSWORD)
# SECRET_KEY 用于签名 session；生产环境务必通过环境变量固定，否则重启后需重新登录
app.secret_key = (os.environ.get('SECRET_KEY') or os.urandom(24).hex())
app.config['PERMANENT_SESSION_LIFETIME'] = int(os.environ.get('SESSION_TIMEOUT', '86400'))  # 默认 24h



def get_db():
    """获取数据库连接（按请求缓存，自动设置 WAL 模式提升并发性能）"""
    if 'db' not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=5000')
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """请求结束时自动关闭数据库连接（统一收口，无需在各路由中手动 close）"""
    db = g.pop('db', None)
    if db:
        db.close()


def _current_user():
    """从 session 获取当前选择的成员 ID"""
    uid = session.get('user_id')
    return int(uid) if uid is not None else None


def _ensure_user():
    """获取当前用户 ID，未选择则回退到成员 1"""
    uid = _current_user()
    return uid if uid is not None else 1


def init_db():
    """初始化数据库表结构"""
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS diet
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  date TEXT NOT NULL, meal TEXT NOT NULL, food TEXT NOT NULL,
                  calories REAL, glucose REAL, eating_order TEXT, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS exercise
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  date TEXT NOT NULL, type TEXT NOT NULL, duration TEXT, intensity TEXT,
                  before_glucose REAL, after_glucose REAL, sugar_carried TEXT,
                  symptom TEXT, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS glucose
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  date TEXT NOT NULL, time TEXT NOT NULL, type TEXT NOT NULL,
                  value REAL NOT NULL, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS medication
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  date TEXT NOT NULL, time_detail TEXT, name TEXT NOT NULL,
                  dose TEXT, time_period TEXT, side_effect TEXT, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS followup
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  date TEXT NOT NULL, weight REAL, waist REAL, hba1c REAL, note TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS goals
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  weight REAL, glucose REAL,
                  updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS custom_drugs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  name TEXT NOT NULL, dose TEXT NOT NULL, time_period TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS profile
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  height REAL, weight REAL, age INTEGER, gender TEXT,
                  glucose_fasting_target REAL, glucose_post_target REAL,
                  weight_target REAL,
                  updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('INSERT OR IGNORE INTO goals (id, weight, glucose) VALUES (1, 56, 7.8)')
    c.execute('''INSERT OR IGNORE INTO profile (id, height, weight, age, gender,
                  glucose_fasting_target, glucose_post_target, weight_target)
                  VALUES (1, 175, 51, 35, "男", 5.6, 7.8, 56)''')

    c.execute('''CREATE TABLE IF NOT EXISTS meal_templates
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL DEFAULT 1,
                  name TEXT NOT NULL,
                  meal TEXT NOT NULL,
                  food TEXT NOT NULL,
                  calories REAL,
                  eating_order TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT DEFAULT '本人',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('INSERT OR IGNORE INTO members (id, name, role) VALUES (1, "本人", "本人")')

    # ========== 性能索引（按 user_id + date 加速查询） ==========
    c.execute('CREATE INDEX IF NOT EXISTS idx_diet_user_date ON diet(user_id, date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_glucose_user_date ON glucose(user_id, date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_exercise_user_date ON exercise(user_id, date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_medication_user_date ON medication(user_id, date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_followup_user_date ON followup(user_id, date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_meal_templates_user ON meal_templates(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_custom_drugs_user ON custom_drugs(user_id)')

    conn.commit()
    conn.close()


@app.route('/')
def index():
    return app.response_class(HTML_CONTENT, mimetype='text/html; charset=utf-8')


# ========== 登录页（未授权时展示） ==========
LOGIN_HTML = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>糖尿病记录工具 - 登录</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; min-height:100vh; display:flex; align-items:center; justify-content:center;
         font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
         background:linear-gradient(135deg,#e8f5e9,#e3f2fd); }
  .card { background:#fff; padding:32px 28px; border-radius:16px; box-shadow:0 10px 40px rgba(0,0,0,.12); width:90%; max-width:360px; }
  h2 { margin:0 0 4px; color:#2e7d32; }
  .sub { color:#888; font-size:.82rem; margin-bottom:20px; }
  label { display:block; font-size:.82rem; color:#555; margin-bottom:6px; }
  input { width:100%; padding:12px; border:1px solid #ddd; border-radius:10px; font-size:1rem; margin-bottom:14px; }
  button { width:100%; padding:12px; border:none; border-radius:10px; background:#2e7d32; color:#fff; font-size:1rem; cursor:pointer; }
  button:active { transform:scale(.98); }
  .msg { color:#c62828; font-size:.82rem; min-height:1.2em; margin-top:8px; text-align:center; }
</style></head>
<body><div class="card">
  <h2>🔐 访问保护</h2>
  <div class="sub">请输入访问密码以进入糖尿病记录工具</div>
  <form id="loginForm">
    <label for="pwd">访问密码</label>
    <input type="password" id="pwd" placeholder="请输入密码" autocomplete="current-password" autofocus>
    <button type="submit">登 录</button>
    <div class="msg" id="msg"></div>
  </form>
</div>
<script>
  document.getElementById('loginForm').addEventListener('submit', async function(e){
    e.preventDefault();
    var pwd = document.getElementById('pwd').value;
    var msg = document.getElementById('msg');
    try {
      var r = await fetch('/api/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({password: pwd}) });
      var d = await r.json();
      if (r.ok && d.ok) { location.href = '/'; }
      else { msg.textContent = d.error || '登录失败'; }
    } catch(err) { msg.textContent = '网络错误，请重试'; }
  });
</script>
</body></html>'''


@app.before_request
def require_auth():
    """单密码 gate：未设置 ACCESS_PASSWORD 时完全开放；设置后所有请求需登录。"""
    if not AUTH_ENABLED:
        return
    path = request.path
    # 登录/登出接口与 PWA 必要资源放行
    if path in ('/api/login', '/api/logout', '/api/auth-status', '/manifest.json', '/sw.js'):
        return
    if session.get('authed'):
        return
    # API 请求返回 401，由前端弹出登录层
    if path.startswith('/api/'):
        return jsonify({'ok': False, 'error': '未授权，请先登录', 'needAuth': True}), 401
    # 页面请求：未登录直接展示登录页
    if path in ('/', ''):
        return app.response_class(LOGIN_HTML, mimetype='text/html; charset=utf-8')
    return jsonify({'ok': False, 'error': '未授权', 'needAuth': True}), 401


@app.route('/api/login', methods=['POST'])
def api_login():
    if not AUTH_ENABLED:
        return jsonify({'ok': True, 'message': '未启用密码保护'})
    data = request.json or {}
    pwd = (data.get('password') or '').strip()
    if pwd and pwd == ACCESS_PASSWORD:
        session['authed'] = True
        session.permanent = True
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': '密码错误'}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('authed', None)
    return jsonify({'ok': True})


@app.route('/api/auth-status', methods=['GET'])
def api_auth_status():
    return jsonify({'enabled': AUTH_ENABLED, 'authed': bool(session.get('authed')), 'user_id': _ensure_user()})


@app.route('/manifest.json')
def manifest():
    m = {
        "name": "糖尿病记录工具",
        "short_name": "糖尿病记录",
        "description": "糖尿病个性化治疗与控糖方案记录工具",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f7fafc",
        "theme_color": "#2c7a7b",
        "icons": [
            {"src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'%3E%3Crect width='192' height='192' rx='40' fill='%232c7a7b'/%3E%3Ctext x='96' y='130' font-size='100' text-anchor='middle' fill='white'%3E🍃%3C/text%3E%3C/svg%3E", "sizes": "192x192", "type": "image/svg+xml"},
            {"src": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Crect width='512' height='512' rx='100' fill='%232c7a7b'/%3E%3Ctext x='256' y='350' font-size='260' text-anchor='middle' fill='white'%3E🍃%3C/text%3E%3C/svg%3E", "sizes": "512x512", "type": "image/svg+xml"}
        ]
    }
    return jsonify(m)


@app.route('/sw.js')
def service_worker():
    sw = '''
const CACHE_NAME = 'diabetes-tracker-v3.0';
const ASSETS = ['/', '/manifest.json'];

// ========== IndexedDB 离线存储 ==========
function openOfflineDB() {
    return new Promise((resolve, reject) => {
        const req = indexedDB.open('diabetes-offline', 1);
        req.onupgradeneeded = () => {
            const db = req.result;
            if (!db.objectStoreNames.contains('pending')) {
                db.createObjectStore('pending', { keyPath: 'id', autoIncrement: true });
            }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
    });
}

async function storePending(reqData) {
    const db = await openOfflineDB();
    const tx = db.transaction('pending', 'readwrite');
    tx.objectStore('pending').add({ url: reqData.url, method: reqData.method, body: reqData.body, timestamp: Date.now() });
    return tx.complete;
}

async function getPending() {
    const db = await openOfflineDB();
    return new Promise((resolve) => {
        const tx = db.transaction('pending', 'readonly');
        const req = tx.objectStore('pending').getAll();
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => resolve([]);
    });
}

async function clearPending() {
    const db = await openOfflineDB();
    const tx = db.transaction('pending', 'readwrite');
    tx.objectStore('pending').clear();
    return tx.complete;
}

async function syncPending() {
    const items = await getPending();
    if (items.length === 0) return;
    let success = true;
    for (const item of items) {
        try {
            const opts = { method: item.method, headers: { 'Content-Type': 'application/json' } };
            if (item.body) opts.body = item.body;
            const r = await fetch(item.url, opts);
            if (!r.ok) { success = false; break; }
        } catch (e) { success = false; break; }
    }
    if (success) await clearPending();
}

// ========== 安装/激活 ==========
self.addEventListener('install', e => {
    e.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return Promise.allSettled(ASSETS.map(url =>
                fetch(url, { cache: 'no-cache' }).then(resp => {
                    if (resp.ok) cache.put(url, resp.clone());
                }).catch(() => {})
            ));
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', e => {
    e.waitUntil(
        caches.keys().then(keys =>
            Promise.all(keys.map(k => k !== CACHE_NAME && caches.delete(k)))
        )
    );
    e.waitUntil(self.clients.claim());
    // 网络恢复后自动同步
    e.waitUntil(syncPending());
});

// ========== Stale-While-Revalidate + 离线写入 ==========
self.addEventListener('fetch', e => {
    const url = new URL(e.request.url);

    // API POST/PUT/DELETE：离线时存入 IndexedDB 等待同步
    if (url.pathname.startsWith('/api/') && e.request.method !== 'GET') {
        e.respondWith(
            fetch(e.request.clone()).catch(async () => {
                // 只缓存写入请求
                if (['POST', 'PUT', 'DELETE'].includes(e.request.method)) {
                    const body = e.request.method !== 'DELETE' ? await e.request.clone().text() : null;
                    await storePending({ url: e.request.url, method: e.request.method, body: body });
                    return new Response(JSON.stringify({ ok: true, offline: true, message: '已离线保存，网络恢复后自动同步' }), {
                        status: 200, headers: { 'Content-Type': 'application/json' }
                    });
                }
                return new Response(JSON.stringify({ ok: false, error: '网络不可用' }), {
                    status: 503, headers: { 'Content-Type': 'application/json' }
                });
            })
        );
        return;
    }

    // GET 请求：SWR 策略（优先缓存，后台更新）
    if (e.request.method === 'GET') {
        // 跳过 API（不缓存数据接口）
        if (url.pathname.startsWith('/api/')) return;

        // ECharts CDN：缓存更久
        if (url.hostname === 'cdn.jsdelivr.net') {
            e.respondWith(
                caches.match(e.request).then(cached => {
                    const fetchPromise = fetch(e.request).then(resp => {
                        if (resp.ok) {
                            const clone = resp.clone();
                            caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
                        }
                        return resp;
                    });
                    return cached || fetchPromise;
                })
            );
            return;
        }

        // 页面资源：SWR
        e.respondWith(
            caches.match(e.request).then(cached => {
                const fetchPromise = fetch(e.request).then(resp => {
                    if (resp.ok) {
                        const clone = resp.clone();
                        caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
                    }
                    return resp;
                }).catch(() => cached);
                return cached || fetchPromise;
            })
        );
    }
});
'''
    return app.response_class(sw, mimetype='application/javascript')


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
    row, conn, _ = _db_op('SELECT * FROM profile WHERE user_id=? AND id=1', (_ensure_user(),), fetchone=True)
    if row:
        return jsonify(dict(row))
    return jsonify({
        'height': 175, 'weight': 51, 'age': 35, 'gender': '男',
        'glucose_fasting_target': 5.6, 'glucose_post_target': 7.8,
        'weight_target': 56
    })


@app.route('/api/profile', methods=['POST'])
def update_profile():
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE profile SET height=?, weight=?, age=?, gender=?,
           glucose_fasting_target=?, glucose_post_target=?, weight_target=?,
           updated_at=CURRENT_TIMESTAMP WHERE user_id=? AND id=1''',
        (data.get('height', 175), data.get('weight', 51),
         data.get('age', 35), data.get('gender', '男'),
         data.get('glucose_fasting_target', 5.6),
         data.get('glucose_post_target', 7.8),
         data.get('weight_target', 56), _ensure_user()),
        commit=True)
    return jsonify({'ok': True})


# ========== 饮食记录 ==========
@app.route('/api/diet', methods=['GET'])
def list_diet():
    rows, conn, _ = _db_op('SELECT * FROM diet WHERE user_id=? ORDER BY id DESC', (_ensure_user(),), fetch=True)
    return jsonify([dict(r) for r in rows])


@app.route('/api/diet', methods=['POST'])
def add_diet():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO diet (user_id, date, meal, food, calories, glucose, eating_order, note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (_ensure_user(), data.get('date'), data.get('meal'), data.get('food'),
         data.get('calories', ''), data.get('glucose', ''),
         data.get('order', ''), data.get('note', '')))
    return jsonify({'ok': True})


@app.route('/api/diet/<int:item_id>', methods=['PUT'])
def update_diet(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE diet SET date=?, meal=?, food=?, calories=?, glucose=?,
           eating_order=?, note=? WHERE user_id=? AND id=?''',
        (data.get('date'), data.get('meal'), data.get('food'),
         data.get('calories', ''), data.get('glucose', ''),
         data.get('order', ''), data.get('note', ''), _ensure_user(), item_id))
    return jsonify({'ok': True})


@app.route('/api/diet/<int:item_id>', methods=['DELETE'])
def delete_diet(item_id):
    _, conn, _ = _db_op('DELETE FROM diet WHERE user_id=? AND id=?', (_ensure_user(), item_id))
    return jsonify({'ok': True})


# ========== 运动记录 ==========
@app.route('/api/exercise', methods=['GET'])
def list_exercise():
    rows, conn, _ = _db_op('SELECT * FROM exercise WHERE user_id=? ORDER BY id DESC', (_ensure_user(),), fetch=True)
    return jsonify([dict(r) for r in rows])


@app.route('/api/exercise', methods=['POST'])
def add_exercise():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO exercise
           (user_id, date, type, duration, intensity, before_glucose, after_glucose,
            sugar_carried, symptom, note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (_ensure_user(), data.get('date'), data.get('type'), data.get('duration'),
         data.get('intensity', ''), data.get('beforeGlucose', ''),
         data.get('afterGlucose', ''), data.get('sugar', ''),
         data.get('symptom', ''), data.get('note', '')))
    return jsonify({'ok': True})


@app.route('/api/exercise/<int:item_id>', methods=['PUT'])
def update_exercise(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE exercise SET date=?, type=?, duration=?, intensity=?,
           before_glucose=?, after_glucose=?, sugar_carried=?, symptom=?,
           note=? WHERE user_id=? AND id=?''',
        (data.get('date'), data.get('type'), data.get('duration'),
         data.get('intensity', ''), data.get('beforeGlucose', ''),
         data.get('afterGlucose', ''), data.get('sugar', ''),
         data.get('symptom', ''), data.get('note', ''), _ensure_user(), item_id))
    return jsonify({'ok': True})


@app.route('/api/exercise/<int:item_id>', methods=['DELETE'])
def delete_exercise(item_id):
    _, conn, _ = _db_op('DELETE FROM exercise WHERE user_id=? AND id=?', (_ensure_user(), item_id))
    return jsonify({'ok': True})


# ========== 血糖记录 ==========
@app.route('/api/glucose', methods=['GET'])
def list_glucose():
    rows, conn, _ = _db_op('SELECT * FROM glucose WHERE user_id=? ORDER BY id DESC', (_ensure_user(),), fetch=True)
    return jsonify([dict(r) for r in rows])


@app.route('/api/glucose', methods=['POST'])
def add_glucose():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO glucose (user_id, date, time, type, value, note)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (_ensure_user(), data.get('date'), data.get('time'), data.get('type'),
         data.get('value'), data.get('note', '')))
    return jsonify({'ok': True})


@app.route('/api/glucose/<int:item_id>', methods=['PUT'])
def update_glucose(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE glucose SET date=?, time=?, type=?, value=?, note=? WHERE user_id=? AND id=?''',
        (data.get('date'), data.get('time'), data.get('type'),
         data.get('value'), data.get('note', ''), _ensure_user(), item_id))
    return jsonify({'ok': True})


@app.route('/api/glucose/<int:item_id>', methods=['DELETE'])
def delete_glucose(item_id):
    _, conn, _ = _db_op('DELETE FROM glucose WHERE user_id=? AND id=?', (_ensure_user(), item_id))
    return jsonify({'ok': True})


# ========== 用药记录 ==========
@app.route('/api/medication', methods=['GET'])
def list_medication():
    rows, conn, _ = _db_op('SELECT * FROM medication WHERE user_id=? ORDER BY id DESC', (_ensure_user(),), fetch=True)
    return jsonify([dict(r) for r in rows])


@app.route('/api/medication', methods=['POST'])
def add_medication():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO medication
           (user_id, date, time_detail, name, dose, time_period, side_effect, note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (_ensure_user(), data.get('date'), data.get('timeDetail', ''),
         data.get('name'), data.get('dose', ''),
         data.get('time', ''), data.get('sideEffect', '无'),
         data.get('note', '')))
    return jsonify({'ok': True})


@app.route('/api/medication/<int:item_id>', methods=['PUT'])
def update_medication(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE medication SET date=?, time_detail=?, name=?, dose=?,
           time_period=?, side_effect=?, note=? WHERE user_id=? AND id=?''',
        (data.get('date'), data.get('timeDetail', ''),
         data.get('name'), data.get('dose', ''),
         data.get('time', ''), data.get('sideEffect', '无'),
         data.get('note', ''), _ensure_user(), item_id))
    return jsonify({'ok': True})


@app.route('/api/medication/<int:item_id>', methods=['DELETE'])
def delete_medication(item_id):
    _, conn, _ = _db_op('DELETE FROM medication WHERE user_id=? AND id=?', (_ensure_user(), item_id))
    return jsonify({'ok': True})


# ========== 随访记录 ==========
@app.route('/api/followup', methods=['GET'])
def list_followup():
    rows, conn, _ = _db_op('SELECT * FROM followup WHERE user_id=? ORDER BY id DESC', (_ensure_user(),), fetch=True)
    return jsonify([dict(r) for r in rows])


@app.route('/api/followup', methods=['POST'])
def add_followup():
    data = request.json
    _, conn, _ = _db_op(
        '''INSERT INTO followup (user_id, date, weight, waist, hba1c, note)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (_ensure_user(), data.get('date'), data.get('weight', ''),
         data.get('waist', ''), data.get('hba1c', ''),
         data.get('note', '')))
    return jsonify({'ok': True})


@app.route('/api/followup/<int:item_id>', methods=['PUT'])
def update_followup(item_id):
    data = request.json
    _, conn, _ = _db_op(
        '''UPDATE followup SET date=?, weight=?, waist=?, hba1c=?, note=? WHERE user_id=? AND id=?''',
        (data.get('date'), data.get('weight', ''),
         data.get('waist', ''), data.get('hba1c', ''),
         data.get('note', ''), _ensure_user(), item_id))
    return jsonify({'ok': True})


@app.route('/api/followup/<int:item_id>', methods=['DELETE'])
def delete_followup(item_id):
    _, conn, _ = _db_op('DELETE FROM followup WHERE user_id=? AND id=?', (_ensure_user(), item_id))
    return jsonify({'ok': True})


# ========== 目标 (goals) ==========
@app.route('/api/goals', methods=['GET'])
def get_goals():
    row, conn, _ = _db_op('SELECT * FROM goals WHERE user_id=? AND id=1', (_ensure_user(),), fetchone=True)
    if row:
        return jsonify(dict(row))
    return jsonify({'weight': 56, 'glucose': 7.8})


@app.route('/api/goals', methods=['POST'])
def update_goals():
    data = request.json
    w = data.get('weight') or 56
    g = data.get('glucose') or 7.8
    _, conn, _ = _db_op(
        'UPDATE goals SET weight=?, glucose=?, updated_at=CURRENT_TIMESTAMP WHERE user_id=? AND id=1',
        (w, g, _ensure_user()))
    return jsonify({'ok': True})


# ========== 自定义快捷用药按钮 ==========
@app.route('/api/custom-drugs', methods=['GET'])
def list_custom_drugs():
    rows, conn, _ = _db_op('SELECT * FROM custom_drugs WHERE user_id=? ORDER BY id ASC', (_ensure_user(),), fetch=True)
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
        'INSERT INTO custom_drugs (user_id, name, dose, time_period) VALUES (?, ?, ?, ?)',
        (_ensure_user(), name, dose, time_period))
    new_id = cur.lastrowid
    return jsonify({'ok': True, 'id': new_id})


@app.route('/api/custom-drugs/<int:item_id>', methods=['DELETE'])
def delete_custom_drug(item_id):
    _, conn, _ = _db_op('DELETE FROM custom_drugs WHERE user_id=? AND id=?', (_ensure_user(), item_id))
    return jsonify({'ok': True})


# ========== 家庭成员管理 ==========
@app.route('/api/members', methods=['GET'])
def list_members():
    rows, conn, _ = _db_op('SELECT * FROM members ORDER BY id ASC', fetch=True)
    return jsonify([dict(r) for r in rows])

@app.route('/api/members', methods=['POST'])
def add_member():
    data = request.json
    name = (data.get('name') or '').strip()
    role = (data.get('role') or '家属').strip()
    if not name:
        return jsonify({'ok': False, 'error': '姓名不能为空'}), 400
    _, conn, cur = _db_op('INSERT INTO members (name, role) VALUES (?, ?)', (name, role))
    new_id = cur.lastrowid
    return jsonify({'ok': True, 'id': new_id})

@app.route('/api/members/<int:item_id>', methods=['PUT'])
def update_member(item_id):
    if item_id == 1:
        return jsonify({'ok': False, 'error': '默认成员不可修改'}), 400
    data = request.json
    name = (data.get('name') or '').strip()
    role = (data.get('role') or '').strip()
    if not name:
        return jsonify({'ok': False, 'error': '姓名不能为空'}), 400
    _, conn, _ = _db_op('UPDATE members SET name=?, role=? WHERE id=?', (name, role, item_id))
    return jsonify({'ok': True})

@app.route('/api/members/<int:item_id>', methods=['DELETE'])
def delete_member(item_id):
    if item_id == 1:
        return jsonify({'ok': False, 'error': '默认成员不可删除'}), 400
    conn = get_db()
    try:
        for t in ['diet', 'exercise', 'glucose', 'medication', 'followup', 'custom_drugs', 'meal_templates']:
            conn.execute(f'DELETE FROM {t} WHERE user_id=?', (item_id,))
        conn.execute('DELETE FROM members WHERE id=?', (item_id,))
        conn.commit()
        if _current_user() == item_id:
            session['user_id'] = 1
        return jsonify({'ok': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/members/switch', methods=['POST'])
def switch_member():
    data = request.json
    uid = data.get('user_id')
    if uid is None:
        return jsonify({'ok': False, 'error': '缺少 user_id'}), 400
    row, conn, _ = _db_op('SELECT id FROM members WHERE id=?', (int(uid),), fetchone=True)
    if not row:
        return jsonify({'ok': False, 'error': '成员不存在'}), 404
    session['user_id'] = int(uid)
    return jsonify({'ok': True, 'user_id': int(uid)})

@app.route('/api/members/current', methods=['GET'])
def current_member():
    uid = _ensure_user()
    row, conn, _ = _db_op('SELECT * FROM members WHERE id=?', (uid,), fetchone=True)
    if row:
        return jsonify(dict(row))
    return jsonify({'id': 1, 'name': '本人', 'role': '本人'})


# ========== 饮食模板 ==========
@app.route('/api/meal-templates', methods=['GET'])
def list_meal_templates():
    rows, conn, _ = _db_op('SELECT * FROM meal_templates WHERE user_id=? ORDER BY id DESC', (_ensure_user(),), fetch=True)
    return jsonify([dict(r) for r in rows])


@app.route('/api/meal-templates', methods=['POST'])
def add_meal_template():
    data = request.json
    name = (data.get('name') or '').strip()
    meal = (data.get('meal') or '').strip()
    food = (data.get('food') or '').strip()
    if not name or not food:
        return jsonify({'ok': False, 'error': 'name 和 food 不能为空'}), 400
    _, conn, cur = _db_op(
        '''INSERT INTO meal_templates (user_id, name, meal, food, calories, eating_order)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (_ensure_user(), name, meal, food, data.get('calories', ''), data.get('eating_order', '')))
    new_id = cur.lastrowid
    return jsonify({'ok': True, 'id': new_id})


@app.route('/api/meal-templates/<int:item_id>', methods=['DELETE'])
def delete_meal_template(item_id):
    _, conn, _ = _db_op('DELETE FROM meal_templates WHERE user_id=? AND id=?', (_ensure_user(), item_id))
    return jsonify({'ok': True})


@app.route('/api/meal-templates/<int:item_id>', methods=['PUT'])
def update_meal_template(item_id):
    data = request.json
    name = (data.get('name') or '').strip()
    meal = (data.get('meal') or '').strip()
    food = (data.get('food') or '').strip()
    if not name or not food:
        return jsonify({'ok': False, 'error': 'name 和 food 不能为空'}), 400
    _, conn, _ = _db_op(
        '''UPDATE meal_templates SET name=?, meal=?, food=?, calories=?, eating_order=?
           WHERE user_id=? AND id=?''',
        (name, meal, food, data.get('calories', ''), data.get('eating_order', ''), _ensure_user(), item_id))
    return jsonify({'ok': True})


# ========== 数据备份与恢复 ==========
# 严格白名单：SQLite 不支持表名参数化，所有动态表名必须先经此校验，杜绝 SQL 注入
ALLOWED_TABLES = {'profile', 'goals', 'custom_drugs', 'meal_templates',
                  'diet', 'exercise', 'glucose', 'medication', 'followup', 'members'}


def _safe_table(name):
    if name not in ALLOWED_TABLES:
        raise ValueError(f'非法的表名: {name}')
    return name


@app.route('/api/backup', methods=['GET'])
def backup_data():
    """导出所有数据为 JSON"""
    backup = {}
    conn = get_db()
    try:
        for t in ALLOWED_TABLES:
            rows = conn.execute(f'SELECT * FROM {_safe_table(t)}').fetchall()
            backup[t] = [dict(r) for r in rows]
    except Exception:
        conn.rollback()
        raise
    return jsonify(backup)


@app.route('/api/restore', methods=['POST'])
def restore_data():
    """从 JSON 恢复所有数据（覆盖现有数据）"""
    data = request.json
    if not isinstance(data, dict):
        return jsonify({'ok': False, 'error': '无效的备份数据'}), 400
    conn = get_db()
    conn.execute('BEGIN IMMEDIATE')
    try:
        # 清空所有业务表（仅白名单内的表）
        for t in ALLOWED_TABLES - {'profile', 'goals', 'members'}:
            conn.execute(f'DELETE FROM {_safe_table(t)}')
        # 恢复数据
        for t, rows in data.items():
            if t not in ALLOWED_TABLES:
                continue  # 跳过非白名单键，防止注入/脏数据
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
                        'INSERT INTO custom_drugs (user_id, name, dose, time_period) VALUES (?, ?, ?, ?)',
                        (r.get('user_id', 1), r.get('name'), r.get('dose'), r.get('time_period')))
            elif t == 'meal_templates':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO meal_templates (user_id, name, meal, food, calories, eating_order)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (r.get('user_id', 1), r.get('name'), r.get('meal'), r.get('food'),
                         r.get('calories', ''), r.get('eating_order', '')))
            elif t == 'diet':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO diet (user_id, date, meal, food, calories, glucose, eating_order, note)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (r.get('user_id', 1), r.get('date'), r.get('meal'), r.get('food'),
                         r.get('calories', ''), r.get('glucose', ''),
                         r.get('eating_order', ''), r.get('note', '')))
            elif t == 'exercise':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO exercise
                           (user_id, date, type, duration, intensity, before_glucose, after_glucose,
                            sugar_carried, symptom, note)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (r.get('user_id', 1), r.get('date'), r.get('type'), r.get('duration'),
                         r.get('intensity', ''), r.get('before_glucose', ''),
                         r.get('after_glucose', ''), r.get('sugar_carried', ''),
                         r.get('symptom', ''), r.get('note', '')))
            elif t == 'glucose':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO glucose (user_id, date, time, type, value, note)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (r.get('user_id', 1), r.get('date'), r.get('time'), r.get('type'),
                         r.get('value'), r.get('note', '')))
            elif t == 'medication':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO medication
                           (user_id, date, time_detail, name, dose, time_period, side_effect, note)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (r.get('user_id', 1), r.get('date'), r.get('time_detail', ''),
                         r.get('name'), r.get('dose', ''),
                         r.get('time_period', ''), r.get('side_effect', '无'),
                         r.get('note', '')))
            elif t == 'followup':
                for r in rows:
                    conn.execute(
                        '''INSERT INTO followup (user_id, date, weight, waist, hba1c, note)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (r.get('user_id', 1), r.get('date'), r.get('weight', ''),
                         r.get('waist', ''), r.get('hba1c', ''),
                         r.get('note', '')))
            elif t == 'members':
                for r in rows:
                    conn.execute(
                        'INSERT OR IGNORE INTO members (id, name, role) VALUES (?, ?, ?)',
                        (r.get('id', 1), r.get('name', '本人'), r.get('role', '本人')))
        conn.commit()
        return jsonify({'ok': True})
    except Exception as e:
        conn.rollback()
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
