import cv2

def detect_faces_with_gpu():
    # 加载使用 GPU 的人脸检测器
    face_cascade = cv2.cuda_CascadeClassifier_create()
    face_cascade.load(cv2.samples.findFile('haarcascades/haarcascade_frontalface_default.xml'))

    # 初始化摄像头
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 将图像上传到 GPU
        gpu_frame = cv2.cuda_GpuMat()
        gpu_frame.upload(frame)

        # 在 GPU 上进行人脸检测
        gray_gpu = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)
        faces_gpu = face_cascade.detectMultiScale(gray_gpu)

        # 将检测结果下载到 CPU
        faces = faces_gpu.download()

        # 在图像上绘制人脸框
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # 显示结果
        cv2.imshow('Face Detection with GPU', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    detect_faces_with_gpu()