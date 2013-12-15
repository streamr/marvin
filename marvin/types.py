"""
    marvin.types
    ~~~~~~~~~~~~

    Our own custom database types.

"""

from sqlalchemy.dialects.postgresql.base import ischema_names
import sqlalchemy as sa

class PostgresJSONType(sa.types.UserDefinedType):
    """ Text search vector type for postgresql. """
    def get_col_spec(self):
        return 'json'


ischema_names['json'] = PostgresJSONType


class JSONType(sa.types.TypeDecorator):
    """ JSONType offers a way of saving JSON data structures to database.

    On PostgreSQL the underlying implementation of this data type is 'json' while
    on other databases its simply 'text'.
    """
    impl = sa.UnicodeText

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Use the native JSON type.
            return dialect.type_descriptor(PostgresJSONType())
        else:
            return dialect.type_descriptor(self.impl)