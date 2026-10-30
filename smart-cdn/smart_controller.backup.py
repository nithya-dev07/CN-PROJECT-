from ryu.app.simple_switch_13 import SimpleSwitch13
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER


class SmartContentController(SimpleSwitch13):
    """Custom SDN controller for the Smart Content Delivery project."""

    def __init__(self, *args, **kwargs):
        super(SmartContentController, self).__init__(*args, **kwargs)
        self.logger.info("Smart Content Delivery Controller started")

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def handle_packet_in(self, ev):
        msg = ev.msg
        self.logger.info(
            "Smart CDN: PacketIn received from switch %s",
            msg.datapath.id
        )
        super(SmartContentController, self). _packet_in_handler(ev)
