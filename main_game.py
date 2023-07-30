import pygame               # zur installation ab python 3.11 vorläufig disen Term verwenden: py -m pip install pygame --pre
from pygame.locals import *
import pygame_widgets
from pygame_widgets.button import Button
import math, random

PINRAD = 15             # Radius
PINOFF_X = 100          # Offset from left
PINOFF_Y = 97           # Offset from top
PINDIST_X = 45          # Distance between pin
PINDIST_Y = 70          # Distance between pin      
PINCOLS = 4           # Number of pins in a row
PINROWS = 6             # Ändern um mit bis zu 8 Reihen zu spielen
BW_PINRAD = 8           # Radius
BW_PINDIST_X= 25        # Distance between pin
BW_PINDIST_Y = 25       # Distance between pin
BW_PINDISTROW = 0       # Distance between pairs
BW_PINCOLS = int(PINCOLS / 2)
BW_PINROWS = PINROWS * 2
BW_PINOFF_X = 40        # Offset from left
BW_PINOFF_Y = (PINROWS * PINDIST_Y + PINOFF_Y ) - (BW_PINROWS * BW_PINDIST_Y - BW_PINDIST_Y/2 )    # Offset from top   
CODE_PINOFF_Y = 70      # Offset from top

BACKGROUND = (180, 180, 180)       # Hintergrund 
FPS = 30

pygame.init()
WIN = pygame.display.set_mode((480 ,640))
pygame.display.set_caption('Mini Master Mind')
clock = pygame.time.Clock() 

# Create buttons and shapes
buttonfont = pygame.font.SysFont('arial', 20)
bt_new = Button(WIN,200 + PINCOLS*35, 47,100,40, radius=4,font = buttonfont,margin=20, text = 'New Game', onClick=lambda: newgame())
bt_check = Button(WIN,200 + PINCOLS*35, PINOFF_Y - 20  + ((PINROWS) * PINDIST_Y),100,40, radius=4, font = buttonfont, text = 'Check', onClick=lambda: check())
bt_cover = Button(WIN,128, 47,PINCOLS*43,40, radius=4, font = buttonfont, text = 'Show', onClick= lambda: bt_cover.setY(90))               # Show the hiden code line 
rowrect = Rect(124,PINOFF_Y - 20  + ((PINROWS) * PINDIST_Y),PINCOLS*45,40)            # Rahmen um aktive Color Pin
# rowrect2 = Rect(53,PINOFF_Y - 25  + ((PINROWS) * PINDIST_Y),50,50)                      # Rahmen um aktive BW Pin
backrect = Rect(50,20,75+PINCOLS*45,(PINDIST_Y * PINROWS) + 120)
backrectframe = Rect(50,20,75+PINCOLS*45,(PINDIST_Y * PINROWS) + 120)

colorpinlist = []
bw_pinlist = []
sec_pinlist = []
act_row = 0
show = False

class ColorPin():
    def __init__(self, row, col, isSecret = False):
        self.y = CODE_PINOFF_Y if isSecret else row * PINDIST_Y + PINOFF_Y
        self.x = col * PINDIST_X + PINOFF_X
        self.color = BACKGROUND             # Wie Hintergrund
        self.colorNo = 0

    def change_color(self):
        self.colorNo += 1                   # Next color
        if self.colorNo > 6:
            self.colorNo = 0

    def draw(self, win):
        match self.colorNo:
            case 0: self.color = BACKGROUND     # Empty pin
            case 1: self.color = 'blue'
            case 2: self.color = 'green'
            case 3: self.color = 'red'
            case 4: self.color = 'orange'
            case 5: self.color = 'yellow'
            case 6: self.color = 'brown'
        pygame.draw.circle(win,'black',[self.x, self.y,], PINRAD, 2)            # Black cyrcle
        pygame.draw.circle(win, (self.color),[self.x, self.y,], PINRAD-2, 0)    # Fill


class BW_pin():         # Black-and-white pin
    def __init__(self,row,col):
        self.x = col * BW_PINDIST_X + BW_PINOFF_X
        self.y = row * BW_PINDIST_Y + BW_PINOFF_Y + BW_PINDISTROW
        self.color = BACKGROUND
        self.colorNo = 0

    def draw(self,win):
        if self.color == 'black':
            pygame.draw.circle(win, 'white',[self.x, self.y,], BW_PINRAD, 1)        # Weisser Rand wenn schwarz gefuellt
        else:
            pygame.draw.circle(win, 'black',[self.x, self.y,], BW_PINRAD, 1)        # Schwarzer Rand
        pygame.draw.circle(win, (self.color),[self.x, self.y,], BW_PINRAD-1, 0)     # Fuellen

        
def make_pinlist():
    global BW_PINDISTROW; BW_PINDISTROW = 0
    colorpinlist.clear()    # leeren
    bw_pinlist.clear()
    sec_pinlist.clear()

    # Liste mit Farbpin instanzen erstellen
    for row in range(PINROWS,0,-1):                     # Nummerierung von unten nach oben
        for col in range(PINCOLS,0,-1):               # Nummerierung rechts nach links
            colorpinlist.append(ColorPin(row,col))      # instanzen erstellen und zu Liste hinzufügen

    # Liste mit Bewertungspin instanzen erstellen
    for row in range(BW_PINROWS,0,-1):                  # Nummerierung von unten rechts nach oben links
        if row % 2 == 0 and row < BW_PINROWS:           # Gerade Anzahl dann
            BW_PINDISTROW -= PINDIST_Y - 2 * BW_PINDIST_Y    # Abstand zwischen 2er Gruppen
        for col in range(BW_PINCOLS,0,-1):
            bw_pinlist.append(BW_pin(row,col))               # instanzen erstellen und zu Liste hinzufügen

    # Liste mit Codepin instanzen erstellen
    for col in range(PINCOLS,0,-1):                   # Von rechts nach links
        sec_pinlist.append(ColorPin(0,col,isSecret=True))        # instanzen erstellen und zu Liste hinzufügen


def check():        # Bewerten des aktuellen Versuchs
    global act_row
    code_color = []; pin_color = []; score_list = []
    found = 0
    for idx in range(PINCOLS):
        code_color.append(sec_pinlist[idx].colorNo)     # Alle Farben des Codes in Liste
        pin_color.append(colorpinlist[idx + (act_row * PINCOLS)].colorNo)  # Alle Farben des Versuchs in Liste
    for idx in range(len(code_color)):                  # 1. Suche Volltreffer
        if code_color[idx] ==  pin_color[idx]:          # Identische Farbe an identischem Ort
            score_list.append(2)                        # 2 = schwarze markierung zur Liste
            pin_color[idx] = -1                         # Setzt -1 damit diser pin nicht mehr zählt bei Suche nach weissen
            code_color[idx] = -2                        # Setzt -2 damit diser pin nicht mehr zählt bei Suche nach weissen
    for idx in range(len(code_color)):                  # 2. Suche nach richtiger Farbe am falschen Ort
        if code_color[idx] in pin_color:                # Index nur suchen wenn in Liste..
            found = pin_color.index(code_color[idx])    # ..ansonsten hier Error
            score_list.append(1)                        # 1 = weisse Markierung
            pin_color[found] = -1                       # Setzt -1 damit diser pin nicht mehr zählt
    if len(score_list) > 0:             
        showscore(score_list)                           # Resultat der Reihe anzeigen
    if act_row < PINROWS-1:                             # Wenn noch nicht bei letzter Reihe
        act_row += 1                                    # Aktive Reihe + 1 (nach oben)
        rowrect.move_ip(0, -PINDIST_Y)                  # Rahmen eins höher (move incrementel (x,y))
        # rowrect2.move_ip(0, -PINDIST_Y)                 # Rahmen eins höher
        bt_check.moveY( -PINDIST_Y)                     # Button eins höher


def showscore(scorelist):
    scorelist.sort()                    # Sortieren, damit keine rückschlüsse auf die position möglich sind
    for idx in range(len(scorelist)):
        if scorelist[idx] == 2:
            bw_pinlist[idx + (act_row * PINCOLS)].color = 'black'
        else:    
            bw_pinlist[idx + (act_row * PINCOLS)].color = 'white'
            

def newgame():               # New Game: Make secret code and clear everything
    global act_row
    make_pinlist()
    act_row = 0
    bt_cover.setY(47)                                           # Set cover button over the code line (hide)
    rowrect.y = PINOFF_Y - 20  + ((PINROWS) * PINDIST_Y)        # Set row marker to lowest row
    bt_check.setY(PINOFF_Y - 20  + ((PINROWS) * PINDIST_Y))
    for idx in range(PINCOLS):
        sec_pinlist[idx].colorNo = random.randint(1,6)          # Make new random code line


def draw_n_fill(WIN):
    pygame.draw.rect(WIN,0xC17C66,backrect,0, 8)  # '#e28743'
    pygame.draw.rect(WIN,'brown',backrectframe,2, 8)  # '#e28743'
    pygame.draw.rect(WIN,'brown',rowrect,2,6)
    #pygame.draw.rect(WIN,'brown',rowrect2,2,6) 
    for colorpin in colorpinlist: 
        colorpin.draw(WIN)
    for bw_pin in bw_pinlist:
        bw_pin.draw(WIN)
    for sec_pin in sec_pinlist:
        sec_pin.draw(WIN)  


def main():
    run = True
    newgame()
    while run:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events :
            if event.type == pygame.QUIT:
                run = False
                break  
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()                    # actual mouse position
                for idx in range(act_row * PINCOLS, act_row * PINCOLS + PINCOLS ):     # Check all pins in active row
                    sqx = (x - colorpinlist[idx].x)**2          # X Mausposition ab Mittelpunkt Kreis (a^2)
                    sqy = (y - colorpinlist[idx].y)**2          # Y Mausposition ab Mittelpunkt Kreis (b^2)
                    if math.sqrt(sqx + sqy) <= PINRAD:           # Wurzel aus a^2 + b^2 = c (radius) :-)
                        colorpinlist[idx].change_color()        # Change color if cklick on a pin in the active row
                        break     

        WIN.fill(BACKGROUND) 
        draw_n_fill(WIN)
        pygame_widgets.update(events)          
        pygame.display.update()
main()