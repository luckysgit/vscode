import sys
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'server'))
from auth import AuthStore
from problems import ProblemStore,ProblemError
from rooms import RoomStore
from test_problems import payload

class RoomTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.auth=AuthStore(self.temp.name+'/db')
        self.users=[self.auth.register(dict(username='RoomUser'+str(i),email=f'room{i}@example.com',password='room test password'),None)[0] for i in range(3)]
        self.a,self.b,self.c=self.users
        self.problems=ProblemStore(self.auth);self.rooms=RoomStore(self.auth,self.problems)
        self.problem=self.problems.create(self.a,payload())
        self.problem=self.problems.action(self.a,self.problem['id'],'publish',{'revision':self.problem['revision']})
    def tearDown(self):self.temp.cleanup()
    def body(self,**extra):return dict(title='Real Room',problemVersionId=self.problem['problemVersionId'],visibility='Public',capacity=2,requestId=str(uuid.uuid4()),**extra)
    def error(self,status,fn):
        with self.assertRaises(ProblemError) as caught:fn()
        self.assertEqual(caught.exception.status,status)
    def test_empty_create_discover_join_persist(self):
        self.assertEqual(self.rooms.list(None,{})['rooms'],[])
        body=self.body();room=self.rooms.create(self.a,body)
        self.assertEqual(room['host'],self.a['username']);self.assertEqual(room['players'],1)
        self.assertEqual(self.rooms.create(self.a,body)['id'],room['id'])
        found=self.rooms.list(self.b,{'search':[room['code']]})['rooms']
        self.assertEqual(len(found),1);self.assertNotIn('problem',found[0])
        joined=self.rooms.action(self.b,room['code'],'join')
        self.assertEqual(joined['players'],2)
        self.assertNotIn('SECRET',str(joined))
        self.assertEqual(self.rooms.action(self.b,room['code'],'join')['players'],2)
        self.assertEqual(RoomStore(self.auth,self.problems).get(self.a,room['id'])['players'],2)
        self.assertEqual(self.rooms.action(self.b,room['id'],'leave')['players'],1)
        self.error(404,lambda:self.rooms.get(self.a,'invalid-code'))
    def test_authority_and_capacity(self):
        self.error(401,lambda:self.rooms.create(None,self.body()))
        guest,_=self.auth.guest(None)
        self.error(403,lambda:self.rooms.create(guest,self.body()))
        body=self.body();body['host']=self.b['username']
        self.error(400,lambda:self.rooms.create(self.a,body))
        self.error(403,lambda:self.rooms.create(self.b,self.body()))
        room=self.rooms.create(self.a,self.body())
        self.error(403,lambda:self.rooms.action(self.b,room['id'],'close'))
        self.error(409,lambda:self.rooms.action(self.a,room['id'],'leave'))
        results=[]
        def join(user):
            try:self.rooms.action(user,room['code'],'join');results.append(200)
            except ProblemError as error:results.append(error.status)
        threads=[threading.Thread(target=join,args=(u,)) for u in (self.b,self.c)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual(sorted(results),[200,409])
        self.assertEqual(self.rooms.get(self.a,room['id'])['players'],2)
        self.rooms.action(self.a,room['id'],'close')
        self.assertEqual(self.rooms.list(self.b,{})['total'],0)
        self.error(409,lambda:self.rooms.action(self.b,room['id'],'join'))
    def test_version_lock_and_unlisted(self):
        body=self.body();body['visibility']='Unlisted'
        room=self.rooms.create(self.a,body)
        self.assertEqual(self.rooms.list(self.b,{})['total'],0)
        self.error(403,lambda:self.rooms.action(self.b,room['id'],'join'))
        self.error(403,lambda:self.rooms.get(self.b,room['id']))
        self.assertEqual(self.rooms.list(self.b,{'search':[room['code']]})['total'],1)
        self.rooms.action(self.b,room['code'],'join')
        draft=self.problems.edit(self.a,self.problem['id'],{'revision':self.problem['revision'],'title':'New version'})
        self.problems.action(self.a,draft['id'],'publish',{'revision':draft['revision']})
        current=self.rooms.get(self.b,room['id'])
        self.assertEqual(current['problemVersionId'],self.problem['problemVersionId'])
        self.assertEqual(current['problem']['title'],'Sum of Two Numbers')
        self.error(409,lambda:self.rooms.create(self.a,self.body()))
