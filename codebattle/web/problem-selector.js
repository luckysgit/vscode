/* Reusable selector: published metadata only, with a pinned version ID. No room dependencies. */
function pbNode(tag, text = '', className = '') {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
}
function pbButton(text, action, className = 'btn btn-secondary') {
  const node = pbNode('button', text, className);
  node.type = 'button';
  node.addEventListener('click', action);
  return node;
}
function pbSelect(label, values) {
  const select = document.createElement('select');
  select.className = 'form-select';
  select.setAttribute('aria-label', label);
  for (const [value, title] of values) {
    const option = pbNode('option', title); option.value = value; select.append(option);
  }
  return select;
}
class ProblemSelector {
  constructor(container, {api = new ProblemBankAPI(), onSelect = () => {}} = {}) {
    this.container = container; this.api = api; this.onSelect = onSelect; this.value = null; this.page = 1;
    this.generation = 0;
    const form = document.createElement('form'); form.className = 'pb-toolbar';
    this.scope = pbSelect('Problem source', [['my','My Problems'],['public','Public Problems']]);
    this.search = document.createElement('input'); this.search.className = 'form-input'; this.search.placeholder = 'Search problems…'; this.search.setAttribute('aria-label','Search selectable problems'); this.search.maxLength = 200;
    this.difficulty = pbSelect('Selector difficulty', [['','All difficulties'],['Easy','Easy'],['Medium','Medium'],['Hard','Hard']]);
    this.tag = document.createElement('input'); this.tag.className = 'form-input'; this.tag.placeholder = 'Tag'; this.tag.setAttribute('aria-label','Selector tag'); this.tag.maxLength = 32;
    this.searchButton = pbButton('Search', () => { this.page = 1; this.load(); });
    form.append(this.scope, this.search, this.difficulty, this.tag, this.searchButton);
    form.addEventListener('submit', event => { event.preventDefault(); this.page = 1; this.load(); });
    for (const control of [this.scope,this.difficulty]) control.addEventListener('change', () => { this.page=1; this.load(); });
    this.status = pbNode('p'); this.status.setAttribute('role','status');
    this.rows = pbNode('div', '', 'pb-list');
    this.selected = pbNode('p','No problem selected.','pb-selected'); this.selected.setAttribute('aria-live','polite');
    this.pager = pbNode('div','','pb-toolbar');
    container.replaceChildren(form,this.status,this.rows,this.pager,this.selected);
    this.load();
  }
  async load() {
    const generation = ++this.generation;
    this.searchButton.disabled = true; this.status.textContent = 'Loading published problems…'; this.rows.replaceChildren();
    try {
      const response = await this.api.list(this.scope.value, {search:this.search.value, difficulty:this.difficulty.value, tag:this.tag.value, selectable:'true',page:this.page});
      if (generation !== this.generation) return;
      this.status.textContent = response.total ? `${response.total} published problem(s)` : 'No published problems match. Publish a problem to select it.';
      for (const problem of response.problems) {
        const card = pbNode('div','','pb-row');
        card.append(pbNode('strong',problem.title),pbNode('p',`${problem.difficulty} · ${problem.tags.join(', ')} · Version ${problem.version} · Updated ${new Date(problem.updatedAt*1000).toLocaleDateString()}`));
        card.append(pbButton('Select', () => {
          this.value = Object.freeze({problemId:problem.id, problemVersionId:problem.problemVersionId});
          this.selected.textContent = `Selected: ${problem.title} · Version ${problem.version}`;
          this.onSelect(this.value);
          this.container.dispatchEvent(new CustomEvent('problem-selected', {detail:this.value,bubbles:true}));
        },'btn btn-primary'));
        this.rows.append(card);
      }
      const previous = pbButton('Previous',()=>{this.page--;this.load();}); previous.disabled=this.page===1;
      const next = pbButton('Next',()=>{this.page++;this.load();}); next.disabled=this.page*response.pageSize>=response.total;
      this.pager.replaceChildren(previous,pbNode('span',`Page ${this.page}`),next);
    } catch (error) { if (generation === this.generation) this.status.textContent=error.message; }
    finally { if (generation === this.generation) this.searchButton.disabled=false; }
  }
  destroy() { this.generation++; this.container.replaceChildren(); this.value=null; }
}
window.ProblemSelector = ProblemSelector;
