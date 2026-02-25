class SymbolTable:
    def __init__(self):
        # map name -> first occurrence info
        self._symbols = {}

    def add(self, name, line, column):
        """Add a symbol.

        Returns:
          None if added successfully,
          existing_info dict if duplicate (contains line and column of first declaration).
        """
        if name in self._symbols:
            return dict(self._symbols[name])
        self._symbols[name] = {"line": line, "column": column}
        return None

    def get(self, name):
        return self._symbols.get(name)

    def all(self):
        return dict(self._symbols)
