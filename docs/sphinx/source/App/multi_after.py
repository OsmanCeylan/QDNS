"""
We need to create more applications along side to default application to enable this design.
Creating Alice applications::

    def alice_default_app(app: QDNS.Application, *user_args):
        # Using localhost queue
        app.put_localhost("Hello second application!")


    def alice_second_app(app: QDNS.Application, *user_args):
        print(app.localhost_queue.get())

Creating Bob applications::

    def bob_default_app(app: QDNS.Application, *user_args):
        print("This application is {} and hosted in {}.".format(app.label, app.host_label))

    def bob_second_app(app: QDNS.Application, *user_args):
        print("This application is {} and hosted in {}.".format(app.label, app.host_label))

Application creation::

    def main():
        logging.basicConfig(level=logging.WARNING)

        alice = QDNS.Node("Alice")
        bob = QDNS.Node("Bob")

        # Default apps.
        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)

        # Sencondary apps.
        alice.create_new_application(alice_second_app, label='second')
        bob.create_new_application(bob_second_app, label='second')

Create new application
######################
"""

def create_new_application(
        function, *args, label: str = None,
        static=None, enabled=None, end_device_if_terminated=None,
        bond_end_with_device=None, delayed_start_time=None
):
    """
    The complete function of create_new_application()

    Args:
        function: Function of application.
        *args: User arguments to pass simulation.
        label: Label of application, default is "default".
        static: Setts application static.
        enabled: Setts application enabled.
        end_device_if_terminated: Ends device simulation if application is termiated.
        bond_end_with_device: Ends device simulation if application is finished.
        delayed_start_time: Starts application after delay.

    Examples:
    =================================================
    >>> self.create_new_application("function: bob_run", *args)
    >>> self.create_new_application("function: alice_run", *args, label="alice_app")
    >>> self.create_new_application("function: bob_run", *args, static=True)
    >>> self.create_new_application("function: bob_run", *args, enabled=False)

    See QDNS/device/application.Application() for more details.

    Raises:
        ValueError: Same name application in device.

    Return:
        Application or None.
    """

    pass