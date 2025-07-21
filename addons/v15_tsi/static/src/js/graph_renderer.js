/** @odoo-module **/

import { GraphRenderer } from "@web/views/graph/graph_renderer";
import { getColor } from "@web/views/graph/colors";

export class CustomGraphRenderer extends GraphRenderer {

    getBarChartData() {
        const chartData = super.getBarChartData();

        // Warna berdasarkan kolom
        const colorMap = {
            lanjut: "#1f77b4",   // Biru
            loss: "#d62728",     // Merah
            suspend: "#ffff00",  // Kuning
            bronze: "#a52a2a",   // Coklat
            silver: "#808080",   // Abu-abu
            gold: "#ffd700",     // Kuning
            "ia reten": "#49a02c", // Hijau
            sv1: "#c0c0c0",      // Silver
            sv2: "#00bfff",      // Biru muda
            rc: "#ffd700",       // Emas (Gold)
            "surveillance 1": "#C0C0C0", // Silver muda
            "surveillance 2": "#00BFFF", // Biru muda
            "recertification": "#FFD700" // Emas
        };

        chartData.datasets.forEach((dataset, datasetIndex) => {
            console.log("Label Dataset:", dataset.label); // Debugging
            const columnLabel = dataset.label?.toLowerCase();
            const color = colorMap[columnLabel] || getColor(datasetIndex);

            // Terapkan warna untuk dataset
            dataset.backgroundColor = color;
            dataset.borderColor = color;
        });

        return chartData;
    }

    getChartConfig() {
        const config = super.getChartConfig();
    
        // Pastikan plugins dan legend terdefinisi
        if (!config.options.plugins) {
            config.options.plugins = {};
        }
        if (!config.options.plugins.legend) {
            config.options.plugins.legend = {};
        }
    
        // Update legend labels untuk warna sesuai dataset
        config.options.plugins.legend.labels = {
            generateLabels: (chart) => {
                return chart.data.datasets.map((dataset, datasetIndex) => ({
                    text: dataset.label,
                    fillStyle: dataset.backgroundColor, // Gunakan warna dari backgroundColor
                    strokeStyle: dataset.borderColor || dataset.backgroundColor, // Gunakan borderColor atau backgroundColor
                    lineWidth: 1,
                    hidden: !chart.isDatasetVisible(datasetIndex),
                    datasetIndex: datasetIndex,
                }));
            },
        };
    
        // Tambahkan konfigurasi untuk plugin DataLabels
        if (!config.options.plugins.datalabels) {
            config.options.plugins.datalabels = {};
        }
    
        config.options.plugins.datalabels = {
            display: true, // Menampilkan label
            color: '#000', // Warna label
            font: {
                weight: 'bold', // Font bold
                size: 12, // Ukuran font label
            },
            formatter: function (value, context) {
                return value; // Format nilai label, bisa disesuaikan
            },
            align: 'top', // Menempatkan label di atas bar
            anchor: 'end', // Menempatkan label pada ujung bar
            offset: 5, // Memberikan jarak antara label dan bar
        };

        // config.options.plugins['afterDraw'] = function(chart) {
        //     const ctx = chart.ctx;
        //     chart.data.datasets.forEach(function(dataset, i) {
        //         dataset.data.forEach(function(value, j) {
        //             const model = chart.getDatasetMeta(i).data[j]._model;
        //             ctx.fillStyle = '#000';  // Warna label
        //             ctx.font = 'bold 12px Arial';
        //             ctx.fillText(value, model.x, model.y - 5);  // Menempatkan label di atas bar
        //         });
        //     });
        // };
    
        return config;
    }
    
}
