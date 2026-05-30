from ultralytics import YOLO
import cv2

ally_model = YOLO("best.pt")

enemy_model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Could not open camera")
    exit()

def overlap(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_area = max(0, xB - xA) * max(0, yB - yA)

    boxA_area = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxB_area = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    if boxA_area == 0 or boxB_area == 0:
        return 0

    return inter_area / min(boxA_area, boxB_area)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    ally_boxes = []

    # Detect Royal Jordanian livery
    ally_results = ally_model(frame, conf=0.9)

    for result in ally_results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])

            ally_boxes.append([x1, y1, x2, y2])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
            cv2.putText(
                frame,
                f"Ally {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

    # Detect general airplanes
    enemy_results = enemy_model(frame, conf=0.4)

    for result in enemy_results:
        for box in result.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            # COCO class 4 = airplane
            if cls_id != 4:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            enemy_box = [x1, y1, x2, y2]

            # If it overlaps with Ally, don't draw Enemy box
            is_ally = False
            for ally_box in ally_boxes:
                if overlap(enemy_box, ally_box) > 0.5:
                    is_ally = True
                    break

            if not is_ally:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(
                    frame,
                    f"Enemy {conf:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

    cv2.imshow("Ally / Enemy Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()