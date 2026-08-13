const alertError  = document.getElementById('alertError');
const buttonDownload = document.getElementById('buttonDownload');
const buttonCheck = document.getElementById('buttonCheck');
const formFile = document.getElementById('formFile');
const messageError = document.getElementById('messageError');
const accordionYANGValidate = document.getElementById('accordionYANGValidate');
const accordionItemErrors = document.getElementById('accordionItemErrors');
const accordionItemYANGValidate = document.getElementById('accordionItemYANGValidate');
const preErrors = document.getElementById('preErrors');
const preYANGValidate = document.getElementById('preYANGValidate');

// enable Bootstrap/Popper tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

reset();

buttonCheck.addEventListener('click', parse);

function reset() {
  for (let tooltip of tooltipList) {
    tooltip.hide();
  }

  alertError.style.display = 'none';
  accordionItemErrors.style.display = 'none';
  accordionItemYANGValidate.style.display = 'none';
  buttonCheck.disabled = false;
  buttonCheck.innerHTML = buttonCheck.dataset.title;
  preErrors.innerHTML = '';
  preYANGValidate.innerHTML = '';
}

function parse() {
  reset();

  buttonCheck.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + buttonCheck.innerHTML;
  buttonCheck.disabled = true;

  apiCall = '/api/yang/validate'

  const formData = new FormData();
  const file = formFile.files[0];

  formData.append('file', file);

  const request = new Request(apiCall, {
    method: 'POST',
    body: formData
  });

  fetch(request)
    .then(function(response) { return response.json(); })
    .then(function(json) {
      reset();
      if (json.errors) {
        accordionItemErrors.style.display = 'block';
        preErrors.innerText = json.errors;
      }
      if (json.pyang) {
        accordionItemYANGValidate.style.display = 'block';
        preYANGValidate.innerText = json.svgcheck;
      }
      if (json.error) {
        alertError.style.display = 'block';
        messageError.innerText = json.error;
      }
      accordionYANGValidate.scrollIntoView();
    })
    .catch((error) => {
      alertError.style.display = 'block';
      messageError.innerText = error;
    });
}
