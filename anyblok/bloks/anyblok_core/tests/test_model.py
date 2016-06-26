# This file is a part of the AnyBlok project
#
#    Copyright (C) 2014 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import TestCase, DBTestCase
from anyblok.model import has_sql_fields, get_fields
from anyblok import Declarations
register = Declarations.register
Model = Declarations.Model


def simple_model():
    Integer = Declarations.Column.Integer
    String = Declarations.Column.String

    @register(Model)
    class Test:
        id = Integer(primary_key=True)
        name = String()


def simple_model_with_tablename():
    Integer = Declarations.Column.Integer
    String = Declarations.Column.String

    @register(Model, tablename='othername')
    class Test:
        id = Integer(primary_key=True)
        name = String()


def simple_models_with_same_table():
    Integer = Declarations.Column.Integer
    String = Declarations.Column.String

    @register(Model)
    class Test:
        id = Integer(primary_key=True)
        name = String()

    @register(Model, tablename='test')
    class Test2:
        id = Integer(primary_key=True)
        name = String()


def simple_models_with_same_table_by_declaration_model():
    Integer = Declarations.Column.Integer
    String = Declarations.Column.String

    @register(Model)
    class Test:
        id = Integer(primary_key=True)
        name = String()

    @register(Model, tablename=Model.Test)
    class Test2:
        id = Integer(primary_key=True)
        name = String()


def simple_models_with_same_table_by_inherit():
    Integer = Declarations.Column.Integer
    String = Declarations.Column.String

    @register(Model)
    class Test:
        id = Integer(primary_key=True)
        name = String()

    @register(Model)
    class Test2:
        id = Integer(primary_key=True)
        name = String()

    @register(Model, tablename='test')  # noqa
    class Test2:
        pass


def simple_models_with_inherit_sqlmodel():
    Integer = Declarations.Column.Integer
    String = Declarations.Column.String

    @register(Model)
    class Test:
        id = Integer(primary_key=True)
        name = String()

    @register(Model)
    class Test2(Model.Test):
        pass

    @register(Model)
    class Test3(Model.Test):
        pass


def model_with_foreign_key():
    Integer = Declarations.Column.Integer
    String = Declarations.Column.String

    @register(Model)
    class TestFk:

        name = String(primary_key=True)

    @register(Model)
    class Test:

        id = Integer(primary_key=True)
        name = String(foreign_key=(Model.TestFk, 'name'))


class TestModel(DBTestCase):

    def check_registry(self, Model):
        t = Model.insert(name="test")
        t2 = Model.query().first()
        self.assertEqual(t2, t)

    def check_registry_same_table(self, Model1, Model2):
        t = Model1.insert(name="test")
        t2 = Model2.query().first()
        self.assertEqual(t2.name, t.name)

    def test_simple_model(self):
        registry = self.init_registry(simple_model)
        self.check_registry(registry.Test)

    def test_simple_model_with_tablename(self):
        registry = self.init_registry(simple_model_with_tablename)
        self.check_registry(registry.Test)
        self.assertEqual(registry.Test.__table__.name, 'othername')
        self.assertEqual(registry.Test.__tablename__, 'othername')

    def test_simple_models_with_same_table(self):
        registry = self.init_registry(simple_models_with_same_table)
        self.check_registry_same_table(registry.Test, registry.Test2)

    def test_simple_models_with_same_table_by_declaration_model(self):
        registry = self.init_registry(
            simple_models_with_same_table_by_declaration_model)
        self.check_registry_same_table(registry.Test, registry.Test2)

    def test_simple_models_with_same_table_by_inherit(self):
        registry = self.init_registry(simple_models_with_same_table_by_inherit)
        self.check_registry_same_table(registry.Test, registry.Test2)

    def test_simple_models_with_inherit_sqlmodel(self):
        registry = self.init_registry(simple_models_with_inherit_sqlmodel)
        self.check_registry_same_table(registry.Test, registry.Test2)

    def test_simple_model_with_wrong_column(self):
        registry = self.init_registry(simple_model)

        try:
            registry.Test.insert(name="test", other="other")
            self.fail('No error when an inexisting colomn has filled')
        except TypeError:
            pass

    def test_simple_model_with_wrong_value(self):
        registry = self.init_registry(simple_model)

        t = registry.Test.insert(name=1)
        registry.old_session_commit()
        self.assertNotEqual(t.name, 1)

    def test_model_with_foreign_key(self):
        registry = self.init_registry(model_with_foreign_key)
        registry.TestFk.insert(name='test')
        self.check_registry(registry.Test)


class TestModelAssembling(TestCase):

    def test_has_sql_fields_ok(self):

        class MyModel:
            one_field = Declarations.Column.String()

        self.assertEqual(has_sql_fields([MyModel]), True)

    def test_has_sql_fields_ko(self):

        class MyModel:
            one_field = None

        self.assertEqual(has_sql_fields([MyModel]), False)

    def test_get_fields(self):

        class MyModel:
            one_field = Declarations.Column.String()

        self.assertEqual(get_fields(MyModel), {'one_field': MyModel.one_field})