import sys,os,cv2

from keras.models import load_model
import numpy as np
from src.utils.datasets import get_labels
from src.utils.inference import detect_faces
from src.utils.inference import draw_text
from src.utils.inference import draw_bounding_box
from src.utils.inference import apply_offsets
from src.utils.inference import load_detection_model
from src.utils.inference import load_image
from src.utils.preprocessor import preprocess_input
#from race import *
sys.path.append('..')
# parameters for loading data and images


def race_emotion(image_path,save_path=None,task='save',faces):
	
	image_path = image_path#'../test_images'#sys.argv[1]
	detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
	emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
	gender_model_path = '../trained_models/gender_models/simple_CNN.81-0.96.hdf5'
	emotion_labels = get_labels('../trained_models/fer2013')
	gender_labels = get_labels('../trained_models/imdb')
	font = cv2.FONT_HERSHEY_SIMPLEX

	base=os.path.basename(image_path)
	name=os.path.splitext(base)[0]
	# hyper-parameters for bounding boxes shape
	gender_offsets = (30, 60)
	gender_offsets = (10, 10)
	emotion_offsets = (20, 40)
	emotion_offsets = (0, 0)

	# loading models
	face_detection = load_detection_model(detection_model_path)
	emotion_classifier = load_model(emotion_model_path, compile=False)
	gender_classifier = load_model(gender_model_path, compile=False)

	# getting input model shapes for inference
	emotion_target_size = emotion_classifier.input_shape[1:3]
	gender_target_size = gender_classifier.input_shape[1:3]

	# loading images
	rgb_image = load_image(image_path, grayscale=False)
	
	gray_image = load_image(image_path, grayscale=True)
	gray_image = np.squeeze(gray_image)
	gray_image = gray_image.astype('uint8')

	#faces = detect_faces(face_detection, gray_image)
	faces=faces
	i=0
	for face_coordinates in faces:
	    x1, x2, y1, y2 = apply_offsets(face_coordinates, gender_offsets)
	    rgb_face = rgb_image[y1:y2, x1:x2]

	    x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
	    gray_face = gray_image[y1:y2, x1:x2]

	    try:
             rgb_face = cv2.resize(rgb_face, (gender_target_size))
             gray_face = cv2.resize(gray_face, (emotion_target_size))
	    except:
	     print '='*10+'exception in resize'
	     continue
             #print 'exception in resize' #continue

	    rgb_face = preprocess_input(rgb_face, False)
	    rgb_face = np.expand_dims(rgb_face, 0)
	    gender_prediction = gender_classifier.predict(rgb_face)
	    gender_label_arg = np.argmax(gender_prediction)
	    gender_text = gender_labels[gender_label_arg]

	    gray_face = preprocess_input(gray_face, True)
	    gray_face = np.expand_dims(gray_face, 0)
	    gray_face = np.expand_dims(gray_face, -1)
	    emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
	    emotion_text = emotion_labels[emotion_label_arg]

	    if gender_text == gender_labels[0]:
             color = (0, 0, 255)
	    else:
             color = (255, 0, 0)
	    
	    
	    crop=rgb_image[y1:y2, x1:x2]
	    crop = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
	    #race=find_race(crop,gender_text)
	    print ('emotion and race are:',emotion_text,race)
	    #cv2.imwrite('images/'+str(i)+'.png', crop)
	    draw_bounding_box(face_coordinates, rgb_image, color)
	    draw_text(face_coordinates, rgb_image, color, 0, -20, 1, 2)
	    #draw_text(face_coordinates, rgb_image, gender_text, color, 0, -20, 1, 2)
	    draw_text(face_coordinates, rgb_image, emotion_text, color, 0, -50, 1, 2)
	    i=i+1

	if task=='save':
		bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
		cv2.imwrite('../OUT/'+name+'.png', bgr_image)
	#print ('')



if __name__ =='__main__':
	

	race_emotion('images/sample/'+img,'images/outcome/',task='save')	

