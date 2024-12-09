// Function to detect the current theme
function detectTheme() {
  return document.documentElement.getAttribute("data-bs-theme") === "dark" ? "dark" : "light";
}

// Function to apply theme and data to a chart
function applyTheme(chart, data, type, theme) {
  const isDark = theme === 'dark';
  const commonOptions = {
    backgroundColor: isDark ? '#1F1F3A' : '#fff',
    tooltip: { trigger: 'item' },
    legend: {
      textStyle: { color: isDark ? '#fff' : '#000' }
    },
  };

  let options = {};

  if (type === 'pie') {
    options = {
      ...commonOptions,
      legend: {
        ...commonOptions.legend,
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: 'Movie Releases',
        type: 'pie',
        radius: ['40%', '70%'],
        data: data,
        itemStyle: {
          borderRadius: 10,
          borderColor: isDark ? '#333' : '#fff',
          borderWidth: 2
        },
        label: { show: false },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold',
            color: isDark ? '#fff' : '#000'
          }
        },
        labelLine: { show: false }
      }]
    };
  } else if (type === 'bar') {
    options = {
      ...commonOptions,
      dataset: { source: data },
      grid: { containLabel: true },
      xAxis: {
        type: 'value',
        axisLabel: { color: isDark ? '#fff' : '#000' }
      },
      yAxis: {
        type: 'category',
        inverse: true, // Ensures top values appear at the top
        axisLabel: {
          color: isDark ? '#fff' : '#000',
          formatter: function(value) {
            const maxLabelLength = 20;
            return value.length > maxLabelLength ? value.slice(0, maxLabelLength) + '...' : value;
          }
        }
      },
      visualMap: {
        orient: 'horizontal',
        left: 'center',
        min: 0,
        max: Math.max(...data.map(item => item.value)),
        text: ['High Score', 'Low Score'],
        dimension: 1,
        inRange: { color: ['#65B581', '#FFCE34', '#FD665F'] }
      },
      series: [{
        type: 'bar',
        encode: { x: 'value', y: 'name' }
      }]
    };
  }

  else if (type === 'bubble') {
    if (!Array.isArray(data) || data.length === 0) {
        console.warn("No data available for bubble chart.");
        return;
    }

    const isDark = theme === 'dark';

    options = {
        backgroundColor: isDark 
            ? new echarts.graphic.RadialGradient(0.3, 0.3, 0.8, [
                  { offset: 0, color: '#1F1F3A' }, { offset: 1, color: '#141426' }
              ])
            : new echarts.graphic.RadialGradient(0.3, 0.3, 0.8, [
                  { offset: 0, color: '#f7f8fa' }, { offset: 1, color: '#cdd0d5' }
              ]),
        title: {
            text: '',
            left: 'center',
            textStyle: { color: isDark ? '#FFFFFF' : '#000000' }
        },
        legend: {
            right: '10%',
            top: '3%',
            data: [
                { name: 'Oscar', icon: 'circle' },
                { name: 'BAFTA', icon: 'circle' }
            ],
            textStyle: { color: isDark ? '#FFFFFF' : '#000000' },
            inactiveColor: isDark ? '#666666' : '#888888' // Darker grey for light theme inactive state
        },
        grid: {
            left: '8%',
            top: '10%',
            right: '8%',
            bottom: '10%',
        },
        xAxis: {
            type: 'value',
            name: 'Rating',
            min: 7,
            max: 10,
            axisLine: {
                lineStyle: { color: isDark ? '#CCCCCC' : '#666666' }
            },
            axisLabel: { color: isDark ? '#FFFFFF' : '#000000' },
            splitLine: {
                lineStyle: { type: 'dashed', color: isDark ? '#444444' : '#DDDDDD' }
            }
        },
        yAxis: {
            type: 'value',
            name: 'Awards',
            min: 0,
            axisLine: {
                lineStyle: { color: isDark ? '#CCCCCC' : '#666666' }
            },
            axisLabel: { color: isDark ? '#FFFFFF' : '#000000' },
            splitLine: {
                lineStyle: { type: 'dashed', color: isDark ? '#444444' : '#DDDDDD' }
            },
            scale: true
        },
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `Title: ${params.data[3]}<br/>Rating: ${params.value[0]}<br/>Awards: ${params.value[1]}<br/>Gross: $${params.value[2]}`;
            }
        },
        series: [
          {
              name: 'Oscar',
              data: data.filter(movie => movie.awardType === 'Oscar').map(movie => [
                  movie.rating,
                  movie.awards,
                  movie.gross,
                  movie.title
              ]),
              type: 'scatter',
              symbolSize: function (data) {
                  return Math.cbrt(data[2]) / 15; // Adjust for visual size
              },
              emphasis: {
                  focus: 'none', // Prevents legend hover from triggering effects
                  label: {
                      show: true,
                      formatter: function (param) {
                          return param.data[3]; // Show title only on bubble hover
                      },
                      position: 'top',
                      color: '#FFFFFF'
                  }
              },
              itemStyle: {
                  shadowBlur: 10,
                  shadowColor: isDark ? 'rgba(120, 36, 50, 0.8)' : 'rgba(204, 46, 72, 0.8)', // Adjust shadow color for light theme
                  shadowOffsetY: 5,
                  color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [
                      { offset: 0, color: isDark ? 'rgb(255, 192, 0)' : 'rgb(251, 118, 123)' }, // Red gradient for light theme
                      { offset: 1, color: isDark ? 'rgb(204, 130, 0)' : 'rgb(204, 46, 72)' } // Red gradient for light theme
                  ])
              },
              legendHoverLink: false // Disable legend hover effect for this series
          },
          {
              name: 'BAFTA',
              data: data.filter(movie => movie.awardType === 'BAFTA').map(movie => [
                  movie.rating,
                  movie.awards,
                  movie.gross,
                  movie.title
              ]),
              type: 'scatter',
              symbolSize: function (data) {
                  return Math.cbrt(data[2]) / 15; // Consistent scaling
              },
              emphasis: {
                  focus: 'none', // Prevents legend hover from triggering effects
                  label: {
                      show: true,
                      formatter: function (param) {
                          return param.data[3]; // Show title only on bubble hover
                      },
                      position: 'top',
                      color: '#FFFFFF'
                  }
              },
              itemStyle: {
                  shadowBlur: 10,
                  shadowColor: isDark ? 'rgba(25, 100, 150, 0.8)' : 'rgba(25, 100, 150, 0.5)', // Ensure consistent shadow color
                  shadowOffsetY: 5,
                  color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [
                      { offset: 0, color: 'rgb(129, 227, 238)' }, // Fixed blue for both themes
                      { offset: 1, color: 'rgb(25, 183, 207)' } // Fixed blue gradient for both themes
                  ])
              },
              legendHoverLink: false // Disable legend hover effect for this series
          }
      ]
    };
    // Force ECharts to update background color correctly
    chart.setOption(options, true); // true forces a full refresh on option change
}
else if (type === 'nested_pie') {
  options = {
      ...commonOptions,
      tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
          ...commonOptions.legend,
          top: 'bottom',
          data: data.map(item => item.name)  // Extracting legend names from data
      },
      series: [
          {
              name: 'Rating Distribution',
              type: 'pie',
              radius: ['0%', '30%'],  // Inner ring
              label: {
                  position: 'inner'
              },
              data: data.inner
          },
          {
              name: 'Genres',
              type: 'pie',
              radius: ['40%', '70%'],  // Outer ring
              label: {
                  position: 'outside',
                  alignTo: 'edge',
                  formatter: '{b}: {d}%'
              },
              data: data.outer
          }
      ]
  };
}


  chart.setOption(options);
}

// Function to initialize a chart with a theme
function initChartWithTheme(domId, data, type) {
  const dom = document.getElementById(domId);
  if (!dom) {
    console.warn(`Element with ID ${domId} not found.`);
    return;
  }

  const chart = echarts.init(dom, 'dark', { renderer: 'canvas', useDirtyRect: false });
  const theme = detectTheme();
  applyTheme(chart, data, type, theme);

  const observer = new MutationObserver(() => {
    const newTheme = detectTheme();
    applyTheme(chart, data, type, newTheme);
  });
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-bs-theme'] });

  window.addEventListener('resize', () => chart.resize());
}


