import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string;
  change?: number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: "up" | "down" | "neutral";
}

export function KPICard({ title, value, change, subtitle, icon, trend }: KPICardProps) {
  // Determine trend based on change if not explicitly provided
  const determinedTrend = trend || (change && change > 0 ? "up" : change && change < 0 ? "down" : "neutral");
  
  const trendColors = {
    up: "text-bts-success",
    down: "text-bts-error",
    neutral: "text-bts-gray-semi-dark",
  };
  
  const TrendIcon = determinedTrend === "up" ? TrendingUp : determinedTrend === "down" ? TrendingDown : Minus;
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon && <div className="h-4 w-4 text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {(change !== undefined || subtitle) && (
          <div className="flex items-center space-x-2 text-xs text-muted-foreground mt-1">
            {change !== undefined && (
              <span className={`flex items-center ${trendColors[determinedTrend]}`}>
                <TrendIcon className="h-3 w-3 mr-1" />
                {Math.abs(change).toFixed(2)}%
              </span>
            )}
            {subtitle && <span>{subtitle}</span>}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

