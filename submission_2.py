# -*- coding: utf-8 -*-
"""Submission 2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1j9CXMQmOECdsvpf_5-kbEd4H4EL3O06l

Dataset : https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset
"""

import numpy as np
import pandas as pd
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf

data_train = pd.read_csv('hour.csv')
data_train

data_train.isnull().sum()

dates = data_train['dteday'].values
temp = data_train['temp'].values

plt.figure(figsize=(15,5))
plt.plot(dates, temp)
plt.title('Temperature', fontsize=20)

from sklearn.model_selection import train_test_split
date_latih, date_test, temp_latih, temp_test = train_test_split(dates, temp, test_size=.2, shuffle=False)

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

train_set = windowed_dataset(temp_latih, window_size=60, batch_size=100, shuffle_buffer=1000)
test_set = windowed_dataset(temp_test, window_size=60, batch_size=100, shuffle_buffer=1000)
model = tf.keras.models.Sequential([
   tf.keras.layers.LSTM(60, return_sequences=True),
   tf.keras.layers.LSTM(60),
   tf.keras.layers.Dense(30, activation="relu"),
   tf.keras.layers.Dense(10, activation="relu"),
   tf.keras.layers.Dense(1)
])

minMae = (data_train['temp'].max() - data_train['temp'].min()) * .1

print(minMae)

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if (logs.get('mae')<minMae) & (logs.get('val_mae')<minMae):
      print('\nProses dihentikan karena tingkat MAE sudah mencapai <10%!')
      self.model.stop_training = True

callbacks = myCallback()

optimizer = tf.keras.optimizers.SGD(learning_rate=1.000e-04, momentum=0.9)
model.compile(
    loss=tf.keras.losses.Huber(),
    optimizer=optimizer,
    metrics=['mae']
    )
history = model.fit(
    train_set,
    epochs=100,
    validation_data=test_set,
    verbose=2,
    callbacks=[callbacks],
    )

plt.plot(history.history['mae'])
plt.plot(history.history['val_mae'])
plt.title('MAE Model')
plt.ylabel('MAE')
plt.xlabel('epoch')
plt.legend(['Training MAE', 'Validation MAE'], loc='upper right')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['Training loss', 'Validation loss'], loc='upper right')
plt.show()