import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor

        # Set any additional class parameters as needed
        self.trial = 1.0

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)

        # If 'testing' is True, set epsilon and alpha to 0
        if testing == True:
            self.epsilon = 0
            self.alpha = 0
        else:
            self.trial += 1 # Update additional class parameters as needed
            
            #### Update epsilon using a decay function of your choice
            #self.epsilon = self.epsilon - 0.05 
            #self.epsilon -= 1.0 / (self.trial**2) 
            self.epsilon = self.epsilon * 0.999  #from udacity forum

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline
      
        # Set 'state' as a tuple of relevant data for the agent        
        state = (inputs['left'], inputs['light'], inputs['oncoming'], waypoint)
        return state

    def get_maxQ(self, state):
        """ The get_maxQ function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """
        maxQ = max(self.Q[state].values())
        return maxQ

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        # When learning, check if the 'state' is not in the Q-table
        if self.learning == True:
            if state not in self.Q.keys():
                self.Q[state] = dict() # If it is not, create a new dictionary for that state
                for action in self.valid_actions:
                    self.Q [state][action]=0.0 #   Then, for each action available, set the initial Q-value to 0.0

        return 
  
    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in.   - exploration and exploitation part [agent exploits first and then explores]. """
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        if self.learning == False:
            # When not learning, choose a random action
            action = random.choice(self.valid_actions)
            print("Choose Action #1: randomly --> {}".format(action))
        else: 
            # When learning, choose a random action with 'epsilon' probability
            if (random.random() < self.epsilon):
                action = random.choice(self.valid_actions)
                print ("Epsilon ====>  {}".format(self.epsilon))
                print ("Trial ====>  {}".format(self.trial))
                print("Choose Action #2:  random action with epsilon probability --> {}".format(action))
            else: 
                # Be sure that when choosing an action with highest Q-value that you randomly select between actions that "tie".
                actionsToChooseFrom = [k for k, v  in self.Q[state].items() if v == self.get_maxQ(state)]
                action = random.choice(actionsToChooseFrom)
                print("Choose Action #3: choosing action with Highest Q-value --> {}".format(action))

        return action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives a reward. This function does not consider future rewards 
            when conducting learning. """
        
        # When learning, implement the value iteration update rule
        if self.learning == True:
                #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
                #self.Q[state][action] += self.alpha*(reward-self.Q[state][action])  
                self.Q[state][action] = (1-self.alpha)*self.Q[state][action] + self.alpha*reward
        return 

    
        
    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action) # Receive a reward
        self.learn(state, action, reward)   # Q-learn
        return
            
def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning=True, alpha=0.5, epsilon=1)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.01, log_metrics=True, display=False, optimized=True)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=100, tolerance =0.05)


if __name__ == '__main__':
    run()
