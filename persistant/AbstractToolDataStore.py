import abc

class AbstractToolDataStore(abc.ABC):
    """
    Abstract base class for tool data storage and retrieval.
    Implementations should handle persistence (e.g., file, database).
    """

    @abc.abstractmethod
    def get_all_tool_data(self):
        """
        Return a list of all tool data dicts.
        Implementations should return all stored tool data.
        """
        pass

    @abc.abstractmethod
    def get_tool_filepath(self, tool_id):
        """Return the full file path or storage key for a tool's data."""
        pass

    @abc.abstractmethod
    def save_tool_data(self, tool_id, data):
        """Save a tool's data."""
        pass

    @abc.abstractmethod
    def load_tool_data(self, tool_id):
        """Load a tool's data."""
        pass

    @abc.abstractmethod
    def delete_tool_data(self, tool_id):
        """Delete a tool's data."""
        pass
