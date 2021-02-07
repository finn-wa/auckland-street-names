Array.from(document.getElementsByTagName('p'))
  .map((x) => x.innerText.trim())
  .filter((x) => x.length > 0 && x !== 'back to top')
  .map((x) => x.split(':'))
  .filter((arr) => arr.length == 2)
  .map((tokens) => {
    return { street: tokens[0].trim(), info: tokens[1].trim() };
  });
