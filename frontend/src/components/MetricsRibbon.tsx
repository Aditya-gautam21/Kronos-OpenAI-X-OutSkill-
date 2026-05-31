"use client";

import { TrendingUp, Activity, Crosshair, DollarSign, Power, AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import { fetchMetrics, fetchBotStatus, startBot } from "@/lib/api";

export function MetricsRibbon() {
  const [isActive, setIsActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [botStatus, setBotStatus] = useState<{ message: string; type: "success" | "error" | null }>({
    message: "",
    type: null,
  });

  const [totalPnl, setTotalPnl] = useState(0);
  const [winRate, setWinRate] = useState(0);
  const [activeStrategies, setActiveStrategies] = useState(0);
  const [drawdown, setDrawdown] = useState(0);
  const [totalExecutions, setTotalExecutions] = useState(0);

  const refreshMetrics = useCallback(async () => {
    try {
      const [m, bs] = await Promise.all([fetchMetrics(), fetchBotStatus()]);
      setTotalPnl(m.total_pnl ?? 0);
      setWinRate(m.win_rate ?? 0);
      setActiveStrategies(m.active_strategies ?? 0);
      setDrawdown(m.drawdown ?? 0);
      setTotalExecutions(bs.total_executions ?? 0);
      setIsActive(bs.is_running ?? false);
    } catch {
      // backend not reachable — keep last values
    }
  }, []);

  useEffect(() => {
    refreshMetrics();
    const interval = setInterval(refreshMetrics, 5000);
    return () => clearInterval(interval);
  }, [refreshMetrics]);

  const pnlColor = totalPnl >= 0 ? "text-green-neon" : "text-red-400";
  const pnlSign = totalPnl >= 0 ? "+" : "";

  const handleToggleBot = async () => {
    setIsLoading(true);
    setBotStatus({ message: "Executing autonomous pipeline...", type: null });
    try {
      const res = await startBot();
      if (res.status === "error") {
        setBotStatus({ message: `Error: ${res.reason}`, type: "error" });
      } else if (res.status === "skipped") {
        setBotStatus({ message: `Skipped: ${res.reason}`, type: "success" });
      } else {
        setBotStatus({ message: "Trade executed successfully", type: "success" });
      }
      await refreshMetrics();
    } catch (e: any) {
      setBotStatus({ message: `Failed to connect: ${e.message || e}`, type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mb-6 space-y-4">
      <div className="flex flex-col md:flex-row justify-between items-center bg-panel border border-panel-border rounded-lg p-4 gap-4">
        <div className="flex-1">
          <h2 className="text-lg font-bold text-white tracking-wider">AUTONOMOUS PIPELINE</h2>
          <p className="text-xs text-zinc-400 font-mono">
            System is currently {isActive ? "running" : "idle"}. {totalExecutions > 0 ? `${totalExecutions} trades executed.` : "Agents standing by."}
          </p>

          {botStatus.message && (
            <div
              className={`mt-3 flex items-center gap-2 text-xs font-mono px-3 py-2 rounded-md border ${
                botStatus.type === "error"
                  ? "bg-red-500/10 text-red-400 border-red-500/30"
                  : botStatus.type === "success"
                  ? "bg-green-neon/10 text-green-neon border-green-neon/30"
                  : "bg-cyan-neon/10 text-cyan-neon border-cyan-neon/30"
              }`}
            >
              {botStatus.type === "error" ? (
                <AlertCircle className="w-4 h-4" />
              ) : botStatus.type === "success" ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                <Loader2 className="w-4 h-4 animate-spin" />
              )}
              {botStatus.message}
            </div>
          )}
        </div>
        <button
          onClick={handleToggleBot}
          disabled={isLoading}
          className={`flex items-center justify-center min-w-[240px] gap-2 px-6 py-3 rounded-md font-mono font-bold tracking-widest text-sm transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed ${
            isActive
              ? "bg-red-500/10 text-red-500 border border-red-500/50 hover:bg-red-500 hover:text-white shadow-[0_0_15px_rgba(239,68,68,0.3)]"
              : "bg-cyan-neon/10 text-cyan-neon border border-cyan-neon/50 hover:bg-cyan-neon hover:text-black shadow-[0_0_15px_rgba(0,240,255,0.3)]"
          }`}
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Power className="w-4 h-4" />}
          {isLoading ? "STARTING..." : isActive ? "STOP PIPELINE" : "START AUTONOMOUS BOT"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: "TOTAL PNL (LIVE)",
            value: `${pnlSign}$${totalPnl.toFixed(2)}`,
            subValue: "Real-time from Binance",
            icon: DollarSign,
            color: pnlColor,
          },
          {
            label: "ACTIVE STRATEGIES",
            value: `${activeStrategies} / 12`,
            subValue: "Open positions",
            icon: Activity,
            color: activeStrategies > 0 ? "text-cyan-neon" : "text-zinc-500",
          },
          {
            label: "GLOBAL DRAWDOWN",
            value: `${drawdown.toFixed(1)}%`,
            subValue: "Max limit: -5.0%",
            icon: TrendingUp,
            color: drawdown < -2 ? "text-orange-neon" : "text-zinc-500",
          },
          {
            label: "WIN RATE",
            value: `${winRate.toFixed(1)}%`,
            subValue: "Trailing 30D",
            icon: Crosshair,
            color: winRate >= 50 ? "text-green-neon" : "text-zinc-500",
          },
        ].map((metric, i) => (
          <div key={i} className="glass-panel rounded-lg p-5 flex flex-col justify-between relative overflow-hidden group">
            <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-5 blur-2xl group-hover:opacity-10 transition-opacity bg-current ${metric.color}`} />

            <div className="flex justify-between items-start mb-4">
              <span className="text-xs font-mono font-bold text-zinc-500 tracking-wider">{metric.label}</span>
              <metric.icon className={`w-4 h-4 ${metric.color}`} />
            </div>

            <div>
              <div className={`text-3xl font-bold font-mono tracking-tight ${metric.color === "text-zinc-500" ? "text-white" : metric.color}`}>
                {metric.value}
              </div>
              <div className="text-xs mt-2 font-mono text-zinc-400">{metric.subValue}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
