import cv2
import errno
import imagezmq
import os
import socket


def create_streamer(file, connect_to='tcp://127.0.0.1:5566', loop=True):
    """
    You can use this function to emulate an IP camera for the counting apps.

    Parameters
    ----------
    file : str
        Path to the video file you want to stream.
    connect_to : str, optional
        Where the video shall be streamed to.
        The default is 'tcp://127.0.0.1:5555'.
    loop : bool, optional
        Whether the video shall be looped. The default is True.

    Returns
    -------
    None.

    """

    # check if file exists and open capture
    if os.path.isfile(file):
        cap = cv2.VideoCapture(file)
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file)

    # Force resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # prepare streaming
    sender = imagezmq.ImageSender(connect_to=connect_to)
   # host_name = socket.gethostname()
    host_name = "Camera 2"
    while True:
        ret, frame = cap.read()

        if ret:
           # print("Sending video frames...")
            # Optionally downscale frame here if needed
            sender.send_image(host_name, frame)
        else:
           # print("Failed to send video frames to app.")
            # if no frame was returned, either restart or stop the stream
            if loop:
                cap = cv2.VideoCapture(file)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            else:
                break


if __name__ == '__main__':
    streamer = create_streamer('video1.mp4')
