"""
    marvin.validators
    ~~~~~~~~~~~~~~~~~

    Some extra validators that can be used in model definitions.

"""
from wtforms.validators import ValidationError

def fk_exists(model):
    """ Validate that the object pointed to by the foreign key exists.

    Usage example::

        class User(db.Model):
            id = db.Column(db.Integer,
                primary_key=True
            )
            group_id = db.Column(db.Integer,
                db.ForeignKey('group.id'),
                info={
                    'validators': fk_exists(Group),
                }
            )

    :param model: The model the foreign key should be checked against.
    """

    def _validate(form, field): # pylint: disable=unused-argument
        obj = model.query.get(field.data)
        if obj is None:
            raise ValidationError("No %s with id %s found." % (model.__tablename__, field.data))

    return _validate
