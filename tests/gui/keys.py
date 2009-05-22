"""

    This module regesters keys and converts them to user event
    this is how they key can be bound to other events 

"""

class Keys:
    """ processes keys including mouse buttons"""
    
    def __init__(self,keyFilename='gui/keys.config'):
        """ create event prosessor """
        self.focus = None
        self.bound = {}
        for n,line in enumerate(open(keyFilename)):
            s = line.split() 
            if s == []:
                continue
            elif line[0] == "#":
                pass
            elif line[0] != "#":
                key,message = s                  
                self.bound[key] = message
            else:
                print "error in keys.txt file on line %i"%n
        for event in self.bound.keys():
            base.accept(event,self.onKey,[event])            
        letters = "abcdefghijklmnopqrstuvwxyz"     
        symbols = "1234567890-=,./[]\\;'`"
        shifted = "!@#$%^&*()_+<>?{}|:\"~"
        work = ['enter','backspace','space']        
        self.mouseEvents = dict.fromkeys(["mouse1", "mouse2", "mouse3"])
        for mouseEvent in ["mouse1", "mouse2", "mouse3","mouse1-up","mouse2-up","mouse3-up"]:
            base.accept(mouseEvent,self.onKey,[mouseEvent])
        for letter in symbols+letters:
            base.accept(letter,self.onKey,[letter])
            base.accept('shift-'+letter,self.onKey,[letter.upper()])
        for event in work:
            base.accept(event,self.onKey,[event])
        for index,key in enumerate(symbols):
            base.accept('shift-'+key,self.onKey, [shifted[index]] )
        self.inputKeys = dict.fromkeys(list(letters+letters.upper()+symbols+shifted)+work)

    def onKey(self,key):
        """ if gui is in focus give keys to that else 
        see if they are bound to action """
        if key in ("mouse1-up","mouse2-up","mouse3-up"):            
            gui.drag = None
        if key in self.mouseEvents:
            #print "looking if gui needs mouse event"
            if gui.baseMouseEvent(key):
                print "gui got mouse event"
                return
        if self.focus != None and key in self.inputKeys:    
            if self.focus.onKey(key):
                return
        if key in self.bound:
            messenger.send(self.bound[key])
        
    
      
        