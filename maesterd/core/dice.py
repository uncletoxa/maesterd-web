import random
import logging
from typing import List, Union, Literal

logger = logging.getLogger(__name__)

DiceType = Literal[4, 6, 8, 10, 12, 20, 100]


def _roll(num_dice: int, dice_type: DiceType) -> List[int]:
    if num_dice < 1 or dice_type < 1:
        raise ValueError("Number of dice and dice type must be at least 1.")
    rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
    logger.debug(f"Dice rolls: {rolls}")
    return rolls


def roll_with_advantage(num_dice: int, dice_type: DiceType) -> List[int]:
    base_rolls = _roll(num_dice, dice_type)
    rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
    logger.debug(f"Advantage rolls: {rolls}")
    final_rolls = [max(r1, r2) for r1, r2 in zip(base_rolls, rolls)]
    logger.debug(f"Final rolls with advantage: {final_rolls}")
    return final_rolls


def roll_with_disadvantage(num_dice: int, dice_type: DiceType) -> List[int]:
    base_rolls = _roll(num_dice, dice_type)
    rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
    logger.debug(f"Disadvantage rolls: {rolls}")
    final_rolls = [min(r1, r2) for r1, r2 in zip(base_rolls, rolls)]
    logger.debug(f"Final rolls with disadvantage: {final_rolls}")
    return final_rolls


def roll(
    num_dice: int = 1, dice_type: DiceType = 20, modifier: int = 0, advantage: bool = False, disadvantage: bool = False
) -> Union[int, List[int]]:
    """
    Rolls dice with optional modifiers and conditions.

    Parameters:
        num_dice (int): Number of dice to roll. Default is 1.
        dice_type (DiceType): Type of dice to roll (e.g., 4, 6, 8, 10, 12, 20, or 100). Default is 20.
        modifier (int): Flat modifier to add to the total roll. Default is 0.
        advantage (bool): If True, rolls twice and takes the higher result for each die.
            Cannot be used with disadvantage. Default is False.
        disadvantage (bool): If True, rolls twice and takes the lower result for each die.
            Cannot be used with advantage. Default is False.

    Returns:
        Union[int, List[int]]: The total roll result if rolling one die, or a list of individual
            roll results if rolling multiple dice.

    Raises:
        ValueError: If both advantage and disadvantage are True, or if num_dice or dice_type is less than 1.
    """
    if advantage and disadvantage:
        raise ValueError("Cannot roll with both advantage and disadvantage.")

    if advantage:
        rolls = roll_with_advantage(num_dice, dice_type)
    elif disadvantage:
        rolls = roll_with_disadvantage(num_dice, dice_type)
    else:
        rolls = _roll(num_dice, dice_type)

    total = sum(rolls) + modifier
    logger.info(f"Rolling {num_dice}d{dice_type} with modifier {modifier}. Total: {total}")
    return total if num_dice == 1 else rolls
