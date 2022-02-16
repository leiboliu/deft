const rmCheck = document.getElementById("rememberMe"), username=document.getElementById("username");
if (localStorage.rmcheckbox && localStorage.rmcheckbox !== "") {
  rmCheck.setAttribute("checked", "checked");
  username.value = localStorage.username;
} else {
  rmCheck.removeAttribute("checked");
  username.value = "";
}
function isRememberMe() {
  if (rmCheck.checked && username.value !== "") {
    localStorage.username = username.value;
    localStorage.rmcheckbox = rmCheck.value;
  } else {
    localStorage.username = "";
    localStorage.rmcheckbox = "";
  }
}