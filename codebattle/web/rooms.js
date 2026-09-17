/* Real server-backed lobby creation, discovery, and membership. */
class RoomsUI {
  constructor() { this.page=1;this.search='';this.listRequest=0;this.lobbyRequest=0;this.busy=false; }
  init() {
    for(const id of ['btn-dash-create-room','btn-create-room-modal']) document.getElementById(id).addEventListener('click',()=>this.openCreate());
    for(const id of ['btn-close-create-room','btn-cancel-create-room']) document.getElementById(id).addEventListener('click',()=>{if(!this.busy){this.selector?.destroy();document.getElementById('modal-create-room').classList.add('hidden');}});
    document.getElementById('form-create-room').addEventListener('submit',event=>{event.preventDefault();this.create();});
    document.getElementById('room-search-form').addEventListener('submit',event=>{event.preventDefault();this.search=document.getElementById('room-search').value;this.page=1;this.load();});
    document.getElementById('btn-refresh-rooms').addEventListener('click',()=>this.load());
    document.getElementById('btn-leave-room').addEventListener('click',()=>this.membership('leave'));
    document.getElementById('btn-close-room').addEventListener('click',()=>{if(confirm('Close this room? No new participants will be able to join.'))this.membership('close');});
    document.getElementById('btn-back-to-rooms').addEventListener('click',()=>switchView('view-rooms'));
    document.getElementById('btn-room-problem-bank').addEventListener('click',()=>{this.selector?.destroy();hideAllModals();problemBankUI.navigate('/problems/my');});
    // Poll shared state, not simulated players. No overlapping requests.
    setInterval(()=>{
      if(document.hidden || this.busy)return;
      if(document.getElementById('view-rooms').classList.contains('active')&&!this.loading)this.load(true);
      if(document.getElementById('view-room-lobby').classList.contains('active')&&state.activeRoom&&!this.refreshing)this.refresh();
    },5000);
  }
  identityChanged(user) {
    const id=user?.id||null;
    if(this.identity===id)return;
    this.identity=id;this.listRequest++;this.loading=false;
    this.selector?.destroy();this.selector=null;this.selection=null;
    state.activeRoom=null;
    for(const name of ['lobby-problem','lobby-members','rooms-grid-container'])document.getElementById(name).replaceChildren();
  }
  requireAccount() {
    if(authService.isAuthenticated())return true;
    document.getElementById('btn-nav-sign-in').click();return false;
  }
  openCreate() {
    if(!this.requireAccount())return;
    this.requestId=crypto.randomUUID();this.selection=null;
    document.getElementById('input-room-title').value='';
    document.getElementById('room-create-error').textContent='';
    document.getElementById('btn-save-room').disabled=true;
    document.getElementById('modal-create-room').classList.remove('hidden');
    this.selector?.destroy();
    this.selector=new ProblemSelector(document.getElementById('room-problem-selector'),{onSelect:value=>{this.selection=value;document.getElementById('btn-save-room').disabled=false;}});
    document.getElementById('input-room-title').focus();
  }
  async create() {
    if(this.busy||!this.selection)return;
    this.busy=true;const userId=state.currentUser.id;
    const button=document.getElementById('btn-save-room');button.disabled=true;
    const message=document.getElementById('room-create-error');message.textContent='Creating room…';
    try {
      const {room}=await roomService.createRoom({title:document.getElementById('input-room-title').value,
        problemVersionId:this.selection.problemVersionId,visibility:document.getElementById('room-visibility').value,
        capacity:Number(document.getElementById('room-capacity').value),requestId:this.requestId});
      if(state.currentUser.id!==userId)return;
      this.selector?.destroy();hideAllModals();this.showLobby(room);
    }catch(error){message.textContent=error.message;}
    finally{this.busy=false;button.disabled=false;}
  }
  async load(silent=false) {
    const request=++this.listRequest;this.loading=true;
    const message=document.getElementById('rooms-status');const grid=document.getElementById('rooms-grid-container');
    if(!silent)message.textContent='Loading rooms…';
    try{
      const data=await roomService.getRooms(this.search,this.page);
      if(request!==this.listRequest)return;
      grid.replaceChildren();message.textContent=data.total?`${data.total} open room(s). Updates every 5 seconds.`:'No rooms found. Create a room or search for its title or code.';
      for(const room of data.rooms){
        const card=pbNode('article','','glass-card room-card');
        card.append(pbNode('span',room.status,'status-pill status-waiting'),pbNode('h3',room.title,'room-title'),pbNode('p',`Host: ${room.host} · Code: ${room.code}`),
          pbNode('p',`${room.problemTitle} · Version ${room.version} · ${room.diff}`),pbNode('p',`${room.players}/${room.max} participants`),
          pbButton(room.isMember?'Open Room':'Join Room',event=>this.join(room.code,event.currentTarget),'btn btn-primary btn-join-action'));
        grid.append(card);
      }
      const previous=pbButton('Previous',()=>{this.page--;this.load();});previous.disabled=this.page===1;
      const next=pbButton('Next',()=>{this.page++;this.load();});next.disabled=this.page*data.pageSize>=data.total;
      document.getElementById('rooms-pagination').replaceChildren(previous,pbNode('span',`Page ${this.page}`),next);
    }catch(error){if(request===this.listRequest){message.textContent=error.message;grid.replaceChildren();}}
    finally{if(request===this.listRequest)this.loading=false;}
  }
  async join(key,button) {
    if(!this.requireAccount())return;
    if(button)button.disabled=true;const userId=state.currentUser.id;
    try{const {room}=await roomService.action(key,'join');if(userId===state.currentUser.id)this.showLobby(room);}
    catch(error){document.getElementById('rooms-status').textContent=error.message;}
    finally{if(button)button.disabled=false;}
  }
  showLobby(room) {state.activeRoom=room;switchView('view-room-lobby');this.drawLobby(room);}
  drawLobby(room) {
    document.getElementById('lobby-room-title').textContent=room.title;
    document.getElementById('lobby-host-name').textContent=room.host;
    document.getElementById('lobby-room-code').textContent=room.code;
    document.getElementById('lobby-status').textContent=`${room.status} · ${room.players}/${room.max} participants · ${room.visibility}`;
    const members=document.getElementById('lobby-members');members.replaceChildren();
    (room.members||[]).forEach(member=>members.append(pbNode('li',`${member.username}${member.isHost?' (Host)':''}`)));
    document.getElementById('btn-leave-room').classList.toggle('hidden',room.isHost||!room.isMember||room.status==='CLOSED');
    document.getElementById('btn-close-room').classList.toggle('hidden',!room.isHost||room.status==='CLOSED');
    const problem=document.getElementById('lobby-problem');problem.replaceChildren();
    if(room.problem){problem.append(pbNode('p',`Problem locked to version ${room.version}`),problemBankUI.studentPreview(room.problem));}
  }
  async refresh() {
    if(!state.activeRoom)return;
    const key=state.activeRoom.code;const userId=state.currentUser.id;this.refreshing=true;
    try{const {room}=await roomService.getRoomByCode(key);if(state.activeRoom?.code===key&&state.currentUser.id===userId){state.activeRoom=room;this.drawLobby(room);}}
    catch(error){document.getElementById('lobby-status').textContent=error.message;}
    finally{this.refreshing=false;}
  }
  async membership(action) {
    if(this.busy||!state.activeRoom)return;this.busy=true;
    const buttons=[document.getElementById('btn-leave-room'),document.getElementById('btn-close-room')];buttons.forEach(b=>b.disabled=true);
    try{await roomService.action(state.activeRoom.code,action);state.activeRoom=null;switchView('view-rooms');}
    catch(error){document.getElementById('lobby-status').textContent=error.message;}
    finally{this.busy=false;buttons.forEach(b=>b.disabled=false);}
  }
}
window.RoomsUI=RoomsUI;
