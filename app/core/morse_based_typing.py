from app.core.eye_gesture import get_gesture_frame
from app.utils.morse_decoder import event_to_letter
from app.utils.text_suggestion import suggest, update_user_cache
from app.utils.speech import speak


class DataProvider:
    def __init__(self):
        self.current_level = 0
        self.blink_count = 0
        self.buffer = ""
        self.written_string = ""

        # Suggestion related
        self.current_suggestion = {"suggestion": [], "type": "none"}
        self.selected_suggestion_index = 0

    def update_selection(self, event):
        self.buffer, self.written_string = event_to_letter(
            event, self.buffer, self.written_string
        )

    def update_suggestions(self):
        prefix_sugg, context_sugg = suggest(self.written_string)
        self.current_suggestion["suggestion"] = prefix_sugg or context_sugg
        self.current_suggestion["type"] = "context" if context_sugg else "prefix" if prefix_sugg else "none"
        while len(self.current_suggestion["suggestion"]) < 4:
            self.current_suggestion["suggestion"].append("")

    def suggestion_selection(self, event):
        if event == "FB":
            no_of_suggestions = len(self.current_suggestion["suggestion"])
            if no_of_suggestions:
                self.selected_suggestion_index = (self.selected_suggestion_index + 1) % no_of_suggestions
            else:
                return
        elif event == "SB":
            if self.current_suggestion["type"] == "prefix":
                # Split into words
                words = self.written_string.split()

                # Replace the last word with the selected suggestion
                words[-1] = self.current_suggestion['suggestion'][self.selected_suggestion_index]

                # Reconstruct the string
                self.written_string = " ".join(words) + " "  # add space after suggestion

                # Update cache
                update_user_cache(words[-1], self.current_suggestion['suggestion'][self.selected_suggestion_index])
            elif self.current_suggestion["type"] == "context":
                words = self.written_string.split()
                self.written_string += f"{self.current_suggestion['suggestion'][self.selected_suggestion_index]} "
                update_user_cache((words[-2], words[-1]), self.current_suggestion['suggestion'][self.selected_suggestion_index])

    def update_all(self):
        event = get_gesture_frame()
        self.update_suggestions()
        if event:
            if event == "FU":
                self.current_level = (self.current_level + 1) % 2
            elif event == "SR":
                speak(self.written_string)

            if self.current_level == 0:
                self.selected_suggestion_index = 0
                self.update_selection(event)
            elif self.current_level == 1:
                self.suggestion_selection(event)

if __name__ == '__main__':
    datasobj = DataProvider()
    while True:
        datasobj.update_all()
        print(datasobj.current_level)
        print(datasobj.buffer)
        print(datasobj.written_string)
        print(datasobj.current_suggestion)
