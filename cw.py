import pygame, numpy as np
from string import ascii_uppercase
from collections import defaultdict

# audio settings
samplerate = 48000
pygame.mixer.init(samplerate,-16,2,512)

# pygame defaults
pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()
pygame.display.set_caption("Morse Code Keyer")
fps = 100

# morse dictionary
morse_alph = [".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."]
morse_num = [".----", "..---", "...--", "....-", ".....", "-....", "--...", "---..", "----.", "-----"]
alph = defaultdict(lambda: "#") # if not found.

for dot_alph, letter in zip(morse_alph, ascii_uppercase):
    alph[dot_alph] = letter
for dot_num, num in zip(morse_num, [1,2,3,4,5,6,7,8,9,0]):
    alph[dot_num] = str(num)

alph[".-.-.-"] = "."
alph["--..--"] = ","
alph["..--.."] = "?"
alph["-..-."] = "/"

# font stuff
font = pygame.font.SysFont("courier bold", 60)

def draw_text(s: str, y, colour = (0,0,0)):
    text_drawing = font.render(s, True, colour)
    screen.blit(text_drawing, ((screen.get_width() - text_drawing.get_width()) // 2, y))

def gen_signal(freq):
    arr = np.array([4096 * np.sin(2.0 * np.pi * freq * x / samplerate) for x in range(0, samplerate)]).astype(np.int16)
    arr2 = np.c_[arr,arr]
    return pygame.sndarray.make_sound(arr2)

def any_key_mode():

    # morse mechanics
    sound = gen_signal(500)
    delay = fps * 0.8 # seconds until character is accepted.
    dash_duration = fps * 0.20 # fifth second for dot -> dash.
    counter = 0 # how long key has been held
    key_toggle = False
    accept_counter = delay
    char = ""
    text = ""

    bg_img = pygame.image.load("UI.png")

    # text stuff
    w = 100
    h = 50

    while True:

        screen.blit(bg_img, (0,0))

        draw_text(char, (screen.get_height() - 2*h) // 2)
        draw_text(text, screen.get_height() - h * 2)

        for event in pygame.event.get():
            
            if event.type == pygame.KEYDOWN:

                # slower dashes
                if event.key == pygame.K_PLUS:
                    dash_duration += 5
                    print("dash duration: " + str(dash_duration / fps) + "s")

                # faster dashes
                elif event.key == pygame.K_MINUS:
                    dash_duration -= 5 if dash_duration > 10 else 0
                    print("dash duration: " + str(dash_duration / fps) + "s")

                # slower accept
                elif event.key == pygame.K_PAGEUP:
                    delay += 10
                    print("current accept: " + str(delay / fps) + "s")

                # faster accept
                elif event.key == pygame.K_PAGEDOWN:
                    delay -= 10 if delay > 10 else 0
                    print("current accept: " + str(delay / fps) + "s")

                # clear current text
                elif event.key == pygame.K_BACKSPACE:
                    text = ""

                elif event.key == pygame.K_ESCAPE:
                    exit()

                elif pygame.key.name(event.key) in ("z", "x", "c", "v", "b", "n", "m", ",", ".", "-"):
                    key_toggle = True
                    accept_counter = delay
                    sound.play(-1)

            elif event.type == pygame.KEYUP:
                if key_toggle:
                    if counter < dash_duration:
                        char += "."
                    else:
                        char += "-"
                key_toggle = False
                print(char)
                counter = 0
                sound.stop()
            
            elif event.type == pygame.QUIT:
                exit()

        if key_toggle:
            counter += 1

        if char != "":
            accept_counter -= 1
        
        if accept_counter == 0:
            text += alph[char]
            accept_counter = delay
            char = ""
            print(text)

        pygame.display.flip()
        clock.tick(fps)

if __name__ == "__main__":
    any_key_mode()