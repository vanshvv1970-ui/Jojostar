import os
import io
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import urllib.request

app = Flask(__name__)
CORS(app)

MODEL_FILE = 'inswapper_128.onnx'
if not os.path.exists(MODEL_FILE):
    print("Downloading Inswapper Model...")
    url = "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx"
    urllib.request.urlretrieve(url, MODEL_FILE)

# Memory Optimization: Use 'buffalo_sc' (Small/Compact) for free tier RAM limits
print("Initializing InsightFace CPU Engine...")
face_app = FaceAnalysis(name='buffalo_sc', providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(320, 320))
swapper = insightface.model_zoo.get_model(MODEL_FILE, download=False)
print("Engine Online!")

@app.route('/')
def health():
    return jsonify({"status": "API is online!"})

@app.route('/swap', methods=['POST'])
def swap_face():
    try:
        if 'source' not in request.files or 'target' not in request.files:
            return jsonify({'error': 'Missing source or target file'}), 400

        src_bytes = request.files['source'].read()
        tgt_bytes = request.files['target'].read()

        src_img = cv2.imdecode(np.frombuffer(src_bytes, np.uint8), cv2.IMREAD_COLOR)
        tgt_img = cv2.imdecode(np.frombuffer(tgt_bytes, np.uint8), cv2.IMREAD_COLOR)

        src_faces = face_app.get(src_img)
        tgt_faces = face_app.get(tgt_img)

        if not src_faces or not tgt_faces:
            return jsonify({'error': 'No face detected'}), 400

        swapped_img = swapper.get(tgt_img, tgt_faces[0], src_faces[0], paste_back=True)

        # Subtle detail sharpening
        gaussian = cv2.GaussianBlur(swapped_img, (0, 0), 2.0)
        final_output = cv2.addWeighted(swapped_img, 1.4, gaussian, -0.4, 0)

        _, buffer = cv2.imencode('.jpg', final_output, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        return send_file(io.BytesIO(buffer), mimetype='image/jpeg')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
        
