"""
QDNS uses default settings in many places. For most of them, QDNS lets users to change them.
Some of them is shown in the below::

    def main():
        QDNS.change_bb84_values(goods_fidelity=0.65, sample_fidelity=0.3, sample_divisor=4)
        QDNS.change_default_application_settings(QDNS.ApplicationSettings(static=False, enabled=True, end_device_if_terminated=True, delayed_start_time=0))
        QDNS.change_deafault_miner_controller_settings(QDNS.MinerControllerSettings(max_cpu_core_count=12, use_real_cores=False))
        QDNS.change_default_connection_length(10.0)  #10 km.
        QDNS.change_logger_name("QDNS")
        QDNS.change_default_ping_time(3.0)  # Ping time out = 3.0 sec.
        QDNS.change_default_device_settings(QDNS.DeviceSettings(otg_device=False, observe_capability=False, idle_after_device_ends=False, start_after_delay=0))
        QDNS.change_default_altitude_formula(new_method)
        QDNS.change_default_socket_settings(QDNS.SocketSettings(max_cc_count=99, max_qc_count=99, auto_ping=True, clear_route_cache=True, enable_routing=True))

        logging.basicConfig(level=logging.WARNING)

        alice = QDNS.Node('Alice')
        bob = QDNS.Node('Bob')

        alice.create_new_application(alice_default_app)
        bob.create_new_application(bob_default_app)

        net = QDNS.Network(alice, bob)
        net.add_channels(alice, bob)

        sim = QDNS.Simulator()
        res = sim.simulate(net, backend=QDNS.STIM_BACKEND)
"""