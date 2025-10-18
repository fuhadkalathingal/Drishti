# Morse Code to Alphabet Mapping (A–Z)
MORSE_TO_ALPHA = {
    '.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e',
    '..-.': 'f', '--.': 'g', '....': 'h', '..': 'i', '.---': 'j',
    '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n', '---': 'o',
    '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't',
    '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y',
    '--..': 'z'
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
                string += morse_to_letter(buffer)
                buffer = ""
            case "FR": 
                string += " "
            case "FL": 
                if buffer:
                    buffer = buffer[:-1]
            case "SL": 
                    buffer = ""
                    string = ""

    return buffer, string

# Example usage:
if __name__ == "__main__":
    code = input("Enter Morse code for a letter (e.g., .-): ").strip()
    string = morse_to_letter(code)
    print("Decoded letter:", string)
