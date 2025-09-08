import React from 'react';
import ReactApexChart from 'react-apexcharts';

const Chart = () => {
    const products = JSON.parse(JSON.parse(document.getElementById('products').textContent));

    // Bar Chart Data
    const barSeries = [{
        name: 'Product Prices',
        data: products.map(product => parseFloat(product.fields.price))
    }];

    const barOptions = {
        chart: {
            height: 350,
            type: 'bar',
        },
        plotOptions: {
            bar: {
                borderRadius: 10,
                dataLabels: {
                    position: 'top',
                },
            }
        },
        dataLabels: {
            enabled: true,
            offsetY: -20,
            style: {
                fontSize: '12px',
                colors: ["#304758"]
            }
        },
        xaxis: {
            categories: products.map(product => product.fields.name),
            position: 'top',
            axisBorder: { show: false },
            axisTicks: { show: false },
        },
        yaxis: {
            axisBorder: { show: false },
            axisTicks: { show: false },
            labels: { show: false }
        },
        title: {
            text: 'Product Prices',
            floating: true,
            offsetY: 330,
            align: 'center',
            style: { color: '#444' }
        }
    };

    // Donut Chart Data
    const donutSeries = products.map(product => parseFloat(product.fields.price));
    const donutLabels = products.map(product => product.fields.name);

    const donutOptions = {
        chart: {
            type: 'donut',
            height: 350,
        },
        labels: donutLabels,
        responsive: [{
            breakpoint: 480,
            options: {
                chart: {
                    width: 200
                },
                legend: {
                    position: 'bottom'
                }
            }
        }],
        dataLabels: {
            enabled: false
        },
        legend: {
            position: 'right',
            offsetY: 0,
            height: 230,
        }
    };

    return (
        <div style={{ display: 'flex', gap: '20px', padding: '20px' }}>
            <div style={{ flex: 1 }}>
                <ReactApexChart
                    options={barOptions}
                    series={barSeries}
                    type="bar"
                    height={350}
                />
            </div>
            <div style={{ flex: 1 }}>
                <ReactApexChart
                    options={donutOptions}
                    series={donutSeries}
                    type="donut"
                    height={350}
                />
            </div>
        </div>
    );
};

export default Chart;