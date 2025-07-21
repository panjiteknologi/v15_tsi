/** @odoo-module **/

import { GraphView } from "@web/views/graph/graph_view";
import { ParetoGraphView } from "./pareto_chart";
import { registry } from "@web/core/registry";

// Custom Graph View
class CustomParetoView extends GraphView {}
CustomParetoView.components.Renderer = ParetoGraphView;
registry.category("views").add("pareto_graph", CustomParetoView);
