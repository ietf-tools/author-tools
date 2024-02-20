const formURL = document.getElementById('formURL');
const buttonIdnits = document.getElementById('buttonIdnits');
const buttonSubmissionCheck = document.getElementById('buttonSubmissionCheck');
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
}

function idnits() {
  reset();

  if (formURL.value.length > 0) {
    if (formURL.checkValidity()) {
      url = '/api/idnits3?url=' + formURL.value;
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

  if (formURL.value.length > 0) {
    if (formURL.checkValidity()) {
      url = '/api/idnits3?url=' + formURL.value;
      url += '&submitcheck=True';
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
  }

  const apiCall = '/api/idnits3';
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
