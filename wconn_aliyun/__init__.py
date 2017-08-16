#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import logging
import pyroute2
import ipaddress


def get_plugin_list():
    return [
        "aliyun",
    ]


def get_plugin(name):
    if name == "aliyun":
        return _PluginObject()
    else:
        assert False


class _PluginObject:

    def init2(self, cfg, tmpDir, ownResolvConf, upCallback, downCallback):
        self.cfg = cfg
        self.tmpDir = tmpDir
        self.ownResolvConf = ownResolvConf
        self.upCallback = upCallback
        self.downCallback = downCallback
        self.logger = logging.getLogger(self.__module__ + "." + self.__class__.__name__)
        self.bAlive = False

    def get_interface(self):
        return "eth1"

    def start(self):
        if "nameservers" in self.cfg["internet"]:
            with open(self.ownResolvConf, "w") as f:
                for ns in self.cfg["internet"]["nameservers"]:
                    f.write("nameserver %s\n" % (ns))
            self.logger.info("Nameservers are \"%s\"." % ("\",\"".join(self.cfg["internet"]["nameservers"])))
        self.logger.info("Started.")

    def stop(self):
        for ifname in ["eth0", "eth1"]:
            with pyroute2.IPRoute() as ipp:
                idx = None
                try:
                    idx = ipp.link_lookup(ifname=ifname)[0]
                except IndexError:
                    continue
                ipp.link("set", index=idx, state="down")
                ipp.flush_addr(index=idx)
                if ifname == "eth1":
                    self.downCallback()

        with open(self.ownResolvConf, "w") as f:
            f.write("")
        self.logger.info("Stopped.")

    def is_connected(self):
        return self.bAlive

    def get_ip(self):
        assert self.is_connected()
        return self.cfg["internet"]["ip"].split("/")[0]

    def get_netmask(self):
        assert self.is_connected()
        return self.cfg["internet"]["ip"].split("/")[1]

    def get_extra_prefix_list(self):
        assert self.is_connected()
        ret = []
        if "intranet" in self.cfg:
            bnet = ipaddress.IPv4Network(self.cfg["intranet"]["ip"], strict=False)
            ret.append((str(bnet.network_address), str(bnet.netmask)))
        return ret

    def get_business_attributes(self):
        # returns {
        #    "bandwidth": 10,           # unit: KB/s, no key means bandwidth is unknown
        #    "billing": "traffic",      # values: "traffic" or "time", no key means no billing
        #    "balance": 10.0,
        #    "balance-unit": "yuan",
        # }
        assert False

    def interface_appear(self, ifname):
        if ifname == "eth0":
            if "intranet" in self.cfg:
                ip = self.cfg["intranet"]["ip"].split("/")[0]
                bnet = ipaddress.IPv4Network(self.cfg["intranet"]["ip"], strict=False)
                with pyroute2.IPRoute() as ipp:
                    idx = ipp.link_lookup(ifname="eth0")[0]
                    ipp.link("set", index=idx, state="up")
                    ipp.addr("add", index=idx, address=ip, mask=bnet.prefixlen, broadcast=str(bnet.broadcast_address))
                    if "routes" in self.cfg["intranet"]:
                        for rt in self.cfg["intranet"]["routes"]:
                            ipp.route('add', dst=rt["prefix"], gateway=rt["gateway"], oif=idx)
            self.logger.info("Intranet interface \"%s\" managed." % (ifname))
            return True

        if ifname == "eth1":
            ip = self.cfg["internet"]["ip"].split("/")[0]
            bnet = ipaddress.IPv4Network(self.cfg["internet"]["ip"], strict=False)
            with pyroute2.IPRoute() as ipp:
                idx = ipp.link_lookup(ifname="eth1")[0]
                ipp.link("set", index=idx, state="up")
                ipp.addr("add", index=idx, address=ip, mask=bnet.prefixlen, broadcast=str(bnet.broadcast_address))
                if "gateway" in self.cfg["internet"]:
                    ipp.route('add', dst="0.0.0.0/0", gateway=self.cfg["internet"]["gateway"], oif=idx)
            self.logger.info("Internet interface \"%s\" managed." % (ifname))
            self.bAlive = True
            try:
                self.upCallback()
            except:
                assert False               # fixme, what to do?
            return True

        return False

    def interface_disappear(self, ifname):
        if ifname == "eth1":
            assert self.bAlive
            self.bAlive = False
            self.downCallback()

    def _bussinessAttrFetch(self):
        pass

    def _bussinessAttrFetchComplete(self):
        pass

    def _bussinessAttrFetchError(self):
        pass

    def _bussinessAttrFetchDispose(self):
        pass