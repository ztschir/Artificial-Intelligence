from OpenNero import *
from common import *
import BlocksTower
import random
from BlocksTower.environment import TowerEnvironment
from BlocksTower.constants import *
from copy import copy

###
#
# Action definitions:
# 0 Jump
# 1 Move Forward
# 2 Put Down
# 3 Pick Up
# 4 Rotate Right
# 5 Rotate Left
#
###

class TowerAgent(AgentBrain):
    """
    An agent designed to solve Towers of Hanoi
    """
    def __init__(self):
        AgentBrain.__init__(self) # have to make this call
        
    def move(self, frm, to):
        if frm == 'a' and to == 'b': return self.atob
        if frm == 'a' and to == 'c': return self.atoc
        if frm == 'b' and to == 'a': return self.btoa
        if frm == 'b' and to == 'c': return self.btoc
        if frm == 'c' and to == 'a': return self.ctoa
        if frm == 'c' and to == 'b': return self.ctob

    def dohanoi(self, n, to, frm, using):
        if n == 0: return
        prefix = '\t'.join(['' for i in range(self.num_towers - n)])
        strn = "Moving depth {n} from {frm} to {to} using {using}".format(n=n, frm=frm, to=to, using=using)
        for a in self.dohanoi(n-1, using, frm, to):
            yield a
        #self.state.label = strn
        for a in self.move(frm, to):
            yield a
        for a in self.dohanoi(n-1, to, using, frm):
            yield a

    def queue_init(self):
        self.init_queue = [1,5]
        self.atob = [5,1,4,3,4,1,5,2,]
        self.btoa = [3,5,1,4,2,4,1,5,]
        self.atoc = [5,1,4,3,4,1,1,5,2,5,1,4,]
        self.ctoa = [4,1,5,3,5,1,1,4,2,4,1,5,]
        self.btoc = [3,4,1,5,2,5,1,4,]
        self.ctob = [4,1,5,3,5,1,4,2,]
        self.end_queue = [0,0,0,5,5,1]

        from module import getMod
        self.num_towers = getMod().num_towers

        #self.state.label = 'Starting to Solve!'
        for a in self.init_queue:
            yield a
        for a in self.dohanoi(self.num_towers, 'b', 'a', 'c'):
            yield a
        #self.state.label = 'Problem Solved!'
        for a in self.end_queue:
            yield a

    def initialize(self,init_info):
        # Create new Agent
        self.action_info = init_info.actions
        return True
        
    def display_planner(self):
        """ show planner internals by running it externally """
        import subprocess
        # solve for show (user can click through)
        subproc = subprocess.Popen(['python', 'BlocksTower/recursive_solver.py'], stdout=subprocess.PIPE)
        plan = ''
        while True:
            try:
                out = subproc.stdout.read(1)
            except:
                break
            if out == '':
                break
            else:
                plan += out
        print plan        

    def start(self, time, sensors):
        """
        return first action given the first observations
        """
        self.display_planner()
        self.action_queue = self.queue_init()
        return self.action_queue.next()

    def reset(self):
        self.display_planner()
        self.action_queue = self.queue_init()
        return True

    def act(self, time, sensors, reward):
        """
        return an action given the reward for the previous action and the new observations
        """
        try:
            return self.action_queue.next()
        except:
            return 1

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        print  "Final reward: %f, cumulative: %f" % (reward[0], self.fitness[0])
        return True

    def destroy(self):
        """
        called when the agent is done
        """
        return True

class TowerAgent2(AgentBrain):
    """
    An agent that uses a STRIPS-like planner to solve the Towers of Hanoi problem
    """
    def __init__(self):
        AgentBrain.__init__(self) # have to make this call
        self.action_queue = [5] # rotate left to reset state first

    def initialize(self,init_info):
        """
        Create the agent.
        init_info -- AgentInitInfo that describes the observation space (.sensors),
                     the action space (.actions) and the reward space (.rewards)
        """
        self.action_info = init_info.actions
        return True

    def queue_init(self):
        import strips2
        import towers3 as towers
        import subprocess
        import strips2_show

        # solve for show (user can click through)
        subproc = subprocess.Popen(['python', 'BlocksTower/strips2.py'], stdout=subprocess.PIPE)
        plan = ''
        while True:
            try:
                out = subproc.stdout.read(1)
            except:
                break
            if out == '':
                break
            else:
                plan += out
        # actually solve to get the plan of actions
        plan = strips2.solve(towers.INIT, towers.GOAL, towers.ACTIONS)
        action_queue = [5]
        state = copy(towers.INIT)
        at = towers.Pole1
        for (move, what, frm, to) in plan:
            frm_pole = strips2_show.get_pole(state, frm)
            to_pole = strips2_show.get_pole(state, to)
            print what, frm, to, at, frm_pole, to_pole
            if at != frm_pole:
                action_queue += MOVES[(at, frm_pole)]
            action_queue += CARRY_MOVES[(frm_pole, to_pole)]
            move(state, what, frm, to)
            at = to_pole
        return action_queue

    def start(self, time, observations):
        """
        return first action given the first observations
        """
        self.action_queue = self.queue_init()
        return self.action_queue.pop(0)

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous
        action and the new observations
        """
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        return True

    def reset(self):
        self.action_queue = self.queue_init()
        return True

    def destroy(self):
        """
        called when the agent is done
        """
        return True

class TowerAgent3(AgentBrain):#2-Disk Strips Planner
    """
    An agent that uses a STRIPS-like planner to solve the Towers of Hanoi problem
    """
    def __init__(self):
        AgentBrain.__init__(self) # have to make this call
        self.action_queue = [5] # rotate left to reset state first

    def initialize(self,init_info):
        """
        Create the agent.
        init_info -- AgentInitInfo that describes the observation space (.sensors),
                     the action space (.actions) and the reward space (.rewards)
        """
        self.action_info = init_info.actions
        return True

    def queue_init(self):
        import subprocess
        # solve for show (user can click through)
        subproc = subprocess.Popen(['python', 'BlocksTower/strips.py', 'BlocksTower/towers3_strips.txt'], stdout=subprocess.PIPE)
        plan = ''
        while True:
            try:
                out = subproc.stdout.read(1)
            except:
                break
            if out == '':
                break
            else:
                plan += out
        print plan
        hl_actions = [] # high level action
        for line in plan.split('\n'):
            words = line.strip().split()
            if len(words) == 3:
                (what, frm, to) = words
                hl_actions.append((what, frm, to))
        
        # use strips2 stuff for translating the output into low level actions
        import strips2
        import towers2 as towers
        import strips2_show
        
        action_queue = [5]
        state = copy(towers.INIT)
        at = towers.Pole1
        for (what, frm, to) in hl_actions:
            frm_pole = strips2_show.get_pole(state, frm)
            to_pole = strips2_show.get_pole(state, to)
            print what, frm, to, at, frm_pole, to_pole
            if at != frm_pole:
                action_queue += MOVES[(at, frm_pole)]
            action_queue += CARRY_MOVES[(frm_pole, to_pole)]
            towers.Move(state, what, frm, to)
            at = to_pole

        return action_queue

    def start(self, time, observations):
        """
        return first action given the first observations
        """
        self.action_queue = self.queue_init()
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous
        action and the new observations
        """
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        return True

    def reset(self):
        self.action_queue = self.queue_init()
        return True

    def destroy(self):
        """
        called when the agent is done
        """
        return True

class TowerAgent4(AgentBrain):#3-Disk Strips Planner 
    """
    An agent that uses a STRIPS-like planner to solve the Towers of Hanoi problem
    """
    def __init__(self):
        AgentBrain.__init__(self) # have to make this call
        self.action_queue = [5] # rotate left to reset state first

    def initialize(self,init_info):
        """
        Create the agent.
        init_info -- AgentInitInfo that describes the observation space (.sensors),
                     the action space (.actions) and the reward space (.rewards)
        """
        self.action_info = init_info.actions
        return True

    def queue_init(self):
        import subprocess
        # solve for show (user can click through)
        subproc = subprocess.Popen(['python', 'BlocksTower/strips.py', 'BlocksTower/towers3_strips.txt'], stdout=subprocess.PIPE)
        plan = ''
        while True:
            try:
                out = subproc.stdout.read(1)
            except:
                break
            if out == '':
                break
            else:
                plan += out
        print plan
        hl_actions = [] # high level action
        for line in plan.split('\n'):
            words = line.strip().split()
            if len(words) == 3:
                (what, frm, to) = words
                hl_actions.append((what, frm, to))
        
        # use strips2 stuff for translating the output into low level actions
        import strips2
        import towers3 as towers
        import strips2_show
        
        action_queue = [5]
        state = copy(towers.INIT)
        at = towers.Pole1
        for (what, frm, to) in hl_actions:
            frm_pole = strips2_show.get_pole(state, frm)
            to_pole = strips2_show.get_pole(state, to)
            print what, frm, to, at, frm_pole, to_pole
            if at != frm_pole:
                action_queue += MOVES[(at, frm_pole)]
            action_queue += CARRY_MOVES[(frm_pole, to_pole)]
            towers.Move(state, what, frm, to)
            at = to_pole

        return action_queue

    def start(self, time, observations):
        """
        return first action given the first observations
        """
        self.action_queue = self.queue_init()
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous
        action and the new observations
        """
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        return True

    def reset(self):
        self.action_queue = self.queue_init()
        return True

    def destroy(self):
        """
        called when the agent is done
        """
        return True

class TowerAgent5(AgentBrain):
    """
    An agent that uses a STRIPS-like planner to solve the Towers of Hanoi problem
    """
    def __init__(self):
        import towers3 as towers
        AgentBrain.__init__(self) # have to make this call
        self.action_queue = [10] # rotate left to reset state first
        self.global_at = towers.Pole1 
        self.global_state = copy (towers.INIT)
    
    def initialize(self,init_info):
        """
        Create the agent.
        init_info -- AgentInitInfo that describes the observation space (.sensors),
                     the action space (.actions) and the reward space (.rewards)
        """
        self.action_info = init_info.actions
        return True

    def semantic_parser(self, plan):
            #Write code for simple semantic grammar here
            #Actions should be returned in the following format:
            #1. Mov Object Source Destination
            #2. Pick Object Source
            #3. Put Object Destination
        import string
        plan = string.lower(plan)
        words = string.split(plan) # A list of the words in the user command
        result = plan # In case we cannot parse the plan propperly, return it unmodified
        if words[0] == "mov" or words[0] == "move":
            result = "Mov " + self.parse_helper(plan)
        elif words[0] == "pick":
            result = "Pick " + self.parse_helper(plan)
        elif words[0] == "put":
            result = "Put " + self.parse_helper(plan)
        else:
            print "ERROR: Instructions must begin with Move, Pick or Put."
        return result
    
    def parse_helper(self, plan):
        """
        Helper method. Given a string representing a plan,
        remove every word other than "disk*" or "pole*"
        """
        import string
        words = string.split(plan)
        result = ""
        for w in words:
            if "disk" in w or "pole" in w:
                result += w.title() + " "
        return result

    def queue_init(self):
        import subprocess
        # solve for show (user can click through)
        subproc = subprocess.Popen(['python', 'BlocksTower/text_interface.py'], stdout=subprocess.PIPE)
        plan = ''
        while True:
            try:
                out = subproc.stdout.read(1)
            except:
                break
            if out == '':
                break
            else:
                plan += out
        print plan

        parsed_plan = self.semantic_parser(plan)
        
        if (self.action_queue == [10]):
                action_queue = [5]
        else:
                action_queue = []

        state = self.global_state
        at = self.global_at
        # use strips2 stuff for translating the output into low level actions
        import strips2
        import towers2 as towers
        import strips2_show
        
        words = parsed_plan.strip().split()
        (command) = words[0]

        if command == 'Mov':
                (what, frm, to) = words[1:]
                frm_pole = strips2_show.get_pole(state, frm)
                to_pole = strips2_show.get_pole(state, to)
                print what, frm, to, at, frm_pole, to_pole
                if at != frm_pole:
                    action_queue += MOVES[(at, frm_pole)]
                action_queue += CARRY_MOVES[(frm_pole, to_pole)]
                towers.Move(state, what, frm, to)
                at = to_pole

        elif command == 'Pick':
                (what, frm) = words[1:]
                frm_pole = strips2_show.get_pole(state, frm)
                if at != frm_pole:
                    action_queue += MOVES[(at, frm_pole)]
                action_queue += [3] #Pick up 
                towers.Move(state, what, frm, frm)
                at = frm_pole

        elif command == 'Put':
                (what, to) = words[1:]
                to_pole = strips2_show.get_pole(state, to)
                if at != to_pole:
                    action_queue += MOVES[(at, to_pole)]
                action_queue += [2] #Put Down 
                towers.Move(state, what, to, to)
                at = to_pole

        self.global_state = state
        self.global_at = at
        
        return action_queue

    def start(self, time, observations):
        """
        return first action given the first observations
        """
        self.action_queue = self.queue_init()
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous
        action and the new observations
        """
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            self.action_queue = self.queue_init()
            return 0

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        return True

    def reset(self):
        self.action_queue = self.queue_init()
        return True

    def destroy(self):
        """
        called when the agent is done
        """
        return True



class MyPlanningAgent(AgentBrain):#Student made 3-disk planner
    """
    An agent that uses a STRIPS-like planner to solve the Towers of Hanoi problem
    """
    def __init__(self):
        AgentBrain.__init__(self) # have to make this call
        self.action_queue = [5] # rotate left to reset state first

    def initialize(self,init_info):
        """
        Create the agent.
        init_info -- AgentInitInfo that describes the observation space (.sensors),
                     the action space (.actions) and the reward space (.rewards)
        """
        self.action_info = init_info.actions
        return True

    def queue_init(self):
        import subprocess
        # solve for show (user can click through)
        subproc = subprocess.Popen(['python', 'BlocksTower/strips.py', 'BlocksTower/towers3_strips.txt'], stdout=subprocess.PIPE)
        plan = ''
        while True:
            try:
                out = subproc.stdout.read(1)
            except:
                break
            if out == '':
                break
            else:
                plan += out
        print plan
        hl_actions = [] # high level action
        for line in plan.split('\n'):
            words = line.strip().split()
            if len(words) == 3:
                (what, frm, to) = words
                hl_actions.append((what, frm, to))
        
        # use strips2 stuff for translating the output into low level actions
        import strips2
        import towers3 as towers
        import strips2_show
        
        action_queue = [5]
        state = copy(towers.INIT)
        at = towers.Pole1
        for (what, frm, to) in hl_actions:
            frm_pole = strips2_show.get_pole(state, frm)
            to_pole = strips2_show.get_pole(state, to)
            print what, frm, to, at, frm_pole, to_pole
            if at != frm_pole:
                action_queue += MOVES[(at, frm_pole)]
            action_queue += CARRY_MOVES[(frm_pole, to_pole)]
            towers.Move(state, what, frm, to)
            at = to_pole

        return action_queue

    def start(self, time, observations):
        """
        return first action given the first observations
        """
        self.action_queue = self.queue_init()
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def act(self, time, observations, reward):
        """
        return an action given the reward for the previous
        action and the new observations
        """
        if len(self.action_queue) > 0:
            return self.action_queue.pop(0)
        else:
            return 0

    def end(self, time, reward):
        """
        receive the reward for the last observation
        """
        return True

    def reset(self):
        self.action_queue = self.queue_init()
        return True

    def destroy(self):
        """
        called when the agent is done
        """
        return True
