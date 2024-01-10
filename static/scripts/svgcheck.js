const alertError  = document.getElementById('alertError');
const buttonDownload = document.getElementById('buttonDownload');
const buttonCheck = document.getElementById('buttonCheck');
const formFile = document.getElementById('formFile');
const messageError = document.getElementById('messageError');
const accordionSVGCheck = document.getElementById('accordionSVGCheck');
const accordionItemErrors = document.getElementById('accordionItemErrors');
const accordionItemSVGCheck = document.getElementById('accordionItemSVGCheck');
const accordionItemParsedSVG = document.getElementById('accordionItemParsedSVG');
const preErrors = document.getElementById('preErrors');
const preSVGCheck = document.getElementById('preSVGCheck');
const codeParsedSVG = document.getElementById('codeParsedSVG');

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
  accordionItemSVGCheck.style.display = 'none';
  accordionItemParsedSVG.style.display = 'none';
  buttonCheck.disabled = false;
  buttonCheck.innerHTML = buttonCheck.dataset.title;
  preErrors.innerHTML = '';
  preSVGCheck.innerHTML = '';
  codeParsedSVG.innerHTML = '';
}

function parse() {
  reset();

  buttonCheck.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>' + buttonCheck.innerHTML;
  buttonCheck.disabled = true;

  apiCall = '/api/svgcheck'

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
      if (json.svgcheck) {
        accordionItemSVGCheck.style.display = 'block';
        preSVGCheck.innerText = json.svgcheck;
      }
      if (json.svg) {
        accordionItemParsedSVG.style.display = 'block';
        text = document.createTextNode(json.svg);
        codeParsedSVG.appendChild(text);
        hljs.highlightAll();
      }
      if (json.error) {
        alertError.style.display = 'block';
        messageError.innerText = json.error;
      }
      accordionSVGCheck.scrollIntoView();
    })
    .catch((error) => {
      alertError.style.display = 'block';
      messageError.innerText = error;
    });
}
