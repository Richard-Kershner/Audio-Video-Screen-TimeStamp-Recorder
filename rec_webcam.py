# python -m pip install –upgrade      // updates pip
# pip install opencv-python (contains both main modules and contribs/extras)
# pip install numpy
# pip install pandas

import cv2
from datetime import datetime, timedelta
import numpy as np

from multiprocessing import shared_memory

def runCapture(webCam, rec_controls_sm, saveFilesPath):
    rec_controls = rec_controls_sm.buf

    cap = cv2.VideoCapture()
    cap.open(webCam)#, cv2.CAP_DSHOW) #webCam 1 or 3
    #frameShape = np.shape(cap.read()[1])
    #frame_height = frameShape[0]
    #frame_width = frameShape[1]

    #writeAVI_file = saveFilesPath + "\\webCamFrames_" + str(webCam) + ".avi"
    #writeVid = cv2.VideoWriter(writeAVI_file, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

    data_frames = []

    # shared script for recording
    data_stamps = []
    waitLoop = True
    stopStamp = 0.0
    while waitLoop:
        stamp = datetime.timestamp(datetime.now())
        if stamp < stopStamp or rec_controls[0] == 1:

            for i in range(30):  #30 fps ? note screen reader was 15.....
                data_stamps.append(datetime.timestamp(datetime.now()))

                data_frames.append( cap.read()[1]) #rev, frame = cap.read()
                #writeVid.write(cap.read()[1])

                cv2.imshow('frame1', data_frames[-1])
                cv2.waitKey(1)

        # shared script for recording
        if rec_controls[0] == 0:
            if stopStamp == -1 and rec_controls[1] != 99:
                nowTime = datetime.now()
                stopStamp = datetime.timestamp(nowTime)
                newSecond = rec_controls[1] - nowTime.second
                if newSecond < 0: # adjust for wrap around the clock 1 - 58 = -57
                    newSecond += 60
                stopStamp = stopStamp + timedelta(seconds = (newSecond))
            elif stamp > stopStamp:
                waitLoop = False

    cap.release()
    cv2.destroyAllWindows()

    data_frames = np.array(data_frames, dtype=np.uint8)
    data_frames.tofile(saveFilesPath + "\\webCamFramesBinary_" + str(webCam) + ".csv")

    data_stamps = np.array(data_stamps, dtype=float)
    data_stamps.tofile(saveFilesPath + "\\webCamTimeStamps_" + str(webCam) + ".csv", sep = ',')

    dataShape = np.array(np.shape(data_frames), dtype=int)
    dataShape.tofile(saveFilesPath+"\\webCamFramesShape_" + str(webCam) + ".csv")
    #writeVid.release()

    print('videos frames shape', np.shape(data_frames), "  len stamps", len(data_stamps))

    return

