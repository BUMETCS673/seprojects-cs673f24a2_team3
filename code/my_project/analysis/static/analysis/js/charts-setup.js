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
      title: {
        text: `Top ${data.length}`,
        left: 'center',
        top: '5%',
        textStyle: {
          color: isDark ? '#fff' : '#000' // Match title color to theme
        }
      },
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
        inRange: { color: ['#65B581', '#FFCE34', '#FD665F'] },
        textStyle: {
          color: isDark ? '#fff' : '#000' // Adjust text color based on theme
        }
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
              const grossFormatted = new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD',
                  minimumFractionDigits: 2
              }).format(params.value[2]);
      
              return `Title: ${params.data[3]}<br/>Rating: ${params.value[0]}<br/>Awards: ${params.value[1]}<br/>Gross Revenue: ${grossFormatted}`;
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
    legend: {
      ...commonOptions.legend,
      top: 'bottom',
      data: data.inner.map(item => item.name).concat(data.outer.map(item => item.name))
    },
    series: [
      {
        name: 'Top 3 Genres Distribution',
        type: 'pie',
        radius: ['0%', '30%'],
        label: {
          position: 'inner',
          formatter: '{b}',
          fontSize: 13,
          fontWeight: 'bold',
          color: isDark ? '#333333' : '#000' // Set the label color in dark theme with a light black color #333333 instead of default white color
        },
        labelLine: { show: false },
        data: data.inner
      },
      {
        name: 'Rating Distribution',
        type: 'pie',
        radius: ['40%', '70%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: isDark ? '#333' : '#fff',
          borderWidth: 2
        },
        label: {
          position: 'outside',
          formatter: '{b}: {c} ({d}%)',
          color: isDark ? '#fff' : '#000'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold',
            color: isDark ? '#fff' : '#000'
          }
        },
        data: data.outer
      }
    ]
  };
}
else if (type === 'funnel') {
  options = {
    ...commonOptions,
    legend: {
      ...commonOptions.legend,
      orient: 'vertical',
      top: 'middle',
      left: 'left',
      data: data.map(item => item.name)
    },
    series: [
      {
        name: 'Movies Produced',
        type: 'funnel',
        left: '10%',
        top: '5%',
        bottom: '5%',
        width: '80%',
        min: 0,
        max: data[0].value,  // Set max dynamically based on highest count
        minSize: '20%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: {
          show: true,
          position: 'inside',
          fontSize: 14,
          color: isDark ? '#fff' : '#000',
          formatter: (params) => {
            return `{${params.name === 'United Kingdom' || params.name === 'France' ? 'ukStyle' : 'defaultStyle'}|${params.name}}`;
          },
          rich: {
            ukStyle: {
              color: '#000',  // Specific color for United Kingdom
              //fontWeight: 'bold'
            },
            defaultStyle: {
              color: isDark ? '#fff' : '#000'  // Default color for other countries
            }
          }
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid',
            color: isDark ? '#fff' : '#000'
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2
        },
        data: data
      }
    ]
  };
}
else if (type === 'tree') {
  options = {
      ...commonOptions,
      series: [
          {
              type: 'tree',
              data: data,
              top: '5%',
              left: '10%',
              bottom: '5%',
              right: '10%',
              symbolSize: 10,
              label: {
                  position: 'top',
                  verticalAlign: 'middle',
                  align: 'right',
                  fontSize: 10,
                  color: isDark ? '#ffffff' : '#000000'
              },
              leaves: {
                  label: {
                      position: 'right',
                      verticalAlign: 'middle',
                      align: 'left'
                  }
              },
              expandAndCollapse: true,
              initialTreeDepth: 2,
              animationDuration: 750,
              animationEasing: 'linear'
          }
      ]
  };
}
else if (type === 'stacked-bar') {
  // Define color set
  const colorSet = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', 
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'
  ];

// Custom legend order: Drama first, Others last
  const customOrder = ["Drama", ...data.genres.filter(genre => genre !== "Drama" && genre !== "Others"), "Others"];
// Reorder the series based on the custom order
  const orderedSeries = customOrder.map((name) => {
  const sid = data.genres.indexOf(name); // Get the original index of the genre
  return {
    name, // Genre name
    type: 'bar',
    stack: 'total',
    barWidth: '60%',
    label: {
      show: false,
      formatter: params => `${(params.value * 100).toFixed(1)}%`,
      color: isDark ? '#ffffff' : '#000000',
    },
    data: data.data.map(row => row[sid]), // Map the corresponding data column
  };
});
 
  // Construct options for the chart
  options = {
    ...commonOptions,
    title: {
      left: 'center',
      textStyle: { color: isDark ? '#ffffff' : '#000000' }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function (params) {
        // Extract axis value from the first parameter
        const axisValue = params[0]?.axisValueLabel || 'Unknown';
        let tooltipText = `<strong>${axisValue}</strong><br>`; // Axis value at the top

        // Iterate over series data
        params.forEach((param) => {
            if (param.seriesName && param.data) {
                const percentage = param.data * 100; // Convert value to percentage
                tooltipText += `${param.seriesName}: ${percentage.toFixed(1)}%<br>`;
            }
        });

        return tooltipText || 'No data available';
      },
      axisPointer: {
        type: 'shadow' // For bar charts
      }
    },
    legend: {
      data: data.genres, // Series names
      textStyle: { color: isDark ? '#ffffff' : '#000000' },
      data: customOrder, // Use the reordered legend
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '15%'
    },
    xAxis: {
      type: 'category',
      data: data.languages, // x-axis categories
      axisLine: { lineStyle: { color: isDark ? '#ffffff' : '#000000' } },
      axisLabel: { color: isDark ? '#ffffff' : '#000000' }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1, // Limit the Y-axis to 1
      axisLine: { lineStyle: { color: isDark ? '#ffffff' : '#000000' } },
      axisLabel: { color: isDark ? '#ffffff' : '#000000' }
    },
    color: colorSet, // Apply the custom color set
    series: orderedSeries
  };
}

// Map options
else if (type === 'map') {
  // Prepare pie chart series for each country
  const pieSeries = data.map((country) => ({
    type: 'pie',
    coordinateSystem: 'geo',
    z: 5, // Ensure pies are rendered above the map
    radius: Math.max(10, Math.min(25, country.value /5)), // Adjust size as needed
    center: country.coordinates || [0, 0], // Fallback if coordinates are not provided
    data: country.languages.map((lang) => ({
      name: lang.name,
      value: lang.value,
    })),
    tooltip: {
      trigger: 'item',
      formatter: function (params) {
          return `${country.name}<br>${params.name}: ${params.value} (${params.percent}%)`;
      }
  },
    label: {
      show: false, // Hide labels for simplicity
    },
    labelLine: {
      show: false, // Hide connecting lines
    },
  }));

   // Define color set
   const colorSet = [
    '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', 
    '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc','#ff8c00', '#32cd32', '#8a2be2'
  ];

  options = {
    ...commonOptions,
    geo: {
      map: 'world',
      roam: true,
      itemStyle: {
        areaColor: '#e7e8ea',
        borderColor: '#999',
      },
      emphasis: {
        itemStyle: {
          areaColor: '#cbb76a',
        },
      },
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      itemGap: 10
    },
    tooltip: {
      trigger: 'item',
      formatter: function (params) {
          if (params.seriesType === 'map') {
              return params.name
                  ? `${params.name}<br>Total Movies: ${params.value || 'No data'}`
                  : 'No data';
          }
      }
  },
    color: colorSet, // Apply the custom color set
    series: [
      {
        type: 'map',
        map: 'world',
        roam: true,
        data: data.map((country) => ({
          name: country.name,
          value: country.value,
        })),
      },
      ...pieSeries, // Add pie chart series
    ],
  };
}

else if (type === 'pie and line') {
  // Transform the passed original data into the required 'source' format
  
  const sourceData = [];
  const header = ['genre', ...data.slice(1).map(row => row[0])]; // ['genre', '1921-1931', '1931-1941', ...]
  sourceData.push(header);

  for (let i = 1; i < data[0].length; i++) {
    const genreRow = [data[0][i]]; // Start with the genre name
    for (let j = 1; j < data.length; j++) {
      genreRow.push(data[j][i]); // Append counts for each interval
    }
    sourceData.push(genreRow);
  }
  // Extract genres for the legend (skip the header row)
  const genres = sourceData.slice(1).map(row => row[0]);

  // Extract year intervals for the x-axis (skip the 'genre' header)
  const yearIntervals = sourceData[0].slice(1);
  
  options = {
    ...commonOptions,
    legend: {
      top: 'top',
      data: genres, // Use genres as legend
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'line',
      },
    },
    dataset: {
      source: sourceData,
    },
    xAxis: {
      type: 'category',
      name: 'Year Interval',
      data: yearIntervals,
    },
    yAxis: {
      type: 'value',
      name: 'Movie Count',
    },
    grid: { top: '55%' },
    series: [
      // Generate a line series for each genre
      ...genres.map((genre, index) => ({
        name: genre,
        type: 'line',
        smooth: true,
        seriesLayoutBy: 'row',
        datasetIndex: 0,
        encode: {
          x: 'Year Interval',
          y: index + 1, // Offset by 1 to skip 'genre' column
        },
        emphasis: { focus: 'series' },
      })),
      // Pie chart series
      {
        type: 'pie',
        id: 'pie',
        radius: '30%',
        center: ['50%', '25%'],
        label: {
          formatter: '{b}: {c} ({d}%)',
        },
        encode: {
          itemName: 'genre',
          value: yearIntervals[0], // Default to the first year interval
          tooltip: yearIntervals[0],
        },
        data: sourceData.slice(1).map(row => ({
          name: row[0], // Genre name
          value: row[1], // Value for the first year interval
        })),
      },
    ],
  };

// Add event listener to dynamically update the pie chart
chart.on('updateAxisPointer', function (event) {
  const xAxisInfo = event.axesInfo[0];
  if (xAxisInfo) {
    const intervalIndex = xAxisInfo.value + 1; // Adjust for 0-based indexing
    const selectedInterval = sourceData[0][intervalIndex]; // Get the selected year interval

    // Update pie chart data
    const updatedPieData = sourceData.slice(1).map(row => ({
      name: row[0], // Genre name
      value: row[intervalIndex], // Value for the selected year interval
    }));

    chart.setOption({
      series: [
        {
          id: 'pie',
          label: {
            formatter: '{b}: {c} ({d}%)',
          },
          encode: {
            value: selectedInterval,
            tooltip: selectedInterval,
          },
          data: updatedPieData,
        },
      ],
    });
  }
 });
}
else if (type === 'dynamic bubble') {
  chart.showLoading();

  // Simulate data loading (use actual data variable passed from Django)
  setTimeout(function () {
    chart.hideLoading();

    // Bubble size calculation
    const sizeFunction = function (value) {
      return Math.sqrt(value)*10; // Adjust bubble size scale
    };

    // Tooltip formatter
    const tooltipFormatter = function (params) {
      const value = params.value;
      return `
        <strong>Country:</strong> ${value[3]}<br>
        <strong>Gross Revenue:</strong> $${value[0]}M<br>
        <strong>Number of Movies:</strong> ${value[1]}<br>
        <strong>Total Count:</strong> ${value[2]}
      `;
    };

    const schema = [
      { name: "Gross Revenue", index: 0, text: "Gross Revenue", unit: "M$" },
      { name: "Number of Movies", index: 1, text: "Number of Movies", unit: "" },
      { name: "Total Count", index: 2, text: "Total Count", unit: "" },
      { name: "Country", index: 3, text: "Country", unit: "" },
    ];

    // Chart options
    const options = {
      ...commonOptions,
      baseOption: {
        timeline: {
          axisType: "category",
          orient: "vertical",
          autoPlay: true,
          inverse: true,
          playInterval: 1500, // Adjust interval speed
          left: '90%',
          right: 0,
          top: 20,
          bottom: 20,
          width: 90,
          height: null,
          symbol: "none",
          checkpointStyle: {
            borderWidth: 2,
            color: "#ff5722",
          },
          controlStyle: {
            showNextBtn: false,
            showPrevBtn: false,
          },
          label: {
            position: 'right', // Keeps the labels aligned near the timeline
            formatter: '{value}', // Ensure the year interval is displayed correctly
            fontSize: 12,
            align: 'right', // Moves the text alignment to the left
            margin: 50,
          },
          data: data.map((item) => item.interval), // Populate timeline with year intervals
        },
        grid: {
          left: '10%', // Moves the chart closer to the left edge
          right: '15%', // Adjust space on the right
          top: '10%', // Keeps space from the top
          bottom: '15%', // Keeps space from the bottom
          containLabel: true, // Ensures labels are included within the grid
        },
        
        tooltip: {
          trigger: "item",
          formatter: (params) => {
            const value = params.data.value;
            const yearInterval = params.seriesName;
            return `
              Year Interval: ${yearInterval}<br>
              Country: ${value[3]}<br>
              Gross Revenue: $${value[0]}M<br>
              Number of Movies: ${value[1]}<br>
              Total Count: ${value[2]}
            `;
          },
        },
        legend: {
          top: "bottom",
          left: "center",
          data: data[0]?.data.map((d) => d.name), // Ensure the first interval contains the country names
        },
        xAxis: {
          type: "log",
          name: schema[0].text,
          nameLocation: 'end',
          nameGap: 40, // Increase the gap to move the label downward
          position: 'bottom', // Ensures it's below the axis line
          nameTextStyle: {
            align: 'right',
            verticalAlign: 'bottom',
            fontSize: 16,
          },
          splitLine: {
            show: false,
          },
          axisLabel: {
            formatter: "{value} M$",
          },
          min: 1,
          max: 12000, // Adjust based on your data range
        },
        yAxis: {
          type: "value",
          name: schema[1].text,
          nameTextStyle: {
          fontSize: 16,
          max: 'dataMax',
          },
          axisLabel: {
            formatter: "{value}",
          },
          splitLine: {
            show: false,
          },
          min: 0,
          max: 200, // Adjust based on your data range
        },
        visualMap: {
          show: true,
          type: 'piecewise',
          dimension: 3, // Use the 'country' dimension for coloring
          categories: [...new Set(data.flatMap((item) => item.data.map((d) => d.name)))], // Extract unique country names
          inRange: {
            color: ['#ff6e76', '#7cffb2', '#61a0a8', '#d48265', '#fddd60', '#4992ff', '#58d9f9', '#ff8a45', '#8d48e3', '#dd79ff'],
          },
          textStyle: {
            fontSize: 12,
          },
          orient: 'horizontal', // Set orientation to horizontal
          left: 'center', // Align to the center horizontally
          bottom: 10, // Place it at the bottom of the chart
          itemWidth: 15, // Adjust the size of the visual map legend items
          itemHeight: 15,
          },
        series: [
          {
            type: "scatter",
            encode: {
              x: 0,
              y: 1,
              tooltip: [0, 1, 2, 3],
            },
            itemStyle: {
              opacity: 0.8,
            },
            data: [], // Placeholder; updated dynamically for each interval
            symbolSize: (val) => sizeFunction(val[2]), // Bubble size based on total count
          },
        ],
        animationDurationUpdate: 1000,
        animationEasingUpdate: "quinticInOut",
      },
      options: data.map((item) => {
        // Calculate dynamic y-axis max
        const maxMovies = Math.max(...item.data.map((d) => d.value[1])); // Find the maximum number of movies for this interval
    
        return {
          title: {
            text: `${item.interval}`,
            textAlign: 'center',
            left: '50%',
            top: '10%',
            textStyle: {
              fontSize: 100, // Large font size for emphasis
              fontWeight: 'bold', // Make the text bold
          }
          },
          yAxis: {
            max: maxMovies + 10, // Add a small buffer to the max value
          },
          series: [
            {
              data: item.data, // Data for the current interval
              name: item.interval,
            },
          ],
        };
      }),
    };     

    // Apply options to chart
    chart.setOption(options);
  }, 1000); // Simulate data loading delay
}

else if (type === 'bar drilldown') {

  const broadData = data.broad;
  const detailedData = data.detailed;
  
  // Define the base chart
  let option = {
    ...commonOptions,
    xAxis: {
      name: 'Runtime (minutes)', // Label for the x-axis
      data: broadData.ranges
    },
    yAxis: {name: 'Number of Movies'},
    dataGroupId: '',
    animationDurationUpdate: 500,
    series: {
      type: 'bar',
      id: 'runtime',
      data: broadData.counts.map((value, index) => ({
        value: value,
        groupId: broadData.ranges[index]
      })),
      universalTransition: {
        enabled: true,
        divideShape: 'clone'
      }
    }
  };
  
  chart.setOption(option);
  
  // Handle drill-down on bar click
  chart.on('click', function (event) {
    if (event.data) {
      const subData = detailedData[event.data.groupId];
      console.log('subData',subData)
      if (!subData) {
        return;
      }
      chart.setOption({
        xAxis: {
          data: subData.ranges
        },
        series: {
          type: 'bar',
          id: 'runtime',
          data: subData.counts,
          universalTransition: {
            enabled: true,
            divideShape: 'clone'
          }
        },
        graphic: [
          {
            type: 'text',
            right: 30,
            top: 50,
            style: {
              text: 'Back',
              fontSize: 22,
              fontWeight: 'bold',
              fill: isDark ? '#fff' : '#000', // Add the conditional text color
            },
            onclick: function () {
              chart.setOption(option);
            }
          }
        ]
      });
    }
  });
    
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

// Assign to window object to make it globally accessible
window.initChartWithTheme = initChartWithTheme;
