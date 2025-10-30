from app.utils.speech import speak

# Morse Code to Alphabet Mapping (A–Z)
MORSE_TO_ALPHA = {
    '.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e',
    '..-.': 'f', '--.': 'g', '....': 'h', '..': 'i', '.---': 'j',
    '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n', '---': 'o',
    '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't',
    '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y',
    '--..': 'z',
    '.....': 'space', '-----': 'delete', '...--': 'play', '---..': 'chat'
}

def morse_to_letter(buffer):
    return MORSE_TO_ALPHA.get(buffer, '')  # '' if not a valid Morse code

def event_to_letter(event, buffer, string):
    if event:
        match event:
            case "FB": 
                buffer += "."
            case "SB":
                buffer += "-"
            case "VSB": 
                tmp = morse_to_letter(buffer)
                buffer = ""

                if tmp == "space":
                    string += " "
                elif tmp == "delete":
                    string = ""
                elif tmp == "play":
                    speak(string)
                elif tmp == "chat":
                    from app.chat_ui import DrishtiAIUI
                    import app.utils.global_state as gs

                    if gs.main_ui:
                        gs.main_ui.withdraw()  # hide main window

                    chat_app = DrishtiAIUI(gs.main_ui)

                    def on_close():
                        chat_app.destroy()
                        if gs.main_ui:
                            gs.main_ui.deiconify()  # show main window again

                    chat_app.protocol("WM_DELETE_WINDOW", on_close)
                    chat_app.wait_window()  # block until chat window is closed
                else:
                    string += tmp
            case "FL": 
                if buffer:
                    buffer = buffer[:-1]
                else:
                    string = string[:-1]

    return buffer, string

# Example usage:
if __name__ == "__main__":
    code = input("Enter Morse code for a letter (e.g., .-): ").strip()
    string = morse_to_letter(code)
    print("Decoded letter:", string)
