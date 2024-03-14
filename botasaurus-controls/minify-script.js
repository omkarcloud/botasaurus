const fs = require('fs');
const UglifyJS = require('uglify-js');

const inputFile = 'dist/index.js';
const minifiedFile = 'dist/index.js';

fs.readFile(inputFile, 'utf8', (err, data) => {
  if (err) {
    console.error('Error reading file:', err);
    return;
  }

  const minifiedCode = UglifyJS.minify(data);

  if (minifiedCode.error) {
    console.error('Error minifying code:', minifiedCode.error);
    return;
  }

  fs.writeFile(minifiedFile, minifiedCode.code, err => {
    if (err) {
      console.error('Error writing minified file:', err);
      return;
    }
    console.log('Minified file created successfully:', minifiedFile);
  });
});
