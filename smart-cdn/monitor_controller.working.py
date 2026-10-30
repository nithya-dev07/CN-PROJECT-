from ryu.app.simple_switch_13 import SimpleSwitch13
from ryu.controller import ofp_event
from ryu.controller.handler import (
    set_ev_cls, MAIN_DISPATCHER, DEAD_DISPATCHER
)
from ryu.lib import hub


class SmartContentController(SimpleSwitch13):
    """Learning switch with periodic port-statistics monitoring."""

    def __init__(self, *args, **kwargs):
        super(SmartContentController, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.logger.info("Smart Content Delivery Controller started")
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        dp = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths[dp.id] = dp
            self.logger.info("Switch %s registered", dp.id)
        elif ev.state == DEAD_DISPATCHER:
            self.datapaths.pop(dp.id, None)
            self.logger.info("Switch %s disconnected", dp.id)

    def _monitor(self):
        while True:
            for dp in list(self.datapaths.values()):
                parser = dp.ofproto_parser
                request = parser.OFPPortStatsRequest(
                    dp, 0, dp.ofproto.OFPP_ANY
                )
                dp.send_msg(request)
            hub.sleep(5)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        for stat in ev.msg.body:
            self.logger.info(
                "PORT STATS switch=%s port=%s rx_bytes=%s tx_bytes=%s",
                ev.msg.datapath.id, stat.port_no,
                stat.rx_bytes, stat.tx_bytes
            )
