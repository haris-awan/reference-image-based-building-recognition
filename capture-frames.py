import os, time
from maix import camera, display, image, app

BATCH = "neg"          # use "pos" at NSTP, then change to "neg" for other buildings and scenes
folder = f"/root/captures/{BATCH}"
os.makedirs(folder, exist_ok=True)

cam = camera.Camera(1280, 720)
disp = display.Display()
n, last = 0, time.time()

while not app.need_exit():
    img = cam.read()
    if time.time() - last >= 1.0:
        img.save(f"{folder}/f_{n:04d}.jpg")
        n += 1; last = time.time()
    img.draw_string(2, 2, f"{BATCH}: {n} saved", color=image.COLOR_RED)
    disp.show(img)