import asyncio
from autogen import (
    AssistantAgent,
    GroupChat, ConversableAgent, register_function, Agent,
)
from autogen.coding import DockerCommandLineCodeExecutor

from agents.tools.github_tools import create_github_gist
from agents.user_proxy_webagent import UserProxyWebAgent
from agents.group_chat_web import GroupChatManagerWeb

from llm_config import GPT4Turbo_config
from agents.utils import render_template


class CodeGenGroupChat:
    def __init__(self, chat_id: str = None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.executor = DockerCommandLineCodeExecutor(
            image="python:3.11-slim",
            timeout=60,
            work_dir="output",
            stop_container=True,
            auto_remove=True
        )

        self.user_proxy = UserProxyWebAgent(
            name="user_proxy",
            description="User Proxy agent to handle sending of tasks to Agents",
            max_consecutive_auto_reply=2,
            code_execution_config=False,
            human_input_mode="NEVER",
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        )

        self.planner = AssistantAgent(
            name="planner",
            description="This is a planner agent that always runs first. "
                        "This agent writes clear step by step plans for "
                        "the Programmer to use. ",
            system_message=render_template("planner.jinja"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            default_auto_reply="",
            llm_config={
                "config_list": [GPT4Turbo_config],
                "temperature": 0.9,
            },
        )

        self.programmer = AssistantAgent(
            name="programmer",
            description="This is the Programmer agent that never goes first. "
                        "This agent writes clean and efficient code, "
                        "and sends it to the Optimizer for testing and review",
            system_message=render_template("programmer.jinja"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=4,
            default_auto_reply="",
            llm_config={
                "config_list": [GPT4Turbo_config],
                "temperature": 0.1,
                "stream": True
            },
        )

        self.optimizer = AssistantAgent(
            name="optimizer",
            description="This is an Optimizer agent that never goes first. "
                        "This agent writes clean and efficient code, "
                        "and only goes after the programmer. ",
            system_message=render_template("optimizer.jinja"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=8,
            default_auto_reply="TERMINATE",
            llm_config={
                "config_list": [GPT4Turbo_config],
                "temperature": 1,
                "stream": True
            },
        )

        self.tester = ConversableAgent(
            name="Tester",
            description="This is an Tester agent that never goes first. "
                        "This agent test the code generated by the programmer, "
                        "along with the changes made by the optimizer, "
                        "and only goes after the programmer and optimizer. ",
            system_message=render_template("tester.jinja"),
            llm_config=False,
            human_input_mode="NEVER",
            code_execution_config={"executor": self.executor, "last_n_messages": 3},
        )

        self.check_in = AssistantAgent(
            name="Check-In",
            description="This is an Check-In agent that never goes first. "
                        "This agent submits the finalized code to GitHub "
                        "Gist, and only goes after the Optimizer approves "
                        "the code. ",
            system_message=render_template("checkin.jinja"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
            default_auto_reply="",
            llm_config={
                "config_list": [GPT4Turbo_config],
                "temperature": 0.1,
            },
        )

        # Add the Tx and Rx queues to the User Proxy
        self.user_proxy.set_queues(
            self.client_sent_queue,
            self.client_receive_queue
        )

        self.groupchat = GroupChat(
            agents=[
                self.user_proxy,
                self.planner,
                self.programmer,
                self.optimizer,
                self.tester,
                self.check_in
            ],
            messages=[],
            max_round=20,
            speaker_selection_method="auto",
        )

        self.manager = GroupChatManagerWeb(
            name="manager",
            description="This is a manager agent that controls and directs other Agents. "
                        "The Manager strictly maintains the workflow order",
            system_message=render_template("manager.jinja"),
            groupchat=self.groupchat,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            default_auto_reply="TERMINATE",
            llm_config={
                "config_list": [GPT4Turbo_config],
                "temperature": 0.1,
            },
        )

        # Tool Functions
        # Register the tool function for use in the workflow
        register_function(
            create_github_gist,
            caller=self.check_in,
            executor=self.user_proxy,
            name="create_github_gist",
            description="Create a GitHub Gist from the code generated by the programmer.",
        )

    async def start(self, message: str):
        await self.user_proxy.a_initiate_chat(
            self.manager, message=message
        )

    def get_agent_messages(self, agent: Agent):
        return [msg for msg in self.groupchat.messages if msg["name"] == agent.name]
