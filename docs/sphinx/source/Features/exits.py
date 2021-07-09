"""
As this documentation has covered so far, many methods that run at simulation time give an exit code.
With using this code users can identify the problem as shown in the below::

    def bob_default_app(app: QDNS.Application, *user_args):
        waiting = app.wait_next_package()

        if waiting["exit_code"] < 0:
            print(QDNS.exit_code_desription(waiting["exit_code"]))

.. code-block:: python

    Wait package timeout.
"""