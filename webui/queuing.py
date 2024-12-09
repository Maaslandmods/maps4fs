import json
import os
from time import sleep
from typing import Generator

from config import QUEUE_FILE, QUEUE_INTERVAL, QUEUE_TIMEOUT

from maps4fs import Logger

logger = Logger(level="DEBUG", to_file=False)


def get_queue(force: bool = False) -> list[str]:
    """Get the queue from the queue file.
    If the queue file does not exist, create a new one with an empty queue.

    Arguments:
        force (bool): Whether to force the creation of a new queue file.

    Returns:
        list[dict[str, str]]: The queue.
    """
    if not os.path.isfile(QUEUE_FILE) or force:
        logger.debug("Queue will be reset.")
        save_queue([])
        return []
    with open(QUEUE_FILE, "r") as f:
        return json.load(f)


def save_queue(queue: list[str]) -> None:
    """Save the queue to the queue file.

    Arguments:
        queue (list[str]): The queue to save to the queue file.
    """
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f)
    logger.debug("Queue set to %s.", queue)


def add_to_queue(session: str) -> None:
    """Add a session to the queue.

    Args:
        session (str): The session to add to the queue.
    """
    queue = get_queue()
    queue.append(session)
    save_queue(queue)
    logger.debug("Session %s added to the queue.", session)


def get_first_item() -> str | None:
    """Get the first item from the queue.

    Returns:
        str: The first item from the queue.
    """
    queue = get_queue()
    if not queue:
        return None
    return queue[0]


def get_position(session: str) -> int | None:
    """Get the position of a session in the queue.

    Args:
        session (str): The session to get the position of.

    Returns:
        int: The position of the session in the queue.
    """
    queue = get_queue()
    if session not in queue:
        return None
    return queue.index(session)


def remove_from_queue(session: str) -> None:
    """Remove a session from the queue.

    Args:
        session (str): The session to remove from the queue.
    """
    queue = get_queue()
    if session in queue:
        queue.remove(session)
        save_queue(queue)
        logger.debug("Session %s removed from the queue.", session)


def wait_in_queue(session: str) -> Generator[int, None, None]:
    """Wait in the queue until the session is the first item.

    Args:
        session (str): The session to wait for.
    """
    retries = QUEUE_TIMEOUT // QUEUE_INTERVAL
    logger.debug(
        "Starting to wait in the queue for session %s with maximum retries %d.", session, retries
    )

    for _ in range(retries):
        position = get_position(session)
        if position == 0 or position is None:
            logger.debug("Session %s is the first item in the queue.", session)
            return
        logger.debug("Session %s is in position %d in the queue.", session, position)
        yield position
        sleep(QUEUE_INTERVAL)


get_queue(force=True)