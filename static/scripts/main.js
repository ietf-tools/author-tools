const alertError  = document.getElementById('alertError');
const buttonDownload = document.getElementById('buttonDownload');
const buttonOpen = document.getElementById('buttonOpen');
const formFile = document.getElementById('formFile');
const messageError = document.getElementById('messageError');
const renderButtons = document.getElementsByClassName('render-btn');
const actionButtons = document.getElementsByClassName('action-btn');
const buttonValidate = document.getElementById('buttonValidate');
const accordionValidation = document.getElementById('accordionValidation');
const accordionItemWarnings = document.getElementById('accordionItemWarnings');
const accordionItemErrors = document.getElementById('accordionItemErrors');
const accordionItemIdnits = document.getElementById('accordionItemIdnits');
const accordionItemBareUnicode = document.getElementById('accordionItemBareUnicode');
const accordionItemNonASCII = document.getElementById('accordionItemNonASCII');
const listWarnings = document.getElementById('listWarnings');
const listErrors = document.getElementById('listErrors');
const listBareUnicode = document.getElementById('listBareUnicode');
const preIdnits = document.getElementById('preIdnits');
const preNonASCII = document.getElementById('preNonASCII');
const buttonDiff = document.getElementById('buttonDiff');
const divDiff = document.getElementById('divDiff');

// enable Bootstrap/Popper tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

reset();

formFile.addEventListener('change', reset);
buttonValidate.addEventListener('click', validate);
buttonDiff.addEventListener('click', diff);

for (let button of renderButtons) {
  button.addEventListener("click", render);
}

function reset(keepDownload) {
  for (let tooltip of tooltipList) {
    tooltip.hide();
  }

  alertError.style.display = 'none';
  if (!keepDownload) {
    buttonDownload.style.display = 'none';
    buttonDownload.setAttribute('download', '');
    buttonDownload.href = '#';
    buttonOpen.style.display = 'none';
    buttonOpen.href = '#';
  }
  messageError.innerHTML = '';
  accordionValidation.style.display = 'none';
  accordionItemWarnings.style.display = 'none';
  accordionItemErrors.style.display = 'none';
  accordionItemIdnits.style.display = 'none';
  accordionItemBareUnicode.style.display = 'none';
  accordionItemNonASCII.style.display = 'none';
  listWarnings.innerHTML = '';
  listErrors.innerHTML = '';
  listBareUnicode.innerHTML = '';
  preIdnits.innerHTML = '';
  preNonASCII.innerHTML = '';
  divDiff.innerHTML = '';
  resetButtons();
}

function resetButtons() {
  for (let button of actionButtons) {
    button.disabled = false;
    button.innerText = button.dataset.title;
  }
}

function disableButtons() {
  for (let button of actionButtons) {
    button.disabled = true;
  }
}

function render(event) {
  reset();

  var button = event.target || event.srcElement;
  button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + button.innerHTML;
  disableButtons();

  const formData = new FormData();
  const format = button.value;
  const file = formFile.files[0];

  formData.append('file', file);

  const apiCall = '/api/render/' + format;

  const request = new Request(apiCall, {
    method: 'POST',
    body: formData
  });

  fetch(request)
    .then(function(response) {
      var contentType = response.headers.get('content-type');
      if (!response.ok && !(contentType && contentType.includes('application/json'))) {
        throw new Error(`There was an issue processing your request. (HTTP Status: ${response.status})`);
      }
      return response.json();
    })
    .then(function(json) {
      resetButtons();
      if (json.error) {
        alertError.style.display = 'block';
        messageError.innerHTML = json.error;
      }
      if (json.logs) {
        if (json.logs.warnings && json.logs.warnings.length > 0) {
          accordionValidation.style.display = 'block';
          accordionItemWarnings.style.display = 'block';
          for (var i in json.logs.warnings) {
            var li  = document.createElement('li');
            li.innerText = json.logs.warnings[i];
            listWarnings.appendChild(li);
          }
        }
        if (json.logs.errors && json.logs.errors.length > 0) {
          accordionValidation.style.display = 'block';
          accordionItemErrors.style.display = 'block';
          for (var i in json.logs.errors) {
            var li  = document.createElement('li');
            li.innerText = json.logs.errors[i];
            listErrors.appendChild(li);
          }
        }
      }
      if (json.url && json.url.length > 0) {
        // file rendering is successful
        download_url = json.url + '?download=1'
        buttonDownload.style.display = 'block';
        buttonDownload.setAttribute('download', download_url);
        buttonDownload.href = download_url;
        buttonOpen.style.display = 'block';
        buttonOpen.setAttribute('href', json.url);
        buttonOpen.href = json.url;
      }
    })
    .catch((error) => {
      resetButtons();
      alertError.style.display = 'block';
      messageError.innerHTML = error;
    });
}

function validate() {
  reset(true);

  buttonValidate.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + buttonValidate.innerHTML;
  disableButtons();

  const formData = new FormData();
  const file = formFile.files[0];

  formData.append('file', file);

  const apiCall = '/api/validate';

  const request = new Request(apiCall, {
    method: 'POST',
    body: formData
  });

  fetch(request)
    .then(function(response) {
      var contentType = response.headers.get('content-type');
      if (!response.ok && !(contentType && contentType.includes('application/json'))) {
        throw new Error(`There was an issue processing your request. (HTTP Status: ${response.status})`);
      }
      return response.json();
    })
    .then(function(json) {
      resetButtons();
      if (json.error) {
        alertError.style.display = 'block';
        messageError.innerHTML = json.error;
      } else {
        accordionValidation.style.display = 'block';
        if (json.warnings && json.warnings.length > 0) {
          accordionItemWarnings.style.display = 'block';
          for (var i in json.warnings) {
            var li  = document.createElement('li');
            li.innerText = json.warnings[i];
            listWarnings.appendChild(li);
          }
        }
        if (json.errors && json.errors.length > 0) {
          accordionItemErrors.style.display = 'block';
          for (var i in json.errors) {
            var li  = document.createElement('li');
            li.innerText = json.errors[i];
            listErrors.appendChild(li);
          }
        }
        if (json.bare_unicode && json.bare_unicode.length > 0) {
          accordionItemBareUnicode.style.display = 'block';
          for (var i in json.bare_unicode) {
            var li  = document.createElement('li');
            li.innerText = json.bare_unicode[i];
            listBareUnicode.appendChild(li);
          }
        }
        if (json.idnits) {
          accordionItemIdnits.style.display = 'block';
          preIdnits.innerHTML = json.idnits;
        }
        if (json.non_ascii) {
          accordionItemNonASCII.style.display = 'block';
          preNonASCII.innerHTML = json.non_ascii;
        }
      }
    })
    .catch((error) => {
      resetButtons();
      alertError.style.display = 'block';
      messageError.innerHTML = error;
    });
}

function diff() {
  reset();

  buttonDiff.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + buttonDiff.innerHTML;
  disableButtons();

  const formData = new FormData();
  const file = formFile.files[0];

  formData.append('file_1', file);
  formData.append('table', 1);
  formData.append('latest', 1);

  const apiCall = '/api/iddiff';

  const request = new Request(apiCall, {
    method: 'POST',
    body: formData
  });

  fetch(request)
    .then(response => response.blob())
    .then(blob => {
      if (blob.type == 'application/json') {
        alertError.style.display = 'block';
        return blob.text();
      }
      else {
        data_blob = URL.createObjectURL(blob);
        buttonDownload.style.display = 'block';
        buttonDownload.setAttribute('download', getDownloadFilename(file));
        buttonDownload.href = data_blob;
        buttonOpen.style.display = 'block';
        buttonOpen.href = data_blob;
        return blob.text();
      }
    })
    .then(data => {
      try {
        resetButtons();
        data = JSON.parse(data);
        messageError.innerHTML = data.error;
      } catch (error) {
        // diff is successful
        divDiff.innerHTML = data;
      }
    })
    .catch((error) => {
      resetButtons();
      alertError.style.display = 'block';
      messageError.innerHTML = error;
    });
}

function getDownloadFilename(file) {
    filename = file.name.replace(/\.[^/.]+$/, '');
    return filename + '.diff.html';
}
