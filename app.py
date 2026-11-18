from flask import Flask, render_template, request, redirect
from ultralytics import YOLO
import os
import cv2
import mysql.connector

app = Flask(__name__)

# =========================
# KONEKSI DATABASE
# =========================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sampah"
)

cursor = db.cursor()

# =========================
# FOLDER UPLOAD
# =========================
UPLOAD_FOLDER = "static/uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# =========================
# LOAD MODEL
# =========================
model_v8 = YOLO("models/yolov8n_best.pt", task="detect")
# model_v9 = YOLO("models/yolov9_100_best.pt", task="detect")
model_v9 = YOLO("models/yolov9t_best.pt", task="detect")
# model_v8 = YOLO("models/yolov8n.onnx", task="detect")
# model_v9 = YOLO("models/yolov9t.onnx", task="detect")
# =========================
# HOME
# =========================
@app.route('/')
def home():

    return render_template(
        'index.html',
        image_v8=None,
        image_v9=None,
        detections_v8=[],
        detections_v9=[]
    )

# =========================
# HISTORY
# =========================
@app.route('/history')
def history():

    sql = """
    SELECT *
    FROM detections
    ORDER BY id DESC
    """

    cursor.execute(sql)
    data = cursor.fetchall()

    return render_template(
        'history.html',
        data=data
    )

# =========================
# DELETE HISTORY
# =========================
@app.route('/delete', methods=['POST'])
def delete():

    selected_ids = request.form.getlist('selected_ids')

    if selected_ids:

        for id in selected_ids:

            sql = """
            DELETE FROM detections
            WHERE id = %s
            """

            cursor.execute(sql, (id,))

        db.commit()

    return redirect('/history')

# =========================
# UPLOAD & DETEKSI
# =========================
@app.route('/upload', methods=['POST'])
def upload():

    if 'image' not in request.files:
        return "Tidak ada file"

    file = request.files['image']

    if file.filename == '':
        return "File kosong"

    # =========================
    # SIMPAN FILE
    # =========================
    filepath = os.path.join(
        app.config['UPLOAD_FOLDER'],
        file.filename
    )

    file.save(filepath)

    # =========================
    # YOLOv8
    # =========================
    results_v8 = model_v8(filepath)
#     results_v8 = model_v8.predict(
#     filepath,
#     conf=0.10
# )
    print("\n===== YOLOV8 =====")
    print(results_v8[0].boxes)
    print("Jumlah box:", len(results_v8[0].boxes))
    print("Nama kelas:", model_v8.names)

    detections_v8 = []

    for box in results_v8[0].boxes:

        conf = float(box.conf[0])
        cls = int(box.cls[0])

        detections_v8.append({
            "confidence": round(conf, 2),
            "class": model_v8.names[cls]
        })

    # =========================
    # YOLOv9
    # =========================
    results_v9 = model_v9(filepath)
#     results_v9 = model_v9.predict(
#     filepath,
#     conf=0.10
# )
    print("\n===== YOLOV9 =====")
    print(results_v9[0].boxes)
    print("Jumlah box:", len(results_v9[0].boxes))
    print("Nama kelas:", model_v9.names)

    detections_v9 = []

    for box in results_v9[0].boxes:

        conf = float(box.conf[0])
        cls = int(box.cls[0])

        detections_v9.append({
            "confidence": round(conf, 2),
            "class": model_v9.names[cls]
        })

    # =========================
    # SIMPAN GAMBAR YOLOv8
    # =========================
    result_image_v8 = results_v8[0].plot()

    output_v8 = os.path.join(
        app.config['UPLOAD_FOLDER'],
        "v8_" + file.filename
    )

    cv2.imwrite(output_v8, result_image_v8)

    # =========================
    # SIMPAN GAMBAR YOLOv9
    # =========================
    result_image_v9 = results_v9[0].plot()

    output_v9 = os.path.join(
        app.config['UPLOAD_FOLDER'],
        "v9_" + file.filename
    )

    cv2.imwrite(output_v9, result_image_v9)

    # =========================
    # AMBIL DATA UNTUK DATABASE
    # =========================
    conf_v8 = detections_v8[0]["confidence"] if detections_v8 else 0
    conf_v9 = detections_v9[0]["confidence"] if detections_v9 else 0

    class_v8 = detections_v8[0]["class"] if detections_v8 else "-"
    class_v9 = detections_v9[0]["class"] if detections_v9 else "-"

    # =========================
    # SIMPAN DATABASE
    # =========================
    sql = """
    INSERT INTO detections
    (
        filename,
        confidence_v8,
        confidence_v9,
        class_v8,
        class_v9
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        file.filename,
        conf_v8,
        conf_v9,
        class_v8,
        class_v9
    )

    cursor.execute(sql, values)
    db.commit()

    print("DATA BERHASIL DISIMPAN")

    # =========================
    # TAMPILKAN HASIL
    # =========================
    return render_template(
    'index.html',
    image_v8=output_v8,
    image_v9=output_v9,
    detections_v8=detections_v8,
    detections_v9=detections_v9
)

# =========================
# RUN FLASK
# =========================
if __name__ == '__main__':
    app.run(debug=True)



# from flask import Flask, render_template, request, redirect
# from ultralytics import YOLO
# import os
# import cv2
# import mysql.connector

# app = Flask(__name__)

# # =========================
# # KONEKSI DATABASE
# # =========================
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="sampah"
# )

# cursor = db.cursor()

# # =========================
# # FOLDER UPLOAD
# # =========================
# UPLOAD_FOLDER = "static/uploads"

# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# # =========================
# # LOAD MODEL
# # =========================
# model_v8 = YOLO("models/yolov8n.onnx", task="detect")
# model_v9 = YOLO("models/yolov9t.onnx", task="detect")


# # =========================
# # HOME
# # =========================
# @app.route('/')
# def home():

#     return render_template(
#         'index.html',
#         image_v8=None,
#         image_v9=None,
#         detections_v8=[],
#         detections_v9=[]
#     )


# # =========================
# # HISTORY
# # =========================
# @app.route('/history')
# def history():

#     sql = """
#     SELECT *
#     FROM detections
#     ORDER BY id DESC
#     """

#     cursor.execute(sql)
#     data = cursor.fetchall()

#     return render_template(
#         'history.html',
#         data=data
#     )


# # =========================
# # DELETE HISTORY
# # =========================
# @app.route('/delete', methods=['POST'])
# def delete():

#     selected_ids = request.form.getlist('selected_ids')

#     if selected_ids:

#         for id in selected_ids:

#             sql = """
#             DELETE FROM detections
#             WHERE id=%s
#             """

#             cursor.execute(sql, (id,))

#         db.commit()

#     return redirect('/history')


# # =========================
# # UPLOAD & DETEKSI
# # =========================
# @app.route('/upload', methods=['POST'])
# def upload():

#     if 'image' not in request.files:
#         return "Tidak ada file"

#     file = request.files['image']

#     if file.filename == '':
#         return "File kosong"

#     # =========================
#     # SIMPAN FILE
#     # =========================
#     filepath = os.path.join(
#         app.config["UPLOAD_FOLDER"],
#         file.filename
#     )

#     file.save(filepath)

#     # =========================
#     # DETEKSI YOLOv8
#     # =========================
#     results_v8 = model_v8.predict(
#         filepath,
#         conf=0.10
#     )

#     detections_v8 = []

#     print("\n===== HASIL YOLOv8 =====")
#     print("Jumlah box:", len(results_v8[0].boxes))

#     for box in results_v8[0].boxes:

#         conf = float(box.conf[0])
#         cls = int(box.cls[0])

#         print(
#             model_v8.names[cls],
#             round(conf, 2)
#         )

#         detections_v8.append({
#             "confidence": round(conf, 2),
#             "class": model_v8.names[cls]
#         })

#     # =========================
#     # DETEKSI YOLOv9
#     # =========================
#     results_v9 = model_v9.predict(
#         filepath,
#         conf=0.10
#     )

#     detections_v9 = []

#     print("\n===== HASIL YOLOv9 =====")
#     print("Jumlah box:", len(results_v9[0].boxes))

#     for box in results_v9[0].boxes:

#         conf = float(box.conf[0])
#         cls = int(box.cls[0])

#         print(
#             model_v9.names[cls],
#             round(conf, 2)
#         )

#         detections_v9.append({
#             "confidence": round(conf, 2),
#             "class": model_v9.names[cls]
#         })

#     # =========================
#     # SIMPAN HASIL V8
#     # =========================
#     result_image_v8 = results_v8[0].plot()

#     output_v8 = os.path.join(
#         app.config["UPLOAD_FOLDER"],
#         "v8_" + file.filename
#     )

#     cv2.imwrite(
#         output_v8,
#         result_image_v8
#     )

#     # =========================
#     # SIMPAN HASIL V9
#     # =========================
#     result_image_v9 = results_v9[0].plot()

#     output_v9 = os.path.join(
#         app.config["UPLOAD_FOLDER"],
#         "v9_" + file.filename
#     )

#     cv2.imwrite(
#         output_v9,
#         result_image_v9
#     )

#     # =========================
#     # DATA DATABASE
#     # =========================
#     conf_v8 = (
#         detections_v8[0]["confidence"]
#         if detections_v8 else 0
#     )

#     conf_v9 = (
#         detections_v9[0]["confidence"]
#         if detections_v9 else 0
#     )

#     class_v8 = (
#         detections_v8[0]["class"]
#         if detections_v8 else "-"
#     )

#     class_v9 = (
#         detections_v9[0]["class"]
#         if detections_v9 else "-"
#     )

#     # =========================
#     # INSERT DATABASE
#     # =========================
#     sql = """
#     INSERT INTO detections
#     (
#         filename,
#         confidence_v8,
#         confidence_v9,
#         class_v8,
#         class_v9
#     )
#     VALUES
#     (
#         %s,%s,%s,%s,%s
#     )
#     """

#     values = (
#         file.filename,
#         conf_v8,
#         conf_v9,
#         class_v8,
#         class_v9
#     )

#     cursor.execute(sql, values)
#     db.commit()

#     print("\nDATA BERHASIL DISIMPAN\n")

#     return render_template(
#         "index.html",
#         image_v8=output_v8,
#         image_v9=output_v9,
#         detections_v8=detections_v8,
#         detections_v9=detections_v9
#     )


# # =========================
# # RUN
# # =========================
# if __name__ == "__main__":
#     app.run(
#         debug=True
#     )