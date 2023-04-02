function updateFileName() {
  var fileInput = document.getElementById("file");
  var fileName = fileInput.files[0].name;
  var fileNameDisplay = document.getElementById("file-name");
  fileNameDisplay.textContent = "Selected file: " + fileName;
}
