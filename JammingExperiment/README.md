# Jamming Experiment

We aim to test our controller in similar setting as Amichai et al 2015. 
---

## Description of setup
1. Since our simulations are 2D, agents are made to move in a 390cm by 260cm arena. 
2. Jammers are modelled as objects that call with the same parameters as the bat being tested. This means all the parameters that influence a bat's call are used as the call parameters of the jammers. Note however this means that jammer calls are not emitted at the same time as the bat; its just the initial parameters that are the same. Jammer are also out of sync with each other.  
3. Speaker positions are taken directly from Amichai et al 2015. Speakers on the top of the ceiling are projected to the same plane as the speakers on the side walls. Bats do not collide with the projected ceiling jammers.

