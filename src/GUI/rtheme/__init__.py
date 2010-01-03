from GUI.theme import *

class RTheme(Theme):

    RAW_DIR = "src/GUI/rtheme"
    
    DEFAULT = StretchBorder("src/GUI/rtheme/frame.png",4)
    
    CHECKOFF = IconLike("src/GUI/rtheme/twotone/checkmark.png")
    CHECKON = IconLike("src/GUI/rtheme/twotone/blank.png")
    
    RADIOON = IconLike("src/GUI/rtheme/twotone/radio-on.png")
    RADIOOFF = IconLike("src/GUI/rtheme/twotone/radio-off.png") 
    
    BAR_TOP = StretchBorder("src/GUI/rtheme/progress-top.png",4)
    
    SCROLL_Y = StretchBorder("src/GUI/rtheme/scrolly.png",2)
    SCROLL_X = StretchBorder("src/GUI/rtheme/scrollx.png",2)
    SCROLLER = StretchBorder("src/GUI/rtheme/progress-top.png",2)
    
    
    BUTTON = StretchBorder("src/GUI/rtheme/button-up.png",4)
    BUTTON_OVER = StretchBorder("src/GUI/rtheme/button-over.png",4)
    BUTTON_DOWN = StretchBorder("src/GUI/rtheme/button-donw.png",4)


    BLACK_FIX_SMALL_FONT = Font(
        "BLACK_FIX_SMALL_FONT",
        "src/GUI/rtheme/fonts/ProFontWindows.ttf",
        8,
        (0,0,0,1))
    
    BLACK_SCIFI_SMALL_FONT = Font(
        "BLACK_SCIFI_SMALL_FONT",
        "src/GUI/rtheme/fonts/kimberle.ttf",
        8,
        (0,0,0,1))


    BLACK_FIX_FONT = Font(
        "BLACK_FIX_FONT",
        "src/GUI/rtheme/fonts/ProFontWindows.ttf",
        10,
        (0,0,0,1))
    
    BLACK_SCIFI_FONT = Font(
        "BLACK_SCIFI_FONT",
        "src/GUI/rtheme/fonts/kimberle.ttf",
        10,
        (0,0,0,1))
    
    BLACK_FIX_BIG_FONT = Font(
        "BLACK_FIX_BIG_FONT",
        "src/GUI/rtheme/fonts/ProFontWindows.ttf",
        14,
        (0,0,0,1))
    
    BLACK_SCIFI_BIG_FONT = Font(
        "BLACK_SCIFI_BIG_FONT",
        "src/GUI/rtheme/fonts/kimberle.ttf",
        14,
        (0,0,0,1))

    DEFAULT_FONT = BLACK_FIX_FONT
    