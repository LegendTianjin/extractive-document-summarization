"""
Created on Sat Mar 17 11:01:27 2018

@author: leo
"""
import warnings
warnings.filterwarnings("ignore")
import pickle
import numpy as np
import matplotlib.pyplot as plt

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers import MaxPooling2D
from keras.layers.convolutional import Conv2D
from keras import regularizers

#from sklearn.model_selection import train_test_split

# Build model
def build_model(input_shape, conv_window_size, num_filters, reg, dropout):
    model = Sequential()
    #model.add(Embedding(max_features,300))

    # we add a Convolution 1D, which will learn num_filters
    # word group filters of size conv_window_size:
    print(input_shape)
    model.add(Conv2D(input_shape=input_shape,
                        filters=num_filters,
                        kernel_size=(1, conv_window_size),
                        padding="valid",
                        activation="relu",
                        strides=1,
                        data_format='channels_first'))
    
    model.add(MaxPooling2D(pool_size=(400, 1)))

    #Fully Connected + Dropout + sigmoid
    model.add(Dropout(dropout))
    model.add(Flatten())
    model.add(Dense(1, activation='sigmoid', kernel_regularizer=regularizers.l2(reg)))
    
    #In addition, an l2−norm constraint of the weights w_r is imposed during training as well

    model.compile(loss='binary_crossentropy',
                  optimizer='adadelta',
                  metrics=['mae'])
    return model

def train(model, x_train, y_train, val_train_ratio=0.2, epochs=1000, batch_size=128):
    history = model.fit(x_train, y_train,
                        batch_size=batch_size,
                        epochs=epochs,
                        validation_split=val_train_ratio,
                        shuffle=True,
                        verbose=1)
    return history

def load_data():
    data = pickle.load(open("preprocessing/wordEmbeddingsToSaliency.pickle", "rb"))
    x_raw = data[::2]
    y = data[1::2]

    x = list()
    for emb in x_raw:
        x.append(emb.tolist())

    x = np.array(x)
    x = np.expand_dims(x, axis=1)
    return x, y

def main():
    # Model Hyperparameters
    conv_window_size = 300
    num_filters = 400
    reg = 0.01
    dropout = 0.5
    
    # Training parameters
    epochs = 10
    batch_size = 128
    test_train_ratio = 0.2
    val_train_ratio = 0.2

    x_train, y_train = load_data()

    #x_train, x_test, y_train, y_test = test_train_split(x, y, test_size=test_train_ratio)

    model = build_model((1, x_train.shape[2], x_train.shape[3]), conv_window_size, num_filters, reg, dropout)
    history = train(model, x_train, y_train, val_train_ratio, epochs, batch_size)

    model.model.save('model.h5') 

    f, (ax1, ax2) = plt.subplots(2, 1)
    ax1.plot(range(1, epochs+1), history.history['val_mean_absolute_error'], 'tab:blue', label="validation MAE")
    ax1.plot(range(1, epochs+1), history.history['mean_absolute_error'], 'tab:red', label="training MAE")

    ax2.plot(range(1, epochs+1), history.history['loss'], 'tab:orange', label="loss")
    ax2.plot(range(1, epochs+1), history.history['val_loss'], 'tab:green', label="validation loss")

    ax1.legend()
    ax2.legend()

    f.savefig('training.png', dpi=300)

if __name__ == "__main__":
    main()