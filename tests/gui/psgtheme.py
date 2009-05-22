from theme import * 

class PSGTheme(Theme):
    TEXTURE = "data/gui.png"
    CHECKON = Stretch(360,40,20,20)
    CHECKOFF = Stretch(400,40,20,20)
    RADIOON = Stretch(280,40,20,20)
    RADIOOFF = Stretch(320,40,20,20)
    PANDA = Tiled(280,80,20,20)
    
    INPUT = TileBorder(20,300,180,180,20)
   
    
    X = Stretch(280,80,20,20)
    DRAG = Stretch(440,80,20,20)
    
    FRAME = TileBorder(20,300,180,180,20)
    FORM = TileBorder(20,20,202-20,182-20,20)
    FRAMEBAR = TileBarX(280,480,140,20,20)
    BUTTON = Tiled(320,420,20,20)
    BUTTON = TileBarX(280,480,140,20,20)
    BUTTON = TileBorder(288,170,490-288,190-170,5)
    BUTTON = TileBorder(290,270,210,20,10)
    BUTTON = Tiled(290,270,210,20)
    INPUT = BUTTON
    MENU  = BUTTON
    PROGRESS_BAR = INPUT
    #BUTTON = Tiled(280,80,20,20)
    #BUTTON = TileBorder(20,20,202-20,182-20,20)
    
    BUTTON = TileBarX(300,300,140,20,20)
    DOWN = Tiled(300,260,200,40)
    TEXTCOLOR = (1,1,1,1)
    LABLECOLOR = TEXTCOLOR
    INPUTCOLOR = TEXTCOLOR