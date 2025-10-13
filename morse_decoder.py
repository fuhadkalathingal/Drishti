# Morse Code to Alphabet Mapping (A–Z)
MORSE_TO_ALPHA = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z'
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
                else:
                    string = string[:-1]
            case "SL": 
                if buffer:
                    buffer = ""
                else:
                    string = ""

    return buffer, string

# Example usage:
if __name__ == "__main__":
    code = input("Enter Morse code for a letter (e.g., .-): ").strip()
    string = morse_to_letter(code)
    print("Decoded letter:", string)
