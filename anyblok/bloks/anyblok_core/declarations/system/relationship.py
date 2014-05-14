from anyblok import Declarations
target_registry = Declarations.target_registry
System = Declarations.Model.System
Mixin = Declarations.Mixin
String = Declarations.Column.String
Boolean = Declarations.Column.Boolean


@target_registry(System)
class RelationShip(Mixin.Field):

    rtype = String(label="Type", nullable=False)
    local_column = String(label="Local column")
    remote_column = String(label="Remote column")
    remote_name = String(label="Remote name")
    remote_model = String(label="Remote model", nullable=False)
    remote = Boolean(label="Remote", default=False)

    @classmethod
    def add_field(cls, rname, relation, model, table):
        local_column = relation.info.get('local_column')
        remote_column = relation.info.get('remote_column')
        remote_model = relation.info.get('remote_model')
        remote_name = relation.info.get('remote_name')
        label = relation.info.get('label')
        nullable = relation.info.get('nullable', True)
        rtype = relation.info.get('rtype')
        if rtype is None:
            return

        vals = dict(code=table + '.' + rname,
                    model=model, name=rname, local_column=local_column,
                    remote_model=remote_model, remote_name=remote_name,
                    remote_column=remote_column, label=label,
                    nullable=nullable, rtype=rtype)
        cls.insert(**vals)

        if remote_name:
            remote_type = "Many2One"
            if rtype == "Many2One":
                remote_type = "One2Many"
            elif rtype == 'Many2Many':
                remote_type = "Many2Many"
            elif rtype == "One2One":
                remote_type = "One2One"

            m = cls.registry.get(remote_model)
            vals = dict(code=m.__tablename__ + '.' + remote_name,
                        model=remote_model, name=remote_name,
                        local_column=remote_column, remote_model=model,
                        remote_name=rname,
                        remote_column=local_column, label=label,
                        nullable=True, rtype=remote_type, remote=True)
            cls.insert(**vals)
