# -*- coding: cp949 -*-

import wx
from twisted.internet import wxreactor
wxreactor.install()

# import twisted reactor *only after* installing wxreactor
from twisted.internet import reactor, protocol
from twisted.protocols import basic


class ChatFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="채팅 프로그램")
        self.protocol = None  # twisted Protocol

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(300, 25))

        sizer.Add(self.text, 5, wx.EXPAND)
        sizer.Add(self.ctrl, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.ctrl.Bind(wx.EVT_TEXT_ENTER, self.send)
        self.ctrl.SetFocus()
    def send(self, evt):
        self.protocol.sendLine(str(self.ctrl.GetValue().encode('cp949')))
        self.ctrl.SetValue("")


class DataForwardingProtocol(basic.LineReceiver):
    def __init__(self):
        self.output = None

    def dataReceived(self, data):
        gui = self.factory.gui

        gui.protocol = self
        if gui:
            val = gui.text.GetValue()
            gui.text.SetValue(val.encode('cp949') + data)
            gui.text.SetInsertionPointEnd()

    def connectionMade(self):
        self.output = self.factory.gui.text  # redirect Twisted's output


class ChatFactory(protocol.ClientFactory):
    def __init__(self, gui):
        self.gui = gui
        self.protocol = DataForwardingProtocol

    def clientConnectionLost(self, transport, reason):
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()


if __name__ == '__main__':
    #IP = raw_input('Type IP Server: ')
    app = wx.App(False)
    frame = ChatFrame()
    frame.Show()
    reactor.registerWxApp(app)
    #reactor.connectTCP(IP, 5001, ChatFactory(frame))
    reactor.connectTCP("localhost", 5001, ChatFactory(frame))
    reactor.run()
