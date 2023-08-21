setButton = document.getElementById('btn')
titleInput = document.getElementById('title')
setButton.addEventListener('click', () => {
  const title = titleInput.value
  window.electronAPI.getDataUpdate(title)
})


function processDataUpdate(data){
  console.log(data);
}