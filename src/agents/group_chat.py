import asyncio
from autogen import (
    AssistantAgent,
    GroupChat,
)
from agents.user_proxy_webagent import UserProxyWebAgent
from agents.groupchatweb import GroupChatManagerWeb
from llm_config import GPT4Turbo_config
from agents.utils import render_template


class AutogenCodeGenGroupChat:
    def __init__(self, chat_id: str = None, websocket=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.client_sent_queue = asyncio.Queue()
        self.client_receive_queue = asyncio.Queue()

        self.user_proxy = UserProxyWebAgent(
            name="user_proxy",
            description="User Proxy agent to handle sending of tasks to Agents",
            system_message="You are a helpful assistant.",
            max_consecutive_auto_reply=10,
            code_execution_config=False,
            human_input_mode="ALWAYS",
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        )

        self.planner = AssistantAgent(
            name="planner",
            description="This is a planner agent that always runs first. "
                        "This agent writes clear step by step plans for "
                        "the Programmer to use. ",
            system_message=render_template("planner.jinja"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=5,
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
                self.optimizer
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

    async def start(self, message: str):
        await self.user_proxy.a_initiate_chat(
            self.manager, message=message
        )
        self.user_proxy.return_chat_messages()