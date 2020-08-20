'''
This code is to build various dataset for SAR
'''
import string
import cv2
import torch.utils.data as data
import os
import torch
import numpy as np
import xml.etree.ElementTree as ET

def dictionary_generator(END='END', PADDING='PAD', UNKNOWN='UNK'):
    '''
    END: end of sentence token
    PADDING: padding token
    UNKNOWN: unknown character token
    '''
    voc = list(string.printable[:-6]) # characters including 9 digits + 26 lower cases + 26 upper cases + 33 punctuations
    
    # update the voc with 3 specifical chars
    voc.append(END)
    voc.append(PADDING)
    voc.append(UNKNOWN)

    char2id = dict(zip(voc, range(len(voc))))
    id2char = dict(zip(range(len(voc)), voc))

    return voc, char2id, id2char

def svt_xml_extractor(img_path, label_path):
    '''
    This code is to extract xml labels from SVT dataset
    Input:
    img_path: path for all image folder
    label_path: xml label path file
    Output:
    dict_img: {image_name: [imgs, labels, lexicon]}
    imgs: list of numpy cropped images with bounding box
    labels: list of string labels
    lexicon: lexicon for this image
    '''
    # create element tree object
    tree = ET.parse(label_path)

    # get root element
    root = tree.getroot()

    # create empty list for news items
    dict_img = []

    # iterate news items
    for item in root.findall('image'):
        name = item.find('imageName').text.split('/')[-1]
        lexicon = item.find('lex').text.split(',')
        rec = item.find('taggedRectangles')
        for r in rec.findall('taggedRectangle'):
            x = int(r.get('x'))
            y = int(r.get('y'))
            w = int(r.get('width'))
            h = int(r.get('height'))
            bdb = (x,y,w,h)
            labels = r.find('tag').text
            dict_img.append([name, bdb,labels,lexicon])

    return dict_img

class svt_dataset_builder(data.Dataset):
    def __init__(self, height, width, seq_len, total_img_path, xml_path):
        '''
        height: input height to model
        width: input width to model
        total_img_path: path with all images
        xml_path: xml labeling file
        seq_len: sequence length
        '''
        # parse xml file and create fully ready dataset
        self.total_img_path = total_img_path
        self.height = height
        self.width = width
        self.seq_len = seq_len
        self.dictionary = svt_xml_extractor(total_img_path, xml_path)
        self.total_img_name = os.listdir(total_img_path)
        self.dataset = []
        self.voc, self.char2id, _ = dictionary_generator()
        self.output_classes = len(self.voc)
        for items in self.dictionary:
            if items[0] in self.total_img_name:
                self.dataset.append([items[0],items[1],items[2]])

    def __getitem__(self, index):
        img_name, bdb, label = self.dataset[index]
        IMG = cv2.imread(os.path.join(self.total_img_path,img_name))
        x, y, w, h = bdb
        # image processing:
        IMG = IMG[y:y+h,x:x+w,:] # crop
        IMG = cv2.resize(IMG, (self.width, self.height)) # resize
        IMG = (IMG - 127.5)/127.5 # normalization to [-1,1]
        IMG = torch.FloatTensor(IMG) # convert to tensor [H, W, C]
        IMG = IMG.permute(2,0,1) # [C, H, W]
        y_true = np.ones(self.seq_len)*self.char2id['PAD'] # initialize y_true with 'PAD', size [seq_len]
        # label processing
        for i, c in enumerate(label):
            index = self.char2id[c]
            y_true[i] = index
        y_true[-1] = self.char2id['END'] # always put 'END' in the end
        y_true = y_true.astype(int) # must to integer index for one-hot encoding
        # convert to one-hot encoding
        y_onehot = np.eye(self.output_classes)[y_true] # [seq_len, output_classes]

        return IMG, torch.FloatTensor(y_onehot)

    def __len__(self):
        return len(self.dataset)

# unit test
if __name__ == '__main__':
    
    img_path = '../svt/img/'
    train_xml_path = '../svt/train.xml'
    test_xml_path = '../svt/test.xml'
    height = 48 # input height pixel
    width = 64 # input width pixel
    seq_len = 40 # sequence length

    train_dict = svt_xml_extractor(img_path, train_xml_path)
    print("Dictionary for training set is:", train_dict)

    train_dataset = svt_dataset_builder(height, width, seq_len, img_path, train_xml_path)

    for i, item in enumerate(train_dataset):
        print(item[0].shape,item[1].shape)

    test_dataset = svt_dataset_builder(height, width, seq_len, img_path, test_xml_path)
    for i, item in enumerate(test_dataset):
        print(item[0].shape,item[1].shape)