import { getDocument, OPS } from './node_modules/pdfjs-dist/legacy/build/pdf.mjs';
import fs from 'node:fs';
const doc = await getDocument({ data:new Uint8Array(fs.readFileSync(process.argv[2])) }).promise;
const page = await doc.getPage(1);
const vp = page.getViewport({ scale: 1 });
const ops = await page.getOperatorList();
const mul=(a,b)=>[a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];
const ap=(m,x,y)=>[m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5]];
let ctm=[1,0,0,1,0,0]; const st=[]; const segs=[];
for (let i=0;i<ops.fnArray.length;i++){
  const fn=ops.fnArray[i], a=ops.argsArray[i];
  if (fn===OPS.save){ st.push(ctm.slice()); continue; }
  if (fn===OPS.restore){ ctm=st.pop()||[1,0,0,1,0,0]; continue; }
  if (fn===OPS.transform){ ctm=mul(ctm,a); continue; }
  if (fn!==OPS.constructPath) continue;
  const chunks=a[1]; if(!Array.isArray(chunks)) continue;
  for (const arr of chunks){
    if (!arr || !ArrayBuffer.isView(arr)) continue;
    let k=0, cur=null;
    while (k < arr.length){
      const op=arr[k++];
      if (op===0){ cur=[arr[k++],arr[k++]]; }                 // moveTo
      else if (op===1){                                        // lineTo
        const nx=[arr[k++],arr[k++]];
        if (cur){ const A=ap(ctm,cur[0],cur[1]), B=ap(ctm,nx[0],nx[1]); segs.push([A[0],A[1],B[0],B[1]]); }
        cur=nx;
      }
      else if (op===2){ k+=6; cur=[arr[k-2],arr[k-1]]; }       // curveTo
      else if (op===3){ /* closePath */ }
      else { k = arr.length; }                                 // неизвестный код — выходим честно
    }
  }
}
const H=vp.height;
const out=segs.map(s=>({
  x0:+Math.min(s[0],s[2]).toFixed(2), x1:+Math.max(s[0],s[2]).toFixed(2),
  top:+(H-Math.max(s[1],s[3])).toFixed(2), bottom:+(H-Math.min(s[1],s[3])).toFixed(2)
})).map(s=>({...s, orient: Math.abs(s.top-s.bottom)<0.01?'h':(Math.abs(s.x0-s.x1)<0.01?'v':'d')}));
console.log(JSON.stringify({count:out.length, segs:out}));
