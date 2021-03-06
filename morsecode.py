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

# morse dictionary. A-Z then 1234567890
morse_alph = [".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---", "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-", "..-", "...-", ".--", "-..-", "-.--", "--.."]
morse_num = [".----", "..---", "...--", "....-", ".....", "-....", "--...", "---..", "----.", "-----"]
alph = defaultdict(lambda: "#") # default unidentified character is '#'.

for dot_alph, letter in zip(morse_alph, ascii_uppercase):
    alph[dot_alph] = letter
for dot_num, num in zip(morse_num, [1,2,3,4,5,6,7,8,9,0]):
    alph[dot_num] = str(num)

# special characters
morse_special = [".-.-.-", "--..--", "..--..", "-.-.--", "-..-.", "---...", "-.-.-.", "-...-", ".-.-.", "-....-", ".-..-.", ".--.-."]
special_translation = [".", ",", "?", "!", "/", ":", ";", "=", "+", "-", "\"", "@"]
for dot_dash, char in zip(morse_special, special_translation):
    alph[dot_dash] = char

def gen_font(size = 60):
    return pygame.font.SysFont("courier bold", size)

def draw_text(s: str, x, y, font, colour = (255,255,255)):
    text_drawing = font.render(s, True, colour)
    if not x: # center if not given.
        width = text_drawing.get_width()
        screen.blit(text_drawing, ((screen.get_width() - width) // 2, y))
        return width
    screen.blit(text_drawing, (x,y))

def gen_signal(freq):
    arr = np.array([4096 * np.sin(2.0 * np.pi * freq * x / samplerate) for x in range(0, samplerate)]).astype(np.int16)
    arr2 = np.c_[arr,arr]
    return pygame.sndarray.make_sound(arr2)

def morse_keyer():

    # morse mechanics
    sound = gen_signal(800)     # Hz sine wave.
    delay = fps * 0.5           # seconds until character is accepted.
    word_delay = fps * 1.5      # seconds until word split occurs.
    word_separation = False     # toggle with enter.
    dash_duration = fps * 0.15
    counter = 0                 # how long key has been held.
    key_toggle = False
    accept_counter = delay      # character is accepted when reaches 0.
    new_word_counter = word_delay
    char = ""
    text = ""                   # first row
    text2 = ""                  # second row

    bg_img = pygame.image.load("UI.png")
    font = gen_font(60)         # dot-dash and translated text
    data_font = gen_font(30)    # timing info in top left

    while True:

        screen.blit(bg_img, (0,0))

        # morse and translation drawings
        draw_text(char, None, (screen.get_height() - 120) // 2, font, (0,0,0))          # morse code
        row1_width = draw_text(text, None, screen.get_height() - 120, font, (0,0,0))    # row 1 text
        if text2:
            draw_text(text2, None, screen.get_height() - 75, font, (0,0,0))             # row 2 text

        # timing info text drawings
        draw_text(f"dash: " + str(dash_duration / fps) + "s", 10, 7, data_font, (255,255,255))
        draw_text(f"char: " + str(delay / fps) + "s", 10, 30, data_font, (255,255,255))
        if word_separation:
            draw_text(f"word: " + str(word_delay / fps) + "s", 10, 53, data_font, (255,255,255))
        else:
            draw_text(f"word split is off", 10, 53, data_font, (255,255,255))

        for event in pygame.event.get():
            
            if event.type == pygame.KEYDOWN:

                # slower dashes
                if event.key == pygame.K_PLUS:
                    dash_duration += 5
                    print("dash duration: " + str(dash_duration / fps) + "s")

                # faster dashes
                elif event.key == pygame.K_MINUS:
                    dash_duration -= 5 if dash_duration > 5 else 0
                    print("dash duration: " + str(dash_duration / fps) + "s")

                # slower accept
                elif event.key == pygame.K_UP:
                    delay += 10
                    print("current accept: " + str(delay / fps) + "s")

                # faster accept
                elif event.key == pygame.K_DOWN:
                    delay -= 10 if delay > 10 else 0
                    print("current accept: " + str(delay / fps) + "s")

                # increases the time between word splits
                elif event.key == pygame.K_RIGHT:
                    word_delay += 10
                    print("current word delay: " + str(word_delay / fps) + "s")

                # decreases the time between word splits
                elif event.key == pygame.K_LEFT:
                    word_delay -= 10 if word_delay > 10 else 0
                    print("current word delay: " + str(word_delay / fps) + "s")

                # clear current text
                elif event.key == pygame.K_BACKSPACE:
                    text = ""

                elif event.key == pygame.K_RETURN:
                    word_separation ^= True
                    print(f"Word separation is", word_separation)

                elif event.key == pygame.K_t:
                    print(text, text2)

                elif event.key == pygame.K_ESCAPE:
                    exit()

                elif pygame.key.name(event.key) in ("z", "x", "c", "v", "b", "n", "m", ",", "."):
                    key_toggle = True
                    new_word_counter = word_delay
                    accept_counter = delay
                    sound.play(-1)

            elif event.type == pygame.KEYUP:
                if key_toggle:
                    if counter < dash_duration:
                        char += "."
                    else:
                        char += "-"
                key_toggle = False
                counter = 0
                sound.stop()
            
            elif event.type == pygame.QUIT:
                exit()

        if key_toggle:
            counter += 1

        if char != "":
            accept_counter -= 1
            if accept_counter == 0 and row1_width < 530:
                text += alph[char]
                accept_counter = delay
                char = ""
            elif accept_counter == 0: # text is too wide, new row.
                text2 += alph[char]
                accept_counter = delay
                char = ""
        
        if not key_toggle and text and text[-1] != " " and word_separation:
            new_word_counter -= 1
            if new_word_counter == 0:
                text += " / "
                new_word_counter = word_delay

        pygame.display.flip()
        clock.tick(fps)

if __name__ == "__main__":
    morse_keyer()