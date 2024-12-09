// cypress/e2e/funnelDataAPI.spec.cy.js

describe('Funnel Data API', () => {
    it('should return the top 10 countries by movie production count', () => {
      // Make a request to the funnel data API
      cy.request('http://localhost:8000/analysis/funnel-data/').then((response) => {
        // Log the entire response body for debugging purposes
        cy.log(JSON.stringify(response.body));
  
        // Check if the request was successful
        expect(response.status).to.eq(200);
  
        // Ensure the response is an array
        expect(response.body).to.be.an('array');
  
        // Check that there are 10 items in the array
        expect(response.body).to.have.length(10);
  
        // Verify that each item has the expected structure
        response.body.forEach((item) => {
          expect(item).to.have.all.keys('name', 'value');
          expect(item.name).to.be.a('string');
          expect(item.value).to.be.a('number');
        });
      });
    });
  });
  
  
  
  