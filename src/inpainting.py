import cv2
import numpy as np


def inpaint_region(image, mask, method="telea"):
    if method == "telea":
        flags = cv2.INPAINT_TELEA
    else:
        flags = cv2.INPAINT_NS
    result = cv2.inpaint(image, mask, 3, flags)
    return result


def auto_detect_foreground(image):
    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (21, 21), 0)
    diff = cv2.absdiff(gray, blurred)
    _, fg_mask = cv2.threshold(diff, 12, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, kernel, iterations=2)
    fg_mask = cv2.bitwise_or(fg_mask, edges)

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    min_area = max(200, h * w * 0.0003)
    max_area = h * w * 0.35

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            cv2.drawContours(mask, [cnt], -1, 255, -1)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
    mask = cv2.dilate(mask, kernel, iterations=2)

    return mask


def inpaint_auto(image):
    mask = auto_detect_foreground(image)
    has_content = cv2.countNonZero(mask) > 0
    if has_content:
        result = inpaint_region(image, mask)
    else:
        result = image.copy()
    return result, mask


def inpaint_manual(image, x1, y1, x2, y2):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    mask = cv2.dilate(mask, kernel, iterations=1)
    result = inpaint_region(image, mask)
    return result, mask
