from eye_gesture import get_gesture_frame

FIRST_BOX = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'
]

SECOND_BOX = [
    'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q'
]

THIRD_BOX = [
    'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]

BOXES = {1: FIRST_BOX, 2: SECOND_BOX, 3: THIRD_BOX}

class DataProvider:
    def __init__(self):
        self.current_box_index = 1
        self.selected_box_index = self.current_box_index
        self.selected_box = BOXES[self.selected_box_index]
        self.blink_count = 0
        self.selected_letter = 'a'
        self.written_string = ''

    def update_selection(self, event):
        if event == "FU":
            self.current_box_index = 1
        elif event == "FL":
            self.current_box_index = 2
        elif event == "FR":
            self.current_box_index = 3

        if  self.current_box_index != self.selected_box_index:
            self.selected_box_index = self.current_box_index
            self.selected_box  = BOXES[self.selected_box_index]
            self.blink_count = 0
            self.selected_letter = self.selected_box[self.blink_count]

        if event == "FB":
            self.blink_count = (self.blink_count + 1) % len(self.selected_box) 
            self.selected_letter = self.selected_box[self.blink_count]
        elif event == "SB":
            self.written_string += self.selected_letter

    def update_all(self):
        event = get_gesture_frame()
        if event:
            self.update_selection(event)


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
