import json
import os
import time

from ryu.app.simple_switch_13 import SimpleSwitch13
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.lib import hub

OUTPUT = "/home/sohan/smart-cdn/port_stats.json"


class SmartContentController(SimpleSwitch13):
    """Learning switch that exports port statistics for the smart client."""

    def __init__(self, *args, **kwargs):
        super(SmartContentController, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.previous = {}
        self.port_load = {}
        self.logger.info("Smart CDN statistics-export controller started")
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def state_change(self, ev):
        dp = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths[dp.id] = dp
        elif ev.state == DEAD_DISPATCHER:
            self.datapaths.pop(dp.id, None)

    def _monitor(self):
        while True:
            for dp in list(self.datapaths.values()):
                req = dp.ofproto_parser.OFPPortStatsRequest(
                    dp, 0, dp.ofproto.OFPP_ANY
                )
                dp.send_msg(req)
            hub.sleep(5)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def port_stats_reply(self, ev):
        now = time.time()
        switch_id = ev.msg.datapath.id

        for stat in ev.msg.body:
            key = (switch_id, stat.port_no)
            old = self.previous.get(key)

            if old:
                elapsed = now - old["time"]
                rx_rate = max(0, stat.rx_bytes - old["rx"]) / max(elapsed, 0.001)
                tx_rate = max(0, stat.tx_bytes - old["tx"]) / max(elapsed, 0.001)
            else:
                rx_rate = 0.0
                tx_rate = 0.0

            self.previous[key] = {
                "time": now, "rx": stat.rx_bytes, "tx": stat.tx_bytes
            }
            self.port_load[str(stat.port_no)] = {
                "rx_bytes_per_sec": round(rx_rate, 2),
                "tx_bytes_per_sec": round(tx_rate, 2)
            }

        temp = OUTPUT + ".tmp"
        with open(temp, "w") as f:
            json.dump({
                "timestamp": now,
                "switch": switch_id,
                "ports": self.port_load
            }, f)
        os.replace(temp, OUTPUT)

        self.logger.info("Exported statistics for switch %s", switch_id)
