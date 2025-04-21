import keyinput
import cv2
import mediapipe as mp
import time

mp_dr = mp.solutions.drawing_utils
mphands = mp.solutions.hands
cap = cv2.VideoCapture(0)
hands = mphands.Hands()

# Function to detect if hand is closed
def is_closed(hand_landmarks):
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    closed = 0
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[pip].y:
            closed += 1
    return closed >= 3

while True:
    rt, video = cap.read()
    video = cv2.cvtColor(video, cv2.COLOR_BGR2RGB)
    results = hands.process(video)
    video = cv2.cvtColor(video, cv2.COLOR_RGB2BGR)
    videoHeight, videoWidth, _ = video.shape
    co = []
    hand_landmarks_list = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_dr.draw_landmarks(video, hand_landmarks, mphands.HAND_CONNECTIONS)
            hand_landmarks_list.append(hand_landmarks)
            for point in mphands.HandLandmark:
                if str(point) == "HandLandmark.WRIST":
                    normalizedLandmark = hand_landmarks.landmark[point]
                    pixelCoordinatesLandmark = mp_dr._normalized_to_pixel_coordinates(
                        normalizedLandmark.x, normalizedLandmark.y, videoWidth, videoHeight
                    )
                    try:
                        co.append(list(pixelCoordinatesLandmark))
                    except:
                        continue

    if len(co) == 2:
        # Gesture-based forward/backward control
        hand1_closed = is_closed(hand_landmarks_list[0])
        hand2_closed = is_closed(hand_landmarks_list[1])

        if hand1_closed and hand2_closed:
            print("Rolling")
            keyinput.press_key('s')
            keyinput.release_key('w')
            time.sleep(0.7)
            
        elif hand1_closed or hand2_closed:
            print("Jumping")
            keyinput.press_key('w')
            keyinput.release_key('s')
            time.sleep(0.7)

        else:
            keyinput.release_key('w')
            keyinput.release_key('s')

        xm, ym = (co[0][0] + co[1][0]) / 2, (co[0][1] + co[1][1]) / 2
        radius = 150
        try:
            m = (co[1][1] - co[0][1]) / (co[1][0] - co[0][0])
        except:
            continue
        x1, y1 = co[0]
        x2, y2 = co[1]

        a = 1 + m ** 2
        b = -2 * xm - 2 * x1 * (m ** 2) + 2 * m * y1 - 2 * m * ym
        c = xm ** 2 + (m ** 2) * (x1 ** 2) + y1 ** 2 + ym ** 2 - 2 * y1 * ym - 2 * y1 * x1 * m + 2 * m * ym * x1 - 22500
        xa = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        xb = (-b - (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)
        ya = m * (xa - x1) + y1
        yb = m * (xb - x1) + y1

        if m != 0:
            ap = 1 + ((-1 / m) ** 2)
            bp = -2 * xm - 2 * xm * ((-1 / m) ** 2) + 2 * (-1 / m) * ym - 2 * (-1 / m) * ym
            cp = xm ** 2 + ((-1 / m) ** 2) * (xm ** 2) + ym ** 2 + ym ** 2 - 2 * ym * ym - 2 * ym * xm * (-1 / m) + 2 * (-1 / m) * ym * xm - 22500
            try:
                xap = (-bp + (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
                xbp = (-bp - (bp ** 2 - 4 * ap * cp) ** 0.5) / (2 * ap)
                yap = (-1 / m) * (xap - xm) + ym
                ybp = (-1 / m) * (xbp - xm) + ym
            except:
                continue

        cv2.circle(video, (int(xm), int(ym)), 150, (195, 255, 62), 15)
        cv2.line(video, (int(xa), int(ya)), (int(xb), int(yb)), (195, 255, 62), 20)

        if x1 > x2 and y1 > y2 and y1 - y2 > 65:
            print("Turn left.")
            keyinput.release_key('s')
            keyinput.release_key('d')
            keyinput.press_key('a')
            time.sleep(0.7)

            cv2.line(video, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)
        elif x2 > x1 and y2 > y1 and y2 - y1 > 65:
            print("Turn left.")
            keyinput.release_key('s')
            keyinput.release_key('d')
            keyinput.press_key('a')
            time.sleep(0.7)

            cv2.line(video, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)
        elif x1 > x2 and y2 > y1 and y2 - y1 > 65:
            print("Turn right.")
            keyinput.release_key('s')
            keyinput.release_key('a')
            keyinput.press_key('d')
            time.sleep(0.7)
            cv2.line(video, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)
        elif x2 > x1 and y1 > y2 and y1 - y2 > 65:
            print("Turn right.")
            keyinput.release_key('s')
            keyinput.release_key('a')
            keyinput.press_key('d')
            time.sleep(0.7)
            cv2.line(video, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)
        else:
            # print("keeping straight")
            keyinput.release_key('s')
            keyinput.release_key('a')
            keyinput.release_key('d')
            keyinput.release_key('w')
            if ybp > yap:
                cv2.line(video, (int(xbp), int(ybp)), (int(xm), int(ym)), (195, 255, 62), 20)
            else:
                cv2.line(video, (int(xap), int(yap)), (int(xm), int(ym)), (195, 255, 62), 20)

    # if len(co) == 1:
    #     print("keeping back")
    #     keyinput.release_key('a')
    #     keyinput.release_key('d')
    #     keyinput.release_key('s')
    #     keyinput.press_key('w')
    #     time.sleep(0.7)

    cv2.imshow("Hand detection frame", cv2.flip(video, 1))
    if cv2.waitKey(1) == ord('q'):
        break
