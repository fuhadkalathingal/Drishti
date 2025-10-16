from eye_gesture import get_gesture_frame
from text_suggestion import suggest, update_user_cache
from speech import speak

FIRST_BOX = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'
]

SECOND_BOX = [
    'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q'
]

THIRD_BOX = [
    'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

FOURTH_BOX = [
    "DEL", "SPACE", "CLEAR", "SPEAK"
]

BOXES = {1: FIRST_BOX, 2: SECOND_BOX, 3: THIRD_BOX, 4: FOURTH_BOX}

class DataProvider:
    def __init__(self):
        self.current_level = 0
        self.current_box_index = 1
        self.selected_box_index = self.current_box_index
        self.selected_box = BOXES[self.selected_box_index]
        self.blink_count = 0
        self.selected_letter = 'a'
        self.written_string = ''
        self.current_suggestion = {"suggestion": [], "type": "prefix"}
        self.selected_suggestion_index = 0

    def update_selection(self, event):
        if event == "FU":
            self.current_box_index = 1
        elif event == "FL":
            self.current_box_index = 2
        elif event == "FR":
            self.current_box_index = 3
        elif event == "SL":
            self.current_box_index = 4

        if  self.current_box_index != self.selected_box_index:
            self.selected_box_index = self.current_box_index
            self.selected_box  = BOXES[self.selected_box_index]
            self.blink_count = 0
            self.selected_letter = self.selected_box[self.blink_count]

        if event == "FB":
            self.blink_count = (self.blink_count + 1) % len(self.selected_box) 
            self.selected_letter = self.selected_box[self.blink_count]
        elif self.selected_box_index != 4:
            if event == "SB":
                self.written_string += self.selected_letter
        else:
            if event == "SB":
                if self.selected_letter == "DEL":
                    self.written_string = self.written_string[:-1]
                elif self.selected_letter == "SPACE":
                    self.written_string += ' '
                elif self.selected_letter == "CLEAR":
                    self.written_string = ""
                elif self.selected_letter == "SPEAK":
                    speak(self.written_string)

    def update_suggestions(self):
        prefix_sugg, context_sugg = suggest(self.written_string)
        self.current_suggestion["suggestion"] = prefix_sugg or context_sugg
        self.current_suggestion["type"] = "prefix" if prefix_sugg else "context"

    def suggestion_selection(self, event):
        if event == "FB":
            no_of_suggestions = len(self.current_suggestion["suggestion"])
            if no_of_suggestions:
                self.selected_suggestion_index = (self.selected_suggestion_index + 1) % no_of_suggestions
            else:
                return
        elif event == "SB":
            if self.current_suggestion["type"] == "prefix":
                last_word = self.written_string.rstrip().split()[-1]
                self.written_string = self.written_string[:len(self.written_string) - len(last_word)] + f"{self.current_suggestion['suggestion'][self.selected_suggestion_index]} "
                update_user_cache(last_word, self.current_suggestion["suggestion"][self.selected_suggestion_index])
            else:
                words = self.written_string.rstrip().split()
                self.written_string += f"{self.current_suggestion['suggestion'][self.selected_suggestion_index]} "
                update_user_cache((words[-2], words[-1]), self.current_suggestion["suggestion"][self.selected_suggestion_index])

    def update_all(self):
        event = get_gesture_frame()
        if event:
            self.update_suggestions()

            if event == "VSB":
                self.current_level = (self.current_level + 1) % 2

            if self.current_level == 0:
                self.selected_suggestion_index = 0
                self.update_selection(event)
            elif self.current_level == 1:
                self.suggestion_selection(event)

if __name__ == '__main__':
    datasobj = DataProvider()
    alphabets = []
    letter = ''
    while True:
        datasobj.update_all()
        next_alphabets = datasobj.selected_box
        next_letter = datasobj.selected_letter
        if next_letter != letter:
            letter = next_letter
            if next_alphabets != alphabets:
                alphabets = next_alphabets

            print(alphabets)
            print(letter)
            print(datasobj.written_string)
            print(datasobj.current_suggestion)
            print(datasobj.selected_suggestion_index)
