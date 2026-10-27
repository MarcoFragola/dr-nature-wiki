export const normalize=value=>String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().trim();
// Bounded edit distance is used only on similarly sized words, after exact matching.
export function nearWord(a,b,limit=1){
  if(Math.abs(a.length-b.length)>limit)return false;
  let prev=Array.from({length:b.length+1},(_,i)=>i),older=null;
  for(let i=1;i<=a.length;i++){
    const row=[i];let best=i;
    for(let j=1;j<=b.length;j++){
      row[j]=Math.min(row[j-1]+1,prev[j]+1,prev[j-1]+(a[i-1]===b[j-1]?0:1));
      if(older&&i>1&&j>1&&a[i-1]===b[j-2]&&a[i-2]===b[j-1])row[j]=Math.min(row[j],older[j-2]+1);
      best=Math.min(best,row[j]);
    }
    if(best>limit)return false;older=prev;prev=row;
  }
  return prev[b.length]<=limit;
}
export function matchesText(text,query){
  const hay=normalize(text),q=normalize(query);if(!q||hay.includes(q))return true;
  const words=hay.split(/[^a-z0-9]+/);
  return q.split(/\s+/).every(token=>words.some(word=>word.includes(token)||(token.length>=4&&nearWord(word,token,token.length>7?2:1))));
}
