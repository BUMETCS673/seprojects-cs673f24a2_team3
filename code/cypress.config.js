
// cypress.config.js

const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://app:8000', // Adjust to match your service name
    supportFile: false,
    specPattern: 'cypress/e2e/**/*.cy.js',
  },
  defaultCommandTimeout: 10000,
});
