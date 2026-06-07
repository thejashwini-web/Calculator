from flask import Flask, request, jsonify, render_template, Response
import math, json, os, random
from datetime import datetime

try:
    import requests as req_lib
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

app = Flask(__name__)
HISTORY_FILE = "history.json"

# ─────────────────────────────────────────────
#  HISTORY
# ─────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def record(expr, result):
    h = load_history()
    h.append({"expression": expr, "result": result,
               "time": datetime.now().strftime("%H:%M:%S")})
    save_history(h)

# ─────────────────────────────────────────────
#  BASIC + SCIENTIFIC MATH
# ─────────────────────────────────────────────
def calculate(op, a, b=None):
    # Basic
    if op == "add":       return a + b
    if op == "subtract":  return a - b
    if op == "multiply":  return a * b
    if op == "divide":
        if b == 0: raise ValueError("Cannot divide by zero!")
        return a / b
    if op == "power":     return a ** b
    if op == "modulus":
        if b == 0: raise ValueError("Cannot modulus by zero!")
        return a % b
    if op == "floor":
        if b == 0: raise ValueError("Cannot floor divide by zero!")
        return a // b
    if op == "sqrt":
        if a < 0: raise ValueError("Cannot square root a negative number!")
        return math.sqrt(a)
    if op == "abs":       return abs(a)

    # Scientific
    if op == "sin":        return round(math.sin(math.radians(a)), 10)
    if op == "cos":        return round(math.cos(math.radians(a)), 10)
    if op == "tan":
        if a % 180 == 90:  raise ValueError("tan(90°) is undefined!")
        return round(math.tan(math.radians(a)), 10)
    if op == "log":
        if a <= 0: raise ValueError("log requires a positive number!")
        return math.log10(a)
    if op == "ln":
        if a <= 0: raise ValueError("ln requires a positive number!")
        return math.log(a)
    if op == "factorial":
        if a < 0 or a != int(a): raise ValueError("Factorial needs a non-negative integer!")
        return math.factorial(int(a))
    if op == "deg_to_rad": return math.radians(a)
    if op == "rad_to_deg": return math.degrees(a)

    # ── NEW MATH FEATURES ──
    if op == "square":     return a ** 2
    if op == "cube":       return a ** 3
    if op == "cube_root":  return math.copysign(abs(a) ** (1/3), a)
    if op == "reciprocal":
        if a == 0: raise ValueError("Cannot take reciprocal of zero!")
        return 1 / a
    if op == "exp":        return math.e ** a   # eˣ

    raise ValueError(f"Unknown operation: {op}")

# ─────────────────────────────────────────────
#  ADVANCED MATH (two numbers)
# ─────────────────────────────────────────────
def gcd(a, b):
    a, b = int(abs(a)), int(abs(b))
    if a == 0 and b == 0: raise ValueError("GCD(0,0) is undefined!")
    return math.gcd(a, b)

def lcm(a, b):
    a, b = int(abs(a)), int(abs(b))
    if a == 0 or b == 0: return 0
    return abs(a * b) // math.gcd(a, b)

def is_prime(n):
    n = int(n)
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

def permutation(n, r):
    n, r = int(n), int(r)
    if r > n: raise ValueError("r cannot be greater than n!")
    if n < 0 or r < 0: raise ValueError("n and r must be non-negative!")
    return math.factorial(n) // math.factorial(n - r)

def combination(n, r):
    n, r = int(n), int(r)
    if r > n: raise ValueError("r cannot be greater than n!")
    if n < 0 or r < 0: raise ValueError("n and r must be non-negative!")
    return math.comb(n, r)

# ─────────────────────────────────────────────
#  UNIT CONVERSIONS
# ─────────────────────────────────────────────
UNIT_CONVERSIONS = {
    "km_to_miles": lambda x: x * 0.621371,
    "miles_to_km": lambda x: x * 1.60934,
    "m_to_ft":     lambda x: x * 3.28084,
    "ft_to_m":     lambda x: x / 3.28084,
    "cm_to_inch":  lambda x: x * 0.393701,
    "inch_to_cm":  lambda x: x / 0.393701,
    "kg_to_lb":    lambda x: x * 2.20462,
    "lb_to_kg":    lambda x: x / 2.20462,
    "g_to_oz":     lambda x: x * 0.035274,
    "oz_to_g":     lambda x: x / 0.035274,
    "c_to_f":      lambda x: (x * 9/5) + 32,
    "f_to_c":      lambda x: (x - 32) * 5/9,
    "c_to_k":      lambda x: x + 273.15,
    "k_to_c":      lambda x: x - 273.15,
    "kmh_to_mph":  lambda x: x * 0.621371,
    "mph_to_kmh":  lambda x: x * 1.60934,
    "ms_to_kmh":   lambda x: x * 3.6,
    "kmh_to_ms":   lambda x: x / 3.6,
    "sqm_to_sqft": lambda x: x * 10.7639,
    "sqft_to_sqm": lambda x: x / 10.7639,
    "liter_to_gal":lambda x: x * 0.264172,
    "gal_to_liter":lambda x: x / 0.264172,
    "ml_to_floz":  lambda x: x * 0.033814,
    "floz_to_ml":  lambda x: x / 0.033814,
    "mb_to_gb":    lambda x: x / 1024,
    "gb_to_mb":    lambda x: x * 1024,
    "gb_to_tb":    lambda x: x / 1024,
    "tb_to_gb":    lambda x: x * 1024,
}

# ─────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate_route():
    data = request.get_json()
    op   = data.get("operation")
    try:
        a = float(data.get("a", 0))
        b = float(data.get("b", 0)) if data.get("b") is not None else None
        result  = calculate(op, a, b)
        symbols = {"add":"+","subtract":"−","multiply":"×","divide":"÷",
                   "power":"^","modulus":"%","floor":"//"}
        singles = ["sqrt","abs","sin","cos","tan","log","ln","factorial",
                   "deg_to_rad","rad_to_deg","square","cube","cube_root",
                   "reciprocal","exp"]
        expr = f"{op}({a})" if op in singles else f"{a} {symbols.get(op,op)} {b}"
        result = int(result) if isinstance(result, float) and result.is_integer() else round(result, 10)
        record(expr, result)
        return jsonify({"result": result, "expression": expr})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/math/gcd", methods=["POST"])
def gcd_route():
    data = request.get_json()
    try:
        a, b = float(data["a"]), float(data["b"])
        result = gcd(a, b)
        expr = f"GCD({int(a)}, {int(b)})"
        record(expr, result)
        return jsonify({"result": result, "expression": expr})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/math/lcm", methods=["POST"])
def lcm_route():
    data = request.get_json()
    try:
        a, b = float(data["a"]), float(data["b"])
        result = lcm(a, b)
        expr = f"LCM({int(a)}, {int(b)})"
        record(expr, result)
        return jsonify({"result": result, "expression": expr})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/math/prime", methods=["POST"])
def prime_route():
    data = request.get_json()
    try:
        n      = float(data["n"])
        result = is_prime(n)
        expr   = f"isPrime({int(n)})"
        record(expr, "Yes" if result else "No")
        return jsonify({"result": result, "label": "Yes ✅" if result else "No ❌"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/math/random", methods=["POST"])
def random_route():
    data = request.get_json()
    try:
        mn  = int(data.get("min", 1))
        mx  = int(data.get("max", 100))
        dec = int(data.get("decimals", 0))
        if mn >= mx: raise ValueError("Min must be less than Max!")
        result = round(random.uniform(mn, mx), dec) if dec > 0 else random.randint(mn, mx)
        expr   = f"random({mn}, {mx})"
        record(expr, result)
        return jsonify({"result": result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/math/permutation", methods=["POST"])
def perm_route():
    data = request.get_json()
    try:
        n, r   = float(data["n"]), float(data["r"])
        result = permutation(n, r)
        expr   = f"P({int(n)},{int(r)})"
        record(expr, result)
        return jsonify({"result": result, "expression": expr})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/math/combination", methods=["POST"])
def comb_route():
    data = request.get_json()
    try:
        n, r   = float(data["n"]), float(data["r"])
        result = combination(n, r)
        expr   = f"C({int(n)},{int(r)})"
        record(expr, result)
        return jsonify({"result": result, "expression": expr})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/convert/unit", methods=["POST"])
def unit_convert():
    data = request.get_json()
    try:
        value  = float(data.get("value", 0))
        fn     = UNIT_CONVERSIONS.get(data.get("conversion"))
        if not fn: return jsonify({"error": "Unknown conversion"}), 400
        return jsonify({"result": round(fn(value), 6)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/convert/currency", methods=["POST"])
def currency_convert():
    if not HAS_REQUESTS:
        return jsonify({"error": "requests library not installed"}), 400
    data = request.get_json()
    try:
        amount   = float(data.get("amount", 1))
        from_cur = data.get("from", "USD")
        to_cur   = data.get("to",   "EUR")
        url      = f"https://api.exchangerate-api.com/v4/latest/{from_cur.upper()}"
        res      = req_lib.get(url, timeout=5)
        rates    = res.json()
        rate     = rates["rates"].get(to_cur.upper())
        if not rate: raise ValueError(f"Unknown currency: {to_cur}")
        result   = round(amount * rate, 4)
        return jsonify({"result": result, "date": rates.get("date","")})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/history", methods=["GET"])
def get_history():
    return jsonify(load_history())

@app.route("/history", methods=["DELETE"])
def clear_history():
    save_history([])
    return jsonify({"message": "History cleared"})

@app.route("/history/download", methods=["GET"])
def download_history():
    history = load_history()
    lines   = ["Calculator History", "=" * 40]
    for i, h in enumerate(history, 1):
        lines.append(f"{i}. [{h.get('time','')}]  {h['expression']} = {h['result']}")
    return Response("\n".join(lines), mimetype="text/plain",
                    headers={"Content-Disposition": "attachment; filename=history.txt"})

@app.route("/history/<int:index>", methods=["DELETE"])
def delete_one_history(index):
    history = load_history()
    if 0 <= index < len(history):
        history.pop(index)
        save_history(history)
        return jsonify({"message": "Deleted"})
    return jsonify({"error": "Invalid index"}), 400
@app.route('/sw.js')
def service_worker():
    sw_content = """
const CACHE = 'calculator-v1';
const FILES = [
  '/',
  '/static/manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(FILES))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(cached => {
      return cached || fetch(e.request).then(response => {
        return caches.open(CACHE).then(cache => {
          cache.put(e.request, response.clone());
          return response;
        });
      }).catch(() => cached);
    })
  );
});
"""
    from flask import Response
    return Response(sw_content, mimetype='application/javascript')


@app.route('/manifest.json')
def manifest():
    import json
    data = {
        "name": "Calculator",
        "short_name": "Calculator",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#f0f2f5",
        "theme_color": "#e67e22",
        "icons": [
            {
                "src": "https://img.icons8.com/fluency/192/calculator.png",
                "sizes": "192x192",
                "type": "image/png"
            }
        ]
    }
    return jsonify(data)
if __name__ == "__main__":
    app.run(debug=True)
