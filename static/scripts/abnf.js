const formInput = document.getElementById('formInput');
const formTextAreaInput = document.getElementById('formTextAreaInput');
const buttonExtract = document.getElementById('buttonExtract');
const buttonParse = document.getElementById('buttonParse');
const accordionAbnfParse = document.getElementById('accordionAbnfParse');
const accordionItemErrors = document.getElementById('accordionItemErrors');
const preErrors = document.getElementById('preErrors');
const accordionItemAbnf = document.getElementById('accordionItemAbnf');
const preAbnf = document.getElementById('preAbnf');

// enable Bootstrap/Popper tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle2="tooltip"]'));
let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});

reset();

formInput.addEventListener('keydown', submit);
buttonExtract.addEventListener('click', extract);
buttonParse.addEventListener('click', parse);

function submit(event) {
  if (event.key == 'Enter') {
    event.preventDefault();
    extract();
  }
}

function reset() {
  for (let tooltip of tooltipList) {
    tooltip.hide();
  }

  resetButtons();
  accordionItemErrors.style.display = 'none';
  preErrors.textContent = '';
  accordionItemAbnf.style.display = 'none';
  preAbnf.textContent = '';
}

function resetButtons() {
  buttonExtract.disabled = false;
  buttonExtract.innerText = buttonExtract.dataset.title;
  buttonParse.disabled = false;
  buttonParse.innerText = buttonParse.dataset.title;
}

function disableButtons() {
  buttonExtract.disabled = true;
  buttonParse.disabled = true;
}

function extract() {
  reset();

  url = '/api/abnf/extract?';

  try {
    urlInput = new URL(formInput.value);
    url = url + 'url=' + urlInput.href;

  } catch (_) {
    url = url + 'doc=' + formInput.value;
  }

  window.location.href = encodeURI(url);
}

function parse() {
  reset();

  buttonParse.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + buttonParse.innerHTML;
  disableButtons();

  apiCall = '/api/abnf/parse'

  const formData = new FormData();
  formData.append('input', formTextAreaInput.value);

  const request = new Request(apiCall, {
    method: 'POST',
    body: formData
  });

  fetch(request)
    .then(function(response) {
      if (!response.ok) {
        throw new Error(`There was an issue processing your request. (HTTP Status: ${response.status})`);
      }
      return response.json();
    })
    .then(function(json) {
      reset();
      if (json.errors) {
        accordionItemErrors.style.display = 'block';
        preErrors.textContent = json.errors;
      }
      if (json.abnf) {
        accordionItemAbnf.style.display = 'block';
        preAbnf.textContent = json.abnf;
      }
      accordionAbnfParse.scrollIntoView();
    })
    .catch(error => {
      accordionItemErrors.style.display = 'block';
      preErrors.textContent = error;
      resetButtons();
    });
}
