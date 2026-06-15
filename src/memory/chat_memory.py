from collections import deque


class ChatMemory:

    def __init__(self, max_history=5):

        self.history = deque(maxlen=max_history)

    def add_message(self, role, content):

        self.history.append(
            {
                "role": role,
                "content": content
            }
        )

    def get_context(self):

        context = ""

        for item in self.history:

            context += f"""
{item['role']}:
{item['content']}
"""

        return context

    def clear(self):

        self.history.clear()


memory = ChatMemory()


if __name__ == "__main__":

    memory.add_message(
        "User",
        "How many casual leaves are allowed?"
    )

    memory.add_message(
        "Assistant",
        "6 Days per year"
    )

    print(memory.get_context())