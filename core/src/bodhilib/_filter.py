from typing import Any, Dict, List, Protocol


class Condition(Protocol):
    """Represents the filter expression of MongoDB query expression."""

    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Returns the result after applying the condition to the record."""

    def to_dict(self) -> Dict[str, Any]:
        """Returns the condition as a dict."""


class OperatorCondition:
    """Represents the filter expression with an operator of MongoDB query expression."""

    operators: List[str] = ["$eq", "$gt", "$lt", "$ne", "$gte", "$lte", "$in", "$nin", "$all"]

    def __init__(self, field: str, operator: str, value: Any) -> None:
        """Construct the Operator condition with given arguments.

        Args:
            field (str): The field name.
            operator (str): The operator.
                One of "$eq", "$gt", "$lt", "$ne", "$gte", "$lte", "$in", "$nin", "$all".
            value (Any): The value to compare.

        Raises:
            ValueError: If the operator is invalid.
        """
        if operator not in self.operators:
            raise ValueError(f"Invalid operator: {operator}")
        self.field: str = field
        self.operator: str = operator
        self.value: Any = value

    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Return the predicate for applying the Operator condition."""
        if self.field not in record:
            raise ValueError(f"field with name {self.field} not found in record, found {record.keys()}")
        if self.operator == "$eq":
            return record[self.field] == self.value  # type: ignore[no-any-return]
        elif self.operator == "$gt":
            return record[self.field] > self.value  # type: ignore[no-any-return]
        elif self.operator == "$lt":
            return record[self.field] < self.value  # type: ignore[no-any-return]
        elif self.operator == "$ne":
            return record[self.field] != self.value  # type: ignore[no-any-return]
        elif self.operator == "$gte":
            return record[self.field] >= self.value  # type: ignore[no-any-return]
        elif self.operator == "$lte":
            return record[self.field] <= self.value  # type: ignore[no-any-return]
        elif self.operator in ("$in", "$nin", "$all"):
            record_tags = record.get(self.field)
            if not isinstance(record_tags, list):
                raise ValueError(f"field with name {self.field} is not a list, found {type(record_tags)}")
            if self.operator == "$in":
                return any(tag in record_tags for tag in self.value)
            elif self.operator == "$nin":
                return not any(tag in record_tags for tag in self.value)
            elif self.operator == "$all":
                return all(tag in record_tags for tag in self.value)
        raise ValueError("Invalid operator: {self.operator}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Operator condition as a dict."""
        return {self.field: {self.operator: self.value}}


class And:
    """Represents the And filter of MongoDB query expression."""

    def __init__(self, conditions: List[Condition]) -> None:
        """Construct the And condition with given arguments."""
        self.conditions = conditions

    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Return the predicate for applying the And condition."""
        return all(condition.evaluate(record) for condition in self.conditions)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the And condition as a dict."""
        return {"$and": [condition.to_dict() for condition in self.conditions]}


class Or:
    """Represents the Or filter of MongoDB query expression."""

    def __init__(self, conditions: List[Condition]) -> None:
        """Construct the Or condition with given arguments."""
        self.conditions = conditions

    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Return the predicate for applying the filter Or condition."""
        return any(condition.evaluate(record) for condition in self.conditions)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Or condition as a dict."""
        return {"$or": [condition.to_dict() for condition in self.conditions]}


class Nor:
    """Represents the Nor filter of MongoDB query expression."""

    def __init__(self, conditions: List[Condition]) -> None:
        """Construct the Nor condition with given arguments."""
        self.conditions = conditions

    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Return the predicate for applying the filter Nor condition."""
        return not any(condition.evaluate(record) for condition in self.conditions)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Nor condition as a dict."""
        return {"$nor": [condition.to_dict() for condition in self.conditions]}


class Filter:
    """Represents the MongoDB query expression."""

    def __init__(self, filter_expr: Dict[str, Any]) -> None:
        """Construct a Filter with given arguments.

        Args:
            filter_expr (dict): The MongoDB query expression as dict.
        """
        self.condition = self._parse(filter_expr)

    @staticmethod
    def from_dict(filter_dict: Dict[str, Any]) -> "Filter":
        """Construct a Filter from a dict."""
        return Filter(filter_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Filter as a dict."""
        return self.condition.to_dict()

    def _parse(self, condition: Dict[str, Any]) -> Condition:
        if "$and" in condition:
            return And([self._parse(sub_condition) for sub_condition in condition["$and"]])
        elif "$or" in condition:
            return Or([self._parse(sub_condition) for sub_condition in condition["$or"]])
        elif "$nor" in condition:
            return Nor([self._parse(sub_condition) for sub_condition in condition["$nor"]])
        for field, value in condition.items():
            if isinstance(value, dict):
                for op, op_value in value.items():
                    return OperatorCondition(field, op, op_value)
            else:
                return OperatorCondition(field, "$eq", value)
        raise ValueError(f"Invalid condition: {condition}")

    def evaluate(self, record: Dict[str, Any]) -> bool:
        """Return the predicate for applying the filter condition."""
        return self.condition.evaluate(record)
