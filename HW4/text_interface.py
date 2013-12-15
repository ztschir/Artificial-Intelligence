import Tkinter as tk
import sys
from text_viewer import TextViewer
import time
import threading
import Queue


class MyDialog:
    def __init__(self, parent):

        top = self.top = parent #tk.Toplevel(parent)

        self.entry_frame = tk.Frame(parent)
        tk.Label(self.entry_frame, text="Please enter English sentence:").pack()

        self.e = tk.Entry(self.entry_frame)
        self.e.pack(padx=15)

        b = tk.Button(self.entry_frame, text="Parse", command=self.parse)
        b.pack(pady=5)
        self.value = ""

        c = tk.Button(self.entry_frame, text="Close", command=self.close)
        c.pack(pady=5)
        
        self.entry_frame.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.log_frame = tk.Frame(parent)
        self.text = tk.Text(self.log_frame)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll = tk.Scrollbar(self.log_frame)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.config(font="Courier 12", yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.text.yview)


        self.log_frame.pack(side=tk.BOTTOM)
        
        #setup other stuff
        self.log_frame.bind('<<display-text>>', self.display_text_handler)
        
        self.message = Queue.Queue()
    
        self.parsed_plan = ""

    def parse(self):
        if self.parsed_plan == "":
            self.value = self.e.get()
            #parse the plan
            self.parsed_plan = self.semantic_parser(self.value)
            self.log_info("{0} -> {1}".format(self.value, self.parsed_plan))
        else:
            self.log_error("Already parsed plan: {0}, cannot parse new plan.".format(self.parsed_plan))
        
    def semantic_parser(self, plan):
            #Write code for simple semantic grammar here
            #Actions should be returned in the following format:
            #1. Mov Object Source Destination
            #2. Pick Object Source
            #3. Put Object Destination
        #But first, if for some reason the plan string is empty just exit
        if (len(plan) == 0):
            return plan

        import string
        plan = string.lower(plan)
        result = []


        # the word down is not technically in the language, but we added it, since it was
        #   one of the example strings that was accepted.
        for valid_string in string.split(plan):
            if ("and" != valid_string and
                "move" != valid_string and
                "from" != valid_string and
                "pick" != valid_string and
                "up" != valid_string and
                "down" != valid_string and
                "put" != valid_string and
                "disk1" != valid_string and
                "disk2" != valid_string and
                "disk3" != valid_string and
                "pole1" != valid_string and
                "pole2" != valid_string and
                "pole3" != valid_string and
                "to" != valid_string and
                "on" != valid_string and
                "left" != valid_string and
                "rigth" != valid_string and
                "middle" != valid_string and
                "pole" != valid_string):
                    self.log_error(str(valid_string) + " not in the valid language.")
                    return plan


        

        for subplan in string.split(plan,"and"):
            
            words = string.split(subplan) # A list of the words in the user command
            subresult = subplan # In case we cannot parse the plan propperly, return it unmodified

            #The verb phrase should come first, so look at the first word
            #If the verb phase is present go ahead and parse the noun phrases
            self.log_info("Expanding sentence 'S' to VP1 NP1 NP3 NP4 | VP1 NP1 NP4 NP3 | VP2 NP1 NP3 | VP3 NP1 NP4,")
            self.log_info("the identifying initial verb phrase...")
            if words[0] == "mov" or words[0] == "move":
                subresult = "Mov " + self.get_noun_phrases(subplan, 1)
            elif words[0] == "pick":
                self.log_info("Case VP2 NP1 NP3 (\"Move\") found.")
                self.log_info("Identifying noun phrases...")            
                subresult = "Pick " + self.get_noun_phrases(subplan, 0)
            elif words[0] == "put":
                self.log_info("Case VP3 NP1 NP4 (\"Move\") found.")
                self.log_info("Identifying noun phrases...")            
                subresult = "Put " + self.get_noun_phrases(subplan, 0)
            else:
                self.log_error(words, "Instructions must begin with Move, Pick or Put.")

            result.append(subresult)
        return result
    
    def get_noun_phrases(self, plan, mode):
        """
        Helper method. Given a string representing a plan,
        finds the noun phrases by removing every word other than "disk*" or "pole*.
		Does not check whether these are in the correct order."
        """
        import string
        words = string.split(plan)
        result = ""

        while ("left" in words or "right" in words or "middle" in words):
            if("left" in words):
                index = words.index("left")
                words.remove("left")
                words[index] = "pole1"
            
            if("right" in words):
                index = words.index("right")
                words.remove("right")
                words[index] = "pole3"

            if("middle" in words):
                index = words.index("middle")
                words.remove("middle")
                words[index] = "pole2"
            
        
        if (mode == 1 and "from" in words and
           (("to" in words and words.index("from") > words.index("to")) or
            ("on" in words and words.index("from") > words.index("on")))):
            self.log_info("Case VP1 NP1 NP4 NP3  (\"Move\") found")
            self.log_info("Identifying noun phrases...")
            words[3], words[5] = words[5], words[3]

            if "pole" not in words[3] or "pole" not in words[5]:
                self.log_error("Destination or source is not a recognized noun phrase")

        elif mode == 1:
            self.log_info("Case VP1 NP1 NP3 NP4  (\"Move\") found")
            self.log_info("Identifying noun phrases...")

        
        for w in words:
            if "disk" in w or "pole" in w:
                self.log_info("\"{0}\" found!".format(w))
                result += w.title() + " "

        if(mode == 1 and len(result.split()) != 3):
            self.log_error("Not a valid command, not enough nouns.")

        elif(mode == 0 and len(result.split()) != 2):
            self.log_error("Not a valid command, not enough nouns.")
                
        return result

    def close(self):
    	if (type(self.parsed_plan) == list):
    	    for command_string in self.parsed_plan:
    	        print command_string
    	else:
    	    print self.parsed_plan
    	self.top.destroy()
        
    def log_info(self, printable_object, message=""):
        s = "[INFO]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')    
    
    def log_error(self, printable_object, message=""):
        s =  "[ERROR]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')        

    def display_text_handler(self, event=None):
        s = self.message.get()
        self.text.insert(tk.END, s)
        self.text.insert(tk.END, '\n')
        self.text.yview(tk.END)



def main():
    root = tk.Tk()
    root.title('Enter Command')
    d = MyDialog(root)
    root.wait_window(d.top)
   

if __name__ == "__main__":
        main()
