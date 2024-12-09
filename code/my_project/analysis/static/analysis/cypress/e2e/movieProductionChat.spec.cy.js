describe('Movie Production Chart', () => {
  beforeEach(() => {
      Cypress.on('window:before:load', (win) => {
          win.echarts = { init: () => ({ setOption: () => {} }),
           graphic: {
            RadialGradient: function() {} // Mock RadialGradient as a no-op function
        }};
          
          win.OverlayScrollbarsGlobal = {}; // Mock if needed
          
      });

      Cypress.on('uncaught:exception', (err) => {
          if (err.message.includes("initMovieProductionChart is not a function")) {
              return false;
          }
      });

      cy.visit('http://localhost:8000/analysis/dashboard');
      cy.wait(500); // Ensure all resources are loaded
  });

  it('defines initMovieProductionChart on the window object', () => {
      cy.window().should('have.property', 'initMovieProductionChart');
  });

//   it('renders Movie Production by Country chart correctly', () => {
//       const mockData = [
//           { value: 100, name: 'United States' },
//           { value: 80, name: 'France' },
//           { value: 60, name: 'Germany' }
//       ];

//       cy.window().then((win) => {
//           expect(win.initMovieProductionChart).to.exist;
//           win.initMovieProductionChart('movies-produced-funnel', mockData);
//       }).then(() => {
//         cy.wait(500); // Wait 500ms to ensure chart is rendered
//     });

//       cy.get('#movies-produced-funnel').should('exist');
//       //cy.get('#movies-produced-funnel').debug();
//       //cy.get('#movies-produced-funnel').contains('United States');
//   });
});
