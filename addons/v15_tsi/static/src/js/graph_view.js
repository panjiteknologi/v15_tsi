/** @odoo-module **/

import { GraphView } from "@web/views/graph/graph_view";
import { CustomGraphRenderer } from "./graph_renderer";
import { registry } from "@web/core/registry";

// Custom Graph View
class CustomGraphView extends GraphView {}
CustomGraphView.components.Renderer = CustomGraphRenderer;
registry.category("views").add("custom_graph", CustomGraphView);
