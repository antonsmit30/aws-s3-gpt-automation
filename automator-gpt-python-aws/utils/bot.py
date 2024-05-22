from openai import OpenAI
import uuid
import json
from utils.worker import Worker
from utils.job import Job
import os
import subprocess
from atexit import register
from utils.util import log_full_message, enable_audio_wrap, log_all_attributes, temp_dir_appender

# testing audio file creation
from pathlib import Path
import base64
import re

speech_file_path = Path(__file__).parent.parent / "data" / "audio" / "bot" / "speech.mp3"
worker_dir_path = Path(__file__).parent.parent / "data" / "worker"
speech_file_path.parent.mkdir(parents=True, exist_ok=True)
worker_dir_path.parent.mkdir(parents=True, exist_ok=True)

@register
def cleanup():
    print("Cleaning up worker instances and job queue")
    MasterBot.job_queue = []

class Bot:

    def __init__(self, open_ai_key, role="user", state=None) -> None:
        self._openai_key = open_ai_key
        self._role = role
        self.state = state
        self._client = OpenAI(
            api_key=self._openai_key
        )
        # a random string value
        self.random_id = str(uuid.uuid4())

    # write a  method for the instance to get its own random id
    def get_random_id(self):
        return self.random_id


class MasterBot(Bot):

    job_queue = []
    instances = [] # Instance states
    tools = [
        {
            "type": "function",
            "function": {
                "name": "run_arbitrary_command",
                "description": """
- **Functionality**: Executes Linux commands locally.
- **Input**: Accepts a comma-separated string, `command`, with command and parameters (e.g., `['ls', '-l']`).
- **Output**: Returns command output and return code as strings (e.g., `return code: 0` for success).
- **Case Sensitivity**: Always use lower case for directory names.
- **Error Handling**: Errors are indicated with the message starting 'Exception occurred'.
""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": """comma separated string called 'command' of command with parameters to run. 
                            For example, the function can take in a command = "ls -l" or command = "which ls" etc."""
                        }
                    },
                    "required": ["command"],
                    }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": """Creates a file locally on the machine. 
                This function can be used for multiple linux related files""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": """The name of the file to create. 
                            Ensure you use camel case for naming files. 
                            Ensure you use lower case for all."""
                        },
                        "file_path": {
                            "type": "string",
                            "description": """The path of the file to create. 
                            Ensure you use camel case for naming files."""
                        },
                        "file_contents": {
                            "type": "string",
                            "description": """The contents of the file to create. 
                            Ensure you use camel case for naming files"""
                        }
                    },
                    "required": ["file_name", "file_path", "file_contents"],
                    }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_directory",
                "description": """Creates a directory locally on the machine. This function can be used for multiple linux related directories""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory_name": {
                            "type": "string",
                            "description": """The name of the directory to create. Ensure you use camel case for naming directories. Ensure you use lower case for all."""
                        },
                        "directory_path": {
                            "type": "string",
                            "description": """The path of the directory to create. Ensure you use camel case for naming directories."""
                        }
                    },
                    "required": ["directory_name", "directory_path"],
                    }
            }
        }
    ]

    def __init__(self, open_ai_key, role="user", state=None) -> None:
        super().__init__(open_ai_key, role, state)
        MasterBot.instances.append(self)
        self._openai_key = open_ai_key
        self._role = role
        self.state = state
        # self.ai_model = "gpt-3.5-turbo-0125"
        self.ai_model = "gpt-4o"
        self._temperature = 1.2
        # self.ai_model = "gpt-3.5-turbo-instruct"
        # self.ai_model = "gpt-4-1106-preview" # Do not enable this unless you want to get *** in the *** in your bank account
        self._client = OpenAI(
            api_key=self._openai_key
        )
        # a random string value
        self.random_id = str(uuid.uuid4())
        self._full_message = [
            {"role": "system", "content": f"""
You are the master of my AWS account. You are responsible for creating and managing infrastructure in AWS using the aws cli tool installed locally on the worker. Follow the following steps strictly:
2. **Interface with the Operator**: You must answer all questions and execute commands as directed.
3. **AWS Expertise**: You must expertly navigate AWS environments using CLI tools.
4. **Creative Problem-Solving**: You must independently interpret user requests, inferring parameters and filling gaps.
5. **Understanding AWS Architecture**: You must recognize required components like execution roles, security groups, and VPCs for tasks such as setting up EC2 instances.
6. **Review and Validation**: You must post-task, review outputs with the operator for accuracy.
7. **Project Management**: You must create and work within specific project directories unless directed otherwise. If a directory does not exist, you must create it.
8. **Clear Communication**: You must clarify ambiguities with the operator and explain your actions in full detail before commencing with the work.
9. **Task Sequencing**: You must understand and maintain the logical order of tasks.
10. **Tool Utilization**: You must read and adhere to tool descriptions. Use 'run_arbitrary_command' for executing Python subprocess.run commands, 
and 'create_file' for file creation. As well as 'create_directory' for directory creation.
Always use /projects as the base directory for your project directories.
12. **Naming Conventions**: you must always use camel case.
13. **Error Handling**: You must reevaluate and retry commands up to three times upon encountering exceptions.
14. **Task Completion Indication**: You must specify 'the operator will proceed with the next task' or 'waiting on operator' based on context.
15. **Command Execution**: You must use aws CLI for AWS resource management and verification.
16. **Linux Commands**: You must check tool availability before use, and use 'run_arbitrary_command' for Linux commands.
Remember, avoid emojis and refer to me as the operator. If the operator asks you for output ensure you return the cli output in your response with code formatting block.
             """},            
        ]
        self._enable_audio = False
    

    def __str__(self):
        return f"bot-{self.random_id}"
    
    # Getters
    @property
    def enable_audio(self):
        return self._enable_audio
    
    @enable_audio.setter
    def enable_audio(self, value: bool):
        self._enable_audio = value

    @property
    def temperature(self):
        return self._temperature
    
    @temperature.setter
    def temperature(self, value: float):
        self._temperature = value

    @property
    def full_message(self):
        return self._full_message
    
    @full_message.setter
    def full_message(self, value: list):
        self._full_message = value

    @log_all_attributes
    # @log_full_message
    # @enable_audio_wrap
    def speak_with_bot(self, message):
        """Submits message to the bot by creating message and creating run"""
        print(f"enable audio: {self._enable_audio}")
        print(f"job queue: {MasterBot.job_queue}")
        # grab message and append
        self._full_message.append({"role": self._role, "content": message})
        response = self._client.chat.completions.create(
            model=self.ai_model,
            messages=self._full_message,
            tools=MasterBot.tools,
            tool_choice="auto",
            temperature=self.temperature,
        )
        print(f"response total tokens: {response.usage.total_tokens}")
        print(f"response prompt tokens: {response.usage.prompt_tokens}")
        print(f"response completion tokens: {response.usage.completion_tokens}")
        # print(f"actual response: {response.choices[0].message}")
        response_content = response.choices[0].message.content
        # check if there are any tool calls
        tool_calls = response.choices[0].message.tool_calls
        print("first response: ", response_content)
        print("first tool calls: ", tool_calls)
        # If tool calls then ai wants to call a function which is great
        # modify message to only include the first message and the last 3 messages
        # self.modify_full_message()
        if tool_calls:
            # go into new loop!
            for _ in range(5):
                # print(f"full message: {self._full_message}")
                # print(f"yea there are tool calls: {tool_calls}")
                available_functions = {
                    "run_arbitrary_command": MasterBot.run_arbitrary_command,
                    "create_file": MasterBot.create_file,
                    "create_directory": MasterBot.create_directory,
                }

                # append bot assistant response to self.message
                self._full_message.append(response.choices[0].message)
                # print(self._full_message)

                # send the info for each function call and function response to the model
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    # print(f"function args: {function_args}")
                    if function_args:
                        # print("there are function args")

                        function_response = function_to_call(**function_args)
                    else:
                        function_response = function_to_call()
                    if function_response == "":
                        function_response = "No response"
                    self._full_message.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response

                    })
                    print(f"{tool_call.function.name} output: {function_response}")

                second_response = self._client.chat.completions.create(
                    model=self.ai_model,
                    messages=self._full_message,
                    temperature=self.temperature,
                )
                print(f"response total tokens: {second_response.usage.total_tokens}")
                print(f"response prompt tokens: {second_response.usage.prompt_tokens}")
                print(f"response completion tokens: {second_response.usage.completion_tokens}")
                second_response_content = f"{second_response.choices[0].message.content}"
                second_tool_calls = second_response.choices[0].message.tool_calls
                print("second response: ", second_response_content)
                print("second tool calls: ", second_tool_calls)
                # if not second_tool_calls and 'I will proceed with the next task' not in second_response_content: #TODO: will revisit and fix this at later stage
                if not second_tool_calls:
                    # append bot assistant response to self.message
                    self._full_message.append({"role": "assistant", "content": second_response_content})
                    # print(self._full_message)
                    # audio
                    if self.enable_audio:
                        no_code_message = re.sub(r'```[^`]*```', '', second_response_content)
                        audio_response = self._client.audio.speech.create(
                            model="tts-1",
                            voice="nova",
                            input=no_code_message,
                        )
                        audio_response.stream_to_file(speech_file_path)
                    print("second response does not need to call any tools, exiting", second_response_content)
                    return second_response_content  
        else:
            # append bot assistant response to self.message
            self._full_message.append({"role": "assistant", "content": response_content})
            # print(self._full_message)
            # audio
            if self.enable_audio:
                no_code_message = re.sub(r'```[^`]*```', '', response_content)
                audio_response = self._client.audio.speech.create(
                    model="tts-1",
                    voice="nova",
                    input=no_code_message,
                )
                audio_response.stream_to_file(speech_file_path)
            return response_content
        
    def modify_full_message(self):
        """Modifies the full message of the bot."""
        if len(self._full_message) > 4:
            # Keep the first item, and the last three items
            self._full_message = [self._full_message[0]] + self._full_message[-3:]
        
    # All Master Bot functions
    @staticmethod
    def run_arbitrary_command(command: str):
        """Runs an arbitrary command locally using subprocess."""
        joined_command: str = f"{''.join(command)}"
        print(f"combined command: {joined_command}")
        try:
            result = subprocess.run(joined_command, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    shell=True)
            if result.stderr.decode("utf-8") != "":
                raise Exception(f"{result.stderr.decode('utf-8')}")
            else:
                return result.stdout.decode("utf-8") 
        except Exception as e:
            print(f"Exception: {e}")
            return f"Exception occurred. {e}"
        
    
    @staticmethod
    # @temp_dir_appender
    def create_file(file_name, file_path, file_contents):
        """Creates a file locally on the machine."""
        try:
            with open(file_path + "/" + file_name, "w") as f:
                f.write(file_contents)
            return "File created"
        except Exception as e:
            return f"Exception occurred. {e}"
        
    @staticmethod
    # @temp_dir_appender
    def create_directory(directory_name, directory_path):
        """Creates a directory locally on the machine."""
        try:
            os.mkdir(directory_path + "/" + directory_name)
            return "Directory created"
        except Exception as e:
            return f"Exception occurred. {e}"
        

    # @staticmethod
    def get_audio_chunk(self):
        """Gets the audio chunk from the speech file."""
        with open(speech_file_path, "rb") as f:
            return f.read()
    
    def get_audio_b64(self):
        """Gets the audio b64 string from the speech file."""
        with open(speech_file_path, "rb") as f:
            # return f.read().encode("base64")
            return base64.b64encode(f.read()).decode("utf-8")
    
        
    def transcribe_audio(self, path):
        """Transcribes the audio file."""
        with open(path, "rb") as f:
            try:
                transcript = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                )
            except Exception as e:
                return f"Exception occurred. {e}"
            return transcript


