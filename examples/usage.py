"""
Usage example to supply to README.md
"""

# Usage

## Using Datumio as image transformer	
import datumio.transforms as dtf
import matplotlib.pyplot as plt
from PIL import Image
import urllib2 as urllib
import io
import numpy as np

# get image from the web as numpy array
url = 'http://cdn.playbuzz.com/cdn/0079c830-3406-4c05-a5c1-bc43e8f01479/7dd84d70-768b-492b-88f7-a6c70f2db2e9.jpg'
img = np.array(Image.open(io.BytesIO(urllib.urlopen(url).read())))

# Apply set transformations to image
tf_params = {
    'rotation': 15,          # rotation in degrees
    'zoom': (1.0, 1.0),      # zoom in (x,y) = (col, row)
    'shear': 0,              # shear in degrees
    'translation': (5, 10),  # translation (x, y)
    'flip_lr': True,         # flip left/right
    'flip_ud': False,        # flip up/down
    'warp_kwargs': {
        'mode': 'wrap',      # wrap rotated pixels
    }
}

img_tf = dtf.transform_image(img, **tf_params)
# datumio returns as float32 by default 
img_tf = img_tf.astype(np.uint8)

plt.figure(); plt.clf()
plt.subplot(211)
plt.imshow(img); plt.title("Original"); plt.axis('off')
plt.subplot(212)
plt.imshow(img_tf); plt.title("Transformed"); plt.axis('off')
plt.show()

## Using Datumio for deep learning models
import datumio.datagen as dtd

# Get paths to data
X_train = 'array-of-paths-to-train-data'
y_train = 'array-of-paths-to-train-labels'
X_valid = 'array-of-paths-to-valid-data'
y_valid = 'array-of-paths-to-valid-labels'

# Create data loder to load up each img with custom transformations
def data_loader(data_path):
    """ Custom loading function to load specific data """
    img = np.array(Image.open(data_path))
    img /= float(255) # scale pixels to 0-1
    return img

# Random realtime data augmentation parameters applied upon loading of each minibatch
rng_aug_params = {'rotation_range': (-20, 20),      # rotate in degrees 
                  'translation_range': (-4, 4),     # translate x,y
                  'do_flip_lr': True,}              # randomly flips left/right
                  
datagen = dtd.DataGenerator()
datagen.set_data_loader(data_loader)        # set custom data loader
datagen.set_samplewise_zmuv(axis=0)         # zero-mean unit variance every minibatch upon loading
datagen.set_rng_aug_params(rng_aug_params)  # sets random augmentation parameters

# create model
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
model = Sequential()

model.add(Convolution2D(32, 3, 3, border_mode='full', input_shape=(3, 32, 32)))
model.add(Activation('relu'))
model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Convolution2D(64, 3, 3, border_mode='full'))
model.add(Activation('relu'))
model.add(Convolution2D(64, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(10))
model.add(Activation('softmax'))
model.compile(loss='categorical_crossentropy', optimizer='sgd')

for epoch in range(10):
    for X_batch, y_batch in datagen.flow(X_train, y_train, shuffle=True, batch_size=32):
        loss = model.train_on_batch(X_batch, y_batch)