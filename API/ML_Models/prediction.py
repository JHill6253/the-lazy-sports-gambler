
import tensorflow as tf
from tensorflow import keras



class Prediction(object):
    
    def __init__(self, data):
        self.data = data.copy()
        
    #Normalize the data
    def sigmoid(self, dataframe):
        
        return((dataframe - self.train_stats['mean'])/self.train_stats['std'])
        
    #Defining the model
    def build_model(self):
        
        input_layer=tf.keras.layers.Input(([len(self.train_dataset.keys())]))
        densel_layer = tf.keras.layers.Dense(units=1, input_shape=([len(self.train_dataset.keys())],))
        output = densel_layer(input_layer)
        model = tf.keras.Model(inputs=input_layer,outputs=output)

        model.compile(loss="mse",optimizer=tf.keras.optimizers.Adam(0.01), metrics=['mae', 'mse'])

        return model
        
    def make_prediction(self, prediction_data):
        
        #set up train and testing data
        self.train_dataset = self.data.sample(frac=0.90, random_state=0)
        self.test_dataset = self.data.drop(self.train_dataset.index)
    
        self.train_labels = self.train_dataset.pop("Points Scored")
        self.test_labels = self.test_dataset.pop("Points Scored")
        
        self.train_stats = self.train_dataset.describe()
        #self.train_stats.pop("Points Scored")
        self.train_stats = self.train_stats.transpose()
        
        #normalize the data
        normed_train_data = self.sigmoid(self.train_dataset)
        normed_test_data = self.sigmoid(self.test_dataset)

        #build the model
        model = self.build_model()
     #   model.summary()
        example_batch = normed_train_data
   #     print((example_batch.keys()))
        example_result = model.predict(example_batch)
    #    example_result

        EPOCHS = 1000
        early_stop = keras.callbacks.EarlyStopping(monitor='loss', patience=10)
        history = model.fit(normed_train_data, self.train_labels, epochs=EPOCHS, callbacks=[early_stop])

        #get key metrics
        loss, mae, mse = model.evaluate(normed_test_data, self.test_labels, verbose=0)

        test_predictions = model.predict(normed_test_data).flatten()


        
        #make prediction
        normed_prediction_data = self.sigmoid(prediction_data)
        game_prediction = model.predict(normed_prediction_data).flatten()
        
        return(game_prediction, mae) #return predicted values
