/* Problem Bank authoring controller. All user content is rendered as text. */
class ProblemBankUI {
  constructor(container) {
    this.root=container; this.api=new ProblemBankAPI(); this.dirty=false; this.busy=false; this.generation=0; this.identity=null;
    this.filters={}; this.page=1;
  }
  init() {
    window.addEventListener('beforeunload', event => { if(this.dirty || this.busy){event.preventDefault();event.returnValue='';} });
    window.addEventListener('popstate', () => {
      if(this.busy){history.pushState({},'',this.path);return;}
      if(this.dirty && !confirm('Discard unsaved problem changes?')) { history.pushState({},'',this.path); return; }
      this.dirty=false; this.route(location.pathname);
    });
    document.getElementById('btn-open-create-problem-modal')?.addEventListener('click',()=>this.navigate('/problems/create'));
  }
  identityChanged(user) {
    const id=user && !user.isGuest ? user.id : null;
    if(id===this.identity)return;
    this.identity=id; this.generation++; this.dirty=false; this.model=null; this.selector?.destroy(); this.root.replaceChildren();
  }
  canLeave(view) {
    if(view==='view-my-problems')return true;
    if(this.busy)return false;
    if(this.dirty && !confirm('Discard unsaved problem changes?'))return false;
    this.dirty=false;
    if(location.pathname.startsWith('/problems/'))history.pushState({},'','/');
    return true;
  }
  navigate(path) {
    if(this.busy)return;
    if(this.dirty && !confirm('Discard unsaved problem changes?'))return;
    this.dirty=false; history.pushState({},'',path); this.route(path);
  }
  async route(path) {
    if(!path.startsWith('/problems/'))return;
    this.generation++;
    this.path=path;
    switchView('view-my-problems');
    if(!authService.isAuthenticated()) {
      this.root.replaceChildren(pbNode('h1','My Problems'),pbNode('p','Sign in or create an account to save and manage your problems.'),
        pbButton('Sign in',()=>document.getElementById('btn-nav-sign-in').click(),'btn btn-primary'),
        pbButton('Create account',()=>document.getElementById('btn-nav-sign-up').click()));
      return;
    }
    this.selector?.destroy(); this.selector=null;
    const parts=path.split('/').filter(Boolean);
    if(parts[1]==='my')return this.list();
    if(parts[1]==='create')return this.editor();
    if(parts[1]==='select') {
      this.root.replaceChildren(pbNode('h1','Select Problem'),pbNode('p','Choose a published version for reuse. Archived problems and unpublished drafts are excluded.'),pbButton('Back to My Problems',()=>this.navigate('/problems/my')));
      const container=pbNode('div');this.root.append(container);this.selector=new ProblemSelector(container,{api:this.api});return;
    }
    if(parts.length===2 || parts[2]==='edit') {
      const token=++this.generation;
      this.root.replaceChildren(pbNode('p','Loading problem…'));
      try {
        const {problem}=await this.api.get(parts[1],true);
        if(token!==this.generation)return;
        if(parts[2]==='edit')this.editor(problem);else this.detail(problem);
      } catch(error) { if(token===this.generation)this.root.replaceChildren(pbNode('p',error.message),pbButton('My Problems',()=>this.navigate('/problems/my'))); }
      return;
    }
    this.root.replaceChildren(pbNode('p','Problem page not found.'),pbButton('My Problems',()=>this.navigate('/problems/my')));
  }
  async list() {
    const token=++this.generation;
    this.root.replaceChildren();
    const header=pbNode('div','','section-header');
    const actions=pbNode('div','','pb-toolbar');
    actions.append(pbButton('+ Create Problem',()=>this.navigate('/problems/create'),'btn btn-primary'),pbButton('Select a problem',()=>this.navigate('/problems/select')));
    header.append(pbNode('h1','My Problems'),actions);
    const form=document.createElement('form');form.className='pb-toolbar';
    const search=document.createElement('input');search.className='form-input';search.placeholder='Search my problems…';search.setAttribute('aria-label','Search my problems');search.maxLength=200;search.value=this.filters.search||'';
    const difficulty=pbSelect('Difficulty filter',[['','All difficulties'],['Easy','Easy'],['Medium','Medium'],['Hard','Hard']]);
    const visibility=pbSelect('Visibility filter',[['','All visibility'],['Private','Private'],['Public','Public']]);
    const status=pbSelect('Status filter',[['','Active problems'],['DRAFT','Draft'],['PUBLISHED','Published'],['ARCHIVED','Archived']]);
    const sort=pbSelect('Sort problems',[['updated','Recently Updated'],['created','Recently Created'],['title','Title'],['difficulty','Difficulty']]);
    const tag=document.createElement('input');tag.className='form-input';tag.placeholder='Filter by tag';tag.setAttribute('aria-label','Tag filter');tag.maxLength=32;tag.value=this.filters.tag||'';
    for(const [key,control] of Object.entries({difficulty,visibility,status,sort}))control.value=this.filters[key]|| (key==='sort'?'updated':'');
    const submit=pbButton('Search',()=>form.requestSubmit());
    form.append(search,difficulty,tag,visibility,status,sort,submit);
    form.addEventListener('submit',event=>{event.preventDefault();this.filters={search:search.value,difficulty:difficulty.value,tag:tag.value,visibility:visibility.value,status:status.value,sort:sort.value};this.page=1;this.list();});
    const message=pbNode('p','Loading problems…');message.setAttribute('role','status');
    const rows=pbNode('div','','pb-list');
    this.root.append(header,form,message,rows);
    submit.disabled=true;
    try {
      const response=await this.api.list('my',{...this.filters,page:this.page});
      if(token!==this.generation)return;
      message.textContent=response.total?`${response.total} problem(s)`:'No problems found. Create your first problem or change the filters.';
      for(const problem of response.problems) {
        const card=pbNode('article','','pb-row');
        card.append(pbNode('h2',problem.title||'Untitled draft'),pbNode('p',`${problem.difficulty} · ${problem.visibility} · ${problem.status}${problem.hasDraft?' · Working draft':''} · Version ${problem.version} · ${problem.testCaseCount} tests`),
          pbNode('p',problem.tags.join(', ')),pbNode('p',`Created ${new Date(problem.createdAt*1000).toLocaleString()} · Updated ${new Date(problem.updatedAt*1000).toLocaleString()}`,'text-subtle'));
        const controls=pbNode('div','','pb-toolbar');
        controls.append(pbButton('Open',()=>this.navigate(`/problems/${problem.id}`)),pbButton('Edit',()=>this.navigate(`/problems/${problem.id}/edit`)),
          pbButton('Duplicate',event=>this.rowAction(event.currentTarget,problem,'duplicate',message)),pbButton('Archive',event=>this.rowAction(event.currentTarget,problem,'archive',message)));
        if(problem.status==='ARCHIVED'){controls.children[1].disabled=true;controls.children[3].disabled=true;}
        card.append(controls);rows.append(card);
      }
      const pager=pbNode('div','','pb-toolbar');const previous=pbButton('Previous',()=>{this.page--;this.list();});previous.disabled=this.page===1;
      const next=pbButton('Next',()=>{this.page++;this.list();});next.disabled=this.page*response.pageSize>=response.total;
      pager.append(previous,pbNode('span',`Page ${this.page}`),next);this.root.append(pager);
    }catch(error){if(token===this.generation)message.textContent=error.message;}
    finally {submit.disabled=false;}
  }
  async rowAction(button,problem,action,message) {
    if(this.busy)return;
    if(action==='archive'&&!confirm(`Archive “${problem.title}”? It will no longer appear in new selections. Previous versions are retained.`))return;
    this.busy=true;button.disabled=true;message.textContent=action==='archive'?'Archiving…':'Duplicating…';
    try {
      const {problem:result}=await this.api.action(problem.id,action,{revision:problem.revision,requestId:button.dataset.requestId ||= crypto.randomUUID()});
      this.busy=false;
      if(action==='duplicate')this.navigate(`/problems/${result.id}/edit`);else{await this.list();const notice=pbNode('p','Problem archived.','pb-success');notice.setAttribute('role','status');this.root.prepend(notice);}
    }catch(error){message.textContent=error.message;}
    finally{this.busy=false;button.disabled=false;}
  }
  studentPreview(problem) {
    const area=pbNode('div','','pb-preview');
    area.append(pbNode('h2',problem.title||'Untitled problem'),pbNode('p',`${problem.difficulty} · ${(problem.tags||[]).join(', ')}`));
    for(const [key,title] of [['description','Problem statement'],['inputFormat','Input format'],['outputFormat','Output format'],['constraints','Constraints'],['explanation','Explanation / Notes']]) {
      if(problem[key])area.append(pbNode('h3',title),pbNode('div',problem[key],'pb-prewrap'));
    }
    area.append(pbNode('h3','Sample test cases'));
    const samples=problem.visibleTestCases || (problem.testCases||[]).filter(test=>!test.isHidden);
    samples.forEach((test,index)=>area.append(pbNode('pre',`Sample ${index+1}\nInput\n${test.input}\nExpected output\n${test.expectedOutput}`,'code-block')));
    return area;
  }
  detail(problem) {
    this.root.replaceChildren(pbButton('Back to My Problems',()=>this.navigate('/problems/my')),pbNode('h1',problem.title||'Untitled draft'),pbNode('p',`${problem.status} · ${problem.visibility} · Version ${problem.version}`));
    const controls=pbNode('div','','pb-toolbar');
    const edit=pbButton('Edit problem',()=>this.navigate(`/problems/${problem.id}/edit`),'btn btn-primary');edit.disabled=problem.status==='ARCHIVED';
    controls.append(edit,pbButton('Version history',()=>this.history(problem)));
    this.root.append(controls,pbNode('h2','Student preview'),this.studentPreview(problem));
    const manage=pbNode('details');manage.append(pbNode('summary','Author-only test cases (includes hidden tests)'));
    problem.testCases.forEach((test,index)=>manage.append(pbNode('pre',`Test ${index+1} · ${test.isHidden?'HIDDEN':'SAMPLE'}\nInput\n${test.input}\nExpected output\n${test.expectedOutput}`,'code-block')));
    this.root.append(manage);
  }
  async history(problem) {
    const token=++this.generation;this.root.replaceChildren(pbNode('p','Loading version history…'));
    try{
      const {versions}=await this.api.versions(problem.id);if(token!==this.generation)return;
      this.root.replaceChildren(pbButton('Back to problem',()=>this.navigate(`/problems/${problem.id}`)),pbNode('h1','Version history'));
      const display=pbNode('div');
      for(const version of versions){const row=pbNode('div','','pb-row');row.append(pbNode('strong',`Version ${version.version} · ${version.title} · ${version.publishedAt?'Published':'Draft'}`),pbButton('View version',async event=>{
        const button=event.currentTarget;button.disabled=true;
        try{const {problem:snapshot}=await this.api.get(problem.id,true,version.id);if(token!==this.generation)return;display.replaceChildren(pbNode('h2',`Version ${snapshot.version} (read only)`),this.studentPreview(snapshot));
          const cases=pbNode('details');cases.append(pbNode('summary','Author-only tests for this version'));snapshot.testCases.forEach(c=>cases.append(pbNode('pre',`${c.isHidden?'HIDDEN':'SAMPLE'}\n${c.input}\nExpected: ${c.expectedOutput}`,'code-block')));display.append(cases);
        }catch(error){display.replaceChildren(pbNode('p',error.message));}finally{button.disabled=false;}
      }));this.root.append(row);}this.root.append(display);
    }catch(error){if(token===this.generation)this.root.replaceChildren(pbNode('p',error.message),pbButton('Back',()=>this.navigate(`/problems/${problem.id}`)));}
  }
  editor(problem) {
    if(problem?.status==='ARCHIVED'){this.detail(problem);return;}
    this.model=problem?structuredClone(problem):{title:'',shortDescription:'',description:'',difficulty:'Easy',visibility:'Private',tags:[],inputFormat:'',outputFormat:'',constraints:'',explanation:'',testCases:[]};
    this.requestId=crypto.randomUUID();this.step=0;this.dirty=false;this.renderEditor();
  }
  renderEditor() {
    const model=this.model;
    this.root.replaceChildren(pbButton('Back to My Problems',()=>this.navigate('/problems/my')),pbNode('h1',model.id?'Edit Problem':'Create Problem'));
    if(model.id)this.root.append(pbNode('p',`Version ${model.version}${model.publishedAt?' is published. Saving changes creates a new draft version.':' · Working draft'}`));
    const steps=pbNode('nav','','pb-toolbar');steps.setAttribute('aria-label','Problem creation steps');
    ['1. Basic Information','2. Input / Output','3. Test Cases','4. Preview'].forEach((label,index)=>{const button=pbButton(label,()=>{this.step=index;this.renderEditor();},index===this.step?'btn btn-primary':'btn btn-secondary');if(index===this.step)button.setAttribute('aria-current','step');steps.append(button);});this.root.append(steps);
    const form=document.createElement('form');form.addEventListener('submit',event=>event.preventDefault());
    form.className='pb-form';
    const field=(key,label,multiline=false,max=10000)=>{
      const group=pbNode('div','','form-group');const id=`pb-${key}`;const caption=pbNode('label',label,'form-label');caption.htmlFor=id;
      const input=document.createElement(multiline?'textarea':'input');input.id=id;input.name=key;input.className='form-input';input.value=model[key];input.maxLength=max;
      if(multiline)input.rows=key==='description'?8:3;
      input.addEventListener('input',()=>{model[key]=input.value;this.dirty=true;});group.append(caption,input);form.append(group);
    };
    if(this.step===0){
      field('title','Title *',false,160);field('shortDescription','Short description',false,500);field('description','Full problem statement *',true,50000);
      const difficulty=pbSelect('Difficulty',[['Easy','Easy'],['Medium','Medium'],['Hard','Hard']]);difficulty.value=model.difficulty;difficulty.addEventListener('change',()=>{model.difficulty=difficulty.value;this.dirty=true;});
      const visibility=pbSelect('Visibility',[['Private','Private'],['Public','Public'],['Organization','Organization (not available yet)']]);visibility.lastChild.disabled=true;visibility.value=model.visibility;visibility.addEventListener('change',()=>{model.visibility=visibility.value;this.dirty=true;});
      form.append(pbNode('label','Difficulty *'),difficulty,pbNode('label','Visibility'),visibility);
      const tags=document.createElement('input');tags.className='form-input';tags.setAttribute('aria-label','Tags');tags.placeholder='array, string, hash map';tags.value=model.tags.join(', ');tags.maxLength=658;tags.addEventListener('input',()=>{model.tags=tags.value.split(',').map(t=>t.trim()).filter(Boolean);this.dirty=true;});form.append(pbNode('label','Tags (comma separated)'),tags);
    }else if(this.step===1){field('inputFormat','Input Format *',true);field('outputFormat','Output Format *',true);field('constraints','Constraints',true);field('explanation','Explanation / Notes',true);
    }else if(this.step===2){
      form.append(pbNode('p','Sample test cases are shown to students. Hidden test cases and expected outputs are available only to you for authoring. Publishing requires at least one of each.'));
      const list=pbNode('div','','pb-list');
      model.testCases.forEach((test,index)=>{
        const card=pbNode('fieldset','','pb-test');card.append(pbNode('legend',`Test ${index+1} · ${test.isHidden?'HIDDEN':'SAMPLE'}`));
        for(const [key,label] of [['input','Input'],['expectedOutput','Expected Output']]){const caption=pbNode('label',label,'form-label');const input=document.createElement('textarea');input.id=`pb-case-${index}-${key}`;caption.htmlFor=input.id;input.className='form-input';input.rows=3;input.maxLength=4096;input.value=test[key];input.addEventListener('input',()=>{test[key]=input.value;this.dirty=true;});card.append(caption,input);}
        const label=pbNode('label',' Hidden test case ');const hidden=document.createElement('input');hidden.type='checkbox';hidden.checked=test.isHidden;hidden.setAttribute('aria-label',`Test ${index+1} hidden`);hidden.addEventListener('change',()=>{test.isHidden=hidden.checked;this.dirty=true;this.renderEditor();});label.prepend(hidden);card.append(label);
        const actions=pbNode('div','','pb-toolbar');
        const duplicate=pbButton('Duplicate',()=>{model.testCases.splice(index+1,0,structuredClone(test));this.dirty=true;this.renderEditor();});duplicate.disabled=model.testCases.length>=50;
        const remove=pbButton('Delete',()=>{model.testCases.splice(index,1);this.dirty=true;this.renderEditor();});
        const up=pbButton('Move Up',()=>{[model.testCases[index-1],model.testCases[index]]=[test,model.testCases[index-1]];this.dirty=true;this.renderEditor();});up.disabled=index===0;
        const down=pbButton('Move Down',()=>{[model.testCases[index+1],model.testCases[index]]=[test,model.testCases[index+1]];this.dirty=true;this.renderEditor();});down.disabled=index===model.testCases.length-1;
        actions.append(duplicate,remove,up,down);card.append(actions);list.append(card);
      });
      const add=pbButton('+ Add Test Case',()=>{model.testCases.push({input:'',expectedOutput:'',isHidden:model.testCases.length>0});this.dirty=true;this.renderEditor();});add.disabled=model.testCases.length>=50;
      form.append(list,add,pbNode('p',`${model.testCases.filter(t=>!t.isHidden).length} samples · ${model.testCases.filter(t=>t.isHidden).length} hidden · Maximum 50 cases, 4KB input/output each.`,'text-subtle'));
    }else{form.append(pbNode('h2','Student preview'),pbNode('p','Only sample tests appear below. Review hidden cases in Step 3.'),this.studentPreview(model));}
    this.root.append(form);
    this.message=pbNode('p','');this.message.setAttribute('role','status');this.message.id='pb-save-status';
    const actions=pbNode('div','','pb-toolbar pb-editor-actions');
    const previous=pbButton('Previous step',()=>{this.step--;this.renderEditor();});previous.disabled=this.step===0;
    const next=pbButton(this.step===2?'Preview':'Next step',()=>{this.step++;this.renderEditor();});next.disabled=this.step===3;
    actions.append(previous,next,pbButton('Save Draft',()=>this.save(false)),pbButton('Publish',()=>this.save(true),'btn btn-primary'));
    this.root.append(this.message,actions);
  }
  async save(publish) {
    if(this.busy)return;
    this.busy=true;
    const controls=[...this.root.querySelectorAll('button,input,textarea,select')];const disabled=controls.map(c=>c.disabled);controls.forEach(c=>c.disabled=true);
    this.message.textContent=publish?'Saving and validating for publication…':'Saving draft…';
    const data={};for(const key of ['title','shortDescription','description','difficulty','visibility','tags','inputFormat','outputFormat','constraints','explanation'])data[key]=this.model[key];
    data.testCases=this.model.testCases.map((c,order)=>({input:c.input,expectedOutput:c.expectedOutput,isHidden:c.isHidden,order}));
    try {
      let saved;
      if(this.model.id && !this.dirty && publish && this.model.hasDraft) saved=this.model;
      else {
        const response=this.model.id?await this.api.edit(this.model.id,{...data,revision:this.model.revision}):await this.api.create({...data,requestId:this.requestId});
        saved=response.problem;this.model=saved;this.dirty=false;
        this.path=`/problems/${saved.id}/edit`;history.replaceState({},'',this.path);
      }
      if(publish){const response=await this.api.action(saved.id,'publish',{revision:saved.revision});this.model=response.problem;}
      this.dirty=false;this.renderEditor();this.message.textContent=publish?`Published version ${this.model.version}.`:'Draft saved to your Problem Bank.';
    }catch(error){this.message.textContent=error.message;}
    finally{this.busy=false;controls.forEach((c,i)=>c.disabled=disabled[i]);}
  }
}
window.ProblemBankUI=ProblemBankUI;
