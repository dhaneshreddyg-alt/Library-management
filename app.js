function openIssue(id, available) {
  const modal=document.getElementById('issueModal');
  document.getElementById('issueForm').action=`/books/${id}/issue`;
  const qty=document.getElementById('issueQty');
  qty.max=available; qty.value=1;
  modal.classList.add('show');
}
function closeIssue(){document.getElementById('issueModal').classList.remove('show');}
document.getElementById('issueModal').addEventListener('click',e=>{if(e.target.id==='issueModal')closeIssue();});
