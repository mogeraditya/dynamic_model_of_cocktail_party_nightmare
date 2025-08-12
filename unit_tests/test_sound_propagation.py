import sys
sys.path.insert(1, '.')

import unittest
from supporting_files.vectors import Vector
import supporting_files.constants as Constants
import math
from players.direct_sound_w_inheritance import DirectSound
from players.echo_sound import EchoSound

import random        


class TestingSoundPropagation(unittest.TestCase):
    def setUp(self):
        self.sound_start_point= Vector(0,0)
        self.points_to_test= [Vector(1,1), Vector(-1,1), Vector(1,-1), Vector(-1,-1)]
        self.creation_time= 0
        self.emitter_id= "tester"
        

    def test_radius_after_time(self):
        #initialize the sound
        sound = DirectSound(
                parameters_df= self.parameters_df,
                origin= self.sound_start_point,
                creation_time= self.creation_time,
                emitter_id= self.emitter_id
            )
        time_passed = 5 #seconds
        sound.update(time_passed)
        calculated_radius= time_passed * Constants.SOUND_SPEED
        radius_of_sound_after_update= sound.current_radius
        self.assertTrue((radius_of_sound_after_update==calculated_radius))
        
    def test_sound_disk_width(self):
        sound = DirectSound(
                parameters_df= self.parameters_df,
                origin= self.sound_start_point,
                creation_time= self.creation_time,
                emitter_id= self.emitter_id
            )
        time_    

    # def test_check_if_given_point_between_two_lines(self):

    #     expected_true_false= [True, True, True, False, False]
    #     computed_true_false= [check_if_given_point_between_two_lines(self.lines, i) 
    #                           for i in self.points_to_test]
    #     # print(computed_true_false)
    #     self.assertTrue((expected_true_false==computed_true_false))

    # def test_check_distance(self):
    #     number_of_d = 2; theta=np.pi/4
    #     expected_true_false= [True, False, False, False, False]
    #     computed_true_false= [check_distance(number_of_d,self.kwargs["min_spacing"], i, theta, self.lines)
    #                             for i in self.points_to_test]
    #     print(computed_true_false)
    #     self.assertTrue((expected_true_false==computed_true_false))
        
    #the other function just implements already tested functions and therefore doesnt require unit test
if __name__ == '__main__':

    unittest.main()