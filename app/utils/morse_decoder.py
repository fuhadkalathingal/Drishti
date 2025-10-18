from app.utils.speech import speak

# Morse Code to Alphabet Mapping (A–Z)
MORSE_TO_ALPHA = {
    '.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e',
    '..-.': 'f', '--.': 'g', '....': 'h', '..': 'i', '.---': 'j',
    '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n', '---': 'o',
    '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't',
    '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y',
    '--..': 'z',
    '.....': 'space', '-----': 'delete', '...--': 'play'
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
                else:
                    string += tmp

            case "FR": 
                string += " "
            case "FL": 
                if buffer:
                    buffer = ""
                else:
                    string = string[:-1]
            #case "SL": 
            #        buffer = ""
            #        string = ""

    return buffer, string

# Example usage:
if __name__ == "__main__":
    code = input("Enter Morse code for a letter (e.g., .-): ").strip()
    string = morse_to_letter(code)
    print("Decoded letter:", string)
