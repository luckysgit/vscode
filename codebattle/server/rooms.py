"""Shared, durable room discovery and membership. No fabricated activity."""
import hashlib
import json
from pathlib import Path
import secrets
import time
import uuid
from problems import account, ProblemError


class RoomStore:
    def __init__(self, auth, problems):
        self.auth, self.problems = auth, problems
        with auth.connect() as db:
            db.executescript(Path(__file__).with_name('migrations').joinpath('002_rooms.sql').read_text())

    @staticmethod
    def _find(db, key):
        row = db.execute('SELECT * FROM rooms WHERE id=? OR code=?', (key,key.upper())).fetchone()
        if not row:
            raise ProblemError('Room not found. Check the room code.',404,'not_found')
        return row

    @staticmethod
    def _member(db, row, user):
        return bool(user and db.execute('SELECT 1 FROM room_members WHERE room_id=? AND user_id=?',(row['id'],user['id'])).fetchone())

    def _serialize(self, db, row, user, details=False):
        version=db.execute('SELECT title,difficulty,problem_id,version_number FROM problem_versions WHERE id=?',(row['problem_version_id'],)).fetchone()
        host=db.execute('SELECT username FROM accounts WHERE id=?',(row['host_id'],)).fetchone()[0]
        joined=self._member(db,row,user)
        result=dict(id=row['id'],code=row['code'],title=row['title'],host=host,
                    isHost=bool(user and user['id']==row['host_id']),isMember=joined,
                    status=row['status'],visibility=row['visibility'],max=row['capacity'],
                    players=db.execute('SELECT COUNT(*) FROM room_members WHERE room_id=?',(row['id'],)).fetchone()[0],
                    problemId=version['problem_id'],problemVersionId=row['problem_version_id'],
                    problemTitle=version['title'],version=version['version_number'],diff=version['difficulty'],createdAt=row['created_at'])
        if details and joined:
            result['members']=[dict(username=r['username'],isHost=r['id']==row['host_id']) for r in db.execute(
                'SELECT a.id,a.username FROM room_members m JOIN accounts a ON a.id=m.user_id WHERE m.room_id=? ORDER BY m.joined_at',(row['id'],))]
            problem=db.execute('SELECT * FROM problems WHERE id=?',(version['problem_id'],)).fetchone()
            result['problem']=self.problems._read(db,problem,row['problem_version_id'],manage=False)
        return result

    def create(self,user,body):
        owner=account(user)
        if not isinstance(body,dict) or set(body)-{'title','problemVersionId','visibility','capacity','requestId'}:
            raise ProblemError('Invalid room fields. Host identity is determined by your session.')
        title=body.get('title','')
        visibility=body.get('visibility','Public')
        capacity=body.get('capacity',20)
        version=body.get('problemVersionId')
        request=body.get('requestId')
        if not isinstance(title,str) or not 1<=len(title.strip())<=160 or '\x00' in title:
            raise ProblemError('Enter a room title of 1–160 characters.')
        if visibility not in ('Public','Unlisted') or type(capacity) is not int or not 2<=capacity<=100:
            raise ProblemError('Choose Public or Unlisted visibility and 2–100 participants.')
        try:
            uuid.UUID(version);uuid.UUID(request)
        except (ValueError,TypeError,AttributeError):
            raise ProblemError('Select a published problem version and supply a unique requestId.') from None
        digest=hashlib.sha256(json.dumps([title.strip(),version,visibility,capacity]).encode()).hexdigest()
        with self.auth.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            existing=db.execute('SELECT * FROM rooms WHERE host_id=? AND request_id=?',(owner,request)).fetchone()
            if existing:
                if existing['payload_hash']!=digest:raise ProblemError('This request was already used with different room details.',409,'conflict')
                return self._serialize(db,existing,user,True)
            problem=db.execute('SELECT p.* FROM problems p JOIN problem_versions v ON v.problem_id=p.id WHERE v.id=? AND v.published_at IS NOT NULL',(version,)).fetchone()
            if not problem or problem['status']!='PUBLISHED' or problem['current_version_id']!=version:
                raise ProblemError('Select the current published version of an available problem.',409,'invalid_version')
            if problem['owner_id']!=owner and problem['visibility']!='Public':
                raise ProblemError('You cannot use another author’s private problem.',403,'forbidden')
            room_id=str(uuid.uuid4())
            for _ in range(10):
                code='CB-'+secrets.token_hex(8).upper()
                if not db.execute('SELECT 1 FROM rooms WHERE code=?',(code,)).fetchone():break
            else:raise ProblemError('Could not allocate a room code. Try again.',503,'code_unavailable')
            now=time.time()
            db.execute('INSERT INTO rooms (id,code,host_id,title,problem_version_id,visibility,capacity,request_id,payload_hash,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
                       (room_id,code,owner,title.strip(),version,visibility,capacity,request,digest,now))
            db.execute('INSERT INTO room_members VALUES (?,?,?)',(room_id,owner,now))
            return self._serialize(db,self._find(db,room_id),user,True)

    def list(self,user,query):
        if set(query)-{'search','page'} or any(len(v)!=1 for v in query.values()):raise ProblemError('Invalid room search.')
        search=query.get('search',[''])[0].strip()
        page=query.get('page',['1'])[0]
        if len(search)>160 or not page.isdigit() or not 1<=int(page)<=100000:raise ProblemError('Invalid room search or page.')
        with self.auth.connect() as db:
            # Unlisted rooms require an exact invitation code (or existing membership).
            owner=user['id'] if user else ''
            clause="r.status='LOBBY' AND (r.visibility='Public' OR r.code=? OR EXISTS(SELECT 1 FROM room_members m WHERE m.room_id=r.id AND m.user_id=?))"
            params=[search.upper(),owner]
            if search:
                clause+=' AND (instr(lower(r.title),lower(?))>0 OR r.code=?)';params.extend([search,search.upper()])
            total=db.execute('SELECT COUNT(*) FROM rooms r WHERE '+clause,params).fetchone()[0]
            rows=db.execute('SELECT r.* FROM rooms r WHERE '+clause+' ORDER BY r.created_at DESC,r.id LIMIT 30 OFFSET ?',(*params,(int(page)-1)*30)).fetchall()
            return dict(rooms=[self._serialize(db,r,user) for r in rows],total=total,page=int(page),pageSize=30)

    def get(self,user,key):
        with self.auth.connect() as db:
            row=self._find(db,key)
            if row['visibility']=='Unlisted' and key.upper()!=row['code'] and not self._member(db,row,user):
                raise ProblemError('Use the invitation code to open this room.',403,'forbidden')
            return self._serialize(db,row,user,True)

    def action(self,user,key,action):
        owner=account(user)
        with self.auth.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=self._find(db,key)
            member=self._member(db,row,user)
            if action=='join':
                if row['status']!='LOBBY':raise ProblemError('This room is closed.',409,'closed')
                if row['visibility']=='Unlisted' and key.upper()!=row['code'] and not member:
                    raise ProblemError('Use the invitation code to join this room.',403,'forbidden')
                count=db.execute('SELECT COUNT(*) FROM room_members WHERE room_id=?',(row['id'],)).fetchone()[0]
                if not member and count>=row['capacity']:raise ProblemError('This room is full.',409,'full')
                db.execute('INSERT OR IGNORE INTO room_members VALUES (?,?,?)',(row['id'],owner,time.time()))
            elif action=='leave':
                if row['host_id']==owner:raise ProblemError('The host must close the room instead of leaving.',409,'host_must_close')
                db.execute('DELETE FROM room_members WHERE room_id=? AND user_id=?',(row['id'],owner))
            elif action=='close':
                if row['host_id']!=owner:raise ProblemError('Only the host can close this room.',403,'forbidden')
                db.execute("UPDATE rooms SET status='CLOSED',closed_at=COALESCE(closed_at,?) WHERE id=?",(time.time(),row['id']))
            else:raise ProblemError('Room action is not implemented.',404,'not_found')
            return self._serialize(db,self._find(db,key),user,True)
