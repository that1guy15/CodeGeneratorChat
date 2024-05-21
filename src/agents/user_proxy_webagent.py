from autogen import Agent, ConversableAgent, UserProxyAgent, AssistantAgent
from typing import Any, Dict, List, Optional, Tuple, Union
try:
    from termcolor import colored
except ImportError:
    def colored(x, *args, **kwargs):
        return x


class UserProxyWebAgent(UserProxyAgent):
    def __init__(self, *args, **kwargs):
        super(UserProxyWebAgent, self).__init__(*args, **kwargs)
        self._reply_func_list = []
        self.register_reply([Agent, None], ConversableAgent.generate_oai_reply)
        self.register_reply([Agent, None], ConversableAgent.generate_code_execution_reply)
        self.register_reply([Agent, None], ConversableAgent.generate_function_call_reply)
        self.register_reply([Agent, None], UserProxyWebAgent.a_generate_tool_calls_reply)
        self.register_reply([Agent, None], UserProxyWebAgent.a_check_termination_and_human_reply)

    def set_queues(self, client_sent_queue, client_receive_queue):
        self.client_sent_queue = client_sent_queue
        self.client_receive_queue = client_receive_queue

    async def a_get_human_input(self, prompt: str) -> str:
        last_message = self.last_message()
        if last_message["content"]:
            await self.client_receive_queue.put(last_message["content"])
            reply = await self.client_sent_queue.get()
            if reply and reply == "DO_FINISH":
                return "exit"
            return reply
        else:
            return
