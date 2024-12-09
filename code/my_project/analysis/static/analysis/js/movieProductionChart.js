// analysis/static/analysis/js/movieProductionChart.js


/**
 * Initializes the "Movie Production by Country" chart by calling initChartWithTheme.
 * @param {string} elementId - The ID of the DOM element to attach the chart.
 * @param {Array} data - The data for the chart.
 */
export function initMovieProductionChart(elementId, data) {
    initChartWithTheme(elementId, data, 'funnel'); // Use 'funnel' type for the movie production country chart
}

// Attach to the global `window` object
window.initMovieProductionChart = initMovieProductionChart;