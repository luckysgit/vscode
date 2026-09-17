"""Persistent problem authoring. Public serialization never reads hidden test rows."""
import hashlib
import json
from pathlib import Path
import re
import time
import uuid


class ProblemError(Exception):
    def __init__(self, message, status=400, code='invalid_request'):
        super().__init__(message)
        self.status, self.code = status, code


FIELDS = {'title': ('title', 160), 'shortDescription': ('short_description', 500),
          'description': ('description', 50000), 'inputFormat': ('input_format', 10000),
          'outputFormat': ('output_format', 10000), 'constraints': ('constraints_text', 10000),
          'explanation': ('explanation', 10000)}
CONTENT = set(FIELDS) | {'difficulty', 'visibility', 'tags', 'testCases'}


def account(user):
    if not user:
        raise ProblemError('Sign in to manage your problems.', 401, 'authentication_required')
    if user['isGuest']:
        raise ProblemError('Create an account or sign in to manage your problems.', 403, 'account_required')
    return user['id']


def validate(body, base=None, publish=False):
    if not isinstance(body, dict) or set(body) - CONTENT - {'revision', 'requestId'}:
        raise ProblemError('Unknown fields or malformed problem payload.')
    data = dict(base or {})
    data.update(body)
    result = {}
    for key, (_, limit) in FIELDS.items():
        value = data.get(key, '')
        if not isinstance(value, str) or len(value) > limit or '\x00' in value:
            raise ProblemError(f'{key} must be text of at most {limit} characters without null bytes.')
        result[key] = value
    result['difficulty'] = data.get('difficulty', 'Easy')
    result['visibility'] = data.get('visibility', 'Private')
    if result['difficulty'] not in ('Easy', 'Medium', 'Hard'):
        raise ProblemError('Difficulty must be Easy, Medium, or Hard.')
    if result['visibility'] not in ('Private', 'Public'):
        raise ProblemError('Visibility must be Private or Public. Organization access is not configured.')
    tags = data.get('tags', [])
    if not isinstance(tags, list) or len(tags) > 20:
        raise ProblemError('Use at most 20 tags.')
    result['tags'] = []
    for tag in tags:
        if not isinstance(tag, str) or not re.fullmatch(r'[\w +#.-]{1,32}', tag.strip(), re.UNICODE):
            raise ProblemError('Tags must contain 1–32 letters, numbers, spaces, +, #, dot, or hyphen.')
        normalized = ' '.join(tag.lower().split())
        if normalized not in result['tags']:
            result['tags'].append(normalized)
    cases = data.get('testCases', [])
    if not isinstance(cases, list) or len(cases) > 50:
        raise ProblemError('Use at most 50 test cases.')
    result['testCases'] = []
    for order, case in enumerate(cases):
        if not isinstance(case, dict) or set(case) - {'input', 'expectedOutput', 'isHidden', 'order'}:
            raise ProblemError('Malformed test case.')
        if type(case.get('isHidden')) is not bool:
            raise ProblemError('Each test case needs a boolean isHidden value.')
        if 'order' in case and (type(case['order']) is not int or case['order'] != order):
            raise ProblemError('Test case order must match its zero-based array position.')
        for key in ('input', 'expectedOutput'):
            if not isinstance(case.get(key), str) or len(case[key].encode('utf-8')) > 4096 or '\x00' in case[key]:
                raise ProblemError(f'Test case {key} must be text of at most 4096 bytes. Empty text is allowed.')
        result['testCases'].append({**case, 'order': order})
    if publish:
        for key in ('title', 'description', 'inputFormat', 'outputFormat'):
            if not result[key].strip():
                raise ProblemError(f'{key} is required before publishing.')
        if not any(not c['isHidden'] for c in result['testCases']) or not any(c['isHidden'] for c in result['testCases']):
            raise ProblemError('Publishing requires at least one sample and one hidden test case.')
    return result


class ProblemStore:
    def __init__(self, auth):
        self.auth = auth
        with auth.connect() as db:
            db.executescript(Path(__file__).with_name('migrations').joinpath('001_problem_bank.sql').read_text())

    @staticmethod
    def _owned(db, problem_id, user):
        owner = account(user)
        row = db.execute('SELECT * FROM problems WHERE id=?', (problem_id,)).fetchone()
        if not row:
            raise ProblemError('Problem not found.', 404, 'not_found')
        if row['owner_id'] != owner:
            raise ProblemError('Only the problem owner may perform this action.', 403, 'forbidden')
        return row

    @staticmethod
    def _revision(row, body):
        if type(body.get('revision')) is not int or body['revision'] != row['revision']:
            raise ProblemError('This problem changed in another tab. Reopen it before saving; your form has been kept.', 409, 'conflict')
        if row['status'] == 'ARCHIVED':
            raise ProblemError('Archived problems cannot be edited or published. Duplicate to create a new draft.', 409, 'archived')

    @staticmethod
    def _read(db, row, version_id=None, manage=False):
        version_id = version_id or (row['draft_version_id'] if manage else None) or row['current_version_id']
        version = db.execute('SELECT * FROM problem_versions WHERE id=? AND problem_id=?', (version_id, row['id'])).fetchone()
        if not version:
            raise ProblemError('Problem version not found.', 404, 'not_found')
        result = {key: version[column] for key, (column, _) in FIELDS.items()}
        result.update(id=row['id'], problemId=row['id'], problemVersionId=version['id'],
                      version=version['version_number'], difficulty=version['difficulty'],
                      visibility=(row['draft_visibility'] or row['visibility']) if manage else row['visibility'], status=row['status'], createdAt=row['created_at'],
                      updatedAt=row['updated_at'], publishedAt=version['published_at'],
                      tags=[r['tag'] for r in db.execute('SELECT tag FROM problem_tags WHERE problem_version_id=? ORDER BY tag', (version_id,))])
        # Explicit SQL projection: a public request never fetches hidden contents or IDs.
        cases = db.execute('SELECT input, expected_output, is_hidden, sort_order FROM test_cases WHERE problem_version_id=?' +
                           ('' if manage else ' AND is_hidden=0') + ' ORDER BY sort_order', (version_id,)).fetchall()
        if manage:
            result.update(revision=row['revision'], currentVersionId=row['current_version_id'],
                          hasDraft=bool(row['draft_version_id']),
                          testCases=[dict(input=c['input'], expectedOutput=c['expected_output'], isHidden=bool(c['is_hidden']), order=c['sort_order']) for c in cases])
        else:
            result['visibleTestCases'] = [dict(input=c['input'], expectedOutput=c['expected_output']) for c in cases]
        return result

    @staticmethod
    def _write_version(db, problem_id, user_id, data, draft_id=None):
        now = time.time()
        values = [data[k] for k in FIELDS]
        if draft_id:
            db.execute('UPDATE problem_versions SET ' + ','.join(column+'=?' for column, _ in FIELDS.values()) + ',difficulty=? WHERE id=? AND published_at IS NULL', (*values, data['difficulty'], draft_id))
            db.execute('DELETE FROM problem_tags WHERE problem_version_id=?', (draft_id,))
            db.execute('DELETE FROM test_cases WHERE problem_version_id=?', (draft_id,))
            version_id = draft_id
        else:
            version_id = str(uuid.uuid4())
            number = db.execute('SELECT COALESCE(MAX(version_number),0)+1 FROM problem_versions WHERE problem_id=?', (problem_id,)).fetchone()[0]
            columns = ','.join(column for column, _ in FIELDS.values())
            db.execute(f'INSERT INTO problem_versions (id,problem_id,version_number,{columns},difficulty,created_by,created_at) VALUES ({",".join("?" for _ in range(13))})',
                       (version_id, problem_id, number, *values, data['difficulty'], user_id, now))
        db.executemany('INSERT INTO problem_tags VALUES (?,?)', [(version_id, tag) for tag in data['tags']])
        db.executemany('INSERT INTO test_cases VALUES (?,?,?,?,?,?,?)',
                       [(str(uuid.uuid4()), version_id, c['input'], c['expectedOutput'], int(c['isHidden']), i, now) for i,c in enumerate(data['testCases'])])
        return version_id

    def create(self, user, body):
        owner = account(user)
        data = validate(body)
        request_id = body.get('requestId')
        if not isinstance(request_id, str) or not re.fullmatch(r'[a-zA-Z0-9-]{16,80}', request_id):
            raise ProblemError('A unique requestId is required to prevent duplicate saves.')
        digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        with self.auth.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            previous = db.execute('SELECT * FROM problem_create_requests WHERE owner_id=? AND request_id=?', (owner, request_id)).fetchone()
            if previous:
                if previous['payload_hash'] != digest:
                    raise ProblemError('This save request was already used for different content.', 409, 'conflict')
                return self._read(db, self._owned(db, previous['problem_id'], user), manage=True)
            problem_id, now = str(uuid.uuid4()), time.time()
            db.execute('INSERT INTO problems (id,owner_id,visibility,draft_visibility,created_at,updated_at) VALUES (?,?,?,?,?,?)', (problem_id, owner, data['visibility'], data['visibility'], now, now))
            version_id = self._write_version(db, problem_id, owner, data)
            db.execute('UPDATE problems SET current_version_id=?,draft_version_id=? WHERE id=?', (version_id, version_id, problem_id))
            db.execute('INSERT INTO problem_create_requests VALUES (?,?,?,?)', (owner, request_id, digest, problem_id))
            return self._read(db, self._owned(db, problem_id, user), manage=True)

    def get(self, user, problem_id, manage=False, version_id=None):
        with self.auth.connect() as db:
            if manage:
                row = self._owned(db, problem_id, user)
            else:
                row = db.execute('SELECT * FROM problems WHERE id=?', (problem_id,)).fetchone()
                if not row:
                    raise ProblemError('Problem not found.', 404, 'not_found')
                owner = bool(user and not user['isGuest'] and row['owner_id'] == user['id'])
                if not owner and (row['visibility'] != 'Public' or row['status'] != 'PUBLISHED'):
                    raise ProblemError('This problem is private or unavailable.', 403, 'forbidden')
                if version_id and not owner:
                    version = db.execute('SELECT published_at FROM problem_versions WHERE id=? AND problem_id=?', (version_id, problem_id)).fetchone()
                    if not version or version['published_at'] is None:
                        raise ProblemError('Version is not published.', 403, 'forbidden')
            return self._read(db, row, version_id, manage)

    def edit(self, user, problem_id, body):
        with self.auth.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._owned(db, problem_id, user)
            self._revision(row, body)
            base = self._read(db, row, manage=True)
            data = validate(body, base)
            version_id = self._write_version(db, problem_id, user['id'], data, row['draft_version_id'])
            # Published content remains the current version until explicitly published again.
            db.execute('UPDATE problems SET draft_version_id=?,draft_visibility=?,revision=revision+1,updated_at=? WHERE id=?', (version_id, data['visibility'], time.time(), problem_id))
            return self._read(db, self._owned(db, problem_id, user), manage=True)

    def action(self, user, problem_id, action, body):
        if not isinstance(body, dict) or set(body) - {'revision', 'requestId'}:
            raise ProblemError('Unexpected action fields.')
        if action == 'duplicate':
            original = self.get(user, problem_id, manage=True)
            data = {k: original[k] for k in CONTENT}
            data.update(title=original['title'][:153] + ' - Copy', visibility='Private', requestId=body.get('requestId'))
            return self.create(user, data)
        with self.auth.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = self._owned(db, problem_id, user)
            self._revision(row, body)
            if action == 'archive':
                db.execute("UPDATE problems SET status='ARCHIVED',archived_at=?,updated_at=?,revision=revision+1 WHERE id=?", (time.time(),time.time(),problem_id))
            elif action == 'publish':
                if not row['draft_version_id']:
                    raise ProblemError('There is no draft to publish.', 409, 'no_draft')
                data = self._read(db, row, manage=True)
                validate({}, data, publish=True)
                db.execute('UPDATE problem_versions SET published_at=? WHERE id=?', (time.time(), row['draft_version_id']))
                db.execute("UPDATE problems SET current_version_id=draft_version_id,visibility=draft_visibility,draft_visibility=NULL,draft_version_id=NULL,status='PUBLISHED',revision=revision+1,updated_at=? WHERE id=?", (time.time(),problem_id))
            else:
                raise ProblemError('Unknown action.', 404, 'not_found')
            return self._read(db, self._owned(db, problem_id, user), manage=True)

    def versions(self, user, problem_id):
        with self.auth.connect() as db:
            self._owned(db, problem_id, user)
            return [dict(id=r['id'], version=r['version_number'], title=r['title'], createdAt=r['created_at'], publishedAt=r['published_at'])
                    for r in db.execute('SELECT * FROM problem_versions WHERE problem_id=? ORDER BY version_number DESC', (problem_id,))]

    def list(self, user, query, mine=False):
        owner = account(user) if mine else None
        allowed = {'search','difficulty','tag','visibility','status','sort','page','selectable'}
        if set(query) - allowed:
            raise ProblemError('Unknown filter.')
        q = {k: v[0] for k,v in query.items()}
        for name, values in [('difficulty',('Easy','Medium','Hard')), ('visibility',('Private','Public')), ('status',('DRAFT','PUBLISHED','ARCHIVED'))]:
            if q.get(name) and q[name] not in values:
                raise ProblemError(f'Invalid {name} filter.')
        sorts = {'updated':'p.updated_at DESC','created':'p.created_at DESC','title':'v.title COLLATE NOCASE ASC',
                 'difficulty':"CASE v.difficulty WHEN 'Easy' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END"}
        sort = q.get('sort','updated')
        if sort not in sorts or not q.get('page','1').isdigit() or not 1 <= int(q.get('page','1')) <= 100000:
            raise ProblemError('Invalid sort or page.')
        if len(q.get('search','')) > 200 or len(q.get('tag','')) > 32 or q.get('selectable','') not in ('','true','false'):
            raise ProblemError('Invalid search, tag, or selection filter.')
        selection = q.get('selectable') == 'true'
        clause, params = (['p.owner_id=?'], [owner]) if mine else (["p.visibility='Public'", "p.status='PUBLISHED'"], [])
        if selection:
            clause.append("p.status='PUBLISHED'")
        elif mine and not q.get('status'):
            clause.append("p.status!='ARCHIVED'")
        for key,col in [('difficulty','v.difficulty'),('visibility', 'COALESCE(p.draft_visibility,p.visibility)' if mine and not selection else 'p.visibility'),('status','p.status')]:
            if q.get(key): clause.append(col+'=?'); params.append(q[key])
        if q.get('search'):
            clause.append("(instr(lower(v.title), lower(?))>0 OR instr(lower(v.description),lower(?))>0)")
            params.extend([q['search'],q['search']])
        if q.get('tag'):
            clause.append('EXISTS(SELECT 1 FROM problem_tags t WHERE t.problem_version_id=v.id AND t.tag=?)')
            params.append(' '.join(q['tag'].lower().split()))
        pointer = 'COALESCE(p.draft_version_id,p.current_version_id)' if mine and not selection else 'p.current_version_id'
        sql = ' FROM problems p JOIN problem_versions v ON v.id='+pointer+' WHERE '+' AND '.join(clause)
        with self.auth.connect() as db:
            total = db.execute('SELECT COUNT(*)'+sql, params).fetchone()[0]
            rows = db.execute('SELECT p.*,v.id AS selected_version'+sql+' ORDER BY '+sorts[sort]+',p.id LIMIT 30 OFFSET ?', (*params,(int(q.get('page','1'))-1)*30)).fetchall()
            items = []
            for row in rows:
                # List responses contain summary metadata only, never any test inputs/answers.
                item = self._read(db, row, row['selected_version'], manage=False)
                item.pop('visibleTestCases')
                for key in ('description','inputFormat','outputFormat','constraints','explanation'): item.pop(key)
                item['testCaseCount'] = db.execute('SELECT COUNT(*) FROM test_cases WHERE problem_version_id=?',(row['selected_version'],)).fetchone()[0]
                item.update(revision=row['revision'],hasDraft=bool(row['draft_version_id']))
                if mine and not selection: item['visibility'] = row['draft_visibility'] or row['visibility']
                items.append(item)
            return dict(problems=items,total=total,page=int(q.get('page','1')),pageSize=30)
