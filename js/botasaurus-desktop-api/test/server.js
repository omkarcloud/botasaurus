const {
  task
} = require('botasaurus/task'); // Import the task function from botasaurus/task

const {
  Server
} = require('../src/server'); // Import the Server class from the local src/server module

// Describe block for grouping related tests
describe('Scraper functions', () => {
  // Individual test case
  it('should add a scraper to the server', async () => {
    // Define a new task named "google_maps_scraper"
    const google_maps_scraper = task({
      name: "google_maps_scraper", 
      run: async ({data}) => {
        return data; // Return the data as is
      }
    });

    // Add the scraper to the Server
    Server.addScraper({
      scraper: google_maps_scraper,
    });
  });
});