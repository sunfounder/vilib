from imutils import paths
import face_recognition
import pickle
import cv2



class Face():
    @staticmethod
    def training(name,pic_path='/home/pi/picture',model_path="/home/pi/trainer/encodings.pickle"):
        
        imagePaths = list(paths.list_images(pic_path))
        
        knownEncodings = []
        knownNames = []
        
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

    #返回  人脸位置、匹配模型名字 、相似度  
    @staticmethod 
    def recognition(img,model_path='/home/pi/trainer/encodings.pickle'):
        
        similaritys = []
        locations = []
        names = []
        
        print("[INFO] loading encodings + face detector...")
        
        #遍历 读取每个人脸模型
        datas = []
        with open(model_path,'rb') as f:
            while True:
                try:
                    datas.append(pickle.load(f))             
                except EOFError:
                    break
        
        # 人脸检测
        locations = face_recognition.face_locations(img,model= "hog")
        
        # face_recognition 人脸编码
        encodings = face_recognition.face_encodings(img, locations)
        
        print('[INFO] %d faces were found ...'%(len(locations)))

        
        i = 0
        #遍理检测到的每个人脸
        for encoding in encodings:
            i += 1
            print("face %d "%i)
            # 
            name = 'unknow'
            fufu = {}
            # 遍历比对每个模型
            for data in datas: 
                matches = face_recognition.compare_faces(data["encodings"],encoding)
                #print(matches,end = '     ')
                    
                count = 0
                for match in matches:             
                    if match == True:
                        count += 1
                        
                name = data["names"][0]  
                similarity  = count/len(matches)           
                print('      ',(similarity*100),'%  ',name)
                
                fufu[name] = similarity
            
        # 取相似的最大的
            name = max(fufu,key=fufu.get)   
            similarity = fufu[name] 
            
            if similarity < 0.5:
                name = "unknow" 
                similarity = 0.0  
            
            print(name,(similarity*100),'%')
                            
            names.append(name)
            similaritys.append(similarity)
            
        return locations,names,similaritys
                
    #调用 my_face_recognition(img)，框出人脸，标出名字和置信度，返回 修改后的图像数组   
    @staticmethod
    def recognition2img(img,model_path='/home/pi/trainer/encodings.pickle'): 
        locations,names,similaritys = my_face_recognition(img)
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
            cv2.putText(img, names[i] + str(similaritys[i]), (left + 6, bottom + 6), font,0.5, (255, 255, 255), 1)
        
        return img