/* Shared room records are authoritative on the server, never in browser storage. */
class RoomService {
  constructor() {
    try { localStorage.removeItem('cb_rooms_history'); } catch (_) { /* Legacy cache is never read. */ }
  }
  async request(path='', method='GET', body) {
    const response=await fetch(`/api/rooms${path}`,{method,credentials:'same-origin',
      headers:{'Content-Type':'application/json'},...(body===undefined?{}:{body:JSON.stringify(body)})});
    const data=await response.json();
    if(!response.ok){const error=new Error(data.error||'Unable to load rooms.');error.status=response.status;throw error;}
    return data;
  }
  getRooms(search='',page=1) {return this.request('?'+new URLSearchParams({search,page}));}
  createRoom(body) {return this.request('','POST',body);}
  getRoomByCode(key) {return this.request('/'+encodeURIComponent(key));}
  action(key,action) {return this.request('/'+encodeURIComponent(key)+'/'+action,'POST',{});}
}
if(typeof window!=='undefined')window.RoomService=RoomService;
if(typeof module!=='undefined'&&module.exports)module.exports=RoomService;
