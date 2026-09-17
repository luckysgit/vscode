"""Problem Bank authorization, validation, publication, persistence, concurrency, and secrecy."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import threading
import unittest
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from auth import AuthStore
from problems import ProblemStore, ProblemError


def payload(**changes):
    data = dict(title='Sum of Two Numbers',shortDescription='Add integers',description='Given A and B, print their sum.',
                difficulty='Easy',visibility='Private',tags=[' Array ', 'math','array'],inputFormat='Two integers A B',
                outputFormat='Print A+B',constraints='-100 <= A,B <= 100',explanation='Add the two values.',
                testCases=[dict(input='2 3',expectedOutput='5',isHidden=False,order=0),
                           dict(input='SECRET-INPUT-925',expectedOutput='SECRET-OUTPUT-739',isHidden=True,order=1)],
                requestId=str(uuid.uuid4()))
    data.update(changes)
    return data


class ProblemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.auth = AuthStore(self.temp.name+'/db.sqlite3')
        self.a,_ = self.auth.register(dict(username='AuthorA',email='a@example.com',password='long test password'),None)
        self.b,_ = self.auth.register(dict(username='AuthorB',email='b@example.com',password='long test password'),None)
        self.guest,_=self.auth.guest(None)
        self.store = ProblemStore(self.auth)
    def tearDown(self): self.temp.cleanup()
    def error(self, code, callback):
        with self.assertRaises(ProblemError) as caught: callback()
        self.assertEqual(caught.exception.status,code,str(caught.exception))
    def publish(self, problem):
        return self.store.action(self.a,problem['id'],'publish',{'revision':problem['revision']})

    def test_ownership_and_private_cases(self):
        p=self.store.create(self.a,payload())
        self.assertEqual(p['version'],1)
        self.assertEqual(p['tags'],['array','math'])
        self.assertEqual(len(self.store.list(self.a,{},True)['problems']),1)
        self.assertEqual(len(self.store.list(self.b,{},True)['problems']),0)
        self.error(403,lambda:self.store.edit(self.b,p['id'],{'revision':1,'title':'steal'}))
        for action in ('archive','publish','duplicate'):
            self.error(403,lambda:self.store.action(self.b,p['id'],action,{'revision':1,'requestId':str(uuid.uuid4())}))
        self.error(403,lambda:self.store.get(self.b,p['id'],True))
        self.error(403,lambda:self.store.get(None,p['id']))
        self.error(403,lambda:self.store.versions(self.b,p['id']))
        self.error(401,lambda:self.store.create(None,payload()))
        self.error(403,lambda:self.store.create(self.guest,payload()))
        public=self.store.get(self.a,p['id'])
        self.assertNotIn('SECRET',json.dumps(public))
        self.assertNotIn('testCases',public)
        self.assertNotIn('SECRET',json.dumps(self.store.list(self.a,{},True)))

    def test_published_history_and_staged_edits(self):
        p=self.publish(self.store.create(self.a,payload(visibility='Public')))
        old=self.store.get(self.a,p['id'],True,p['problemVersionId'])
        draft=self.store.edit(self.a,p['id'],{'revision':p['revision'],'title':'New title','visibility':'Private',
                                           'testCases':[dict(input='4 5',expectedOutput='9',isHidden=False),dict(input='10 20',expectedOutput='30',isHidden=True)]})
        self.assertEqual(draft['version'],2)
        self.assertEqual(self.store.get(None,p['id'])['title'],'Sum of Two Numbers')
        self.error(403,lambda:self.store.get(self.b,p['id'],version_id=draft['problemVersionId']))
        self.assertEqual(self.store.list(self.a,{'selectable':['true']},True)['problems'][0]['problemVersionId'],p['problemVersionId'])
        new=self.publish(draft)
        self.assertEqual(new['currentVersionId'],new['problemVersionId'])
        self.assertEqual(new['version'],2)
        self.assertEqual(self.store.get(self.a,p['id'],True,p['problemVersionId'])['testCases'],old['testCases'])
        self.assertEqual(self.store.get(self.a,p['id'],True,p['problemVersionId'])['title'],old['title'])
        self.assertEqual(len(self.store.versions(self.a,p['id'])),2)
        self.error(403,lambda:self.store.get(None,p['id']))
        with self.auth.connect() as db:
            for sql,args in [ ('UPDATE problem_versions SET title=? WHERE id=?',('bad',p['problemVersionId'])),
                              ('DELETE FROM test_cases WHERE problem_version_id=?',(p['problemVersionId'],)),
                              ('DELETE FROM problem_tags WHERE problem_version_id=?',(p['problemVersionId'],))]:
                with self.assertRaises(sqlite3.IntegrityError): db.execute(sql,args)

    def test_public_projection_archive_duplicate_persistence(self):
        p=self.publish(self.store.create(self.a,payload(visibility='Public')))
        for user in (None,self.guest,self.b,self.a):
            response=self.store.get(user,p['id'])
            self.assertNotIn('SECRET',json.dumps(response));self.assertEqual(len(response['visibleTestCases']),1)
        self.assertEqual(len(self.store.list(None,{},False)['problems']),1)
        clone=self.store.action(self.a,p['id'],'duplicate',{'requestId':str(uuid.uuid4())})
        self.assertNotEqual(clone['id'],p['id']);self.assertNotEqual(clone['problemVersionId'],p['problemVersionId'])
        self.assertEqual(clone['visibility'],'Private');self.assertEqual(clone['status'],'DRAFT')
        with self.auth.connect() as db:
            ids=[{r[0] for r in db.execute('SELECT id FROM test_cases WHERE problem_version_id=?',(v,))} for v in (p['problemVersionId'],clone['problemVersionId'])]
            self.assertFalse(ids[0]&ids[1])
        archived=self.store.action(self.a,p['id'],'archive',{'revision':p['revision']})
        self.assertEqual(archived['status'],'ARCHIVED')
        self.assertEqual(self.store.list(self.a,{'selectable':['true']},True)['total'],0)
        self.assertEqual(self.store.list(self.a,{'status':['ARCHIVED']},True)['total'],1)
        self.error(409,lambda:self.store.edit(self.a,p['id'],{'revision':archived['revision'],'title':'no'}))
        reopened=ProblemStore(AuthStore(self.auth.path))
        self.assertEqual(reopened.get(self.a,p['id'],True)['testCases'],p['testCases'])

    def test_validation_drafts_and_failed_publish(self):
        p=self.store.create(self.a,{'requestId':str(uuid.uuid4())})
        self.error(400,lambda:self.publish(p))
        self.assertEqual(self.store.get(self.a,p['id'],True)['status'],'DRAFT')
        for data in [payload(title='x'*161),payload(difficulty='expert'),payload(visibility='Organization'),
                     payload(tags=['<script>']),payload(testCases=[dict(input='a',expectedOutput='b',isHidden='false')]),
                     payload(testCases=[dict(input='a',isHidden=False)]),payload(testCases=[dict(input='a'*4097,expectedOutput='',isHidden=True)]),
                     payload(testCases=[dict(input='',expectedOutput='',isHidden=True,order=-1)]),payload(owner_id=self.b['id'])]:
            self.error(400,lambda:self.store.create(self.a,data))
        self.error(400,lambda:self.store.list(self.a,{'sort':['x; DROP TABLE problems']},True))
        self.error(400,lambda:self.store.list(self.a,{'status':['invalid']},True))
        malicious=self.store.create(self.a,payload(title='<script>alert(1)</script>'))
        self.assertEqual(malicious['title'],'<script>alert(1)</script>')

    def test_filters_and_stale_writes_idempotency(self):
        data=payload();p=self.store.create(self.a,data)
        self.assertEqual(self.store.create(self.a,data)['id'],p['id'])
        self.error(409,lambda:self.store.create(self.a,{**data,'title':'changed'}))
        self.assertEqual(self.store.list(self.a,{'search':['sum'],'tag':['math'],'difficulty':['Easy']},True)['total'],1)
        draft=self.store.edit(self.a,p['id'],{'revision':1,'title':'Changed'})
        self.assertEqual(draft['version'],1)
        self.error(409,lambda:self.store.edit(self.a,p['id'],{'revision':1,'title':'lost update'}))
        outcomes=[]
        def save():
            try: self.store.edit(self.a,p['id'],{'revision':draft['revision'],'title':'concurrent'});outcomes.append(200)
            except ProblemError as e: outcomes.append(e.status)
        threads=[threading.Thread(target=save) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual(sorted(outcomes),[200,409])
