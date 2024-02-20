const formURL = document.getElementById('formURL');
const buttonIdnits = document.getElementById('buttonIdnits');
const buttonSubmissionCheck = document.getElementById('buttonSubmissionCheck');
const switchVerbose = document.getElementById('switchVerbose');
const switchVeryVerbose = document.getElementById('switchVeryVerbose');
const switchShowText = document.getElementById('switchShowText');
const switchSubmissionCheck = document.getElementById('switchSubmissionCheck');
const tabLinks = document.getElementsByClassName('tab-link');

// enable Bootstrap/Popper tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle2="tooltip"]'));
let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

reset();

formURL.addEventListener('keydown', submit);
buttonIdnits.addEventListener('click', idnits);
buttonSubmissionCheck.addEventListener('click', submissionCheck);
for (let tabLink of tabLinks) {
  tabLink.addEventListener('click', resetOther);
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

function submit(event) {
  formURL.classList.remove('is-invalid');
  if (event.key == 'Enter') {
    event.preventDefault();
    idnits();
  }
}

function reset() {
  for (let tooltip of tooltipList) {
    tooltip.hide();
  }

  resetButtons();
}

function resetButtons() {
  buttonIdnits.disabled = false;
  buttonIdnits.innerText = buttonIdnits.dataset.title;
  buttonSubmissionCheck.disabled = false;
  buttonSubmissionCheck.innerText = buttonSubmissionCheck.dataset.title;
}

function disableButtons() {
  buttonIdnits.disabled = true;
  buttonSubmissionCheck.disabled = true;
}

function idnits() {
  reset();

  buttonIdnits.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + buttonIdnits.innerHTML;
  disableButtons();

  if (formURL.value.length > 0) {
    if (formURL.checkValidity()) {

      url = '/api/idnits?url=' + formURL.value;
      if (switchVeryVerbose.checked) {
        url += '&verbose=2';
      } else if (!switchVerbose.checked) {
        url += '&verbose=0';
      }
      if (!switchShowText.checked) {
        url += '&hidetext=True';
      }
      if (!switchSubmissionCheck.checked) {
        url += '&submitcheck=True';
      }

      window.location.href = url;
    } else {
      formURL.classList.add('is-invalid');
      event.preventDefault();
      event.stopPropagation();
    }
  } else {
    idnitsPost(submissionCheck=false);
  }
}

function submissionCheck() {
  reset();

  buttonSubmissionCheck.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + buttonSubmissionCheck.innerHTML;
  disableButtons();

  if (formURL.value.length > 0) {
    if (formURL.checkValidity()) {
      url = '/api/idnits?url=' + formURL.value;
      url += '&submitcheck=True&hidetext=True';
      window.location.href = url;
    } else {
      formURL.classList.add('is-invalid');
      event.preventDefault();
      event.stopPropagation();
    }
  } else {
    idnitsPost(submissionCheck=true);
  }
}

function idnitsPost(submissionCheck) {
  const form = document.getElementById('form-tab-file');
  const formData = new FormData();

  if (submissionCheck) {
    formData.append('submitcheck', 'True');
  } else {
    if (switchVeryVerbose.checked) {
      formData.append('verbose', '2');
    } else if (!switchVerbose.checked) {
      formData.append('verbose', '0');
    }
    if (!switchShowText.checked) {
      formData.append('hidetext', 'True');
    }
    if (!switchSubmissionCheck.checked) {
      formData.append('submitcheck', 'True');
    }
  }

  const apiCall = '/api/idnits';
  form.method = 'POST';
  form.action = apiCall;
  form.enctype='multipart/form-data'
  for (const [key, value] of formData) {
    const hiddenField = document.createElement('input');
    hiddenField.type = 'hidden';
    hiddenField.id = key;
    hiddenField.name = key;
    hiddenField.value = value;
    form.appendChild(hiddenField);
  }
  form.submit();
}
