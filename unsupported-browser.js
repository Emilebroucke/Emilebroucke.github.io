function getBrowser() {
  const ua = navigator.userAgent; let tem; let 
    M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
  if (/trident/i.test(M[1])) {
    tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
    return { name: 'IE', version: (tem[1] || '') };
  }
  if (window.navigator.userAgent.indexOf('Edg') > -1) {
    tem = ua.match(/Edg\/(\d+)/)
    if (tem != null) { return { name: 'Edge', version: tem[1] }; }      
  }
  if (M[1] === 'Chrome') {
    tem = ua.match(/\bOPR\/(\d+)/)
    if (tem != null) { return { name: 'Opera', version: tem[1] }; }
  }
  M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
  tem = ua.match(/version\/(\d+)/i);
  if (tem !== null) { 
    M.splice(1, 1, tem[1]);
  }
  return {
    name: M[0],
    version: +M[1],
  };
}

// check browser to see if it's IE and redirect to unsupported browser webpage

const browser = getBrowser();

if (browser.name === 'IE') {
  window.location = 'unsupported-browser.html';
}
