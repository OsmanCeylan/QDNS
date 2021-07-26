__all__ = ["backend", "commands", "device", "interactions", "networking", "rtg_apps", "simulation", "tools"]

__version__ = 0.55
__git__ = "-stable"
__rc__ = ""
__version_string__ = "{}{}{}".format(__version__, __git__, __rc__)

# FROM Backend
from QDNS.backend.tools.config import (
    BackendConfiguration,
    CIRQ_BACKEND,
    QISKIT_BACKEND,
    STIM_BACKEND,
    SDQS_BACKEND
)
from QDNS.backend.tools.noise import (
    channels,
    depolarisation_channel,
    bit_flip_channel,
    phase_flip_channel,
    bit_and_phase_flip_channel,
    reset_channel,
    no_noise_channel,
    default_noise_pattern,
    change_default_noise_pattern,
    NoisePattern
)
from QDNS.backend.cirq_backend import change_cirq_simulator
from QDNS.backend.qiskit_backend import change_qiskit_simulator

# FROM Commands
from QDNS.commands import api
from QDNS.commands import library
from QDNS.commands.tools import (
    package_expire_time,
    qubit_expire_time,
    respond_expire_time,
    qstream_capacity,
    set_qubit_expire_time,
    set_package_expire_time,
    set_respond_expire_time,
    set_qubit_stream_capacity
)

# FROM Device
from QDNS.device.tools.application_manager import ApplicationManager
from QDNS.device.tools.application_tools import (
    DEFAULT_APPLICATION_NAME,
    set_default_application_name,
    application_states,
    ApplicationSettings,
    default_application_settings,
    change_default_application_settings
)
from QDNS.device.tools.blocklist import BlockList
from QDNS.device.tools.device_tools import (
    device_states,
    DeviceIdentification,
    ChannelIdentification,
    ApplicationManagerSettings,
    default_application_manager_settings,
    change_default_application_manager_settings,
    DeviceSettings,
    default_device_settings,
    change_default_device_settings
)
from QDNS.device.tools.listener import Listener
from QDNS.device.tools.port import (
    CLASSIC_PORT,
    QUANTUM_PORT,
    Port
)
from QDNS.device.tools.port_manager import (
    port_manager_states,
    use_simple_queue_for_ports,
    PortManagerSetting,
    default_port_manager_setting,
    change_default_port_manager_setting,
    PortManager,
    set_use_simple_queue_for_ports
)
from QDNS.device.tools.socket_info import (
    SocketInformation,
    ConnectivityInformation,
    PortInformation
)
from QDNS.device.tools.socket_tools import (
    socket_states,
    default_ping_time,
    max_avaible_classic_connection,
    max_avaible_quantum_connection,
    SocketSettings,
    default_socket_settings,
    change_default_socket_settings,
    change_default_ping_time
)
from QDNS.device.application import Application
from QDNS.device.device import (
    Device,
    Router,
    Observer,
    Node
)
from QDNS.device.network_adapter import NetworkSocket

# FROM Interactions
from QDNS.interactions import (
    request,
    respond,
    signal
)

# FROM Networking
from QDNS.networking.network import Network

# FROM RtgLayer
from QDNS.rtg_apps.qkd import (
    BB84_METHOD,
    E91_METHOD,
    BB84_GOODS_FIDELITY,
    BB84_SAMPLE_FIDELITY,
    BB84_SAMPLE_DIVISOR,
    E91_SAMPLE_FIDELITY,
    E91_SAMPLE_DIVISOR,
    change_bb84_values,
    change_e91_values,
)
from QDNS.rtg_apps.routing import (
    ROUTE_WAIT_SEND_RESPOND,
    ROUTE_REQUEST_TIMEOUT
)

# FROM Simulation
from QDNS.simulation.controller import MinerController
from QDNS.simulation.kernel import Kernel as Simulator
from QDNS.simulation.miner import Process
from QDNS.simulation.tools import (
    core_count,
    thread_count,
    simulation_states,
    kernel_layer_label,
    MinerControllerSettings,
    default_controller_settings,
    change_deafault_miner_controller_settings,
    SimulationResults
)

# FROM Tools
from QDNS.tools.any_settings import AnySettings
from QDNS.tools.communication import (
    classic_package_live_count,
    set_classic_package_live_count,
    InternetLayer,
    ApplicationLayer,
    Package
)
from QDNS.tools import gates
from QDNS.tools.instance_logger import (
    default_logger_name,
    default_logger_format,
    default_logger_level,
    change_logger_name,
    change_logger_format,
    change_default_logger_level,
    get_logger,
    SubLogger
)
from QDNS.tools.layer import (
    THREAD_LAYER,
    PROCESS_LAYER,
    layer_types,
    layers,
    Layer
)
from QDNS.tools.module import (
    ModuleSettings,
    default_module_setting,
    change_default_module_setting,
    MODULE_STATES,
    Module
)
from QDNS.tools.queue_manager import QueueManager
from QDNS.tools.state_handler import StateHandler
from QDNS.tools.state_handler import GENERAL_STATE_FLAGS
from QDNS.tools.various_tools import (
    dev_mode,
    string_encode,
    string_decode,
    ran_gen,
    flush_queue,
    int2base,
    fiber_formula,
    tensordot,
    TerminatableThread
)
