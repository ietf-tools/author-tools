const alertError  = document.getElementById('alertError');
const formFile1 = document.getElementById('formFile1');
const formFile2 = document.getElementById('formFile2');
const formID1 = document.getElementById('formID1');
const formID2 = document.getElementById('formID2');
const formURL1 = document.getElementById('formURL1');
const formURL2 = document.getElementById('formURL2');
const messageError = document.getElementById('messageError');
const buttonCompare = document.getElementById('buttonCompare');
const buttonWdiff = document.getElementById('buttonWdiff');
const buttonAbdiff = document.getElementById('buttonAbdiff');
const buttonChbars = document.getElementById('buttonChbars');
const divDiff = document.getElementById('divDiff');
const buttonDownload = document.getElementById('buttonDownload');
const buttonOpen = document.getElementById('buttonOpen');
const buttonShare = document.getElementById('buttonShare');
const tabLinks = document.getElementsByClassName('tab-link');
const switchRaw = document.getElementById('switchRaw');
const switchIdDiff = document.getElementById('switchIdDiff');

// enable Bootstrap/Popper tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle2="tooltip"]'));
let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

reset();

formFile1.addEventListener('change', reset);
formFile2.addEventListener('change', reset);
formID1.addEventListener('keydown', submit);
formID2.addEventListener('keydown', submit);
formURL1.addEventListener('keydown', submit);
formURL2.addEventListener('keydown', submit);
buttonCompare.addEventListener('click', compare);
buttonWdiff.addEventListener('click', compare);
buttonAbdiff.addEventListener('click', compare);
buttonChbars.addEventListener('click', compare);
for (let tabLink of tabLinks) {
  tabLink.addEventListener('click', resetOther);
}

function submit(event) {
  if (event.key == 'Enter') {
    event.preventDefault();
    compare();
  }
}

function resetOther(event) {
  const clickedItem = event.target || event.srcElement;
  others = clickedItem.dataset.others.split(',');
  others.forEach(resetForm);
}

function resetForm(form_id) {
  const form = document.getElementById(form_id);
  form.reset();
}

function reset() {
  for (let tooltip of tooltipList) {
    tooltip.hide();
  }

  alertError.style.display = 'none';
  messageError.innerHTML = '';
  divDiff.innerHTML = '';
  buttonDownload.style.display = 'none';
  buttonDownload.setAttribute('download', '');
  buttonDownload.href = '#';
  buttonOpen.style.display = 'none';
  buttonOpen.href = '#';
  buttonShare.style.display = 'none';
  buttonShare.href = '#';
  resetButtons();
}

function resetButtons() {
  buttonCompare.disabled = false;
  buttonCompare.innerText = buttonCompare.dataset.title;
  buttonWdiff.disabled = false;
  buttonWdiff.innerText = buttonWdiff.dataset.title;
  buttonAbdiff.disabled = false;
  buttonAbdiff.innerText = buttonAbdiff.dataset.title;
  buttonChbars.disabled = false;
  buttonChbars.innerText = buttonChbars.dataset.title;
}

function disableButtons() {
  buttonCompare.disabled = true;
  buttonWdiff.disabled = true;
  buttonAbdiff.disabled = true;
  buttonChbars.disabled = true;
}

function getShareableURL(button) {
  var url = '';

  if (formID1.value.length > 0) {
    url = '/diff?doc_1=' + formID1.value;
    if (formID2.value.length > 0) {
      url += '&doc_2=' + formID2.value;
    }
    else if (formURL2.value.length > 0) {
      url += '&url_2=' + formURL2.value;
    }
  }
  else if (formURL1.value.length > 0) {
    url = '/diff?url_1=' + formURL1.value;
    if (formURL2.value.length > 0) {
      url += '&url_2=' + formURL2.value;
    }
    else if (formID2.value.length > 0) {
      url += '&doc_2=' + formID2.value;
    }
  }
  else if (formID2.value.length > 0) {
    url = '/diff?doc_2=' + formID2.value;
  }
  else if (formURL2.value.length > 0) {
    url = '/diff?url_2=' + formURL2.value;
  }

  if (button.value == 'wdiff') {
    url += '&wdiff=1'
  }

  if (button.value == 'abdiff') {
    url += '&abdiff=1'
  }

  if (button.value == 'chbars') {
    url += '&chbars=1'
  }

  if (switchRaw.checked) {
    url += '&raw=1'
  }

  if (switchIdDiff.checked) {
    url += '&iddiff=1'
  }

  return url;
}

function getDownloadFilename(file1, file2, type) {
    filename = ''
    if (file1) {
      filename = file1.name.replace(/\.[^/.]+$/, '');
    }
    else if (file2) {
      filename = file2.name.replace(/\.[^/.]+$/, '');
    }
    else if (formID1.value.length > 0) {
      filename = formID1.value;
    }
    else if (formURL1.value.length > 0) {
      filename = formURL1.value;
    }
    else if (formID2.value.length > 0) {
      filename = formID2.value;
    }
    else if (formURL2.value.length > 0) {
      filename = formURL2.value;
    }

    if (type == 'abdiff' || type == 'chbars') {
      return filename + '.diff.txt';
    } else {
      return filename + '.diff.html';
    }
}

function compare(event) {
  reset();

  var button = event.target || event.srcElement;

  button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + button.innerHTML;
  disableButtons();

  const formData = new FormData();
  const file1 = formFile1.files[0];
  const file2 = formFile2.files[0];

  formData.append('file_1', file1);
  formData.append('file_2', file2);

  if (formID1.value.length > 0) {
    formData.append('doc_1', formID1.value);
  }
  if (formID2.value.length > 0) {
    formData.append('doc_2', formID2.value);
  }
  if (formURL1.value.length > 0) {
    formData.append('url_1', formURL1.value);
  }
  if (formURL2.value.length > 0) {
    formData.append('url_2', formURL2.value);
  }
  if (button.value == 'wdiff') {
    formData.append('wdiff', 1);
  }
  if (button.value == 'abdiff') {
    formData.append('abdiff', 1);
  }
  if (button.value == 'chbars') {
    formData.append('chbars', 1);
  }
  if (switchRaw.checked) {
    formData.append('raw', 1);
  }
  if (switchIdDiff.checked) {
    formData.append('iddiff', 1);
  }

  const apiCall = '/api/iddiff';

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
      return response.blob();
    })
    .then(blob => {
      if (blob.type == 'application/json') {
        alertError.style.display = 'block';
        return blob.text();
      }
      else {
        data = URL.createObjectURL(blob);
        buttonDownload.style.display = 'block';
        buttonDownload.setAttribute('download', getDownloadFilename(file1, file2, button.value));
        buttonDownload.href = data;
        buttonOpen.style.display = 'block';
        buttonOpen.href = data;

        if (!file1 && !file2) {
          buttonShare.style.display = 'block';
          buttonShare.href = getShareableURL(button);
        }

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

        if (button.value == 'wdiff') {
          var html = document.createElement( 'html' );
          html.innerHTML = data;
          divDiff.innerHTML = html.getElementsByTagName('body')[0].innerHTML;
        } else if (button.value == 'abdiff' || button.value == 'chbars') {
          var pre = document.createElement( 'pre' );
          var text = document.createTextNode(data)
          pre.appendChild(text);
          divDiff.innerHTML = pre.outerHTML;
        } else {
          var html = document.createElement( 'html' );
          html.innerHTML = data;
          divDiff.appendChild(html.getElementsByTagName('table')[0]);
        }
      }
    })
    .catch((error) => {
      resetButtons();
      alertError.style.display = 'block';
      messageError.innerHTML = error;
    });
}
