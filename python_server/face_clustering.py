import face_recognition
from imutils import build_montages
import cv2
from sklearn.cluster import DBSCAN
import numpy as np
import os

class Face():
    def __init__(self, frame_id, name, box, encoding):
        self.frame_id = frame_id
        self.name = name
        self.box = box
        self.encoding = encoding

class ExtractPeopleFaces():
    def __init__(self, src_file):
        self.faces = []
        self.run_encoding = False
        self.src_file = src_file
        filename = os.path.basename(src_file)
        name, ext = os.path.splitext(filename)
        self.video_dir = os.path.join('results', name)
        if not os.path.exists(self.video_dir):
            os.mkdir(self.video_dir)
        self.capture_dir = os.path.join(self.video_dir, "captures")
        self.people_dir = os.path.join(self.video_dir, "people")

    def capture_filename(self, frame_id):
        return "frame_%08d.jpg" % frame_id

    def getFaceImage(self, image, box):
        img_height, img_width = image.shape[:2]
        (top, right, bottom, left) = box
        box_width = right - left
        box_height = bottom - top
        top = max(top - box_height, 0)
        bottom = min(bottom + box_height, img_height - 1)
        left = max(left - box_width, 0)
        right = min(right + box_width, img_width - 1)
        return image[top:bottom, left:right]

    def encode(self, capture_per_second, stop=0):
        src = cv2.VideoCapture(self.src_file)
        if not src.isOpened():
            return

        self.faces = []
        frame_id = 0
        frame_rate = src.get(5)
        stop_at_frame = int(stop * frame_rate)
        frames_between_capture = int(round(frame_rate) / capture_per_second)

        print("start encoding from src: %dx%d, %f frame/sec" % (src.get(3), src.get(4), frame_rate))
        print(" - capture every %d frame" % frames_between_capture)
        if stop_at_frame > 0:
            print(" - stop after %d frame" % stop_at_frame)

        if not os.path.exists(self.capture_dir):
            os.mkdir(self.capture_dir)

        self.run_encoding = True
        while self.run_encoding:
            ret, frame = src.read()
            if frame is None:
                break

            frame_id += 1
            if frame_id % frames_between_capture != 0:
                continue

            if stop_at_frame > 0 and frame_id > stop_at_frame:
                break

            rgb = frame[:, :, ::-1]
            boxes = face_recognition.face_locations(rgb, model="hog")

            print("frame_id =", frame_id, boxes)
            if not boxes:
                continue

            encodings = face_recognition.face_encodings(rgb, boxes)

            faces_in_frame = []
            for box, encoding in zip(boxes, encodings):
                face = Face(frame_id, None, box, encoding)
                faces_in_frame.append(face)

            # save the frame
            pathname = os.path.join(self.capture_dir,
                                    self.capture_filename(frame_id))
            cv2.imwrite(pathname, frame)
            self.faces.extend(faces_in_frame)

        self.run_encoding = False
        src.release()
        return

    def cluster(self):
        if len(self.faces) is 0:
            print("no faces to cluster")
            return

        print("start clustering %d faces..." % len(self.faces))
        encodings = [face.encoding for face in self.faces]

        # cluster the embeddings
        clt = DBSCAN(metric="euclidean")
        clt.fit(encodings)

        # determine the total number of unique faces found in the dataset
        label_ids = np.unique(clt.labels_)
        num_unique_faces = len(np.where(label_ids > -1)[0])
        print("clustered %d unique faces." % num_unique_faces)
        
        os.system("rm -rf " + self.video_dir + "/ID*")
        if not os.path.exists(self.people_dir):
            os.mkdir(self.people_dir)

        for label_id in label_ids:
            dir_name = "ID%d" % label_id
            os.mkdir(os.path.join(self.video_dir, dir_name))

            # find all indexes of label_id
            indexes = np.where(clt.labels_ == label_id)[0]
            indexes = np.random.choice(indexes, size=min(4, len(indexes)), replace=False)

            # save face images
            faces = []
            for i in indexes:
                frame_id = self.faces[i].frame_id
                box = self.faces[i].box
                (top, right, bottom, left) = box

                pathname = os.path.join(self.capture_dir,
                                        self.capture_filename(frame_id))
                image = cv2.imread(pathname)
                faces.append(image[top:bottom, left:right])
                face_image = self.getFaceImage(image, box)
                
                filename = dir_name + "-" + self.capture_filename(frame_id)
                pathname = os.path.join(self.video_dir, dir_name, filename)
                cv2.imwrite(pathname, face_image)

            montage = build_montages(faces, (96, 96), (2, 2))[0]
            filename = os.path.join(self.people_dir, dir_name + '.jpg')
            cv2.imwrite(filename, montage)
            print("label_id %d" % label_id, "has %d faces" % len(indexes),
                  "in '%s' directory" % dir_name)
    
        print('clustering done')
        

# epf = ExtractPeopleFaces("uploads/yunayoona.mov")
# epf.encode(10)
# epf.cluster()