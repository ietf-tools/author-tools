const alertError  = document.getElementById('alertError');
const messageError = document.getElementById('messageError');

alertError.style.display = 'none';
messageError.textContent = '';

const apiCall = '/api/version';

const request = new Request(apiCall, {
  method: 'GET',
});

fetch(request)
  .then(function(response) { return response.json(); })
  .then(function(json) {
    document.getElementById('spanIetfat').textContent = json.versions.author_tools_api;
    document.getElementById('spanXml2rfc').textContent = json.versions.xml2rfc;
    document.getElementById('spanKramdown').textContent = json.versions['kramdown-rfc'];
    document.getElementById('spanMmark').textContent = json.versions.mmark;
    document.getElementById('spanId2xml').textContent = json.versions.id2xml;
    document.getElementById('spanIdnits').textContent = json.versions.idnits;
    document.getElementById('spanIddiff').textContent = json.versions.iddiff;
    document.getElementById('spanWeasyprint').textContent = json.versions.weasyprint;
    document.getElementById('spanAasvg').textContent = json.versions.aasvg;
    document.getElementById('spanBap').textContent = json.versions.bap;
    document.getElementById('spanSvgcheck').textContent = json.versions.svgcheck;
    document.getElementById('spanRfcdiff').textContent = json.versions.rfcdiff;
    document.getElementById('spanRst2rfcxml').textContent = json.versions.rst2rfcxml;
  })
  .catch(error => {
      alertError.style.display = 'block';
      messageError.textContent = 'Error occured while retrieving version infomation.';
  });
