
#
# The Localizer binds the models together and controls the update cycle in its "update" method.
#

import numpy as np
import matplotlib.pyplot as plt
# The Localizer is the "controller" for the process. In its update()-method, at the moment a mere skeleton, 
# one cycle of the localisation process should be implemented by you. The return values of update() 
# are assumed to go in exactly this form into the viewer, this means that you should only modify the 
# return-parameters of update() if you do not want to use the graphical interface (or you need to change that too!)

import random
import importlib

from models import StateModel,TransitionModel,ObservationModel,RobotSimAndFilter


class Localizer:
    def __init__(self, sm, version = 0):

        self.__sm = sm

        self.__tm = TransitionModel(self.__sm)
        self.__om = ObservationModel(self.__sm)
        self.version = version  # version for evaluation purposes: 0 = full, 1 = no observation matrix, 2 = no transition matrix
        # self.eval_type = eval_type # 0 = evaluation for one max prob., 1 = evaluation for sum over all states corresponding to one cell

        # change in initialise in case you want to start out with something else
        # initialise can also be called again, if the filtering is to be reinitialised without a change in grid size
        self.initialise()

    # retrieve the transition model that we are currently working with
    def get_transition_model(self) -> np.array:
        return self.__tm

    # retrieve the observation model that we are currently working with
    def get_observation_model(self) -> np.array:
        return self.__om

    # the current true pose (x, y, h) that should be kept in the local variable __trueState
    def get_current_true_pose(self) -> (int, int, int):
        x, y, h = self.__sm.state_to_pose(self.__trueState)
        return x, y, h

    # the current probability distribution over all states
    def get_current_f_vector(self) -> np.array(float):
        return self.__fVec

    # the current sensor reading (as position in the grid). "Nothing" is expressed as None
    def get_current_reading(self) -> (int, int):
        ret = None
        if self.__sense != None:
            ret = self.__sm.reading_to_position(self.__sense)
        return ret;

    # get the currently most likely position, based on single most probable pose
    def most_likely_position(self) -> (int, int):
        return self.__estimate

    ################################### Here you need to really fill in stuff! ##################################
    # if you want to start with something else, change the initialisation here!
    #
    # (re-)initialise for a new run without change of size
    def initialise(self):
        self.__trueState = random.randint(0, self.__sm.get_num_of_states() - 1)
        print("Inint state ", self.__sm.state_to_pose(self.__trueState))
        self.__sense = None
        self.__fVec = np.ones(self.__sm.get_num_of_states()) / (self.__sm.get_num_of_states())
        self.__estimate = self.__sm.state_to_position(np.argmax(self.__fVec))
    
        self.__rs = RobotSimAndFilter.RobotSim(self.__sm, self.__tm, self.__om)
        self.__HMM = RobotSimAndFilter.HMMFilter(self.__sm, self.__tm, self.__om)
        
    #
    #  Implement the update cycle:
    #  - robot moves one step, generates new state / pose
    #  - sensor produces one reading based on the true state / pose
    #  - filtering approach produces new probability distribution based on
    #  sensor reading, transition and sensor models
    #
    #  Add an evaluation in terms of Manhattan distance (average over time) and "hit rate"
    #  you can do that here or in the simulation method of the visualisation, using also the
    #  options of the dashboard to show errors...
    #
    #  Report back to the caller (viewer):
    #  Return
    #  - true if sensor reading was not "nothing", else false,
    #  - AND the three values for the (new) true pose (x, y, h),
    #  - AND the two values for the (current) sensor reading (if not "nothing")
    #  - AND the current estimated position
    #  - AND the error made in this step
    #  - AND the new probability distribution
    #
    def update(self) -> (bool, int, int, int, int, int, int, int, int, np.array(1)) :
        # update all the values to something sensible instead of just reading the old values...
        # 

        # move one step from __trueState, generate new __trueState
        self.__trueState, self.__sense = self.__rs.step(self.__trueState)
        
        # this block can be kept as is
        ret = False  # in case the sensor reading is "nothing" this is kept...
        tsX, tsY, tsH = self.__sm.state_to_pose(self.__trueState)
        srX = -1
        srY = -1
        if self.__sense != None:
            srX, srY = self.__sm.reading_to_position(self.__sense)
            ret = True
        
        # update the probability distribution
        self.__estimate = np.argmax(self.__HMM.update(self.__sense, self.version))
        eX, eY = self.__sm.state_to_position(self.__estimate)
        print("Estimate ", self.__sm.state_to_pose(self.__estimate))
        
        # this should be updated to spit out the actual error for this step
        error = self.ManhattanDistance(self.__trueState, self.__estimate)    
        
        # if you use the visualisation (dashboard), this return statement needs to be kept the same
        # or the visualisation needs to be adapted (your own risk!)
        return ret, tsX, tsY, tsH, srX, srY, eX, eY, error, self.__fVec


    def ManhattanDistance(self, trueState, estimate):
        truePosition = self.__sm.state_to_position(trueState)
        estimatedPosition = self.__sm.state_to_position(estimate)
        return abs(truePosition[0] - estimatedPosition[0]) + abs(truePosition[1] - estimatedPosition[1])