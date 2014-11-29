import threading
from inspect import ismethod


class EnvironmentException(Exception):
    """ Simple Exception for environment """


class EnvironmentManager:
    """ Manage the Environment for an application """

    environment = None

    @classmethod
    def define_environment_cls(cls, Environment):
        """ Define the class use for the environment

        :param Environment: class of environment
        :exception: EnvironmentException
        """

        def check_classmethod(method, acceptNone=False):
            if not hasattr(Environment, method):
                raise EnvironmentException("No %r found" % method)

            m = getattr(Environment, method)

            if m is None:
                if acceptNone:
                    return

            if ismethod(m):
                return

            raise EnvironmentException("%r must be a class method" % m)

        check_classmethod('scoped_function_for_session', acceptNone=True)
        check_classmethod('setter')
        check_classmethod('getter')

        cls.environment = Environment

    @classmethod
    def set(cls, key, value):
        """ Save the value of the key in the environment

        :param key: the key of the value to save
        :param value: the value to save
        :exception: EnvironmentException
        """
        if cls.environment is None:
            raise EnvironmentException("No environment defined")

        cls.environment.setter(key, value)

    @classmethod
    def get(cls, key, default=None):
        """ Load the value of the key in the environment

        :param key: the key of the value to load
        :param default: return this value if not value loaded for the key
        :rtype: the value of the key
        :exception: EnvironmentException
        """
        if cls.environment is None:
            raise EnvironmentException("No environment defined")

        return cls.environment.getter(key, default)

    @classmethod
    def scoped_function_for_session(cls):
        """ Save the value of the key in the environment """
        return cls.environment.scoped_function_for_session


class ThreadEnvironment:
    """ Use the thread, to get the environment """

    scoped_function_for_session = None
    """ No scoped function here because for none value sqlalchemy use already
    thread to save the session """

    values = {}

    @classmethod
    def setter(cls, key, value):
        """ Save the value of the key in the environment

        :param key: the key of the value to save
        :param value: the value to save
        """
        if str(threading.current_thread()) not in cls.values:
            cls.values[str(threading.current_thread())] = {}

        cls.values[str(threading.current_thread())][key] = value

    @classmethod
    def getter(cls, key, default):
        """ Load the value of the key in the environment

        :param key: the key of the value to load
        :param default: return this value if not value loaded for the key
        :rtype: the value of the key
        """
        if str(threading.current_thread()) not in cls.values:
            return default

        return cls.values[str(threading.current_thread())].get(key, default)


EnvironmentManager.define_environment_cls(ThreadEnvironment)
