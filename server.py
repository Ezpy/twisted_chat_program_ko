# -*- coding: cp949 -*-

from twisted.internet import reactor, protocol
from twisted.protocols import basic
import time

def t():
    return "["+ time.strftime("%H:%M:%S") +"] "

class EchoProtocol(basic.LineReceiver):
    name = "Unnamed"

    def connectionMade(self):
        self.sendLine(" ::: 채팅 프로그램 :::")
        self.sendLine("\t[도움말]")
        self.sendLine(" - userlist: 현재 접속중인 사람을 보여줌")
        self.sendLine(" - blocklist: 지금까지 차단한 사람을 보여줌")
        self.sendLine(" - @닉네임 메시지: 귓속말")
        self.sendLine(" - #채팅방: 채팅방 개설")
        self.sendLine(" - #채팅방 메시지: 해당 채팅방에 메시지 전달")
        self.sendLine(" - !닉네임: 해당 닉네임 차단하기")
        self.sendLine(" - $: 현재 상태 변경하기")
        self.sendLine("")
        self.sendLine("반갑습니다. 닉네임을 입력해주세요 !")
        self.count = 0
        self.blocklist = []
        self.roomlist = []
        self.status = 1
        self.factory.clients.append(self)

        print t() + "+ 새로운 접속: "+ self.transport.getPeer().host

    def connectionLost(self, reason):
        self.sendMsg("- %s 나갔습니다." % self.name)
        print t() + "- 연결이 끊겼습니다: "+ self.name
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        if not self.count:
            self.username(line)
        elif line == 'quit':
            self.sendLine("Goodbye.")
            self.transport.loseConnection()
            return
        elif line == "userlist":
            self.chatters()
            return
        elif line == "blocklist":
            self.GetBlockList()
            return
        elif line.startswith('!'):
            self.Add2BlockUser(line[1:])
        elif line.startswith('$'):
            if self.status:
                self.status = False
                self.sendLine(t()+'자리비움으로 상태가 변경되었습니다')
            else:
                self.status = True
                self.sendLine(t()+'온라인으로 상태가 변경되었습니다')
        elif line.startswith('#'):
            s = line.split(' ')
            groupname = s[0][1:]
            if len(s) > 1:
                # sending message to groups
                if s[1] == '삭제':
                    self.DeleteGroup(groupname)
                else:
                    message = line[line.find(' '):].strip()
                    self.Send2Group(groupname, message, self.name)
            else:
                # creating group
                self.CreateGroup(line[1:])
        elif line.startswith('@'):
            username = line[:line.find(' ')].strip()[1:]
            message = line[line.find(' '):].strip()

            self.send2user(username, message)
        else:
            self.sendMsg(self.name +": " + line)

    def username(self, line):
        for x in self.factory.clients:
            if x.name == line:
                self.sendLine("이미 사용중인 닉네임입니다. 다른 닉네임을 사용해주세요.")
                return

        self.name = line
        self.chatters()
        self.sendLine("재밌게 채팅하세요 ^^")
        self.sendLine("")
        self.count += 1
        self.sendMsg("+ %s가 접속하였습니다." % self.name)
        print '%s~ %s의 닉네임은 이제 %s입니다' % (t(), self.transport.getPeer().host, self.name)

    def chatters(self):
        #x = len(self.factory.clients) - 1
        x = len(self.factory.clients)
        self.sendLine(" ** 현재 %i명 접속중" % (x) )

        if len(self.factory.clients) > 1:
            self.sendLine(' - 접속중인 아이디')
            user_count = 1
            for client in self.factory.clients:
            
                if client is not self:

                    self.sendLine(' %d: %s' % (user_count, client.name))
                    user_count += 1

        self.sendLine("")

    def sendMsg(self, message):
        # 모두에게 보내는 메시지 ! > 차단한 사람 제외
        for client in self.factory.clients:
            if self.name not in client.blocklist:
                client.sendLine(t() + message)
    def send2user(self, receiver, message):
        found = False
        for client in self.factory.clients:
            if client.name == receiver and self.name not in client.blocklist:
            # (조건) 귓 대상인 경우 && 귓 대상의 차단 리스트에 전송하는 사람이 없는 경우!
                if client.status == False:
                    self.sendLine(t()+client.name+' - 지금은 부재중입니다')
                else:
                    client.sendLine(t()+'@'+self.name+' '+message)
                found = True
        if found == False:
        # 귓속말 대상이 존재하지 않았다면 알려줌 -> 그러나 차단중인것은 모름..ㅎ
            self.sendLine(t() + '[오류] 귓속말 대상을 찾지 못하였습니다')

    def GetBlockList(self):
        self.sendLine(t()+' - 차단 리스트 -')
        self.sendLine(t()+str(self.blocklist))
    def Add2BlockUser(self, username):
        if username in self.blocklist:
        # 이미 차단 목록에 있는 경우
            self.sendLine(t()+username+'은 이미 차단목록에 있습니다')
        else:
            self.blocklist.append(username)
            self.sendLine(t()+username+'을 차단목록에 추가하였습니다')
    def CreateGroup(self, groupname):
        if groupname in self.factory.groups:
            if groupname in self.roomlist:
                self.sendLine(t()+'이미 존재하는 채팅방명입니다')
            else:
                self.sendLine(t()+groupname+' 채팅방에 들어갔습니다')
                self.roomlist.append(groupname)
        else:
            self.sendMsg('[알림] '+self.name+'이 '+groupname+' 채팅방을 개설하였습니다')
            self.factory.groups.append(groupname)
            self.roomlist.append(groupname)
    def DeleteGroup(self, groupname):
        if groupname not in self.factory.groups:
            self.sendLine(t()+'존재하지 않는 채팅방명입니다')
        else:
            self.sendMsg('[알림] '+self.name+'이 '+groupname+' 채팅방을 삭제하였습니다')
            self.factory.groups.remove(groupname)
    def Send2Group(self, groupname, message, sender):
        if groupname not in self.roomlist:
            self.sendLine(t()+'[오류] 현재 채팅방에 있는 구성원이 아닙니다')
        else:
            for client in self.factory.clients:
                if groupname in client.roomlist:
                    client.sendLine(t()+'#'+groupname+' ('+sender+') '+message)

class EchoServerFactory(protocol.ServerFactory):
    protocol  = EchoProtocol
    clients = []
    groups = []

if __name__ == "__main__":
    reactor.listenTCP(5001, EchoServerFactory())
    reactor.run()
