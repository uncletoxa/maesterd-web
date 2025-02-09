# from typing import Literal

from langchain.agents import tool
from maesterd.core import dice
from maesterd.core.session import CampaignSession


roll_dice_tool = tool(dice.roll)


@tool
def get_pc_state_tool(pc_name: str):
    """
    Get the state of a player character. This includes the character's name HP status (max and current), AC, and if
    the character is alive or not.

    Parameters
    ----------
    pc_name: str
        The name of the player character. Character names can be retrieved by using `get_pcs` tool.
    """
    return CampaignSession.get_pc_state(pc_name)


@tool
def get_pcs_tool():
    """
    Get a list of player characters' names.
    """
    return CampaignSession.get_pc_names()
