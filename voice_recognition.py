import speech_recognition as sr  # type: ignore
import pyaudio
import json
import os
import pyperclip  # type: ignore
import keyboard
import customtkinter as ctk  # type: ignore

CONFIG_FILE = "config.json"


def get_audio_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info["maxInputChannels"] > 0:
            devices.append((device_info["index"], device_info["name"]))
    p.terminate()
    return devices


def save_config(device, language):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"device": device, "language": language}, f)


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def transcribe_audio(device_index):
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        status_label.configure(text="Escuchando... Habla ahora")
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
        status_label.configure(text="Transcribiendo...")
        try:
            language = "es-ES" if language_var.get() == "Español" else "en-US"
            text = recognizer.recognize_google(audio, language=language)
            if write_anywhere_var.get():
                keyboard.write(text)
            else:
                text_output.insert("end", text + "\n")
                text_output.see("end")
        except sr.UnknownValueError:
            text_output.insert("end", "No se pudo entender el audio.\n")
        except sr.RequestError:
            text_output.insert(
                "end", "Error de conexión. Verifica tu internet.\n"
            )  # noqa E501
    status_label.configure(text="Listo para transcribir")


def start_transcription():
    selected_device = device_combobox.get()
    device_index = next(
        index for index, name in devices if name == selected_device
    )  # noqa: E501
    save_config(selected_device, language_var.get())
    transcribe_audio(device_index)


def copy_text():
    text = text_output.get("0.0", "end")
    pyperclip.copy(text)
    status_label.configure(text="Texto copiado al portapapeles")


# Configuración de CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Crear la ventana principal
root = ctk.CTk()
root.title("Transcriptor de Voz")
root.geometry("500x600")
root.attributes("-topmost", True)  # Mantiene la ventana siempre al frente

# Frame principal
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Obtener dispositivos de audio
devices = get_audio_devices()

# Cargar configuración
config = load_config()

# Widgets
device_label = ctk.CTkLabel(main_frame, text="Selecciona el micrófono:")
device_label.pack(pady=10)

device_combobox = ctk.CTkOptionMenu(
    main_frame, values=[name for _, name in devices], width=300
)
device_combobox.pack(pady=5)
device_combobox.set(
    config.get(
        "device", devices[0][1] if devices else "No se encontraron micrófonos"
    )  # noqa E501
)

# Selector de idioma
language_var = ctk.StringVar(value=config.get("language", "Español"))
language_label = ctk.CTkLabel(main_frame, text="Selecciona el idioma:")
language_label.pack(pady=5)
language_menu = ctk.CTkOptionMenu(
    main_frame, variable=language_var, values=["Español", "English"], width=300
)
language_menu.pack(pady=5)

start_button = ctk.CTkButton(
    main_frame, text="Iniciar Transcripción", command=start_transcription
)
start_button.pack(pady=10)

write_anywhere_var = ctk.BooleanVar()
write_anywhere_check = ctk.CTkCheckBox(
    main_frame, text="Escribir en cualquier lugar", variable=write_anywhere_var
)
write_anywhere_check.pack(pady=5)

status_label = ctk.CTkLabel(main_frame, text="Listo para transcribir")
status_label.pack(pady=5)

text_output = ctk.CTkTextbox(main_frame, height=200, width=400)
text_output.pack(pady=10, fill="both", expand=True)

copy_button = ctk.CTkButton(main_frame, text="Copiar Texto", command=copy_text)
copy_button.pack(pady=5)

root.mainloop()
