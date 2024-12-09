
describe('Movie Production Chart', () => {
    it('displays the chart when data is provided', () => {
        cy.visit('http://localhost:8000/analysis/dashboard'); // replace with your actual URL

        // Check if the chart container exists and is populated
        cy.get('#movies-produced-funnel').should('exist');
        cy.get('#movies-produced-funnel').should('have.class', 'echarts'); // Check for eCharts class
    });
});