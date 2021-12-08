# pip install pipwin
# pip install pyaudio
import pyaudio
import wave

from datetime import datetime, timedelta
import numpy as np

from multiprocessing import shared_memory

def runCapture(recDevice, rec_controls_sm, saveFilesPath, SECONDS = 1):
    rec_controls = rec_controls_sm.buf
    p = pyaudio.PyAudio()
    micName = p.get_device_info_by_host_api_device_index(0, recDevice).get('name')
    RATE = 44100  # 14700/second  44100/ 3secs
    #SECONDS = 1 # ? multiple of RATE
    CHUNK = int(RATE * SECONDS)  # 44100 # 14700/second  44100/ 3secs ? 44100/30 = 1470
    FORMAT = pyaudio.paInt16
    FORMATstr = "pyaudio.paInt16"
    # pyaudio.paInt16 format, the samples are 16-bit integers, so their range is from -32,768 to 32,767.
    CHANNELS = 1
    stream = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK,
                            input_device_index=recDevice)

    data_chunks = []

    # shared script for recording
    data_stamps = []
    waitLoop = True
    stopStamp = 0.0
    while waitLoop:
        stamp = datetime.timestamp(datetime.now())

        # frame reading is embedded in stream.read(CHUNK..... no for loop
        data_stamps.append(datetime.timestamp(datetime.now()))

        #data_chunks.append(stream.read(CHUNK, exception_on_overflow=False))
        data_chunks.append(stream.read(CHUNK))

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

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(saveFilesPath + "\\audio_" + str(recDevice) + ".wav", 'wb')
    wf.setnchannels(1) # CHANNELS
    wf.setsampwidth(p.get_sample_size(FORMAT))#data_chunks[-1].get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(data_chunks))
    wf.close()

    audFrames = []
    for data in data_chunks:
        #print(len(data))
        numpyData = np.frombuffer(data, dtype=np.int16)
        audFrames.append(numpyData)
    audFrames = np.array(audFrames, dtype=np.int16)
    audFrames.tofile(saveFilesPath + "\\audioNpInt16_" + str(recDevice) + ".bin")

    #audFrames = []
    #for data in data_chunks:
    #    print(len(data))
    #    numpyData = np.frombuffer(data, dtype=np.float)
    #    audFrames.append(numpyData)
    #audFrames = np.array(audFrames)
    #audFrames.tofile(saveFilesPath + "\\audioNpFloat_" + str(recDevice) + ".bin")

    data_raw = np.array(data_chunks)
    data_raw.tofile(saveFilesPath + "\\audioFramesRaw_" + str(recDevice) + ".bin")

    #data_chunks = data_chunks.astype(np.int16)
    #print('audio raw', data_raw.dtype, np.shape(data_raw))


    data_stamps = np.array(data_stamps, dtype=float)#, dtype=np.longdouble)

    #print("audio stampss:", len(data_stamps), data_stamps[0], data_stamps[-1], recDevice, " micName: ", micName)
    data_stamps.tofile(saveFilesPath+"\\audioStamps_" + str(recDevice) + ".csv", sep = ',')

    lines = ['RATE:' + str(RATE), 'SECONDS:' + str(SECONDS), 'CHUNK:' + str(CHUNK), "FORMAT:" + FORMATstr]#str(FORMAT)]
    lines.append('rawType:' + str(data_raw.dtype))
    lines.append('rawShape:' + str(np.shape(data_raw)))
    print('audio', len(data_stamps), lines, micName)
    with open(saveFilesPath + "\\audioStats_" + str(recDevice) + ".txt", "w") as fhandle:
        for line in lines:
            fhandle.write(f'{line}\n')

    return

