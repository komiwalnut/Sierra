from typing import Dict, List, Optional, Tuple
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from mpl_toolkits.basemap import Basemap
import logging
import asyncio
import numpy as np
from matplotlib.path import Path as MatPath
from matplotlib.patches import PathPatch
import matplotlib.dates as mdates
from datetime import datetime
from src.settings import CACHE_DIR

logger = logging.getLogger(__name__)


class StormVisualizer:
    def __init__(self):
        self.output_dir = CACHE_DIR
        self.output_dir.mkdir(exist_ok=True)
        self.storm_colors = ['#FF3366', '#3366FF', '#FF9933', '#33CC33']

    def _create_typhoon_symbol(self, center_x, center_y, size=80000, rotation=0, is_start=False):
        theta = np.linspace(0, 8 * np.pi, 150)
        r = size * theta / (8 * np.pi)
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        vertices = []

        for angle in [0, 90, 180, 270]:
            rad = np.radians(angle + rotation)
            rot_x = x * np.cos(rad) - y * np.sin(rad)
            rot_y = x * np.sin(rad) + y * np.cos(rad)
            vertices.extend(list(zip(rot_x + center_x, rot_y + center_y)))

        return vertices

    async def plot_storm_path(self, events: List[Dict]) -> Optional[Path]:
        if not events or not isinstance(events, list):
            logger.error("No valid events data provided")
            return None

        try:
            return await asyncio.to_thread(self._plot_storm_path_sync, events)
        except Exception as e:
            logger.exception("Failed to create storm visualization: %s", str(e))
            return None

    def _normalize_magnitude(self, magnitude: float) -> float:
        return 1 + (magnitude / 130) * 7

    def _plot_storm_path_sync(self, events: List[Dict]) -> Optional[Path]:
        try:
            fig = plt.figure(figsize=(12, 7.5))
            ax = fig.add_axes([0.1, 0.1, 0.8, 0.88])

            m = Basemap(projection='merc',
                        llcrnrlat=2,
                        urcrnrlat=23,
                        llcrnrlon=108,
                        urcrnrlon=145,
                        resolution='h',
                        ax=ax)

            m.drawcoastlines(linewidth=0.5, color='gray')
            m.drawcountries(linewidth=0.5, color='gray')
            m.drawmapboundary(fill_color='#ADE8F4')
            m.fillcontinents(color='#90BE6D', lake_color='#ADE8F4')

            m.drawparallels(np.arange(0, 25, 5), labels=[1, 0, 0, 0], fontsize=10, linewidth=0.2)
            m.drawmeridians(np.arange(105, 146, 5), labels=[0, 0, 0, 1], fontsize=10, linewidth=0.2)

            for idx, event in enumerate(events):
                if not isinstance(event, dict) or 'geometry' not in event:
                    logger.warning(f"Invalid event data at index {idx}")
                    continue

                storm_data = event.get("geometry", [])
                if not storm_data:
                    logger.warning(f"No geometry data for event {event.get('title', 'Unknown')}")
                    continue

                try:
                    lats = [point["coordinates"][1] for point in storm_data]
                    lons = [point["coordinates"][0] for point in storm_data]
                    magnitudes = [point["magnitudeValue"] for point in storm_data]
                    dates = [datetime.fromisoformat(point["date"].replace('Z', '+00:00'))
                             for point in storm_data]
                except (KeyError, IndexError) as e:
                    logger.error(f"Error extracting storm data: {e}")
                    continue

                x, y = m(lons, lats)
                color = self.storm_colors[idx % len(self.storm_colors)]

                points = np.array([x, y]).T.reshape(-1, 1, 2)
                segments = np.concatenate([points[:-1], points[1:]], axis=1)

                for i in range(len(segments)):
                    seg = segments[i]
                    width = self._normalize_magnitude(magnitudes[i])
                    plt.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                             '-', color=color, linewidth=width, alpha=0.7)

                for i in range(len(x)):
                    outer_size = 16 if i == 0 else 8
                    inner_size = 8 if i == 0 else 4

                    plt.plot(x[i], y[i], 'o',
                             markersize=outer_size + 4,
                             markerfacecolor='white',
                             markeredgecolor=color,
                             markeredgewidth=2)
                    plt.plot(x[i], y[i], 'o',
                             markersize=inner_size,
                             markerfacecolor=color,
                             markeredgecolor=color)

                for i, (px, py) in enumerate([points[0][0], points[-1][0]]):
                    if i == 0:
                        for size_mult in [1.2, 1.0, 0.8]:
                            vertices = self._create_typhoon_symbol(
                                px, py,
                                size=140000 * size_mult,
                                rotation=45 if size_mult == 1.0 else 0,
                                is_start=True
                            )
                            for j in range(0, len(vertices) - 1, 2):
                                plt.plot([vertices[j][0], vertices[j + 1][0]],
                                         [vertices[j][1], vertices[j + 1][1]],
                                         color=color,
                                         alpha=0.7 * size_mult,
                                         linewidth=2 if size_mult == 1.0 else 1)

                    else:
                        vertices = self._create_typhoon_symbol(px, py, size=80000)
                        for j in range(0, len(vertices) - 1, 2):
                            plt.plot([vertices[j][0], vertices[j + 1][0]],
                                     [vertices[j][1], vertices[j + 1][1]],
                                     color=color,
                                     alpha=0.7)

                for pos, point_date in [(points[0][0], dates[0]), (points[-1][0], dates[-1])]:
                    text = f"{event['title']}\n{point_date.strftime('%m/%d %H:%M UTC')}"
                    ha = 'right' if point_date == dates[0] else 'left'

                    outline_width = 4 if point_date == dates[0] else 3
                    plt.text(pos[0], pos[1], text,
                             color=color,
                             fontsize=12 if point_date == dates[0] else 10,
                             fontweight='bold',
                             horizontalalignment=ha,
                             verticalalignment='bottom',
                             path_effects=[path_effects.withStroke(linewidth=outline_width, foreground='white')])

                plt.plot([], [], '-', color=color,
                         label=f"{event['title']} (Max: {max(magnitudes):.0f}kts)")

            plt.legend(loc='upper right',
                       bbox_to_anchor=(0.99, 0.99),
                       fontsize=10,
                       facecolor='white',
                       edgecolor='none',
                       framealpha=0.7)

            plt.annotate("Points represent 6-hour intervals • Line width indicates storm intensity",
                         xy=(0.5, -0.07),
                         xycoords='axes fraction',
                         ha='center',
                         va='top',
                         fontsize=11,
                         fontweight='bold',
                         bbox=dict(facecolor='white',
                                   alpha=0.7,
                                   edgecolor='none',
                                   pad=2))

            output_path = self.output_dir / "storm_path.png"
            plt.savefig(output_path,
                        dpi=300,
                        bbox_inches='tight',
                        pad_inches=0.1)
            plt.close()
            return output_path

        except Exception as e:
            logger.exception("Failed to create storm visualization: %s", str(e))
            plt.close()
            return None
