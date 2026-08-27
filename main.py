import sounddevice as sd
import scipy.io.wavfile as wav
from pygame import *

# === Налаштування аудіо та вікна ===
fs = 44100
chunk = 1024
width, height = 1200, 650

voice_file = 'voice.wav'


songs_list = [
    {"title": "Arctic Monkeys", "file": "arctic.mp3"},
    {"title": "TV Girl", "file": "TV Girl-Song About Me.mp3"},
    {"title": "Whatsaheart", "file": "whatsaheart - lovesick.mp3"}
]
current_song_index = 0
music_file = songs_list[current_song_index]["file"]


init()
font.init()
mixer.init()
mixer.music.set_volume(0.5)

window = display.set_mode((width, height))
display.set_caption("Karaoke Retrowave")
clock = time.Clock()


font_title = font.SysFont('Arial', 30, bold=True)
font_btn = font.SysFont('Arial', 20, bold=True)
font_header = font.SysFont('Arial', 32, bold=True)


bg_img = transform.scale(image.load('bg.jpg'), (width, height))

main_btn_img = transform.scale(image.load('button.png'), (450, 110))
main_btn_rect = main_btn_img.get_rect(center=(width // 2, height // 2))

song_btn_img = transform.scale(image.load('song_btn.png'), (350, 70))

song_rects = []
for i in range(len(songs_list)):
    rect = song_btn_img.get_rect(topleft=(40 + i * 375, 90))
    song_rects.append(rect)

# === Змінні стану ===
is_recording = False
recording = None
data = [0.0] * chunk


def audio_callback(indata, frames, time_info, status):
    global data
    if status:
        print(status)
    data = [sample * 160 for sample in indata[:, 0].tolist()]



stream = sd.InputStream(
    callback=audio_callback,
    channels=1,
    samplerate=fs,
    blocksize=chunk,
    dtype='float32'
)
stream.start()



def start_recording():
    global recording
    recording = sd.rec(int(fs * 60), samplerate=fs, channels=1, dtype='int16')


def stop_and_save_recording():
    global recording
    sd.stop()
    if recording is not None:
        wav.write(voice_file, fs, recording)


def play_combined():
    mixer.music.load(music_file)
    mixer.music.play()
    try:
        voice_sound = mixer.Sound(voice_file)
        voice_sound.play()
    except Exception as e:
        print("Помилка відтворення голосу:", e)



running = True
rect_text = 'Старт запису'

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            # 1. Вибір пісні
            if not is_recording:
                for idx, rect in enumerate(song_rects):
                    if rect.collidepoint(e.pos):
                        current_song_index = idx
                        music_file = songs_list[current_song_index]["file"]
                        mixer.music.stop()


            if main_btn_rect.collidepoint(e.pos):
                if not is_recording:
                    is_recording = True
                    rect_text = 'Зупинити та прослухати'
                    mixer.music.load(music_file)
                    mixer.music.play()
                    start_recording()
                else:
                    is_recording = False
                    rect_text = 'Старт запису'
                    stop_and_save_recording()
                    play_combined()

    window.blit(bg_img, (0, 0))


    header_surface = font_header.render(f"ТРЕК: {songs_list[current_song_index]['title']}", True, (255, 255, 255))
    window.blit(header_surface, ((width - header_surface.get_width()) // 2, 25))

    for idx, rect in enumerate(song_rects):
        window.blit(song_btn_img, rect)

        if idx == current_song_index:
            draw.rect(window, (255, 0, 128), rect, width=4, border_radius=15)

        song_text = font_btn.render(songs_list[idx]["title"], True, (255, 255, 255))
        st_x = rect.x + (rect.width - song_text.get_width()) // 2
        st_y = rect.y + (rect.height - song_text.get_height()) // 2
        window.blit(song_text, (st_x, st_y))

    points = []
    wave_center_y = height - 90
    for i, sample in enumerate(data):
        x = int(i * width / chunk)
        y = int(wave_center_y + sample)
        points.append((x, y))

    if len(points) > 1:
        draw.lines(window, (255, 20, 147), False, points, 6)


    window.blit(main_btn_img, main_btn_rect)
    text_surface = font_title.render(rect_text, True, (255, 255, 255))
    text_x = main_btn_rect.x + (main_btn_rect.width - text_surface.get_width()) // 2
    text_y = main_btn_rect.y + (main_btn_rect.height - text_surface.get_height()) // 2
    window.blit(text_surface, (text_x, text_y))

    display.update()
    clock.tick(60)


stream.stop()
stream.close()
quit()











