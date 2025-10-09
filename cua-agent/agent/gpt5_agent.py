from computers import Computer
from utils import (
    create_chat_completion,
    parse_action_from_text,
    show_image,
    check_blocklisted_url,
)


class GPT5Agent:
    """
    Agent using GPT-5 Nano (or GPT-4o) instead of computer-use-preview.

    Key differences from CUA Agent:
    - Uses Chat Completions API instead of Responses API
    - Model returns natural language, we parse it into actions
    - We manually manage screenshot loop
    - More flexible but requires text parsing
    """

    def __init__(
        self,
        model="gpt-5-nano",  # Can also use "gpt-4o"
        computer: Computer = None,
        system_prompt: str = None,
        max_api_calls: int = 20,
    ):
        self.model = model
        self.computer = computer
        self.conversation_history = []
        self.print_steps = True
        self.debug = False
        self.show_images = False
        self.max_api_calls = max_api_calls
        self.api_calls_made = 0

        # Default system prompt for UI testing
        self.system_prompt = system_prompt or """You are a Computer-Use web agent. You can only act by calling the provided tools.

Mission:
- Complete each assessment question accurately and advance to the next question.
- Use precise selectors and robust waits; minimize unnecessary actions.
- Keep a running list of answer choices you have already tried along with the feedback received.
- Surface any UX/UI issues or front-end improvement ideas in your final summary.

Rules:
- Always call observe() if the page might have changed since the last action.
- Before clicking, read the current question text and enumerate the visible answer choices from the most recent observe() output.
- After every click, immediately observe(); use the feedback panel to determine whether the choice was correct or wrong, then note that outcome in your Thought so you never retry a known-wrong choice.
- If a click does not change the UI, observe() again and choose a different strategy rather than re-clicking the same coordinates blindly.
- Stop when the success criteria are satisfied (question correct, explanation captured, or navigation complete), then return a concise summary covering assessment progress and UX findings without further tool calls.
- NEVER invent selectors; target elements listed in observe() or, when unavoidable, use coordinates that clearly land inside the intended element.
- For text entry: type before submitting and confirm the result with observe() or extract().

Response format for every turn:
Thought: <succinct reasoning that names the question, lists already-tried answers with their outcomes, and states the exact next action and why>
Action: <exactly one literal command chosen from {Observe, Wait N seconds, Click at (X, Y), Type 'text', Scroll down N, Scroll up N}>

Keep the Action line literal; no commentary after it."""

    def debug_print(self, *args):
        if self.debug:
            print(*args)

    def add_screenshot_to_conversation(self, screenshot_base64: str, user_message: str = None):
        """Add a screenshot (and optional text) to conversation history"""
        content = []

        if user_message:
            content.append({"type": "text", "text": user_message})

        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{screenshot_base64}"
            }
        })

        self.conversation_history.append({
            "role": "user",
            "content": content
        })

    def get_model_response(self) -> str:
        """
        Call GPT-5 Nano with current conversation history.
        Returns the model's text response.
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)

        if self.debug:
            print(f"[DEBUG] Calling {self.model} with {len(messages)} messages...")

        if self.api_calls_made >= self.max_api_calls:
            raise RuntimeError(
                f"Max API call limit ({self.max_api_calls}) reached; stopping the agent."
            )

        response = create_chat_completion(
            messages=messages,
            model=self.model,
            max_tokens=3000,
            temperature=0.7,
        )

        if "error" in response:
            raise ValueError(f"API Error: {response['error']}")

        self.api_calls_made += 1

        if self.debug:
            # Inspect full payload when debugging to understand multimodal responses
            print("[DEBUG] Full response payload:", response)

        assistant_message = response["choices"][0]["message"]["content"]

        if self.debug:
            # Helps inspect the raw payload in truncated/structured replies
            print("[DEBUG] Raw choice payload:", response["choices"][0])

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def execute_action_if_found(self, text: str) -> bool:
        """
        Parse text for actions and execute them via Playwright.
        Returns True if action was found and executed, False otherwise.
        """
        action = parse_action_from_text(text)

        if not action:
            return False

        action_type = action["type"]
        action_args = {k: v for k, v in action.items() if k != "type"}

        if self.print_steps:
            print(f"🤖 Executing: {action_type}({action_args})")

        # Execute action on computer
        method = getattr(self.computer, action_type)
        method(**action_args)

        return True

    def run_turn(self, user_input: str = None, print_steps=True, show_images=False, debug=False):
        """
        Run one turn of interaction:
        1. Take screenshot
        2. Send to GPT-5 Nano with user input
        3. Get response
        4. Parse and execute any actions
        5. Return model's analysis
        """
        self.print_steps = print_steps
        self.show_images = show_images
        self.debug = debug

        # Take screenshot
        screenshot_base64 = self.computer.screenshot()

        if self.show_images:
            show_image(screenshot_base64)

        # Add to conversation
        self.add_screenshot_to_conversation(screenshot_base64, user_input)

        # Get model's response
        response_text = self.get_model_response()

        if self.print_steps:
            print(f"\n💬 {self.model}: {response_text}\n")

        # Try to execute any actions mentioned in response
        action_executed = self.execute_action_if_found(response_text)

        # If action was executed, take another screenshot for next turn
        if action_executed:
            new_screenshot = self.computer.screenshot()

            if self.show_images:
                show_image(new_screenshot)

            # Add result screenshot to conversation
            self.add_screenshot_to_conversation(
                new_screenshot,
                "Here's the result after executing that action. What should I do next?"
            )

        return response_text

    def run_interactive_loop(self, print_steps=True, show_images=False, debug=False):
        """
        Run an interactive testing session.
        User can give instructions, model analyzes and suggests actions.
        """
        self.print_steps = print_steps
        self.show_images = show_images
        self.debug = debug

        print(f"\n🤖 GPT-5 Nano UI Testing Agent")
        print(f"   Model: {self.model}")
        print(f"   Type 'exit' to quit\n")

        # Initial screenshot
        screenshot = self.computer.screenshot()

        if self.show_images:
            show_image(screenshot)

        self.add_screenshot_to_conversation(
            screenshot,
            "Analyze this application. What do you see? What should we test first?"
        )

        # Get initial analysis
        initial_response = self.get_model_response()
        if self.print_steps:
            print(f"💬 {self.model}: {initial_response}\n")

        # Interactive loop
        while True:
            try:
                user_input = input("> ")
                if user_input.lower() == "exit":
                    break

                self.run_turn(user_input, print_steps, show_images, debug)

            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                if debug:
                    import traceback
                    traceback.print_exc()
