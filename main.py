import cv2
import time
from emailing import send_email

video = cv2.VideoCapture(0)
time.sleep(2)

first_frame = None
status_list = []
# Wait a few seconds to allow the environment to stabilize
for _ in range(5):
    check, frame = video.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (31, 31), 0)
    time.sleep(0.5)  # Let the camera stabilize
first_frame = gray_frame  # Use the last stable frame

while True:
    status = 0
    check, frame = video.read()
    cv2.imshow("My video", frame)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (31, 31), 0)

    if first_frame is None:
        first_frame = gray_frame_gau
        continue  # Skip the rest of the loop to avoid using the initial unstable frame

    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
    thres_frame = cv2.threshold(delta_frame, 50, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thres_frame, None, iterations=2)

    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        else:
            x, y, w, h = cv2.boundingRect(contour)
            rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (105, 255, 0), 2)
            if rectangle.any():
                status = 1

    status_list.append(status)
    status_list = status_list[-2:]
    if status_list[0] == 1 and status_list[1] == 0:
        send_email()
    print(status_list)

    cv2.imshow("dil", dil_frame)
    cv2.imshow("tht", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break

video.release()
