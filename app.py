from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import google.generativeai as genai
import io
import os

# ✅ Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))  # Use Render Env Var
model = genai.GenerativeModel("models/gemini-1.5-flash")

app = Flask(__name__)
code_storage = {}

@app.route('/')
def home():
    return "✅ AI Code Analyzer is running!"

@app.route('/upload_chunk', methods=['POST'])
def upload_chunk():
    try:
        image_file = request.files['image']
        session_id = request.form['session_id']
        img = Image.open(image_file.stream)
        code = pytesseract.image_to_string(img)

        if session_id not in code_storage:
            code_storage[session_id] = []
        code_storage[session_id].append(code)

        return jsonify({"status": "chunk received", "lines": len(code.splitlines())})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_merged_code', methods=['POST'])
def get_merged_code():
    session_id = request.json.get('session_id')
    if session_id not in code_storage:
        return jsonify({"error": "No code found"}), 404
    full_code = "\n".join(code_storage[session_id])
    return jsonify({"code": full_code})

@app.route('/reset_session', methods=['POST'])
def reset_session():
    session_id = request.json.get('session_id')
    if session_id in code_storage:
        del code_storage[session_id]
    return jsonify({"status": "session reset"})

@app.route('/explain_code', methods=['POST'])
def explain_code():
    code = request.json.get("code")
    prompt = f"Explain this code line-by-line in beginner-friendly way:\n\n{code}"
    try:
        response = model.generate_content(prompt)
        return jsonify({"explanation": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug_code', methods=['POST'])
def debug_code():
    code = request.json.get("code")
    prompt = f"Find bugs, infinite loops, or TLE risks in this code. Return the issues in **red** color using markdown `**` and rest in *blue* using `*`. Suggest fixes too:\n\n{code}"
    try:
        response = model.generate_content(prompt)
        return jsonify({"debug_report": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/heatmap', methods=['POST'])
def heatmap():
    code = request.json.get("code")
    prompt = f"Give a performance heatmap for this code. Highlight bottlenecks as `**RED**` and optimized parts as `*BLUE*`:\n\n{code}"
    try:
        response = model.generate_content(prompt)
        return jsonify({"heatmap": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask():
    code = request.json.get("code")
    question = request.json.get("question")
    prompt = f"Given this code:\n{code}\n\nAnswer this question: {question}"
    try:
        response = model.generate_content(prompt)
        return jsonify({"answer": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compile', methods=['POST'])
def compile_code():
    code = request.json.get("code")
    return jsonify({"output": f"✅ Code received. Simulated execution. Length: {len(code)} characters."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render default port fallback
    app.run(host="0.0.0.0", port=port)
