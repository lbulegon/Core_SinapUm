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
      const n = node as {
        x?: number;
        y?: number;
        risk?: number;
        risk_index?: number;
        color?: string;
        size?: number;
      };
      const x = n.x ?? 0;
      const y = n.y ?? 0;
      const r =
        n.size != null
          ? Number(n.size) / globalScale / 4
          : 6 + (Number(n.risk ?? n.risk_index ?? 0) * 0.15) / globalScale;
      const fill = n.color || "#c45c26";
      ctx.beginPath();
      ctx.arc(x, y, r, 0, 2 * Math.PI, false);
      ctx.fillStyle = fill;
      ctx.fill();
    },
    []
  );

  return (
    <div className="graph-shell">
      <ForceGraph2D
        graphData={data}
        nodeLabel={(node: object) => {
          const n = node as { id?: string; risk?: number; risk_index?: number };
          const risk = n.risk ?? n.risk_index ?? "—";
          return `${n.id ?? "?"} (risco: ${risk})`;
        }}
        nodeCanvasObject={paint}
        nodePointerAreaPaint={(node, color, ctx, globalScale) => {
          const n = node as { x?: number; y?: number; size?: number };
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
        backgroundColor="#070605"
      />
    </div>
  );
}
