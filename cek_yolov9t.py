from ultralytics import YOLO

model = YOLO("models/yolov9t_best.pt")

results = model.predict(
    "static/uploads/kertas.jpeg",
    save=True,
    conf=0.01
)

print(results[0].boxes)
print("Jumlah:", len(results[0].boxes))