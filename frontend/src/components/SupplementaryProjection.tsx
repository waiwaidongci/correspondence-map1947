import {useMemo, useState} from 'react';
import type {Run,User,ProjectionResult,SupplementaryPoint} from '../types/domain';
import {researchApi} from '../api/research';
import {Notice} from './common/Notice';
import {Table} from './common/Table';
import {useAsync} from '../hooks/useAsync';
import {dec,pct} from '../utils/format';

function template(codes:string[]){return JSON.stringify([{code:'NEW',label:'新类别',counts:Object.fromEntries(codes.map(c=>[c,0]))}],null,0);}

function parseList(text:string,axis:string):{error?:string;value?:any[]}{
 let raw:any;
 try{raw=JSON.parse(text);}catch{return {error:`补充${axis}不是合法JSON数组`};}
 if(!Array.isArray(raw)||raw.length===0)return {error:`补充${axis}须为非空JSON数组，空数组请直接留空`};
 for(const item of raw){
  if(typeof item.code!=='string'||!item.code.trim())return {error:`补充${axis}存在缺少 code 的条目`};
  if(typeof item.label!=='string'||!item.label.trim())return {error:`补充${axis} ${item.code} 缺少 label`};
  if(!item.counts||typeof item.counts!=='object'||Array.isArray(item.counts))return {error:`补充${axis} ${item.code} 的 counts 须为 {对侧code: 计数} 对象`};
  for(const [k,v] of Object.entries(item.counts)){
   if(typeof v!=='number'||!Number.isInteger(v)||v<0||v>1000000)return {error:`补充${axis} ${item.code} 对 ${k} 的计数须为0..1000000整数`};
  }
 }
 const codes=raw.map((x:any)=>x.code);
 if(new Set(codes).size!==codes.length)return {error:`补充${axis}类别 code 不得重复`};
 return {value:raw.map((x:any)=>({code:x.code.trim(),label:x.label.trim(),counts:x.counts}))};
}

export function SupplementaryProjection({run,user,result,onChange}:{run:Run;user:User;result:ProjectionResult|null;onChange:(p:ProjectionResult|null)=>void}){
 const r=run.result;
 const colCodes=useMemo(()=>(r.column_categories||[]).map(c=>c.code),[r]);
 const rowCodes=useMemo(()=>(r.row_categories||[]).map(c=>c.code),[r]);
 const [rowsText,setRowsText]=useState('');
 const [colsText,setColsText]=useState('');
 const {busy,error,message,act}=useAsync();
 const readonly=user.role==='viewer';
 const usable=run.status==='succeeded'&&r.direction_available;

 function submit(){
  const pr=rowsText.trim()?parseList(rowsText,'行'):{value:[] as any[]};
  const pc=colsText.trim()?parseList(colsText,'列'):{value:[] as any[]};
  const errors:string[]=[];
  if(pr.error)errors.push(pr.error);
  if(pc.error)errors.push(pc.error);
  if(errors.length){act(async()=>{throw new Error(errors.join('；'))});return;}
  const rowList=pr.value||[],colList=pc.value||[];
  if(!rowList.length&&!colList.length){act(async()=>{throw new Error('至少提供一个补充行或补充列')});return;}
  act(async()=>{
   const out=await researchApi.project({run_id:run.id,rows:rowList,columns:colList});
   onChange(out);
   const rejected=out.projected_points.filter(p=>p.status==='rejected').length;
   return rejected?`投影完成：${out.projected_points.length-rejected} 个可绘制，${rejected} 个被拒绝（见原因）`:'投影完成，参考轴与惯量保持不变';
  });
 }

 const rejected=(result?.projected_points||[]).filter(p=>p.status==='rejected');

 return <section className="supplementary-panel">
  <header><small>SUPPLEMENTARY / ILLUSTRATIVE POINTS</small><h2>补充类别投影：不重算参考分析</h2>
   <p>新增行/列按 code 匹配对侧活动类别，投影到本次运行的固定轴。参考点、奇异值、惯量与独立性诊断保持不变；补充点单独标示坐标与表示质量（cos²），<b>不参与轴贡献</b>。源数据变化使指纹失效时后端拒绝投影。</p></header>
  {!usable?<Notice error="参考分析未成功或没有可解释方向，暂不能投影补充点。"/>:<>
   <div className="supp-form-grid">
    <label>补充行（计数键为列 code：{colCodes.join('、')}）
     <textarea rows={4} value={rowsText} onChange={e=>setRowsText(e.target.value)} placeholder={template(colCodes)} disabled={readonly}/></label>
    <label>补充列（计数键为行 code：{rowCodes.join('、')}）
     <textarea rows={4} value={colsText} onChange={e=>setColsText(e.target.value)} placeholder={template(rowCodes)} disabled={readonly}/></label>
   </div>
   <div className="supp-actions">
    <button className="primary" disabled={busy||readonly} onClick={submit}>{busy?'投影中…':'投影到选定分析 →'}</button>
    {result&&<button disabled={busy} onClick={()=>onChange(null)}>清除结果</button>}
    {readonly&&<small>观察员只读，投影需研究员或负责人权限。</small>}
   </div>
   <Notice error={error} message={message}/>
   {result&&<div className="supp-reference">
     <span>参考N <b>{result.reference_n}</b></span><span>总惯量 <b>{dec(result.reference_total_inertia,4)}</b></span>
     <span>显示轴 <b>{result.reference_displayed_axes}</b></span><span>参考指纹 <b>{result.reference_fingerprint.slice(0,18)}…</b></span>
     <em>以上在投影中保持不变</em></div>}
   {result&&<Table headers={['补充类别','点集','状态','录入总数','主坐标(显示轴)','表示质量 cos²','χ²距离²','说明 / 拒绝原因']}>
     {result.projected_points.map((p:SupplementaryPoint)=><tr key={p.axis+p.code} className={p.status==='rejected'?'rejected-row':''}>
      <td><strong>{p.code} / {p.label}</strong>{p.missing_codes.length>0&&<small>缺省按0：{p.missing_codes.join('、')}</small>}</td>
      <td>{p.axis==='row'?'补充行':'补充列'}</td>
      <td>{p.status==='projected'?<span className="ok-pill">已投影</span>:<span className="warn-pill">已拒绝</span>}</td>
      <td>{p.supplementary_total??'—'}</td>
      <td>{p.coordinates.length?p.coordinates.map(v=>dec(v)).join(' / '):'—'}</td>
      <td>{p.display_quality==null?'—':pct(p.display_quality)}{p.centroid&&<small>质心处 cos² 无定义</small>}</td>
      <td>{p.chi_square_distance_squared==null?'—':dec(p.chi_square_distance_squared,4)}</td>
      <td className="reason-cell">{p.reason||(p.display_quality!=null&&p.display_quality<.5?'表示较差，勿仅凭图解释':'可绘制，不参与轴贡献')}</td>
     </tr>)}
   </Table>}
   {result&&rejected.length>0&&<p className="warning-copy">有 {rejected.length} 个补充类别未投影：未知 code、与活动/零边际类别撞码或零总边际都会被拒绝并说明原因，不会混入原表重算。</p>}
   {result&&<p className="fine">{result.projection_note}</p>}
  </>}
 </section>;
}
