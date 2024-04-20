from typing import List, TypeVar, Iterable, Optional, Tuple

from specklepy.objects.base import Base
import sys

from flatten import extract_base_and_transform

T = TypeVar("T", bound=Base)


class Utilities:
    @staticmethod
    def is_displayable_object(speckle_object: Base) -> bool:
        """
        Determines if a given Speckle object is displayable.

        This function checks if the speckle_object has a display value
        and returns True if it does, otherwise it returns False.

        Args:
            speckle_object (Base): The Speckle object to check.

        Returns:
            bool: True if the object has a display value, False otherwise.
        """
        return Utilities.try_get_display_value(speckle_object) is not None

    @staticmethod
    def try_get_display_value(speckle_object: Base) -> Optional[List[T]]:
        """Try fetching the display value from a Speckle object.

        Args:
            speckle_object (Base): The Speckle object to extract the display value from.

        Returns:
            Optional[List[T]]: A list containing the display values. If no display value is found,
                               returns None.
        """
        raw_display_value = getattr(speckle_object, "displayValue", None) or getattr(
            speckle_object, "@displayValue", None
        )

        if raw_display_value is None:
            return None

        if isinstance(raw_display_value, Iterable):
            display_values = list(
                filter(lambda x: isinstance(x, Base), raw_display_value)
            )
            return display_values if display_values else None

    @staticmethod
    def get_byte_size(speckle_object: Base) -> int:
        """Calculate the total byte size of the display values of a Speckle object.
            Keeps drilling down until it gets to vertices, or it returns 0 if it can't find any.

        Args:
            speckle_object (Base): The Speckle object for which to compute the byte size.

        Returns:
            int: The total byte size of all display values that have vertices.
        """
        if speckle_object is None:
            return 0

        display_values = Utilities.try_get_display_value(speckle_object)

        if display_values is None:
            display_values = speckle_object

        if isinstance(display_values, Iterable):
            return sum(
                [sys.getsizeof(display_value) for display_value in display_values]
            )

        if not hasattr(display_values, "vertices"):
            return 0

        return sys.getsizeof(display_values["vertices"])

    @staticmethod
    def filter_displayable_bases(root_object: Base) -> List[Base]:
        """
        Filters out objects that are not displayable or don't have valid IDs.

        Args:
            root_object: The root object to start the filtering from.

        Returns:
            List of displayable bases with valid IDs.
        """
        displayable_objects = [
            base  # 'base' is now the first element of the tuple 'b'
            for base, instance_id, transform in list(
                extract_base_and_transform(root_object)
            )
            if Utilities.is_displayable_object(base) and getattr(base, "id", None)
        ]

        return displayable_objects
