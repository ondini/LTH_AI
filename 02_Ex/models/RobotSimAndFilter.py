
import random
import numpy as np

from models import TransitionModel,ObservationModel,StateModel

class RobotSim:
    def __init__(self, sm, tm, om):
        self.__sm = sm # state model
        self.__tm = tm # transition model
        self.__om = om # observation model
    
    def step(self, current_state):
        # get the transition probability matrix
        T = self.__tm.get_T()
        # get probabilities for successor states
        pT = T[current_state, :]
        # sample a successor state
        next_state = np.random.choice(self.__sm.get_num_of_states(), p=pT) 

        # get the observation probability vector
        pO = self.__om.get_o_reading_for_state(next_state)
        # sample an observation
        sense = np.random.choice(self.__om.get_nr_of_readings(), p=pO)
        if sense == self.__om.get_nr_of_readings() - 1:
            sense = None

        print("RobotSim: current_state = ", self.__sm.state_to_pose(current_state) ," next_state = ", self.__sm.state_to_pose(next_state), "sense = ", self.__sm.reading_to_position(sense))
        return next_state, sense
        

class HMMFilter:
    def __init__(self, sm, tm, om):
        self.__sm = sm # state model
        self.__tm = tm # transition model
        self.__om = om # observation model
        self.__beliefs = np.ones(self.__sm.get_num_of_states()) / (self.__sm.get_num_of_states())
    
    def update(self, reading):
        self.__beliefs = self.__om.get_o_reading(reading) @ self.__tm.get_T_transp() @ self.__beliefs
        self.__beliefs = self.__beliefs / np.sum(self.__beliefs)
        
        return self.__beliefs
    

        
        
        
