from copy import deepcopy


class Memory:
    id = 0
    def __init__(self):
        self.messages = []
       

    def prepare_message(self, role, content):
        return {
            "role": role,
            "content": content
        }
    def  save_to_memory(self, role, message):
        message = self.prepare_message(role, message)
        self.messages.append(message)

    def save_message(self, message):
        """Preserve complete messages, including tool calls and result IDs."""
        self.messages.append(deepcopy(message))


    def get_memory(self):
        return self.messages


