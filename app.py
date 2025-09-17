from flask import Flask, request, send_file, jsonify, render_template
import service
from pydantic import ValidationError
from DTO import requestDTO

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET"])
def get_parameter():
    defaults = service.get_parameter()
    return render_template("index.html", defaults=defaults)

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("images")
    slot = request.form.get("slot", type=int)
    try:
        paths = service.handle_upload(files, slot)
        return jsonify({"uploaded_paths": paths}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
    
@app.route("/clear_slot", methods=["POST"])
def clear_slot():
    slot = request.form.get("slot", type=int)
    try:
        service.clear_slot(slot)
        return jsonify({"message": f"Slot {slot} cleared"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500
    
@app.route("/generate", methods=["POST"])
def generate():
    try:
        dto = requestDTO(**request.json)  # validate input
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return jsonify({"error": errors}), 400

    try:
        result_path = service.generate_and_show(dto)
        return jsonify({"result_path": result_path}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.route("/result", methods=["GET"])
def result():
    try:
        result_path = service.get_result()
        return send_file(result_path, mimetype="image/png", as_attachment=False)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

@app.route("/download", methods=["GET"])
def download():
    try:
        result_path = service.get_result()
        return send_file(result_path, mimetype="image/png", as_attachment=True)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)