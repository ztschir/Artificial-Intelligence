import random
from OpenNero import *
from common import *
import Maze
from Maze.constants import *

from heapq import heappush, heappop

def dfs_heuristic(r,c):
    return 0

def manhattan_heuristic(r,c):
    return (ROWS - r) + (COLS - c)

def get_action_index(move):
    if move in MAZE_MOVES:
        action = MAZE_MOVES.index(move)
        print 'Picking action', action, 'for move', move
        return action
    else:
        return None

class Cell:
    def __init__(self, h, r, c):
        self.h = h
        self.r = r
        self.c = c
    def __cmp__(self, other):
        return cmp(self.h, other.h)

class RandomAgent(AgentBrain):
    """
    A uniform random baseline - a very simple agent
    """
    def __init__(self):
        AgentBrain.__init__(self) # have to make this call

    def initialize(self, init_info):
        """
        create a new agent
        """
        self.action_info = init_info.actions
        return True

    def start(self, time, observations):
        """
        return first action given the first observations
        """
        return self.action_info.random()

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous action and the new observations
        """
        return self.action_info.random()

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        return True

class CustomRLAgent(AgentBrain):
    """
    Write your custom reinforcement learning agent here!
    """
    def __init__(self, gamma, alpha, epsilon):
        """
        Constructor that is called from CustomRLRobot.xml
        Parameters:
        @param gamma reward discount factor (between 0 and 1)
        @param alpha learning rate (between 0 and 1)
        @param epsilon parameter for the epsilon-greedy policy (between 0 and 1)
        """
        AgentBrain.__init__(self) # initialize the superclass
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        """
        Our Q-function table. Maps from a tuple of observations (state) to 
        another map of actions to Q-values. To look up a Q-value, call the predict method.
        """
        self.Q = {} # our Q-function table
        print 
    
    def __str__(self):
        return self.__class__.__name__ + \
            ' with gamma: %g, alpha: %g, epsilon: %g' \
            % (gamma, alpha, epsilon)
    
    def initialize(self, init_info):
        """
        Create a new agent using the init_info sent by the environment
        """
        self.action_info = init_info.actions
        self.sensor_info = init_info.sensors
        return True
    
    def predict(self, observations, action):
        """
        Look up the Q-value for the given state (observations), action pair.
        """
        o = tuple([x for x in observations])
        if o not in self.Q:
            return 0
        else:
            return self.Q[o][action]
    
    def update(self, observations, action, new_value):
        """
        Update the Q-function table with the new value for the (state, action) pair
        and update the blocks drawing.
        """
        o = tuple([x for x in observations])
        actions = self.get_possible_actions(observations)
        if o not in self.Q:
            self.Q[o] = [0 for a in actions]
        self.Q[o][action] = new_value
        self.draw_q(o)
    
    def draw_q(self, o):
        e = get_environment()
        if hasattr(e, 'draw_q'):
            e.draw_q(o, self.Q)

    def get_possible_actions(self, observations):
        """
        Get the possible actions that can be taken given the state (observations)
        """
        aMin = self.action_info.min(0)
        aMax = self.action_info.max(0)
        actions = range(int(aMin), int(aMax+1))
        return actions
        
    def get_max_action(self, observations):
        """
        get the action that is currently estimated to produce the highest Q
        """
        actions = self.get_possible_actions(observations)
        max_action = actions[0]
        max_value = self.predict(observations, max_action)
        for a in actions[1:]:
            value = self.predict(observations, a)
            if value > max_value:
                max_value = value
                max_action = a
        return (max_action, max_value)

    def get_epsilon_greedy(self, observations, max_action = None, max_value = None):
        """
        get the epsilon-greedy action
        """
        actions = self.get_possible_actions(observations)
        if random.random() < self.epsilon: # epsilon of the time, act randomly
            return random.choice(actions)
        elif max_action is not None and max_value is not None:
            # we already know the max action
            return max_action
        else:
            # we need to get the max action
            (max_action, max_value) = self.get_max_action(observations)
            return max_action
    
    def start(self, time, observations):
        """
        Called to figure out the first action given the first observations
        @param time current time
        @param observations a DoubleVector of observations for the agent (use len() and [])
        """
        self.previous_observations = observations
        self.previous_action = self.get_epsilon_greedy(observations)
        return self.previous_action

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous action and the new observations
        @param time current time
        @param observations a DoubleVector of observations for the agent (use len() and [])
        @param the reward for the agent
        """
        # get the reward from the previous action
        r = reward[0]
        
        # get the updated epsilon, in case the slider was changed by the user
        self.epsilon = get_environment().epsilon
        
        # get the old Q value
        Q_old = self.predict(self.previous_observations, self.previous_action)
        
        # get the max expected value for our possible actions
        (max_action, max_value) = self.get_max_action(observations)
        
        # update the Q value
        self.update( \
            self.previous_observations, \
            self.previous_action, \
            Q_old + self.alpha * (r + self.gamma * max_value - Q_old) )
        
        # select the action to take
        action = self.get_epsilon_greedy(observations, max_action, max_value)
        self.previous_observations = observations
        self.previous_action = action
        return action

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        # get the reward from the last action
        r = reward[0]
        o = self.previous_observations
        a = self.previous_action

        # get the updated epsilon, in case the slider was changed by the user
        self.epsilon = get_environment().epsilon

        # Update the Q value
        Q_old = self.predict(o, a)
        q = self.update(o, a, Q_old + self.alpha * (r - Q_old) )
        return True

class SearchAgent(AgentBrain):
    """ Base class for maze search agents """

    def __init__(self):
        """ constructor """
        AgentBrain.__init__(self)
    def highlight_path(self):
        """
        backtrack to highlight the path
        """
        # retrace the path
        node = (ROWS - 1, COLS - 1)
        while node in self.backpointers:
            self.mark_path(node[0],node[1])
            next_node = self.backpointers[node]
            del self.backpointers[node]
            node = next_node
            if node == (0,0):
                break

class DFSSearchAgent(SearchAgent):
    """
    Depth first search implementation
    """
    def __init__(self):
        """
        A new Agent
        """
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.visited = set([])
        self.adjlist = {}
        self.parents = {}
        self.backpointers = {}

    def dfs_action(self, observations):
        r = observations[0]
        c = observations[1]
        # if we have not been here before, build a list of other places we can go
        if (r,c) not in self.visited:
            tovisit = []
            for m, (dr,dc) in enumerate(MAZE_MOVES):
                r2, c2 = r+dr, c+dc
                if not observations[2 + m]: # can we go that way?
                    if (r2,c2) not in self.visited:
                        tovisit.append( (r2,c2) )
                        self.parents[ (r2,c2) ] = (r,c)
            # remember the cells that are adjacent to this one
            self.adjlist[(r, c)] = tovisit
        # if we have been here before, check if we have other places to visit
        adjlist = self.adjlist[(r,c)]
        k = 0
        while k < len(adjlist) and adjlist[k] in self.visited:
            k += 1
        # if we don't have other neighbors to visit, back up
        if k == len(adjlist):
            current = self.parents[(r,c)]
        else: # otherwise visit the next place
            current = adjlist[k]
        self.visited.add((r,c)) # add this location to visited list
        get_environment().mark_maze_blue(r, c) # mark it as blue on the maze
        v = self.constraints.get_instance() # make the action vector to return
        dr, dc = current[0] - r, current[1] - c # the move we want to make
        v[0] = get_action_index( (dr, dc) )
        # remember how to get back
        if (r+dr,c+dc) not in self.backpointers:
            self.backpointers[(r+dr, c+dc)] = (r,c)
        return v

    def initialize(self, init_info):
        self.constraints = init_info.actions
        return True

    def start(self, time, observations):
        # return action
        return self.dfs_action(observations)

    def reset(self):
        self.visited = set([])
        self.parents = {}
        self.backpointers = {}

    def act(self, time, observations, reward):
        # return action
        return self.dfs_action(observations)

    def end(self, time, reward):
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        self.reset()
        return True

    def mark_path(self, r, c):
        get_environment().mark_maze_white(r,c)

class GenericSearchAlgorithm(SearchAgent):
    """
    Generic search algorithm with retrace and a heuristic function
    """
    def __init__(self):
        """
        constructor
        """
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        SearchAgent.__init__(self)
        self.backpointers = {}
        self.reset()

    def reset(self):
        """
        Reset the agent
        """
        self.parents = {}
        self.queue = [] # queue of cells to visit (front)
        self.visited = set([]) # set of nodes we have visited
        self.enqueued = set([]) # set of things in the queue (superset of visited)
        self.backpointers = {} # a dictionary from nodes to their predecessors
        self.goal = None # we have no idea where to go at first

    def initialize(self, init_info):
        """
        initialize the agent with sensor and action info
        """
        self.constraints = init_info.actions
        return True

    def get_next_step(self, r1, c1, r2, c2):
        """
        return the next step when trying to get from current r1,c1 to target r2,c2
        """
        back2 = [] # cells between origin and r2,c2
        r,c = r2,c2 # back track from target
        while (r,c) in self.backpointers:
            r,c = self.backpointers[(r,c)]
            if (r1,c1) == (r,c): # if we find starting point, we need to move forward
                return back2[-1] # return the last step
            back2.append((r,c))
        return self.backpointers[(r1,c1)]

    def enque(self, cell ):
        self.queue.append( cell )

    def deque(self):
        return self.queue.pop(0)

    def get_action(self, r, c, observations):
        """
        Given:
         - some places we could go in our queue
         - some backtracking links on how we got there
        Return:
         - The next step for the agent to take
        """
        if not self.goal: # first, figure out where we are trying to go
            (r2, c2) = self.deque()
            self.mark_target(r2,c2)
            self.goal = (r2, c2)
        # then, check if we can get there
        r2, c2 = self.goal
        dr, dc = r2 - r, c2 - c
        action = get_action_index((dr,dc))
        v = self.constraints.get_instance() # make the action vector to return
        # first, is the node reachable in one action?
        if action is not None and observations[2 + action] == 0:
            v[0] = action # if yes, do that action!
        else:
            # if not, we have to figure out a path to get there from the backtracking dictionary
            (r2,c2) = self.get_next_step(r,c,r2,c2)
            dr, dc = r2 - r, c2 - c # how to get back there?
            v[0] = get_action_index((dr,dc)) # what action is that?
        return v # return the action

    def visit(self, row, col, observations):
        """
        visit the node row, col and decide where we can go from there
        """
        if (row,col) not in self.visited:
            self.mark_visited(row,col)
        # we are at row, col, so we mark it visited:
        self.visited.add((row,col))
        self.enqueued.add((row,col)) # just in case
        # if we have reached our current subgoal, mark it visited
        if self.goal == (row, col):
            print  'reached goal: ' + str((row, col))
            self.goal = None
        # then we queue up some places to go next
        for i, (dr,dc) in enumerate(MAZE_MOVES):
            if observations[2+i] == 0: # are we free to perform this action?
                # the action index should correspond to sensor index - 2
                r2 = row + dr # compute the row we could move to
                c2 = col + dc # compute the col we could move to
                if (r2,c2) not in self.enqueued:
                    self.mark_the_front(row,col,r2,c2)
                    self.enqueued.add((r2,c2))
                    self.enque( (r2,c2) )
                    assert self.backpointers.get((row,col)) != (r2,c2)
                    self.backpointers[(r2,c2)] = row, col # remember where we (would) come from

    def start(self, time, observations):
        """
        Choose initial action after receiving the first sensor vector.
        For the manual A* search, we enqueue the neighboring nodes and move to one of them.
        """
        # interpret the observations
        row = int(observations[0])
        col = int(observations[1])
        # first, visit the node we are in and queue up some places to go
        self.visit(row, col, observations)
        # now we have some candidate states and a way to return if we don't like it there, so let's try one!
        return self.get_action(row,col,observations)

    def act(self, time, observations, reward):
        """
        Choose an action after receiving the current sensor vector and the instantaneous reward from the previous time step.
        For the manual A* search, we deque our next node and check if we can go there. If we can, we do, and mark the node visited.
        If we cannot, we have to follow the path to the goal.
        """
        # interpret the observations
        row = int(observations[0])
        col = int(observations[1])
        # first, visit the node we are in and queue up some places to go
        self.visit(row, col, observations)
        # now we have some candidate states and a way to return if we don't like it there, so let's try one!
        return self.get_action(row,col,observations)

    def end(self, time, reward):
        """
        at the end of an episode, the environment tells us the final reward
        """
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        self.reset()
        return True

    def mark_the_front(self, r, c, r2, c2):
        get_environment().mark_maze_green(r2,c2)

    def mark_target(self, r, c):
        get_environment().mark_maze_yellow(r,c)

    def mark_visited(self, r, c):
        get_environment().mark_maze_blue(r,c)

    def mark_path(self, r, c):
        get_environment().mark_maze_white(r,c)

class BFSSearchAgent(GenericSearchAlgorithm):
    """
    Egocentric Breadth First Search algorithm.
    The only change is that we use a simple queue instead of a priority queue
    """
    def __init__(self):
        """
        A new Agent
        """
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        GenericSearchAlgorithm.__init__(self)

    def enque(self, cell ):
        self.queue.append(cell)

    def deque(self):
        return self.queue.pop(0)

    def get_action(self, r, c, observations):
        """
        we override the get_action method so that we can spawn marker agents and teleport
        """
        if not self.goal: # first, figure out where we are trying to go
            (r2,c2) = self.deque()
            get_environment().unmark_maze_agent(r2,c2)
            get_environment().mark_maze_yellow(r2,c2)
            self.goal = (r2, c2)
        # then, check if we can get there
        r2, c2 = self.goal
        dr, dc = r2 - r, c2 - c
        action = get_action_index((dr,dc)) # try to find the action (will return None if it's not there)
        v = self.constraints.get_instance() # make the action vector to return
        # first, is the node reachable in one action?
        if action is not None and observations[2 + action] == 0:
            v[0] = action # if yes, do that action!
        else:
            # if not, we should teleport and return null action
            get_environment().teleport(self, r2, c2)
            v[0] = 4
        return v # return the action

    def mark_the_front(self, r, c, r2, c2):
        get_environment().mark_maze_green(r2,c2)
        get_environment().mark_maze_agent("data/shapes/character/SydneyStatic.xml", r, c, r2, c2)

    def mark_visited(self, r, c):
        get_environment().unmark_maze_agent(r,c)
        get_environment().mark_maze_blue(r,c)

class AStarSearchAgent(GenericSearchAlgorithm):
    """
    Egocentric A* algorithm - actually it is just like BFS but the queue is a priority queue
    """
    def __init__(self):
        """
        A new Agent
        """
        # this line is crucial, otherwise the class is not recognized as an AgentBrainPtr by C++
        GenericSearchAlgorithm.__init__(self)

    def reset(self):
        GenericSearchAlgorithm.reset(self)
        # minimize the Manhattan distance
        self.heuristic = manhattan_heuristic

    def enque(self, cell ):
        (r,c) = cell
        heappush(self.queue, Cell(self.heuristic(r, c), r, c))

    def deque(self):
        cell = heappop(self.queue)
        h, r, c = cell.h, cell.r, cell.c
        return (r,c)

class FrontAStarSearchAgent(AStarSearchAgent):
    """
    Egocentric A* algorithm with teleportation between fronts
    """
    def get_action(self, r, c, observations):
        """
        we override the get_action method so that we can teleport from place to place
        """
        if not self.goal: # first, figure out where we are trying to go
            (r2, c2) = self.deque()
            get_environment().unmark_maze_agent(r2,c2)
            get_environment().mark_maze_yellow(r2,c2)
            self.goal = (r2, c2)
        # then, check if we can get there
        r2, c2 = self.goal
        dr, dc = r2 - r, c2 - c
        action = get_action_index((dr,dc)) # try to find the action (will return None if it's not there)
        v = self.constraints.get_instance() # make the action vector to return
        # first, is the node reachable in one action?
        if action is not None and observations[2 + action] == 0:
            v[0] = action # if yes, do that action!
        else:
            # if not, we should teleport and return null action
            get_environment().teleport(self, r2, c2)
            v[0] = MAZE_NULL_MOVE
        return v # return the action

class CloningAStarSearchAgent(FrontAStarSearchAgent):
    """
    Egocentric A* algorithm with teleportation between fronts and fronts marked by stationary agents
    """
    def get_action(self, r, c, observations):
        """
        we override the get_action method so that we can spawn marker agents and teleport
        """
        if not self.goal: # first, figure out where we are trying to go
            (r2,c2) = self.deque()
            get_environment().unmark_maze_agent(r2,c2)
            get_environment().mark_maze_yellow(r2,c2)
            self.goal = (r2, c2)
        # then, check if we can get there
        r2, c2 = self.goal
        dr, dc = r2 - r, c2 - c
        action = get_action_index((dr,dc)) # try to find the action (will return None if it's not there)
        v = self.constraints.get_instance() # make the action vector to return
        # first, is the node reachable in one action?
        if action is not None and observations[2 + action] == 0:
            v[0] = action # if yes, do that action!
        else:
            # if not, we should teleport and return null action
            get_environment().teleport(self, r2, c2)
            v[0] = 4
        return v # return the action

    def mark_the_front(self, r, c, r2, c2):
        get_environment().mark_maze_green(r2,c2)
        get_environment().mark_maze_agent("data/shapes/character/SydneyStatic.xml", r, c, r2, c2)

    def mark_visited(self, r, c):
        get_environment().unmark_maze_agent(r,c)
        get_environment().mark_maze_blue(r,c)

class FirstPersonAgent(AgentBrain):
    """
    A human-controlled agent
    """
    key_pressed = None
    action_map = CONT_MAZE_ACTIONS
    def __init__(self):
        AgentBrain.__init__(self) # do not remove!
        self.time = 0
    def initialize(self, init_info):
        self.constraints = init_info.actions
        return True
    def key_action(self):
        self.time += 1
        action = self.constraints.get_instance()
        if FirstPersonAgent.key_pressed:
            action[0] = FirstPersonAgent.action_map[FirstPersonAgent.key_pressed]
            FirstPersonAgent.key_pressed = None
        else:
            action[0] = MAZE_NULL_MOVE
        return action
    def start(self, time, observations):
        return self.key_action()
    def act(self, time, observations, reward):
        return self.key_action()
    def end(self, time, reward):
        return True

class MoveForwardAndStopAgent(AgentBrain):
    """
    Just move forward and stop!
    """
    def __init__(self):
        AgentBrain.__init__(self) # do not remove!
    def initialize(self, init_info):
        self.actions = init_info.actions # action constraints
        self.idle_action = self.actions.get_instance()
        self.idle_action[0] = MAZE_NULL_MOVE # do-nothing action
        return True
    def start(self, time, observations):
        marker_states = get_environment().marker_states
        if self.state.id in marker_states:
            ((r1,c1), (r2,c2)) = marker_states[self.state.id]
            v = self.actions.get_instance()
            dr, dc = r2-r1, c2-c1
            a = get_action_index( (dr, dc) )
            if a is not None:
                # return the action in the (dr,dc) direction
                v[0] = a
                return v
        return self.idle_action
    def act(self, time, observations, reward):
        return self.idle_action
    def end(self, time, reward):
        return True









        

class MyRLAgent(AgentBrain):
    """
    Write your custom reinforcement learning agent here!
    """


    def __init__(self, gamma, alpha, epsilon):
        """
        Constructor that is called from CustomRLRobot.xml
        Parameters:
        @param gamma reward discount factor (between 0 and 1)
        @param alpha learning rate (between 0 and 1)
        @param epsilon parameter for the epsilon-greedy policy (between 0 and 1)
        """
        AgentBrain.__init__(self) # initialize the superclass

        # Change your mode here!!
        # 0 for tabular
        # 1 for tiling approximator
        # 2 for nearest neighbors
        self.mode = 2
        
        self.gamma = gamma
        self.alpha = alpha
        self.epsilon = epsilon
        """
        Our Q-function table. Maps from a tuple of observations (state) to 
        another map of actions to Q-values. To look up a Q-value, call the predict method.
        """
        self.Q = {} # our Q-function table
        print 
    
    def __str__(self):
        return self.__class__.__name__ + \
            ' with gamma: %g, alpha: %g, epsilon: %g' \
            % (gamma, alpha, epsilon)
    
    def initialize(self, init_info):
        """
        Create a new agent using the init_info sent by the environment
        """
        self.action_info = init_info.actions
        self.sensor_info = init_info.sensors
        return True

    def predict(self, observations, action):
        """
        Look up the Q-value for the given state (observations), action pair.
        """
        o = tuple([x for x in observations])

        if(self.mode < 2):
            if o not in self.Q:
                return (0, 0)
            else:
                return (self.Q[o][action],0)
        
        course_position = self.get_coarse_adj(observations)
        cur_pos = self.fine_grain_pos(observations[0], observations[1])

        closest_positions = [cur_pos]
        
        for pos in course_position:

            ori_pos = self.course_grain_pos(o[0], o[1])
            new_pos = self.course_grain_pos(pos[0], pos[1])
            dr = new_pos[0] - ori_pos[0]
            dc = new_pos[1] - ori_pos[1]
            
            if (ori_pos, new_pos) in get_environment().maze.walls:
                continue

            if (new_pos[0] < 0 or new_pos[1] < 0 or
                new_pos[0] > 8 or new_pos[1] > 8):
                continue

            # Diag
            if (dr != 0 and dc != 0):
                row_check = tuple([ori_pos[0], new_pos[1]])
                col_check = tuple([new_pos[0], ori_pos[1]])

                if ((new_pos, row_check) in get_environment().maze.walls and
                    (new_pos, col_check) in get_environment().maze.walls):
                    continue

                if ((ori_pos, row_check) in get_environment().maze.walls and
                    (ori_pos, col_check) in get_environment().maze.walls):
                    continue

                if ((ori_pos, row_check) in get_environment().maze.walls and
                    (new_pos, col_check) in get_environment().maze.walls):
                    continue

                if ((new_pos, row_check) in get_environment().maze.walls and
                    (ori_pos, col_check) in get_environment().maze.walls):
                    continue
                    
                    
            if len(closest_positions) < 3:
                closest_positions.append(tuple([pos[0], pos[1]]))
            else:
                for prev_pos in closest_positions:
                    if(self.euclidean_dist(o[0], o[1], pos[0], pos[1])
                       < self.euclidean_dist(o[0], o[1], prev_pos[0], prev_pos[1])):
                       closest_positions.remove(tuple([prev_pos[0], prev_pos[1]]))
                       closest_positions.append(tuple([pos[0], pos[1]]))
                       break


        distance = [self.euclidean_dist(o[0], o[1], x[0],  x[1]) for x in closest_positions]

        print "Distances: " + str(distance) + " Sum: " + str(sum(distance))

        weights = [1 - x / sum(distance) for x in distance]


        weight_pos = []

        value = 0

        if (len(closest_positions) > 0 ):
            if (closest_positions[0] not in self.Q):
                value += 0
            else:
                value += weights[0] * self.Q[closest_positions[0]][action]
            weight_pos.append(tuple([closest_positions[0], weights[0]]))
        if (len(closest_positions) > 1 ):
            if (closest_positions[1] not in self.Q):
                value += 0
            else:
                value += weights[1] * self.Q[closest_positions[1]][action]
            weight_pos.append(tuple([closest_positions[1], weights[1]]))                
        if (len(closest_positions) > 2 ):
            if (closest_positions[2] not in self.Q):
                value += 0
            else:
                value += weights[2] * self.Q[closest_positions[2]][action]
            weight_pos.append(tuple([closest_positions[2], weights[2]]))
        return (value, weight_pos)
                    
     
    def update(self, observations, action, new_value):
        """
        Update the Q-function table with the new value for the (state, action) pair
        and update the blocks drawing.
        """
        o = tuple([x for x in observations])

        if(self.mode != 0):
            o = self.fine_grain_pos(observations[0], observations[1])

        actions = self.get_possible_actions(observations)


        if o not in self.Q:
            self.Q[o] = [0 for a in actions]

        if(math.isnan(new_value) or new_value is None):
            self.Q[o][action] = 0
        else:
            self.Q[o][action] = new_value
            
        
        self.draw_q(o)

    def fine_grain_pos(self, row, col, x = 0, y = 0):
        course_row = ((row - 10) // 20) + x
        truc_fine_row = (course_row + 1) * 20
        course_col = ((col - 10) // 20) + y
        truc_fine_col = (course_col + 1) * 20
        return tuple([truc_fine_row, truc_fine_col])
 
    def course_grain_pos(self, row, col, x = 0, y = 0):
        course_row = ((row - 10) // 20) + x
        course_col = ((col - 10) // 20) + y
        return tuple([course_row, course_col])
        
    def get_coarse_adj(self, observations):
        tl_pos  = self.fine_grain_pos(observations[0], observations[1], -1, 1)
        t_pos   = self.fine_grain_pos(observations[0], observations[1], 0, 1)
        tr_pos  = self.fine_grain_pos(observations[0], observations[1], 1, 1)
        r_pos   = self.fine_grain_pos(observations[0], observations[1], 1, 0)
        br_pos  = self.fine_grain_pos(observations[0], observations[1], 1, -1)
        b_pos   = self.fine_grain_pos(observations[0], observations[1], 0, -1)
        bl_pos  = self.fine_grain_pos(observations[0], observations[1], -1, -1)
        l_pos   = self.fine_grain_pos(observations[0], observations[1], -1, 0)
        return tuple([tl_pos, t_pos, tr_pos, r_pos, br_pos, b_pos, bl_pos, l_pos])
        
    def euclidean_dist(self, x1, y1, x2, y2):
        return math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))
        
    def draw_q(self, o):
        e = get_environment()
        if hasattr(e, 'draw_q'):
            e.draw_q(o, self.Q)

    def get_possible_actions(self, observations):
        """
        Get the possible actions that can be taken given the state (observations)
        """
        aMin = self.action_info.min(0)
        aMax = self.action_info.max(0)

        actions = range(int(aMin), int(aMax+1))
        return actions
        
    def get_max_action(self, observations):
        """
        get the action that is currently estimated to produce the highest Q
        """
        actions = self.get_possible_actions(observations)
        max_action = actions[0]
        (max_value, dummy) = self.predict(observations, max_action)
        for a in actions[1:]:
            (value, weight_pos) = self.predict(observations, a)
            if value > max_value:
                max_value = value
                max_action = a
        return (max_action, max_value)

    def get_epsilon_greedy(self, observations, max_action = None, max_value = None):
        """
        get the epsilon-greedy action
        """
        actions = self.get_possible_actions(observations)
        if random.random() < self.epsilon: # epsilon of the time, act randomly
            return random.choice(actions)
        elif max_action is not None and max_value is not None:
            # we already know the max action
            return max_action
        else:
            # we need to get the max action
            (max_action, max_value) = self.get_max_action(observations)
            return max_action
    
    def start(self, time, observations):
        """
        Called to figure out the first action given the first observations
        @param time current time
        @param observations a DoubleVector of observations for the agent (use len() and [])
        """
        self.previous_observations = observations
        self.previous_action = self.get_epsilon_greedy(observations)
        return self.previous_action

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous action and the new observations
        @param time current time
        @param observations a DoubleVector of observations for the agent (use len() and [])
        @param the reward for the agent
        """
        # get the reward from the previous action
        r = reward[0]
        
        # get the updated epsilon, in case the slider was changed by the user
        self.epsilon = get_environment().epsilon
        

        # get the old Q value
        (Q_old, weight_pos) = self.predict(self.previous_observations, self.previous_action)
        
        # get the max expected value for our possible actions
        (max_action, max_value) = self.get_max_action(observations)
        
        # update the Q value
        if (self.mode < 2):
            self.update( \
                         self.previous_observations, \
                         self.previous_action, \
                         Q_old + self.alpha * (r + self.gamma * max_value - Q_old) )

        
        #Nearest Neighbors
        else:
            self.update(weight_pos[0][0], self.previous_action, 
                        Q_old + self.alpha * weight_pos[0][1] * 
                        (r + self.gamma * max_value - Q_old) )

            if (len(weight_pos) > 1):
                self.update(weight_pos[1][0], self.previous_action,
                            Q_old + self.alpha * weight_pos[1][1] * 
                            (r + self.gamma * max_value - Q_old) )
            if( len(weight_pos) > 2):
                self.update(weight_pos[2][0], self.previous_action,
                            Q_old + self.alpha * weight_pos[2][1] * 
                            (r + self.gamma * max_value - Q_old) ) 
        
        # select the action to take
        action = self.get_epsilon_greedy(observations, max_action, max_value)
        self.previous_observations = observations
        self.previous_action = action
        return action

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        # get the reward from the last action
        r = reward[0]
        o = self.previous_observations
        a = self.previous_action

        # get the updated epsilon, in case the slider was changed by the user
        self.epsilon = get_environment().epsilon

        # Update the Q value
        Q_old = self.predict(o, a)
        q = self.update(o, a, Q_old + self.alpha * (r - Q_old) )
        return True
