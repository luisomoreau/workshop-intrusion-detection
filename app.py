import cv2
import os
import time
import numpy as np
from flask import Flask, render_template, Response
from edge_impulse_linux.image import ImageImpulseRunner

app = Flask(__name__, static_folder='templates/assets')

runner = None
countPeople = 0
inferenceSpeed = 0
videoCaptureDeviceId = int(0) # use 0 for web camera
    
def now():
    return round(time.time() * 1000)

def gen_frames():  # generate frame by frame from camera
    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, 'modelfile.eim')
    print('MODEL: ' + modelfile)
    global countPeople
    global inferenceSpeed

    while True:
        
        with ImageImpulseRunner(modelfile) as runner:
            try:
                model_info = runner.init()
                print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
                labels = model_info['model_parameters']['labels']

                camera = cv2.VideoCapture(videoCaptureDeviceId)
                ret = camera.read()[0]
                if ret:
                    backendName = "dummy" #backendName = camera.getBackendName() this is fixed in opencv-python==4.5.2.52
                    w = camera.get(3)
                    h = camera.get(4)
                    print("Camera %s (%s x %s) in port %s selected." %(backendName,h,w, videoCaptureDeviceId))
                    camera.release()
                else:
                    raise Exception("Couldn't initialize selected camera.")
                
                next_frame = 0 # limit to ~10 fps here
                
                for res, img in runner.classifier(videoCaptureDeviceId):
                    count = 0
                    
                    if (next_frame > now()):
                        time.sleep((next_frame - now()) / 1000)

                    # print('classification runner response', res)

                    if "classification" in res["result"].keys():
                        print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                        for label in labels:
                            score = res['result']['classification'][label]
                            print('%s: %.2f\t' % (label, score), end='')
                        print('', flush=True)

                    elif "bounding_boxes" in res["result"].keys():
                        # print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                        countPeople = len(res["result"]["bounding_boxes"])
                        inferenceSpeed = res['timing']['classification']
                        for bb in res["result"]["bounding_boxes"]:
                            # print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                            img = cv2.rectangle(img, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (0, 0, 255), 2)
                        
                    ret, buffer = cv2.imencode('.jpg', img)
                    frame = buffer.tobytes()
                    yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

                    next_frame = now() + 100
                    
            finally:
                if (runner):
                    runner.stop()


def get_inference_speed():
    while True:
        # print(inferenceSpeed)
        yield "data:" + str(inferenceSpeed) + "\n\n"
        time.sleep(0.1)

def get_people():
    while True:
        # print(countPeople)
        yield "data:" + str(countPeople) + "\n\n"
        time.sleep(0.1)

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/inference_speed')
def inference_speed():
	return Response(get_inference_speed(), mimetype= 'text/event-stream')

@app.route('/people_counter')
def people_counter():
	return Response(get_people(), mimetype= 'text/event-stream')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)