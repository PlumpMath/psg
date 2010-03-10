from GUI.Treegui.theme import *

class RTheme(Theme):

    RAW_DIR = "src/GUI/rtheme"
    
    DEFAULT = StretchBorder("frame.png",4)
    
    CHECKOFF = IconLike("twotone/checkmark.png")
    CHECKON = IconLike("twotone/blank.png")
    
    RADIOON = IconLike("twotone/radio-on.png")
    RADIOOFF = IconLike("twotone/radio-off.png") 
    
    BAR_TOP = StretchBorder("progress-top.png",4)
    
    BIG_BORDER = StretchBorder("frame.png",20)
    
    SCROLL_Y = StretchBorder("scrolly.png",2)
    SCROLL_X = StretchBorder("scrollx.png",2)
    SCROLLER = StretchBorder("progress-top.png",2)
    
    
    BUTTON = StretchBorder("button-up.png",4)
    BUTTON_OVER = StretchBorder("button-over.png",4)
    BUTTON_DOWN = StretchBorder("button-donw.png",4)


    BLACK_FIX_SMALL_FONT = Font(
        "BLACK_FIX_SMALL_FONT",
        "fonts/ProFontWindows.ttf",
        8,
        (0,0,0,1))
    
    BLACK_SCIFI_SMALL_FONT = Font(
        "BLACK_SCIFI_SMALL_FONT",
        "fonts/kimberle.ttf",
        8,
        (0,0,0,1))


    BLACK_FIX_FONT = Font(
        "BLACK_FIX_FONT",
        "fonts/ProFontWindows.ttf",
        10,
        (0,0,0,1))
    
    BLACK_SCIFI_FONT = Font(
        "BLACK_SCIFI_FONT",
        "fonts/kimberle.ttf",
        10,
        (0,0,0,1))
    
    BLACK_FIX_BIG_FONT = Font(
        "BLACK_FIX_BIG_FONT",
        "fonts/ProFontWindows.ttf",
        14,
        (0,0,0,1))
    
    BLACK_SCIFI_BIG_FONT = Font(
        "BLACK_SCIFI_BIG_FONT",
        "fonts/kimberle.ttf",
        14,
        (0,0,0,1))

    DEFAULT_FONT = BLACK_FIX_FONT
    
