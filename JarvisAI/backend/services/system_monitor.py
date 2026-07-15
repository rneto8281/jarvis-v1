"""
Serviço de monitoramento de sistema.

Centraliza a coleta de métricas de hardware (CPU, RAM, disco, rede),
isolando a dependência da biblioteca ``psutil`` do restante da
aplicação (Repository/Adapter pattern) — se a fonte de dados mudar no
futuro, apenas este módulo precisa ser alterado.
"""

from __future__ import annotations

import platform
from dataclasses import dataclass

import psutil


@dataclass
class SystemSnapshot:
    """Fotografia do estado atual do sistema em um instante."""

    sistema_operacional: str
    cpu_percent: float
    ram_percent: float
    ram_usada_gb: float
    ram_total_gb: float
    disco_percent: float
    disco_usado_gb: float
    disco_total_gb: float
    rede_enviado_mb: float
    rede_recebido_mb: float
    bateria_percent: float | None
    bateria_carregando: bool | None


class SystemMonitor:
    """Coleta métricas de uso de hardware do computador local."""

    def coletar(self) -> SystemSnapshot:
        """Realiza uma coleta pontual de todas as métricas suportadas.

        Returns:
            Um :class:`SystemSnapshot` com os valores atuais.
        """

        memoria = psutil.virtual_memory()
        disco = psutil.disk_usage("/")
        rede = psutil.net_io_counters()
        bateria = self._coletar_bateria()

        return SystemSnapshot(
            sistema_operacional=f"{platform.system()} {platform.release()}",
            cpu_percent=psutil.cpu_percent(interval=0.2),
            ram_percent=memoria.percent,
            ram_usada_gb=round(memoria.used / (1024**3), 2),
            ram_total_gb=round(memoria.total / (1024**3), 2),
            disco_percent=disco.percent,
            disco_usado_gb=round(disco.used / (1024**3), 2),
            disco_total_gb=round(disco.total / (1024**3), 2),
            rede_enviado_mb=round(rede.bytes_sent / (1024**2), 2),
            rede_recebido_mb=round(rede.bytes_recv / (1024**2), 2),
            bateria_percent=bateria[0],
            bateria_carregando=bateria[1],
        )

    @staticmethod
    def _coletar_bateria() -> tuple[float | None, bool | None]:
        """Coleta dados de bateria, quando disponíveis no hardware."""

        try:
            info = psutil.sensors_battery()
        except Exception:
            return None, None

        if info is None:
            return None, None

        return round(info.percent, 1), info.power_plugged
