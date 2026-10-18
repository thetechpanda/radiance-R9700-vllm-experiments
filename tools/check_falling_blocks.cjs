// Headless smoke checks with mocked DOM/canvas; not browser or rules qualification.
const fs=require('fs'),vm=require('vm'),path=require('path');
const root=path.resolve(__dirname,'..');
for(let i=0;i<4;i++){
 const file=path.join(root,`examples/rocm-7.14/falling-blocks/agent-${i}/index.html`);
 const html=fs.readFileSync(file,'utf8'); const script=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
 new vm.Script(script,{filename:file});
 const elements={},events={},frames=[];
 const gradient={addColorStop(){}};
 const ctx=new Proxy({measureText:s=>({width:String(s).length*8}),createLinearGradient:()=>gradient,createRadialGradient:()=>gradient},{get:(o,k)=>k in o?o[k]:(()=>{})});
 function el(id){return elements[id]??=new Proxy({id,width:300,height:600,style:{},textContent:'',innerHTML:'',classList:{add(){},remove(){},toggle(){}},getContext:()=>ctx,getBoundingClientRect:()=>({width:300,height:600,left:0,top:0}),addEventListener(){},blur(){},appendChild(){}},{get:(o,k)=>k in o?o[k]:undefined});}
 const sandbox={console,Math,JSON,Date,Map,Set,performance:{now:()=>0},document:{getElementById:el,querySelector:s=>el(s),querySelectorAll:()=>[],createElement:()=>el('created')},localStorage:{getItem:()=>null,setItem(){}},requestAnimationFrame:f=>frames.push(f),setTimeout:()=>1,clearTimeout(){},setInterval:()=>1,clearInterval(){}};
 sandbox.window={innerWidth:1365,innerHeight:900,devicePixelRatio:1,addEventListener:(k,f)=>(events[k]??=[]).push(f)};
 sandbox.window.window=sandbox.window; const context=vm.createContext(sandbox);
 vm.runInContext(script,context,{timeout:3000});
 function key(code){for(const kind of ['keydown','keyup'])for(const f of events[kind]||[])f({code,key:code,repeat:false,preventDefault(){}});}
 for(let t=1;t<=120;t++){const cb=frames.shift();if(cb)cb(t*16.667);}
 // Use game functions directly to avoid browser audio APIs in this headless check.
 const probes=[
  `if(state!=='playing')throw Error('not playing'); const before=piece.x;tryMove(1,0);if(piece.x!==before+1)throw Error('movement');doPause();if(state!=='paused')throw Error('pause');doPause();doHardDrop();if(score<=0)throw Error('drop score');newGame();if(score!==0)throw Error('reset');`,
  `if(state!=='playing')throw Error('not playing');const before=piece.col;tryMove(1,0);if(piece.col!==before+1)throw Error('movement');togglePause();if(state!=='paused')throw Error('pause');togglePause();hardDrop();if(score<=0)throw Error('drop score');restart();if(score!==0)throw Error('reset');`,
  `if(state!=='playing')throw Error('not playing');const before=active.col;move(1);if(active.col!==before+1)throw Error('movement');togglePause();if(state!=='paused')throw Error('pause');togglePause();hardDrop();if(score<=0)throw Error('drop score');resetGame();if(score!==0)throw Error('reset');`,
  `if(over||paused)throw Error('not playing');const before=active.col;tryMove(1,0);if(active.col!==before+1)throw Error('movement');togglePause();if(!paused)throw Error('pause');togglePause();hardDrop();if(score<=0)throw Error('drop score');newGame();if(score!==0)throw Error('reset');`
 ];
 try{vm.runInContext(probes[i],context,{timeout:3000}); console.log(`Agent ${i}: syntax, boot, 120 render frames, movement, pause, hard drop scoring and reset PASS`)}catch(e){console.log(`Agent ${i}: PROBE FAILED ${e.message}`); console.log(vm.runInContext(`JSON.stringify({state:typeof state==='undefined'?null:state,piece:typeof piece==='undefined'?null:piece})`,context));process.exitCode=1;}
}
