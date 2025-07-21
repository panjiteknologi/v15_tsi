/** @odoo-module **/

import { GraphRenderer } from "@web/views/graph/graph_renderer";
import { registry } from "@web/core/registry";
import { Component, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Chart } from "chart.js";

export class CustomParetoView extends GraphRenderer {

    setup() {
        this.orm = useService("orm");
        this.chartRef = useRef("paretoCanvas");
        onMounted(this.renderChart.bind(this));
    }

    async fetchData() {
        const data = await this.orm.call("crm.customer.survey", "search_read", [
            [],
            ["tanggal_audit", "average_score", "cumulative_percentage", "order_field"],
        ]);

        data.sort((a, b) => a.order_field - b.order_field);

        return {
            labels: data.map((item) => item.tanggal_audit),
            barValues: data.map((item) => item.average_score),
            lineValues: data.map((item) => item.cumulative_percentage),
        };
    }

    async renderChart() {
        const { labels, barValues, lineValues } = await this.fetchData();
        const ctx = this.chartRef.el.getContext("2d");

        new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        type: "bar",
                        label: "Average Score",
                        data: barValues,
                        backgroundColor: "rgba(75, 192, 192, 0.5)",
                        yAxisID: "y",
                    },
                    {
                        type: "line",
                        label: "Cumulative %",
                        data: lineValues,
                        borderColor: "red",
                        backgroundColor: "rgba(255, 0, 0, 0.5)",
                        yAxisID: "y1",
                        fill: false,
                        tension: 0.4,
                        pointStyle: "circle",
                        pointRadius: 5,
                        pointHoverRadius: 8,
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        type: "linear",
                        position: "left",
                        title: { display: true, text: "Average Score" },
                    },
                    y1: {
                        type: "linear",
                        position: "right",
                        title: { display: true, text: "Cumulative %" },
                        ticks: { callback: (value) => value + "%" },
                    },
                },
            },
        });
    }
    
}
