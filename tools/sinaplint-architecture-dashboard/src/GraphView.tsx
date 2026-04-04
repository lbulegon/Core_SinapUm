import ForceGraph2D from "react-force-graph-2d";
import { useCallback } from "react";

type GraphData = {
  nodes: { id: string; risk?: number; risk_index?: number; color?: string; size?: number }[];
  links: { source: string; target: string }[];
};

type Props = {
  data: GraphData;
  onNodeClick: (node: object) => void;
};

export function GraphView({ data, onNodeClick }: Props) {
  const paint = useCallback(
    (node: object, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const n = node as { x?: number; y?: number; risk?: number; risk_index?: number; color?: string; size?: number };
      const x = n.x ?? 0;
      const y = n.y ?? 0;
      const r = n.size != null ? Number(n.size) / globalScale / 4 : 6 + (Number(n.risk ?? n.risk_index ?? 0) * 0.15) / globalScale;
      const fill = n.color || "#22c55e";
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI, false);
      ctx.fillStyle = fill;
      ctx.fill();
    },
    []
  );

  return (
    <div style={{ width: "100%", height: "100%", background: "#000", borderRadius: 16 }}>
      <ForceGraph2D
        graphData={data}
        nodeLabel={(node: object) => {
          const n = node as { id?: string; risk?: number; risk_index?: number; impact_score?: number };
          const risk = n.risk ?? n.risk_index ?? "—";
          return `${n.id ?? "?"} (risk: ${risk}${n.impact_score != null ? `, impact: ${n.impact_score}` : ""})`;
        }}
        nodeCanvasObject={paint}
        nodePointerAreaPaint={(node, color, ctx, globalScale) => {
          const n = node as { x?: number; y?: number; size?: number; risk?: number; risk_index?: number };
          const x = n.x ?? 0;
          const y = n.y ?? 0;
          const r = n.size != null ? Number(n.size) / globalScale / 4 : 8;
          ctx.fillStyle = color;
          ctx.beginPath();
          ctx.arc(x, y, r + 2, 0, 2 * Math.PI, false);
          ctx.fill();
        }}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        onNodeClick={onNodeClick}
        backgroundColor="#000000"
      />
    </div>
  );
}
