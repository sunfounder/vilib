from imutils import paths
import face_recognition
import pickle
import cv2
import sys
import os
import time 

class Face():

    model_data = []


    # 人脸检测（使用face_detection库）
    @staticmethod
    def detect(img):
        resize_img = cv2.resize(img, (160,120),interpolation=cv2.INTER_LINEAR)            
        face_locations = face_recognition.face_locations(resize_img)
        for (y,w,h,x) in face_locations:
            x = x*4
            y = y*4
            w = w*4
            h = h*4
            cv2.rectangle(img,(x,y),(w,h),(0,255,0),2)
        return img

    @staticmethod  
    def load_model(model_path='/home/pi/trainer/encodings.pickle'):

        print("[INFO] loading encodings + face detector...")
        with open(model_path,'rb') as f:
            while True:
                try:
                    Face.model_data.append(pickle.load(f))             
                except EOFError:
                    break


    @staticmethod
    def training(name,pic_path='/home/pi/picture',model_path="/home/pi/trainer/encodings.pickle"):
              
        if not os.path.exists(pic_path):
            print("The path of pictures cannot be found.")
            return
        
        imagePaths = list(paths.list_images(pic_path))

        if not len(imagePaths) > 0:
            #print(len(imagePaths))
            print("There is no image in this directory.")  
            return

        knownEncodings = []
        knownNames = []

        while not os.path.exists(model_path):
            print('model_file does not exist. Creating it now ... ')
            # 注意参数前面留空格
            os.system('sudo mkdir -p -m=777 '+model_path.rsplit('/',1)[0])
            os.system('sudo touch '+model_path)
            os.system('sudo chmod 777 '+model_path)
            #注意加延时防止卡死
            time.sleep(0.1)

        
        for (i, imagePath) in enumerate(imagePaths):
            print("[INFO] processing image {}/{}".format(i + 1,
            len(imagePaths)))
            
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            boxes = face_recognition.face_locations(rgb,model= "hog")
            
            encodings = face_recognition.face_encodings(rgb, boxes)
            
            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)
              

        # dump the facial encodings + names to disk
        print("[INFO] serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        
        #注意使用 "ab" 进行 二进制文件追加写入
        f = open(model_path, "ab")   
        f.write(pickle.dumps(data))
        f.close()
        print("[INFO] done...")



    #返回  人脸位置、匹配模型名字 、相似度  
    @staticmethod 
    def recognition(img):
        
        similaritys = []
        locations = []
        names = []
            
        
        if Face.model_data is None:
            print("Error: The model data was not loaded correctly")

        
        # 人脸检测
        locations = face_recognition.face_locations(img,model= "hog")
        
        # face_recognition 人脸编码
        encodings = face_recognition.face_encodings(img, locations)
        
        #print('[INFO] %d faces were found ...'%(len(locations)))
      
        #遍理检测到的每个人脸
        for encoding in encodings:
           
            name = 'unknow'
            similarity = 0.0 
            result = {}
            # 遍历比对每个模型
            for data in Face.model_data: 
                matches = face_recognition.compare_faces(data["encodings"],encoding)
                #print(matches,end = '     ')
                    
                count = 0
                for match in matches:             
                    if match == True:
                        count += 1
                        
                name = data["names"][0]  
                similarity  = count/len(matches)           
                #print('      ',(similarity*100),'%  ',name)
                
                result[name] = similarity
            
        # 取相似的最大的
            if result is not None:
                name = max(result,key=result.get)   
                similarity = result[name] 
            
                if similarity < 0.5:
                    name = "unknow" 
                    similarity = 0.0  
            
            print(name,(similarity*100),'%')
                            
            names.append(name)
            similaritys.append(similarity)
            
        return locations,names,similaritys
                
    #调用 recognition(img)，框出人脸，标出名字和置信度，返回 修改后的图像数组   
    @staticmethod
    def recognition2img(img): 
        locations,names,similaritys = Face.recognition(img)
        #print(locations)
        #print(names)
        #print(similaritys)
        
        for i,box in enumerate(locations): 
            #注意这里的顺序
            top, right, bottom, left = box
            
            # 在面部周围绘制一个方框
            cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 1)
            # 在脸下绘制名称
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, names[i] + str(similaritys[i]*100)+'%', (left + 6, bottom + 6), font,0.5, (255, 255, 255), 1)
        
        return img

# def main(args1 = None,args2 = '/home/pi/picture',args3 = "/home/pi/trainer/encodings.pickle"):
#     if args1 is None:
#         args1 = sys.argv[1:]
        
def main(name = None,pic_path = None,model_path = None):
    #3个参数
    if len(sys.argv) > 4:
        print("Too many parameters")
    elif len(sys.argv) == 4:
        name = sys.argv[1]    
        pic_path = sys.argv[2]
        model_path = sys.argv[3]

        Face.training(name,pic_path,model_path)
        # print(len(sys.argv))
        # print(args1)
        # print(args2)
        # print(args3)   
        
    else:
        print("Please Complement parameter ：name,pic_path,model_path")
        print("eg ：face_train xiaoming  /home/pi/picture/xiaoming  /home/pi/trainer/encodings.pickle")
    


# if __name__ == "__main__":
#     main()
         