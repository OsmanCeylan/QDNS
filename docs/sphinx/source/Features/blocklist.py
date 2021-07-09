"""
QDNS allows users to create, update or remove blocklist for every application.
These methods still can be used  in simulation run time::

    def alice_default_app(app: QDNS.Application, *user_args):
        app.block_list.add_device("Bob", all_communication=False, all_packages=False, all_protocols=False, all_qubit_streams=True)
        app.block_list.update_device("Charlie", all_communication=False, all_packages=True, all_protocols=True, all_qubit_streams=False)
        app.block_list.remove_device("Charlie")

        print("Accept communication with Bob is: ", app.block_list.get_all_communication("Bob"))
        print("Blocked count: ", app.block_list.blocked_count)
        print("Alice filtered device count: ", app.block_list.device_count)
"""