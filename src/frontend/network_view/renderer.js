let back_button = document.getElementById("back_button");
back_button.onclick = () => {
  window.electronAPI.loadHome();
};
