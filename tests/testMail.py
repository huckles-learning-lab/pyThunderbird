'''
Created on 24.10.2020

@author: wf
'''
import unittest
from lodstorage.sql import SQLDB
from thunderbird.mail import Mail, Thunderbird
import mailbox
import getpass
import os
import socket

class TestMail(unittest.TestCase):
    '''
    Test Thunderbird mail access
    '''

    def setUp(self):
        self.debug=False
        user=getpass.getuser()
        if user!="wf":
            self.mockMail()
        pass

    def tearDown(self):
        pass
    
    def mockMail(self):
        '''
        need to create a mock SQLITE gloda
        '''
        db="/tmp/gloda.sqlite"
        profile="/tmp/tb.profile"
        mboxFile=profile+"/Mail/Local Folders/WF.sbd/2020-10"
        os.makedirs(os.path.dirname(mboxFile),exist_ok=True)
        messagesLod=[{'id': 1003, 'folderID': 1003, 'messageKey': 1, 'conversationID': 286140, 'date': 1601640003000000, 'headerMessageID': 'mailman.45.1601640003.19840.wikidata@lists.wikimedia.org', 'deleted': 0}]
        foldersLod=[{'id': 1003,'folderURI': 'mailbox://nobody@Local%20Folders/WF/2020-10'}]
        sqlDB=SQLDB(db)
        mEntityInfo=sqlDB.createTable(messagesLod,"messages","id",withDrop=True)
        sqlDB.store(messagesLod,mEntityInfo)
        fEntityInfo=sqlDB.createTable(foldersLod,"folderLocations","id",withDrop=True)
        sqlDB.store(foldersLod,fEntityInfo)
        mboxContent="""From MAILER-DAEMON Sat Oct 24 14:37:31 2020
From: wikidata-request@lists.wikimedia.org
Subject: Wikidata Digest, Vol 107, Issue 2
To: wikidata@lists.wikimedia.org
Reply-To: wikidata@lists.wikimedia.org
Date: Sat, 03 Oct 2020 12:00:03 +0000
Message-ID: <mailman.45.1601640003.19840.wikidata@lists.wikimedia.org>
MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit
Sender: "Wikidata" <wikidata-bounces@lists.wikimedia.org>
Send Wikidata mailing list submissions to
    wikidata@lists.wikimedia.org

        
"""
        file=open(mboxFile,'w')
        file.write(mboxContent)
        file.close()
        Thunderbird.profiles['wf']=Thunderbird(user='wf',db=db,profile=profile)


    def testCreateMailbox(self):
        mboxFile="/tmp/testMailbox"
        mbox=mailbox.mbox(mboxFile)
        message=Mail.create_message("john@doe.com", "mary@doe.com", "Hi Mary!", {"Subject":"Let's talk"})
        mbox.add(message)
        mbox.close()
        
    def getMockedMail(self):
        mail=Mail("wf","mailman.45.1601640003.19840.wikidata@lists.wikimedia.org",debug=self.debug)
        return mail
    
    def testIssue1(self):
        '''
        test Mail access
        '''
        mail=self.getMockedMail()
        self.assertEqual(mail.tb.user,'wf')
        self.assertTrue(mail.msg is not None)
        subject=mail.msg.get("subject")
        if self.debug:
            print (subject)
        self.assertEqual(subject,"Wikidata Digest, Vol 107, Issue 2")
        pass

    def testIssue2(self):
        '''
        see https://github.com/WolfgangFahl/pyThunderbird/issues/2
        Given a user id lookup the thunderbird profile
        '''
        user='wf'
        tb=Thunderbird.get(user)
        self.assertEqual(tb.user,user)
        
    def testIssue4(self):
        '''
        https://github.com/WolfgangFahl/pyThunderbird/issues/4
        Folderpath mapping should work on all levels
        '''
        folderURI="mailbox://nobody@Local Folders/WF/Friends/Diverse"
        expectedSbdFolder='/Mail/Local Folders/WF.sbd/Friends.sbd/Diverse'
        expectedFolder="WF/Friends/Diverse"
        sbdFolder,folder=Mail.toSbdFolder(folderURI)
        self.assertEqual(sbdFolder,expectedSbdFolder)
        self.assertEqual(folder,expectedFolder)
        
        
    def testIssue8(self):
        '''
        https://github.com/WolfgangFahl/pyThunderbird/issues/8
        make from and to headers clickable to allow replying to mail just displayed
        '''
        mail=self.getMockedMail()
        self.assertEqual(mail.fromUrl,"<a href='mailto:wikidata-request@lists.wikimedia.org'>wikidata-request@lists.wikimedia.org</a>")
        self.assertEqual(mail.toUrl,"<a href='mailto:wikidata@lists.wikimedia.org'>wikidata@lists.wikimedia.org</a>")
        
    def testIssue10(self):
        '''
        https://github.com/WolfgangFahl/pyThunderbird/issues/10
        display wikison notation for cut&paste into Semantic MediaWiki
        '''
        mail=self.getMockedMail()
        wikison=mail.asWikiMarkup()
        expected="""{{mail
|user=wf
|id=mailman.45.1601640003.19840.wikidata@lists.wikimedia.org
|from=wikidata-request@lists.wikimedia.org
|to=wikidata@lists.wikimedia.org
|subject=Wikidata Digest, Vol 107, Issue 2
}}"""
        if self.debug:
            print (wikison)
        self.assertEqual(expected,wikison)
        pass
    
    def isDeveloper(self)->bool:
        '''
        check whether we test on the developer machine
        '''
        user=getpass.getuser()
        host=socket.gethostname()
        
        return user=="wf" and host=="fix.bitplan.com"
    
    def testHeaderIssue(self):
        '''
         File "/hd/sengo/home/wf/source/python/pyThunderbird/thunderbird/mail.py", line 158, in __init__
    part.filename=str(make_header(decode_header(partname)))
  File "/usr/lib/python3.8/email/header.py", line 80, in decode_header
    if not ecre.search(header):
TypeError: expected string or bytes-like object
        '''
        if self.isDeveloper():
            user="wf"
            tb=Thunderbird.get(user)
            debug=False
            mailid="<61418716.20495.1635242774805@sb2-itd-337.admin.sb2>"
            mail=Mail(user,mailid=mailid,tb=tb,debug=debug)
            self.assertTrue(mail.found)
            if debug:
                print(mail)
            msgParts=mail.msgParts
            if debug:
                for i,msgPart in enumerate(msgParts):
                    print (f"{i}:{msgPart.filename}")
            
            self.assertTrue(msgParts[3].filename.startswith("Rü"))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testMail']
    unittest.main()
