"""
Copyright 2024 HaiyangLi

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import inspect
from pydantic import Field
from lionagi.libs import convert, ParseUtil
from .message import RoledMessage, MessageRole


class ActionRequest(RoledMessage):
    """
    Represents a request for an action with function and arguments.

    Inherits from `RoledMessage` and provides attributes specific to action requests.

    Attributes:
        function (str): The name of the function to be called.
        arguments (dict): The keyword arguments to be passed to the function.
        action_response (str): The ID of the action response that this request corresponds to.
    """

    function: str | None = Field(
        None, description="The name of the function to be called"
    )

    arguments: dict | None = Field(
        None, description="The keyword arguments to be passed to the function"
    )

    action_response: str | None = Field(
        None,
        description="The id of the action response that this request corresponds to",
    )

    def __init__(
        self,
        function=None,
        arguments=None,
        sender=None,  # sender is the assistant who made the request
        recipient=None,  # recipient is the actionable component
        **kwargs,
    ):
        """
        Initializes the ActionRequest.

        Args:
            function (str or function, optional): The function to be called.
            arguments (dict, optional): The keyword arguments for the function.
            sender (str, optional): The sender of the request.
            recipient (str, optional): The recipient of the request.
        """
        function = function.__name__ if inspect.isfunction(function) else function
        arguments = _prepare_arguments(arguments)

        super().__init__(
            role=MessageRole.ASSISTANT,
            sender=sender,
            recipient=recipient,
            content={"action_request": {"function": function, "arguments": arguments}},
            **kwargs,
        )
        self.function = function
        self.arguments = arguments

    def is_responded(self):
        """
        Checks if the action request has been responded to.

        Returns:
            bool: True if the action request has a response, otherwise False.
        """
        return self.action_response is not None

    def clone(self, **kwargs):
        """
        Creates a copy of the current ActionRequest object with optional additional arguments.

        This method clones the current object, preserving its function and arguments.
        It also retains the original `action_response` and metadata, while allowing
        for the addition of new attributes through keyword arguments.

        Args:
            **kwargs: Optional keyword arguments to be included in the cloned object.

        Returns:
            ActionRequest: A new instance of the object with the same function, arguments,
            and additional keyword arguments.
        """
        import json

        arguments = json.dumps(self.arguments)
        request_copy = ActionRequest(
            function=self.function, arguments=json.loads(arguments), **kwargs
        )
        request_copy.action_response = self.action_response
        request_copy.metadata["origin_ln_id"] = self.ln_id
        return request_copy


def _prepare_arguments(arguments):
    """
    Prepares the arguments for the action request.

    Args:
        arguments (Any): The arguments to be prepared.

    Returns:
        dict: The prepared arguments.

    Raises:
        ValueError: If the arguments are invalid.
    """
    if not isinstance(arguments, dict):
        try:
            arguments = ParseUtil.fuzzy_parse_json(convert.to_str(arguments))
        except Exception as e:
            raise ValueError(f"Invalid arguments: {e}") from e
    if isinstance(arguments, dict):
        return arguments
    raise ValueError(f"Invalid arguments: {arguments}")
