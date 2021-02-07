function scrape() {
  const tables = document.querySelectorAll('#content table tbody');
  return Array.from(tables).map((t) => Array.from(t.querySelectorAll('.normal')).map((row) => row.innerText));
}

function extract(streetTable) {
  return {
    street: streetTable[1],
    suburb: streetTable[2],
    info: streetTable[3],
  };
}

scrape().map((s) => extract(s));
