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

def log_info(printable_object, message=""):
    print "[INFO]{0}:{1}".format(printable_object, message)


def log_error(printable_object, message=""):
    print "[ERROR]{0}:{1}".format(printable_object, message)


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
        subproc = subprocess.Popen(['python', 'BlocksTower/strips.py', 'BlocksTower/towers2_strips.txt'], stdout=subprocess.PIPE)
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
        self.source_of_disk_in_hand = None
        return True

    def check_on_pole(self, query_disk, query_pole, state):
        """
        Checks whether the specified disk is on the specified pole.
        This function calls it's recursively if the disk is on another disk.
        """
        import towers3 as towers        
        
        #check the obvious
        if (towers.Clear(query_pole) in state):
            return False
        if (towers.On(query_disk, query_pole) in state):
            return True
        if not(query_disk in towers.DISKS):
            #somehow we're asking about something that isn't a disk, it's probably another pole, so just return false
            return False   
        #see what this disk is actually on, and make it the new querey
        new_query = None
        #is the current query disk on a disk?
        for disk in towers.DISKS:
            if (towers.On(query_disk, disk) in state):
                new_query = disk
                break
        if (new_query == None):
            #it's not on a disk, try looking at the poles
            for pole in towers.POLES:
                if (towers.On(query_disk, pole) in state):
                    new_query = pole
                    break
        
        #if we still haven't found what it's on somethign is wrong, print an error and return false
        if (new_query == None):
            log_error("The query item ({0}) is a disk, but it not on anything, something is very wrong! (state:{1})".format(query_disk, state))
            return False
        else: #the disk is on something, find out if it is what we are looking for
            return self.check_on_pole(new_query, query_pole, state)
        
        
    def check_can_put(self, query_disk, destination, state):
        """
        Checks whether the specified disk can be
        placed on the specified pole (or disk on a pole), given the state.
        """
        import towers3 as towers
        
        if (towers.Clear(destination) in state):
            return True
        
        #if the destination isn't clear, find out what IS on it
        #this isn't particularly elligant, since it checks disks that can't even be here in this state
        for disk in towers.DISKS:
            if (towers.On(disk, destination) in state):
                #check and see if we might be able to put the disk in question here
                if (towers.Smaller(query_disk, disk) in state):
                    return self.check_can_put(query_disk, disk, state)
                else:
                    return False
        
        #if somehow we got through the loop and didn't find SOME disk on the supposedly clear pole then something is wrong
        log_error("The destination location ({0}) is not clear, however no disk could be identified as being on it. (state:{1})".format(destination, state))
        return False

    def get_top_object(self, pole, state):
        """
        Gets the top object on the specified pole, returns pole if the pole is clear
        """
        import towers3 as towers
        #check the obvious
        if (towers.Clear(pole) in state):
            return pole
        
        on_object = pole 
        #see if the query disk is On another disk
        for disk in towers.DISKS:
            if self.check_on_pole(disk, pole, state):
                if(towers.Smaller(disk, on_object) in state):
                    on_object = disk
        return on_object
                        
                
    def get_object_below(self, query_disk, state):
        """
        Thes the object below the specificied disk, returns None if it can't find anything
        """
        import towers3 as towers
        object_below = None
        #is it a disk?
        for disk in towers.DISKS:
            if (towers.On(query_disk, disk) in state):
                object_below = disk
                break
        if (object_below == None):
            for pole in towers.POLES:
                if (towers.On(query_disk, pole) in state):
                    object_below = pole
                    break
        return object_below

    def queue_init(self):
        import subprocess
        # solve for show (user can click through)
        subproc = subprocess.Popen(['python', 'BlocksTower/text_interface.py'], stdout=subprocess.PIPE)
        parsed_plan = ''
        while True:
            try:
                out = subproc.stdout.read(1)
            except:
                break
            if out == '':
                break
            else:
                parsed_plan += out
        parsed_plan = parsed_plan.splitlines()
        print parsed_plan
        
        if (self.action_queue == [10]):
                action_queue = [5]
        else:
                action_queue = []

        state = self.global_state
        at = self.global_at
        # use strips2 stuff for translating the output into low level actions
        import strips2
        import towers3 as towers
        import strips2_show

        #Get a count of how many commands to parse, of the parser didn't return anything then make sure we don't try to process and commands
        if (len(parsed_plan) == 0):
            return []
        
		#the plan could be a list of strings or a string, if it's a string then put it in a single element list
        if (type(parsed_plan) == str):
			parsed_plan = [parsed_plan]
            
        
        number_of_commands = len(parsed_plan)
        log_info(parsed_plan, "Plan appears to contain {0} commands.".format(number_of_commands))
            
        for command_number in range(number_of_commands):
            words = parsed_plan[command_number].strip().split()
            (command) = words[0]

        	 #check and see if this command string is value i.e. 'Mov disk pole pole', 'Pick, disk pole', etc
            if command == 'Mov':
                if len(words) != 4:
    				log_error(parsed_plan[command_number], "Invalid command string, the \'Mov\' command expects the format Mov disk from_pole to_pole")
    				continue
                #check the args
                elif not(words[1][0:4] == 'Disk' and (words[1][4] == '1' or words[1][4] == '2' or words[1][4] == '3')):
                    log_error(parsed_plan[command_number], "Invalid command string, the \'Mov\' command expects the format Mov disk from_pole to_pole")
                    continue
                elif not(words[2][0:4] == 'Pole' and (words[2][4] == '1' or words[2][4] == '2' or words[2][4] == '3')):
    				log_error(parsed_plan[command_number], "Invalid command string, the \'Mov\' command expects the format Mov disk from_pole to_pole")
    				continue
                elif not(words[3][0:4] == 'Pole' and (words[3][4] == '1' or words[3][4] == '2' or words[3][4] == '3')):
    				log_error(parsed_plan[command_number], "Invalid command string, the \'Mov\' command expects the format Mov disk from_pole to_pole")
    				continue
            elif (command == 'Pick') or (command == 'Put'):
    			if len(words) != 3:
    				log_error(parsed_plan[command_number], "Invalid command string, the \'Pick\' or \'Put\' command expects the format Mov disk from/to_pole")
    				continue
    			#check the args
    			elif not(words[1][0:4] == 'Disk' and (words[1][4] == '1' or words[1][4] == '2' or words[1][4] == '3')):
    				log_error(parsed_plan[command_number], "Invalid command string, the \'Pick\' or \'Put\' command expects the format Mov disk from/to_pole")
    				continue
    			elif not(words[2][0:4] == 'Pole' and (words[2][4] == '1' or words[2][4] == '2' or words[2][4] == '3')):
    				log_error(parsed_plan[command_number], "Invalid command string, the \'Pick\' or \'Put\' command expects the format Mov disk from/to_pole")
    				continue
		#if we got this far the action must be good, but make sure it is legal in the current state before trying to do it
            if command == 'Mov':
                #check if we are holding something
                if (self.source_of_disk_in_hand != None):
                    log_error("Can't pick up another disk, because we are alreadying holding one.")
                    break
                (what, frm, to) = words[1:]
                frm_pole = strips2_show.get_pole(state, frm)
                to_pole = strips2_show.get_pole(state, to)
                print what, frm, to, at, frm_pole, to_pole
                #do a sanity check before doing anything
                #! make sure that what we are picking up is where it is supposed to be and that it is on top
                if not(towers.Clear(what) in state):
                    log_error(words, "Can't pick up {0}, because there is something on it".format(what))
                    break
                elif not(self.check_on_pole(what, frm_pole, state)):                        
                    log_error(words, "Can't pick up {0} because it's not at the specified location {1}".format(what, frm_pole))
                    break                
                #now check if the destination pole is clear, or if it is not, whether the disk(s) on it are largers
                elif not(self.check_can_put(what, to_pole, state)):
                    log_error(words, "Can't put {0} on {1}, because a smaller disk is already there.".format(what, to_pole))
                    break
                #now that everything looks okay, perform the nessecary actions
                if at != frm_pole:
                    action_queue += MOVES[(at, frm_pole)]
                action_queue += CARRY_MOVES[(frm_pole, to_pole)]
                if towers.Move(state, what, self.get_object_below(what, state), self.get_top_object(to_pole, state)):
                    print "move successful"
                at = to_pole
                
            elif command == 'Pick':
                #check if we are holding something
                if (self.source_of_disk_in_hand != None):
                    log_error("Can't pick up another disk, because we are alreadying holding one.")                
                    break
                (what, frm) = words[1:]
                frm_pole = strips2_show.get_pole(state, frm)
                #do a sanity check before doing anything
                #! make sure that what we are picking up is where it is supposed to be and that it is on top
                if not(towers.Clear(what) in state):
                    log_error(words, "Can't pick up {0}, because there is something on it".format(what))
                    break     
                if not(self.check_on_pole(what, frm_pole, state)):
                    log_error(words, "Can't pick up {0} because it's not at the specified location {1}".format(what, frm_pole))
                    break
                if at != frm_pole:
                    action_queue += MOVES[(at, frm_pole)]
                action_queue += [3] #Pick up 
                self.source_of_disk_in_hand = self.get_object_below(what, state)#store where the disk we are picking up came from so we can clean up the state when we put it down
                towers.Move(state, what, self.get_object_below(what, state), self.source_of_disk_in_hand)
                at = frm_pole

            elif command == 'Put':
                (what, to) = words[1:]
                to_pole = strips2_show.get_pole(state, to)
                #now check if the destination pole is clear, or if it is not, whether the disk(s) on it are largers
                if not(self.check_can_put(what, to_pole, state)):
                    log_error(words, "Can't put {0} on {1}, because a smaller disk is already there.".format(what, to_pole))
                    break                
                #everything looks okay, take the action
                if at != to_pole:
                    action_queue += MOVES[(at, to_pole)]
                action_queue += [2] #Put Down 
                towers.Move(state, what, self.source_of_disk_in_hand, self.get_top_object(to_pole, state))
                self.source_of_disk_in_hand = None#clear the source of the disk we are holding, since we put it down                    
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

