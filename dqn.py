import environment
import util
import random
from collections import deque

import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = ""


import keras as K
import numpy as np

class DQN:

    def __init__(self, env, memory_len = 2000, gamma = 0.95, epsilon = 1.0, epsilon_min = 0.01, epsilon_decay = 0.995, learning_rate = 0.01, tau = 0.05):
        self.env = env
        self.memory = deque(maxlen=memory_len)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.tau = tau

        # the input of the neural network is the occupancy of each base station and the actual bitrate of the UE requesting the connection
        self.input_count = (len(env.bs_list) * 2) + 1
        # the output of the neural network is the Q-values corresponding to the actions
        # the action corresponds to which base station will accept the incoming connection from the UE
        self.output_count = len(env.bs_list)

        self.model = self.create_model()
        self.target_model = self.create_model()

    
    def create_model(self):
        model = K.models.Sequential()
        model.add(K.layers.Dense(24, input_dim = self.input_count, activation = "relu"))
        model.add(K.layers.Dense(48, activation = "relu"))
        model.add(K.layers.Dense(24, activation = "relu"))
        model.add(K.layers.Dense(self.output_count))
        model.compile(loss = "mean_squared_error", optimizer = K.optimizers.Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, new_state, done): 
        self.memory.append([state, action, reward, new_state, done])

    def replay(self):
        batch_size = 32
        if len(self.memory) < batch_size: 
            return
        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            state, action, reward, new_state, done = sample
            target = self.target_model.predict(state)
            if done:
                target[0][action] = reward
            else:
                Q_future = max(self.target_model.predict(new_state)[0])
                target[0][action] = reward + Q_future * self.gamma
            self.model.fit(state, target, epochs=1, verbose=0)
    
    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i]
        self.target_model.set_weights(target_weights)
    
    def act(self, state, rsrp):
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            return random.choice(list(rsrp))
        print("ACTION VECTOR FROM DQN %s" %self.model.predict(state)[0])
        prediction = self.model.predict(state)[0]

        #this to avoid that the choosen AP is not visible by the user
        actual_prediction = []
        for i in range(0, len(prediction)):
            if i in rsrp:
                actual_prediction.append(prediction[i])
        return np.argmax(actual_prediction)

    def save_model(self, path):
        self.model.save(path)   
    


    